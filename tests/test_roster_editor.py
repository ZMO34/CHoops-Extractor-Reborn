import pytest
pytestmark = pytest.mark.unit
import struct
from support import WorkspaceTest,roster_fixture,iff_fixture
from choops_py.roster.adapters import load_bytes
from choops_py.roster.editor_model import EditorModel
from choops_py.roster.workflow import save_model
from choops_py.core.errors import ToolError
class RosterTests(WorkspaceTest):
    def test_decode_safe_fields_unknown_bytes_and_undo(self):
        m=roster_fixture();self.assertTrue(m.validate()['valid']);self.assertEqual(m.rows['players'][0]['first_name'],'Ana');before=bytes(m.data)
        m.edit('players',0,'jersey_number',23);m.edit('players',0,'height_inches',75);m.edit('players',0,'position_code',4)
        self.assertEqual(m.rows['players'][0]['jersey_number'],23);self.assertEqual(m.rows['players'][0]['position'],'C');self.assertEqual(m.data[0x40+0x18:0x40+0x1a],before[0x40+0x18:0x40+0x1a])
        m.undo();self.assertEqual(m.rows['players'][0]['position_code'],0);m.revert();self.assertEqual(bytes(m.data),before)
    def test_same_length_name_and_invalid_edit(self):
        m=roster_fixture();m.edit('players',0,'first_name','Ann');self.assertEqual(m.rows['players'][0]['first_name'],'Ann')
        with self.assertRaises(ToolError):m.edit('players',0,'first_name','Alex')
        with self.assertRaises(ToolError):m.edit('players',0,'position_code',8)
        with self.assertRaises(ToolError):m.edit('players',0,'skin_tone',1)
    def test_shared_string_and_invalid_pointer_validation(self):
        m=roster_fixture();target=0x40+0x14+struct.unpack_from('>i',m.data,0x40+0x14)[0];field=0x40+308+0x14;struct.pack_into('>i',m.data,field,target-field);m.reload()
        with self.assertRaises(ToolError):m.edit('players',0,'first_name','Ann')
        struct.pack_into('>i',m.data,0x40+0x10,0x7fffffff);self.assertFalse(m.validate()['valid'])
    def test_team_assignments_and_reference_bias(self):
        m=roster_fixture();m.edit('teams',0,'roster_slots',1,slot=0);self.assertEqual(m.rows['teams'][0]['roster_slots'][0],1)
        pos=0x500+0x6c;self.assertEqual(pos+struct.unpack_from('>i',m.data,pos)[0],0x40+308+0x11)
        m.edit('teams',0,'arena_index',1);m.edit('teams',0,'coach_index',1);m.edit('teams',0,'rival1_index',1);m.edit('teams',0,'asset_id',1)
        self.assertEqual(m.rows['teams'][0]['arena_index'],1);self.assertEqual([struct.unpack_from('>H',m.data,0x500+i)[0] for i in (0x18c,0x190,0x194)],[1,1,1])
        with self.assertRaises(ToolError):m.edit('teams',0,'roster_slots',9,slot=0)
    def test_source_wrapper_preservation(self):
        m=roster_fixture();payload=m.original
        sources=[load_bytes(payload),load_bytes(struct.pack('>I',len(payload))+payload),load_bytes(iff_fixture([payload],[(0xc61649b2,[0])],compressed=True,padding=128))]
        for i,source in enumerate(sources):
            model=EditorModel(source,m.tables);model.edit('players',0,'jersey_number',24);out=self.work/f'roster{i}'
            save_model(model,out);loaded=load_bytes(out.read_bytes());self.assertEqual(loaded.kind,source.kind);self.assertEqual(loaded.payload,bytes(model.data));self.assertEqual(source.original,sources[i].original)
    def test_patch_requires_matching_source(self):
        m=roster_fixture()
        with self.assertRaises(ToolError):m.apply_document({'source_sha256':'wrong','edits':[]})
    def test_patch_is_atomic(self):
        m=roster_fixture();before=bytes(m.data)
        with self.assertRaises(ToolError):m.apply_document({'source_sha256':m.document()['source_sha256'],'edits':[
            {'table':'players','index':0,'field':'jersey_number','value':24},
            {'table':'players','index':0,'field':'position','value':99}]})
        self.assertEqual(bytes(m.data),before);self.assertEqual(m.edits,[]);self.assertEqual(m.history,[])
    def test_overlapping_string_storage_is_blocked(self):
        m=roster_fixture();field=0x40+0x14;target=field+struct.unpack_from('>i',m.data,field)[0]
        other=0x40+308+0x14;struct.pack_into('>i',m.data,other,target+2-other);m.reload();before=bytes(m.data)
        with self.assertRaises(ToolError):m.edit('players',1,'first_name','XY')
        self.assertEqual(bytes(m.data),before)
