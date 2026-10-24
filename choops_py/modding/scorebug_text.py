"""Bounded PS3 SCNE text bindings and authored font-style properties.

Style entries serialize a 16-byte value followed by type/key/reserved words.
They are not key/value records starting at the type word. Runtime text callbacks
select by text-record name; bone names stay independent of those bindings.
"""
import math
import struct
import zlib
from collections import Counter

from ..formats.binary import Binary

FONT = 0xbf045bdb
COLOR = (0x6109ea5a, 0x97de0310, 0x6814845a)
SHADOW = (0x53c67207, 0x661f09b0, 0x7dfc668b)


def _records(header):
    b=Binary(header);count=b.u32(0x4c)
    if count>4096:raise ValueError('SCNE text count exceeds limit')
    table=b.relative(0x50) if count else 0;b.slice(table,count*144)
    if count and table%16:raise ValueError('SCNE text table must be 16-byte aligned')
    records={}
    for i in range(count):
        at=table+i*144;name=b.utf16(b.relative(at+64),'be')
        if name in records:raise ValueError('Ambiguous SCNE text binding')
        style=b.relative(at+80);n=b.u32(style)
        if style%16:raise ValueError('SCNE text properties must be 16-byte aligned for native vector loads')
        if n>1024:raise ValueError('SCNE text property count exceeds limit')
        b.slice(style+16,n*32);properties={}
        for j in range(n):
            value=style+16+j*32;kind=b.u32(value+16);key=b.u32(value+20)
            if key in properties:raise ValueError('Ambiguous SCNE text property')
            properties[key]=(value,kind)
        records[name]=(at,properties)
    return b,records


def inspect_styles(header):
    b,records=_records(header);rows=[]
    for name,(at,properties) in records.items():
        font=None
        if FONT in properties:
            value,kind=properties[FONT]
            if kind!=3:raise ValueError('Font alias is not a string property')
            font=b.utf16(b.relative(value),'be') if b.u32(value) else ''
        def values(keys):
            return [b.u32(properties[k][0]) if k in properties and properties[k][1]==0 else None for k in keys]
        literal=None
        if 0x72b6694d in properties and 0x92f9b3f9 in properties:
            flags,flag_type=properties[0x72b6694d];vector,vector_type=properties[0x92f9b3f9]
            if flag_type==0 and vector_type==2 and b.u32(flags)&0x10:
                lo,hi=struct.unpack('>2f',b.slice(vector,8))
                if not all(math.isfinite(v) and 0<=v<=65535 and v==int(v) for v in (lo,hi)):raise ValueError('Invalid literal text ID vector')
                literal=(int(hi)<<16)|int(lo)|1
        alpha=properties.get(0xad44372a)
        alpha=struct.unpack('>f',b.slice(alpha[0],4))[0] if alpha and alpha[1]==1 else None
        rows.append(dict(binding=name,font=font,color=values(COLOR),shadow=values(SHADOW),literal_id=literal,alpha=alpha))
    return rows


