import csv
import io
import pytest
from support import roster_fixture
from choops_py.roster import bulk

pytestmark=pytest.mark.unit


def test_jump_shot_write_preserves_all_other_bytes_and_undo():
    model=roster_fixture();before=bytes(model.data)
    model.edit('players',0,'jump_shot_code',111)
    changed=[i for i,(a,b) in enumerate(zip(before,model.data)) if a!=b]
    assert changed==[model.row_offset('players',0)+0x83]
    assert model.rows['players'][0]['jump_shot_code']==111
    with pytest.raises(ValueError):model.edit('players',0,'jump_shot_code',112)
    model.undo();assert bytes(model.data)==before


@pytest.mark.parametrize('field,limit',[('short_name',16),('school_name',16),('abbreviation',4),('mascot_plural',16),('event_name',64),('student_section',32)])
def test_school_text_uses_confirmed_game_capacity_not_existing_length(field,limit):
    model=roster_fixture();before=bytes(model.data)
    assert model.name_capacity('teams',0,field)==limit
    model.edit('teams',0,field,'X'*limit)
    assert model.rows['teams'][0][field]=='X'*limit
    with pytest.raises(ValueError):model.edit('teams',0,field,'X'*(limit+1))
    model.undo();assert bytes(model.data)==before


@pytest.mark.parametrize('field,value', [('jersey_number','true'), ('first_name','["Ann"]'), ('first_name','{"name":"Ann"}')])
def test_csv_rejects_wrong_json_types_without_mutating(field,value):
    model=roster_fixture();before=bytes(model.data)
    rows=list(csv.DictReader(io.StringIO(bulk.export_csv(model))))
    row=next(r for r in rows if r['table']=='players' and r['index']=='0' and r['field']==field)
    row['value']=value
    output=io.StringIO();writer=csv.DictWriter(output,bulk.CSV_COLUMNS);writer.writeheader();writer.writerows(rows)
    with pytest.raises(ValueError,match='expected a JSON'):
        bulk.csv_changes(model,output.getvalue())
    assert bytes(model.data)==before


def test_csv_round_trip_changes_rollback_and_conflict():
    model=roster_fixture();before=bytes(model.data)
    text=bulk.export_csv(model)
    assert bulk.csv_changes(model,text)==[]
    rows=list(csv.DictReader(io.StringIO(text)))
    row=next(r for r in rows if r['table']=='players' and r['index']=='0' and r['field']=='jersey_number')
    row['value']='23'
    output=io.StringIO();writer=csv.DictWriter(output,bulk.CSV_COLUMNS);writer.writeheader();writer.writerows(rows)
    changes=bulk.csv_changes(model,output.getvalue());bulk.apply_changes(model,changes)
    assert model.rows['players'][0]['jersey_number']==23
    with pytest.raises(ValueError,match='changed since export'):bulk.csv_changes(model,output.getvalue())
    model.undo();assert bytes(model.data)==before
    broken=changes+[dict(table='players',index=0,field='position_code',slot=None,old=0,value=9)]
    with pytest.raises(ValueError):bulk.apply_changes(model,broken)
    assert bytes(model.data)==before and model.edits==[]


def test_ratings_multi_paste_is_atomic_and_replayable():
    model=roster_fixture();model.edit('players',0,'attribute_ratings',88,slot=3)
    text=bulk.rating_document(model.rows['players'][0]);before=bytes(model.data)
    bulk.paste_ratings(model,[1],text)
    assert model.rows['players'][1]['attribute_ratings'][3]==88
    model.undo();assert bytes(model.data)==before
    with pytest.raises(ValueError):bulk.paste_ratings(model,[1],text.replace('88','999'))


def test_compare_selected_compatible_fields():
    model,other=roster_fixture(),roster_fixture()
    other.edit('players',0,'attribute_ratings',95,slot=4)
    changes=bulk.compare(model,other)['changes']
    assert len(changes)==1
    before=bytes(model.data);bulk.apply_changes(model,changes)
    assert model.rows['players'][0]['attribute_ratings'][4]==95
    model.undo();assert bytes(model.data)==before


def test_names_grow_to_game_entry_limit_with_undo():
    model=roster_fixture();before=bytes(model.data)
    assert model.name_capacity('players',0,'first_name')==16
    model.edit('players',0,'first_name','Al')
    assert model.rows['players'][0]['first_name']=='Al'
    assert model.name_capacity('players',0,'first_name')==16
    model.edit('players',0,'first_name','Ann')
    assert model.rows['players'][0]['first_name']=='Ann'
    model.undo();model.undo();assert bytes(model.data)==before
    model.edit('players',0,'first_name','Alexandria')
    assert model.rows['players'][0]['first_name']=='Alexandria'
    with pytest.raises(ValueError):model.edit('players',0,'first_name','A'*17)


def test_redshirt_controls_preserve_scholarship_weight_and_class():
    model=roster_fixture()
    model.edit('players',0,'scholarship_status',1)
    model.edit('players',0,'class_code',6)
    model.edit('players',0,'redshirt_used',1)
    before=bytes(model.data);weight=model.rows['players'][0]['weight_lbs']
    model.edit('players',0,'redshirt_code',2)
    row=model.rows['players'][0]
    assert row['redshirt_used']==0 and row['redshirt_code']==2
    assert row['scholarship_status']==1 and row['weight_lbs']==weight and row['class_code']==6
    model.undo();assert bytes(model.data)==before
    model.edit('players',0,'redshirt_code',3)
    model.edit('players',0,'redshirt_used',1)
    assert model.rows['players'][0]['redshirt_code']==0


def test_growing_text_preserves_wrappers_and_zip_members():
    import struct,zipfile
    from choops_py.roster.adapters import load_bytes
    from choops_py.roster.editor_model import EditorModel
    from choops_py.formats.tool_wrapper import wrap
    base=roster_fixture();userdata=struct.pack('>I',len(base.data))+base.data
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as z:
        z.comment=b'preserve';z.writestr('save/USERDATA',userdata);z.writestr('other',b'untouched')
    for raw in (userdata,wrap(21,[bytes(base.data)]),output.getvalue()):
        model=EditorModel(load_bytes(bytes(raw)),base.tables)
        model.edit('players',0,'first_name','Alexandria')
        encoded=model.source.encode(bytes(model.data));source=load_bytes(encoded)
        assert source.kind==model.source.kind and source.payload==bytes(model.data)
        reopened=EditorModel(source,base.tables)
        assert reopened.rows['players'][0]['first_name']=='Alexandria'
        if source.kind=='save-zip':
            with zipfile.ZipFile(io.BytesIO(encoded)) as z:
                assert z.comment==b'preserve' and z.read('other')==b'untouched'
