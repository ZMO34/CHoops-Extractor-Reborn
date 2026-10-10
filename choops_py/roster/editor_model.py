"""Transactional roster editor; validated field writes and unsaved undo."""
import struct
from collections import defaultdict
from ..formats.binary import Binary
from ..archive.manifests import digest
from ..core.errors import ToolError
from .schema import TABLES,STRING_FIELDS,REFERENCES,EDITABLE,POSITIONS,PALETTE_OFFSET,PALETTE_COUNT,detect_tables,RATING_OFFSET,RATING_COUNT,PLAYER_PROPERTIES,PLAYER_SCALARS,TENDENCY_OFFSET,TENDENCY_NAMES
from .adapters import load,load_bytes

class EditorModel:
    def __init__(self,source,tables=None):
        self.source=source;self.tables=dict(tables if tables is not None else detect_tables(source.payload));self.original=source.payload;self.data=bytearray(self.original)
        self.edits=[];self.history=[];self.redo_history=[]
        for name,(start,count,size) in self.tables.items():Binary(self.data).slice(start,count*size)
        self.rows={};self.issues=[];self.string_users=defaultdict(list);self.reload()
    @classmethod
    def open(cls,path):return cls(load(path))
    def row_offset(self,table,index):
        if table not in self.tables:raise ToolError('unknown_roster_table',table)
        start,count,size=self.tables[table]
        if not isinstance(index,int) or not 0<=index<count:raise ToolError('roster_index_out_of_range',f'{table} index {index}')
        return start+index*size
    def string(self,field,user):
        value=struct.unpack_from('>i',self.data,field)[0]
        if value in (0,-1):return ''
        target=field+value
        try:
            b=Binary(self.data);end=target
            for _ in range(256):
                code=b.u16(end,'<')
                if not code:
                    text=b.slice(target,end-target).decode('utf-16-le')
                    if any(ord(c)<32 for c in text):raise ValueError('Control character in roster string')
                    self.string_users[target].append(user);self.string_ranges[target]=end+2;return text
                end+=2
            raise ValueError('String exceeds 256 characters')
        except (ValueError,UnicodeError) as error:
            self.issues.append({'kind':'invalid_string_pointer','field_offset':field,'detail':str(error)});return ''
    def reference(self,field,table,bias,empty_player=False):
        delta=struct.unpack_from('>i',self.data,field)[0]
        if delta in (0,-1):return None
        start,count,size=self.tables[table];target=field+delta;index=(target-start)//size
        if not 0<=index<count or (target-start)%size!=bias:
            self.issues.append({'kind':'invalid_table_pointer','field_offset':field,'target':target,'table':table,'expected_bias':bias});return None
        return None if empty_player and index==0 else index
    def reload(self):
        self.rows={};self.issues=[];self.string_users=defaultdict(list);self.string_ranges={}
        b=Binary(self.data)
        for table,(start,count,size) in self.tables.items():
            rows=[]
            for index in range(count):
                off=start+index*size;row={'index':index,'row_offset':off}
                for name,rel in STRING_FIELDS.get(table,{}).items():row[name]=self.string(off+rel,(table,index,name))
                if table=='players':
                    row.update(jersey_number=self.data[off+0x1b],height_inches=self.data[off+0x3a],position_code=self.data[off+0x3b]);row['display_name']=(row['first_name']+' '+row['last_name']).strip();row['position']=POSITIONS.get(row['position_code'],'Unknown')
                    row['attribute_ratings'] = [max(35,min(99,b.u16(off+RATING_OFFSET+i*2)//100)) for i in range(RATING_COUNT)]
                    row['shot_tendencies'] = list(b.slice(off+TENDENCY_OFFSET,len(TENDENCY_NAMES)))
                    row['properties'] = {f['name']:(int.from_bytes(b.slice(off+f['offset'],f['size']),'big')>>f['shift'])&((1<<f['bits'])-1) for f in PLAYER_PROPERTIES}
                    for name,(rel,field_size,shift,bits,_,_) in PLAYER_SCALARS.items():
                        row[name]=(int.from_bytes(b.slice(off+rel,field_size),'big')>>shift)&((1<<bits)-1)
                elif table=='teams':
                    row['asset_id']=b.u16(off+0x18c);row['team_index_check']=b.u16(off+0x18e)
                    row['palette_colors'] = ['#'+b.slice(off+PALETTE_OFFSET+i*4,4).hex().upper() for i in range(PALETTE_COUNT)]
                    row['mascot_asset_id'] = b.u16(off+0x192)
                    for field,(rel,target,bias) in REFERENCES.items():
                        if target in self.tables:row[field]=self.reference(off+rel,target,bias)
                    row['roster_slots']=[self.reference(off+0x6c+slot*4,'players',0x11,True) for slot in range(16)]
                elif table=='conferences':
                    row['team_indices'] = []
                    for slot in range(32):
                        field = off+0x6e0+slot*4
                        if b.u32(field) in (0,0xffffffff):
                            break
                        team_index = self.reference(field,'teams',0x31)
                        if team_index is None:
                            break
                        row['team_indices'].append(team_index)
                rows.append(row)
            self.rows[table]=rows
    def validate(self):
        self.reload()
        return {'valid':not self.issues,'issues':self.issues,'source_type':self.source.kind,'counts':{name:len(rows) for name,rows in self.rows.items()},'unsaved_edits':len(self.edits),'read_only_fields':['skin tone','conference','prestige','unknown appearance bytes','long strings','unconfirmed palette roles']}
    def edit(self,table,index,field,value,slot=None):
        if field not in EDITABLE.get(table,()):raise ToolError('roster_field_read_only',f'{table}.{field} is not a confirmed writable field')
        off=self.row_offset(table,index);before=bytes(self.data);old_row=self.rows[table][index];old_value=old_row[field]
        changes=[]
        if field in STRING_FIELDS.get(table, {}):
            rel=STRING_FIELDS[table][field];pos=off+rel;delta=struct.unpack_from('>i',self.data,pos)[0]
            if delta in (0,-1):raise ToolError('missing_string_storage','Cannot create a string heap entry')
            target=pos+delta
            encoded=str(value).encode('utf-16-le');old=str(old_value).encode('utf-16-le')
            if len(encoded)!=len(old):raise ToolError('string_length_mismatch','Names must retain their original UTF-16 byte length')
            if any(ord(c)<32 for c in str(value)):raise ToolError('invalid_roster_name','Control characters are blocked')
            if len(self.string_users.get(target,[]))!=1:raise ToolError('shared_string_write_blocked','This name storage is shared with other rows; heap relocation is not validated')
            end=target+len(encoded)
            if any(other!=target and target<limit and other<end for other,limit in self.string_ranges.items()):
                raise ToolError('shared_string_write_blocked','This name overlaps another string storage range')
            if any(target<start+count*size and start<end for start,count,size in self.tables.values()):
                raise ToolError('invalid_string_storage','Name storage overlaps a fixed roster table')
            changes.append((target,encoded))
        elif table=='teams' and field=='palette_colors':
            slot = self.integer(slot)
            if not 0 <= slot < PALETTE_COUNT:
                raise ToolError('palette_slot_out_of_range','Palette slot must be 0..30')
            text = str(value).removeprefix('#')
            if len(text) != 8 or any(c not in '0123456789abcdefABCDEF' for c in text):
                raise ToolError('invalid_palette_color','Use #RRGGBBAA with eight hex digits')
            old_value = old_value[slot]
            changes.append((off+PALETTE_OFFSET+slot*4,bytes.fromhex(text)))
        elif table=='players' and field in PLAYER_SCALARS:
            value=self.integer(value)
            rel,size,shift,bits,low,high=PLAYER_SCALARS[field]
            if not low<=value<=high:raise ToolError('roster_value_out_of_range',f'{field} must be {low}..{high}')
            original=int.from_bytes(Binary(self.data).slice(off+rel,size),'big')
            mask=((1<<bits)-1)<<shift
            changes.append((off+rel,((original&~mask)|(value<<shift)).to_bytes(size,'big')))
        elif table=='players' and field=='shot_tendencies':
            slot=self.integer(slot);value=self.integer(value)
            if not 0<=slot<len(TENDENCY_NAMES) or not 0<=value<=99:
                raise ToolError('tendency_out_of_range','Tendency channel must be 0..3 and value 0..99')
            old_value=old_value[slot]
            changes.append((off+TENDENCY_OFFSET+slot,bytes([value])))
        elif table=='players' and field=='attribute_ratings':
            slot=self.integer(slot);value=self.integer(value)
            if not 0 <= slot < RATING_COUNT or not 35 <= value <= 99:
                raise ToolError('rating_out_of_range','Attribute channel must be 0..29 and rating 35..99')
            old_value=old_value[slot]
            changes.append((off+RATING_OFFSET+slot*2,struct.pack('>H',value*100)))
        elif table=='players':
            value=self.integer(value);ranges={'jersey_number':(0,99),'height_inches':(36,100),'position_code':(0,4)}
            lo,hi=ranges[field]
            if not lo<=value<=hi:raise ToolError('roster_value_out_of_range',f'{field} must be {lo}..{hi}')
            rel={'jersey_number':0x1b,'height_inches':0x3a,'position_code':0x3b}[field];changes.append((off+rel,bytes([value])))
        elif field=='asset_id':
            value=self.integer(value)
            if value not in {r['asset_id'] for r in self.rows['teams']}:raise ToolError('new_asset_id_blocked','Select an existing roster asset ID; creating new assets is not validated')
            ids=[Binary(self.data).u16(off+r) for r in (0x18c,0x190,0x194)]
            if len(set(ids))!=1:raise ToolError('asset_id_repeats_mismatch','Original repeated asset IDs disagree')
            for rel in (0x18c,0x190,0x194):changes.append((off+rel,struct.pack('>H',value)))
        else:
            if field=='roster_slots':
                slot=self.integer(slot)
                if not 0<=slot<16:raise ToolError('roster_slot_out_of_range','Slot must be 0..15')
                pos=off+0x6c+slot*4;target_table='players';bias=0x11;old_value=old_value[slot]
            else:
                rel,target_table,bias=REFERENCES[field];pos=off+rel
            value=None if value is None or str(value).strip().lower() in ('','none','-1') else self.integer(value)
            if value is None:encoded=b'\0'*4
            else:
                target=self.row_offset(target_table,value)+bias;encoded=struct.pack('>i',target-pos)
            changes.append((pos,encoded))
        for pos,data in changes:Binary(self.data).slice(pos,len(data));self.data[pos:pos+len(data)]=data
        result=self.validate()
        # Pre-existing invalid data must not be silently blessed by the editor.
        if not result['valid']:
            self.data=bytearray(before);self.reload();raise ToolError('roster_validation_failed',str(result['issues'][:5]))
        if self.data==before:return
        self.redo_history=[];self.history.append((before,list(self.edits)));self.edits.append({'table':table,'index':index,'field':field,'slot':slot,'old':old_value,'value':value})
    @staticmethod
    def integer(value):
        if isinstance(value,bool):raise ToolError('invalid_roster_value','Expected integer')
        try:
            if isinstance(value,float) and not value.is_integer():raise ValueError('Fractional value')
            return int(value)
        except (TypeError,ValueError) as error:raise ToolError('invalid_roster_value',str(value)) from error
    def undo(self):
        if self.history:
            self.redo_history.append((bytes(self.data),list(self.edits)));data,self.edits=self.history.pop();self.data=bytearray(data);self.reload()
    def redo(self):
        if self.redo_history:
            self.history.append((bytes(self.data),list(self.edits)))
            data,self.edits=self.redo_history.pop();self.data=bytearray(data);self.reload()
    def revert(self):self.data=bytearray(self.original);self.history=[];self.redo_history=[];self.edits=[];self.reload()
    def document(self):return {'schema':1,'source_type':self.source.kind,'source_sha256':digest(self.source.original),'payload_sha256':digest(self.original),'tables':self.rows,'editable_fields':{k:list(v) for k,v in EDITABLE.items()},'validation':self.validate()}
    def apply_document(self,document):
        before=bytes(self.data);history=list(self.history);edits=list(self.edits);redo=list(self.redo_history)
        try:self._apply_document(document)
        except Exception:
            self.data=bytearray(before);self.history=history;self.edits=edits;self.redo_history=redo;self.reload()
            raise
    def _apply_document(self,document):
        if document.get('source_sha256')!=digest(self.source.original):raise ToolError('roster_source_mismatch','Patch must include the original source SHA256')
        if 'edits' in document:
            for e in document['edits']:self.edit(e['table'],int(e['index']),e['field'],e['value'],e.get('slot'))
        elif 'tables' in document:
            edits=[]
            for table,rows in document['tables'].items():
                if table not in self.rows or len(rows)!=len(self.rows[table]):raise ToolError('roster_table_shape_changed',table)
                for index,row in enumerate(rows):
                    original=self.rows[table][index]
                    for field,value in row.items():
                        if field not in original:raise ToolError('roster_unknown_field',field)
                        if value==original[field]:continue
                        if field not in EDITABLE.get(table,()):raise ToolError('roster_field_read_only',field)
                        if field in ('roster_slots','palette_colors','attribute_ratings','shot_tendencies'):
                            if len(value)!=(16 if field=='roster_slots' else PALETTE_COUNT if field=='palette_colors' else RATING_COUNT if field=='attribute_ratings' else len(TENDENCY_NAMES)):raise ToolError('roster_table_shape_changed','List field length changed')
                            for slot,(a,b) in enumerate(zip(original[field],value)):
                                if a!=b:edits.append((table,index,field,b,slot))
                        else:edits.append((table,index,field,value,None))
            for args in edits:self.edit(*args)
        else:raise ToolError('invalid_roster_patch','Expected edits or tables')