def inspect_text_dependencies(parts):
    """Report observed split-HUD text owners/markers and indexed draw activity.

    Zero submitted triangles is diagnostic evidence, not proof that the engine
    suppresses text. Alpha, native culling, stencil and GPU state are not modeled.
    """
    if len(parts) != 2:
        raise ValueError('Text dependency audit requires a split HUD scene')
    b, records = _records(parts[0])
    payload = Binary(parts[1])
    count = b.u32(0x44)
    if count > 4096:
        raise ValueError('HUD model count exceeds audit limit')
    table = b.relative(0x48) if count else 0
    b.slice(table, count * 176)
    models = {}
    index_budget = 0
    bone_budget = 0
    draw_budget = 0
    for i in range(count):
        at = table + i * 176
        name = b.utf16(b.relative(at), 'be')
        if name in models:
            raise ValueError('Ambiguous HUD model ' + name)
        bones = b.u32(at + 0x60)
        bone_budget += bones
        if bone_budget > 100000:
            raise ValueError('HUD bone count exceeds audit limit')
        bone_table = b.relative(at + 0x64) if bones else 0
        b.slice(bone_table, bones * 48)
        markers = [
            b.utf16(b.relative(bone_table + j * 48 + 32), 'be')
            for j in range(bones)
        ]
        if len(set(markers)) != len(markers):
            raise ValueError('Ambiguous HUD marker in ' + name)
        marker_hashes = {
            marker: b.u32(bone_table + j * 48 + 36)
            for j, marker in enumerate(markers)
        }
        if b.u32(at + 0x84) != 1 or b.u32(at + 0xa4) != 0x20000010:
            raise ValueError('Unsupported split HUD index/stream layout')
        descriptor = b.relative(at + 0x88)
        vertices = b.u32(descriptor + 16)
        index_count = b.u32(at + 0xa8)
        index_budget += index_count
        if index_budget > 2000000 or not 1 <= vertices <= 250000:
            raise ValueError('HUD geometry exceeds audit limit')
        indices = struct.unpack(
            '>' + str(index_count) + 'H',
            payload.slice(b.u32(at + 0xac) - 1, index_count * 2),
        )
        if any(x != 65535 and x >= vertices for x in indices):
            raise ValueError('HUD index outside vertex buffer')
        runs = b.u32(at + 0x7c)
        if runs > 10000:
            raise ValueError('HUD draw count exceeds audit limit')
        draw = b.relative(at + 0x80) if runs else 0
        b.slice(draw, runs * 48)
        triangles = 0
        for j in range(runs):
            primitive, first, size = struct.unpack(
                '>3I', b.slice(draw + j * 48, 12),
            )
            if primitive != 6 or first + size > index_count:
                raise ValueError('Unsupported HUD draw/index range')
            draw_budget += size
            if draw_budget > 2000000:
                raise ValueError('HUD submitted indices exceed audit limit')
            strip = []
            for index in indices[first:first + size]:
                if index == 65535:
                    strip = []
                else:
                    strip.append(index)
                    if len(strip) >= 3 and len(set(strip[-3:])) == 3:
                        triangles += 1
        models[name] = dict(
            markers=markers, bones=bones, submitted_triangles=triangles,
            marker_hashes=marker_hashes,
            marker_hash_counts=dict(Counter(marker_hashes.values())),
        )
    rows = []
    for binding, (_, properties) in records.items():
        names = []
        for key in (0xe27ec83b, 0xae7e1958):
            item = properties.get(key)
            if item is None or item[1] != 3 or not b.u32(item[0]):
                raise ValueError('Text model/marker string missing: ' + binding)
            names.append(b.utf16(b.relative(item[0]), 'be'))
        owner, marker = names
        model = models.get(owner)
        # Observed native bone lookup (7f9ab8) compares +36, not the name.
        # ASCII marker hashes match case-sensitive CRC32 in supplied HUDs.
        # Do not invent the conversion/hash contract for non-ASCII names.
        native_marker_resolved = None
        if marker.isascii():
            wanted = zlib.crc32(marker.encode('ascii')) & 0xffffffff
            native_marker_resolved = (
                model is not None
                and model['marker_hashes'].get(marker) == wanted
                and model['marker_hash_counts'].get(wanted) == 1
            )
        rows.append(dict(
            binding=binding, owner=owner, marker=marker,
            resolved=model is not None and marker in model['markers'],
            native_marker_resolved=native_marker_resolved,
            owner_submitted_triangles=(
                model['submitted_triangles'] if model is not None else None
            ),
        ))
    return dict(
        mode='read-only', text=rows, models=models,
        runtime_visibility_verified=False,
    )


def edit_styles(parts, changes):
    if len(parts)!=2:raise ValueError('Text styles require a split SCNE')
    b,records=_records(parts[0]);out=bytearray(parts[0]);names=set(records);report=[]
    for name,change in changes.items():
        if name not in records:raise ValueError('Unknown SCNE text binding '+name)
        if set(change)-{'font','binding','literal_id','align','alpha','color','max_width'}:raise ValueError('Unsupported SCNE text style edit')
        at,properties=records[name]
        if 'max_width' in change:
            width=change['max_width'];limit=properties.get(0x11fa397c);flags=properties.get(0x72b6694d)
            if type(width) not in (int,float) or not math.isfinite(width) or not 0<width<=4096:raise ValueError('Invalid native text width')
            if limit is None or limit[1]!=0 or flags is None or flags[1]!=0:raise ValueError('Missing native text width/flags properties')
            if any(sum(1 for _,props in records.values() if props.get(key)==properties[key])!=1 for key in (0x11fa397c,0x72b6694d)):raise ValueError('Native text width properties are shared')
            # Loader reads this numeric property through the generic conversion
            # accessor. Source stores an integer; preserve its serialized type.
            if width!=int(width):raise ValueError('Native text width must use whole authored units')
            struct.pack_into('>I',out,limit[0],int(width))
            struct.pack_into('>I',out,flags[0],b.u32(flags[0])|0x100)
        for option,keys,kind in [('alpha',(0xad44372a,),1),('color',COLOR,0)]:
            if option not in change:continue
            values=[change[option]] if option=='alpha' else change[option]
            if not isinstance(values,(list,tuple)) or len(values)!=len(keys):raise ValueError('Invalid text '+option)
            if option=='alpha':
                if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in values):raise ValueError('Invalid text alpha')
            elif any(type(v) is not int or not 0<=v<=255 for v in values):raise ValueError('Invalid text color')
            for key,value in zip(keys,values):
                prop=properties.get(key)
                if prop is None or prop[1]!=kind:raise ValueError('Missing typed text '+option+' property')
                if sum(1 for _,props in records.values() if props.get(key)==prop)!=1:raise ValueError('Text '+option+' property is shared')
                struct.pack_into('>f' if kind==1 else '>I',out,prop[0],value)
        for option in ('font','binding'):
            if option not in change:continue
            value=change[option]
            if not isinstance(value,str) or not 1<=len(value)<=128 or any(ord(c)<32 for c in value):raise ValueError('Invalid SCNE text string')
            if option=='font':
                if FONT not in properties or properties[FONT][1]!=3:raise ValueError('Missing string font property')
                field=properties[FONT][0]
                if sum(1 for _,props in records.values() if FONT in props and props[FONT][0]==field)!=1:raise ValueError('Font property is shared by another text record')
            else:
                if value in names and value!=name:raise ValueError('SCNE text binding already exists')
                names.discard(name);names.add(value);field=at+64
            out.extend(bytes((-len(out))%4));target=len(out);out.extend(value.encode('utf-16-be')+bytes(2))
            struct.pack_into('>I',out,field,target-field+1)
        if 'literal_id' in change or 'align' in change:
            flags=properties.get(0x72b6694d)
            if flags is None or flags[1]!=0:raise ValueError('Missing integer text flags')
            if sum(1 for _,props in records.values() if props.get(0x72b6694d)==flags)!=1:raise ValueError('Text flags are shared by another record')
            value=struct.unpack_from('>I',out,flags[0])[0]
            if 'literal_id' in change:
                key=change['literal_id'];vector=properties.get(0x92f9b3f9)
                if type(key) is not int or not 0<key<0xffffffff or not key&1:raise ValueError('Invalid literal text ID')
                if vector is None or vector[1]!=2:raise ValueError('Missing literal ID vector')
                if sum(1 for _,props in records.values() if props.get(0x92f9b3f9)==vector)!=1:raise ValueError('Literal vector is shared by another record')
                struct.pack_into('>2f',out,vector[0],key&0xffff,key>>16);value|=0x10
            if 'align' in change:
                if change['align']!='center':raise ValueError('Only confirmed center alignment is writable')
                value=(value&~0x30000)|0x30000
            struct.pack_into('>I',out,flags[0],value)
        report.append(dict(source=name,**change))
    if len(out)>len(parts[0]):out.extend(bytes((-len(out))%4))
    result=[bytes(out),parts[1]]
    # Reparse, including duplicate-name and property-layout guards.
    inspect_styles(result[0])
    return result,report
