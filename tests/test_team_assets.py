import json
import struct
import uuid
from pathlib import Path

import pytest

from support import iff_fixture, txtr_fixture
from test_roster_semantics import header_roster
from choops_py.archive.hash_names import hash_name
from choops_py.archive.manifests import OUTPUT
from choops_py.archive.usrdir_reader import Archive
from choops_py.modding.team_assets import prepare, inventory, available_ids, roster_model, export_folder, arena_selector
from choops_py.roster.adapters import load_bytes
from choops_py.roster.editor_model import EditorModel


def logo_fixture():
    import zlib
    from choops_py.formats.cdf_backed_iff_writer import name_trailer
    head, image = txtr_fixture(split=True)
    name='teamselectlogo.cdf'; end=148+len(name.encode('utf-16-be'))+2
    header=bytearray(end)
    struct.pack_into('>10I',header,0,0xf0985030,end,end,0,2,21,1,77,97,113)
    for off,start,size in ((40,end,len(head)),(72,end+176,len(image))):
        struct.pack_into('>8I',header,off,1,1,16,size,0,start,size,0)
    struct.pack_into('>I',header,104,5)
    struct.pack_into('>5I',header,108,zlib.crc32(b'logo003'),0x5c369069,2,0,0)
    struct.pack_into('>I',header,128,5)
    struct.pack_into('>4I',header,132,0,len(head),len(head),len(image))
    header[148:]=name.encode('utf-16-be')+b'\0\0'
    return bytes(header)+name_trailer([{'name':'logo003','type':'TXTR'}]), head+image


def game(tmp_path, *, shared=True, logos=False):
    raw, starts = header_roster()
    for i in range(2):
        off = starts['teams'] + i * 704
        for field in (0x18c, 0x190, 0x194):struct.pack_into('>H', raw, off + field, 3 if shared else 3 + i)
        struct.pack_into('>H', raw, off + 0x18e, i)
        field = off + 0x44
        struct.pack_into('>i', raw, field, starts['arenas'] + 25 - field)
    # String code deliberately differs: native routing must use numeric 77.
    anchor = starts['arenas'] + 24
    struct.pack_into('>H', raw, anchor + 0x12, 77)
    for i, variant in enumerate((0, 1)):
        struct.pack_into('>II', raw, starts['uniforms'] + i * 8, (3 << 22) | (77 << 12) | (variant << 8) | 35, 0x48001000)
    payloads = {'roster_english.iff': iff_fixture([bytes(raw)], [(0xc61649b2, [0])], compressed=True),
                's077.iff': iff_fixture(txtr_fixture()),
                **{f'{prefix}u{bank}077.iff': iff_fixture(txtr_fixture()) for prefix in ('', 'sel') for bank in 'ha'}}
    if logos:
        logo_iff, cdf = logo_fixture()
        payloads.update({'teamselectlogo.iff':logo_iff,'teamselectlogo.cdf':cdf})
    source = tmp_path / 'game'; usr = source / 'PS3_GAME' / 'USRDIR'; usr.mkdir(parents=True)
    rows = sorted(payloads, key=hash_name); cursor = 2048; body = bytearray(2048)
    for i, name in enumerate(rows):
        payload = payloads[name]
        struct.pack_into('>4I', body, 40 + i * 16, hash_name(name), cursor // 2048, 0, len(payload))
        body += payload + b'\0' * (-len(payload) % 2048); cursor = len(body)
    struct.pack_into('>6I', body, 0, 0xaa00b3bf, 2048, 1, 0, len(rows), 0)
    struct.pack_into('>II8s', body, 24, len(body) // 2048, 0, '0A\0\0'.encode('utf-16-be'))
    (usr / '0A').write_bytes(body)
    return source


def request(assets, team=0, target=900):
    return [dict(team=team, id=target, assets=assets)]


def test_separate_owner_preserves_shared_team_and_orders_all_five(tmp_path):
    source = game(tmp_path); archive = Archive(source); original, before = roster_model(archive)
    result = prepare(archive, request(['z']))
    after = EditorModel(load_bytes(result['replacements']['roster_english.iff']))
    assert [u['variant_code'] for u in after.rows['uniforms'] if u['team_asset_id'] == 900] == [0, 1, 2, 3, 4]
    assert [u['uniform_asset_id'] for u in after.rows['uniforms'] if u['team_asset_id'] == 900] == [77, 77, 900, 900, 900]
    assert len(result['additions']) == 6
    assert after.rows['teams'][0]['uniform_owner_id'] == 900
    assert after.rows['teams'][1] == before.rows['teams'][1]
    assert after.rows['teams'][0]['asset_id'] == 3
    assert bytes(after.data[before.row_offset('players', 0):before.row_offset('players', 0) + 2 * 308]) == bytes(before.data[before.row_offset('players', 0):before.row_offset('players', 0) + 2 * 308])
    assert roster_model(archive)[0] == original


def test_stadium_numeric_route_and_other_arena_references_survive_batch(tmp_path):
    source = game(tmp_path); archive = Archive(source)
    result = prepare(archive, [dict(team=i, id=900+i, assets=['stadium']) for i in range(2)])
    model = EditorModel(load_bytes(result['replacements']['roster_english.iff']))
    assert arena_selector(model, model.rows['teams'][0]) == (900, 0)
    assert arena_selector(model, model.rows['teams'][1]) == (901, 0)
    assert model.tables['arenas'][1] == 4
    assert set(result['additions']) == {'s900.iff', 's901.iff'}
    assert model.rows['arenas'][2]['arena_code']=='900' and model.rows['arenas'][3]['arena_code']=='901'
    for i in (0,1):
        field=model.row_offset('arenas',2+i)+0x24
        target=field+struct.unpack_from('>i',model.data,field)[0]-1
        assert target==model.row_offset('teams',i)+0x30


@pytest.mark.parametrize('changes', [request(['x'], target=1024), request(['x'], target=-1), request(['x'], target=3), request(['bogus']), request(['x'], team=5), request([])])
def test_bad_plans_do_not_write_source(tmp_path, changes):
    source = game(tmp_path); path = source/'PS3_GAME/USRDIR/0A'; old = path.read_bytes()
    with pytest.raises(ValueError):prepare(Archive(source), changes)
    assert path.read_bytes() == old


def test_list_reports_shared_active_inactive_and_numeric_stadium(tmp_path):
    archive = Archive(game(tmp_path)); _, model = roster_model(archive)
    rows = inventory(archive, model)
    assert 's077.iff' in rows[0]['stadium'] and 'Present' in rows[0]['stadium']
    assert 'Active' in rows[0]['h'] and rows[0]['x'] == 'Inactive'
    assert 'Uniforms 2' in rows[0]['shared']
    assert 3 not in available_ids(archive, model) and 77 not in available_ids(archive, model)


def test_unique_owner_can_fill_missing_without_consuming_another_id(tmp_path):
    archive = Archive(game(tmp_path, shared=False))
    result = prepare(archive, request(['x', 'y', 'z'], target=3))
    model = EditorModel(load_bytes(result['replacements']['roster_english.iff']))
    assert model.rows['teams'][0]['uniform_owner_id'] == 3
    assert len(model.rows['uniforms']) == 5
    assert set(result['additions']) == {f'{p}u{b}003.iff' for p in ('', 'sel') for b in 'xyz'}


@pytest.mark.parametrize('workers', [1, 2])
def test_loose_folder_applies_additions_to_normal_preview_and_build(tmp_path, workers):
    from choops_py.studio.services import stage_folder
    from choops_py.studio.preview_source import PreviewArchive
    from choops_py.archive.build_copy import build
    archive = Archive(game(tmp_path)); result = prepare(archive, request(['stadium', 'x']))
    root = OUTPUT/'temp'/('team_assets_test_'+uuid.uuid4().hex)
    folder = export_folder(result, root/'loose', archive.path)
    report = stage_folder(archive.path, folder, root/'prepared', workers=workers)
    assert set(report['added_assets']) == {'s900.iff', 'ux900.iff', 'selux900.iff'}
    preview = PreviewArchive(archive, Path(report['mod']))
    for name in result['additions']:
        entry = next(e for e in preview.entries if e['name'] == name)
        assert preview.read(entry) == result['additions'][name]
    build(archive.path, report['mod'], root/'built')
    rebuilt = Archive(root/'built')
    assert {e['hash'] for e in rebuilt.entries} == {e['hash'] for e in archive.entries} | {hash_name(n) for n in result['additions']}
    assert arena_selector(roster_model(rebuilt)[1], roster_model(rebuilt)[1].rows['teams'][0]) == (900, 0)
    # A stale or tampered added file cannot silently enter a preview/build.
    doc = json.loads((Path(report['mod'])/'additions.json').read_text())
    target = Path(report['mod'])/doc['entries'][0]['path']; target.write_bytes(b'broken')
    with pytest.raises(ValueError, match='changed'):PreviewArchive(archive, report['mod'])


def test_team_matrix_checkboxes_and_auto_id(qtbot, tmp_path):
    from choops_py.studio.app import Window
    studio = Window(); qtbot.addWidget(studio)
    archive = Archive(game(tmp_path)); _, model = roster_model(archive)
    panel = studio.team_assets_panel
    panel.loaded((archive, model, inventory(archive, model), available_ids(archive, model)))
    assert panel.table.rowCount() == 2
    panel.check_missing()
    plans = panel.requests()
    assert len(plans) == 2 and plans[0]['id'] != plans[1]['id']
    assert plans[0]['assets'] == ['x', 'y', 'z']
    panel.search.setText('no match')
    assert panel.table.isRowHidden(0)


def test_menu_logo_clones_and_stages_with_template_layout_and_live_preview(tmp_path):
    from choops_py.studio.services import stage_folder
    from choops_py.studio.preview_source import PreviewArchive
    from choops_py.formats.cdf_backed_iff import CDFPair
    from choops_py.modding.team_assets import read_named
    archive=Archive(game(tmp_path,logos=True))
    old=read_named(archive,'teamselectlogo.cdf')
    plan=prepare(archive,request(['menu_logo']))
    root=OUTPUT/'temp'/('team_assets_test_'+uuid.uuid4().hex)
    folder=export_folder(plan,root/'loose',archive.path)
    result=stage_folder(archive.path,folder,root/'prepared',workers=1)
    preview=PreviewArchive(archive,result['mod'])
    new_iff=read_named(preview,'teamselectlogo.iff');new_cdf=read_named(preview,'teamselectlogo.cdf')
    assert {r['name'] for r in CDFPair(new_iff,new_cdf).records}=={'logo003','logo900'}
    assert new_cdf[:len(old)]==old
    assert inventory(preview,roster_model(preview)[1])[0]['menu_logo']=='logo900 — Present'


def test_build_preflight_recovers_missing_linked_alternate_from_home(tmp_path):
    from choops_py.roster.uniforms import append_uniform,encode_roster_iff
    from choops_py.archive.importer import stage
    from choops_py.archive.build_copy import build
    archive=Archive(game(tmp_path)); original,model=roster_model(archive)
    modified=encode_roster_iff(original,append_uniform(bytes(model.data),1,888,2))
    root=OUTPUT/'temp'/('team_assets_test_'+uuid.uuid4().hex);root.mkdir(parents=True)
    incoming=root/'roster.iff';incoming.write_bytes(modified)
    stage(root/'prepared',incoming,'roster_english.iff')
    (root/'prepared/import_options.json').write_text('{"schema":1,"allow_archive_growth":true}')
    report=build(archive.path,root/'prepared',root/'built')
    assert set(report['added_assets'])=={'ux888.iff','selux888.iff'}
    assert len(report['warnings'])==2 and all('Home slot' in w for w in report['warnings'])
    from choops_py.modding.team_assets import read_named
    rebuilt=Archive(root/'built')
    from choops_py.archive.add_assets import meaningful_iff
    assert meaningful_iff(read_named(rebuilt,'ux888.iff'))==meaningful_iff(read_named(archive,'uh077.iff'))


def test_classic_shared_arena_forks_without_touching_classification_or_original(tmp_path):
    archive=Archive(game(tmp_path));_,model=roster_model(archive)
    from choops_py.roster.schema import TEAM_TYPE_OFFSET
    payload=bytearray(model.data);off=model.row_offset('teams',1)
    struct.pack_into('>I',payload,off+TEAM_TYPE_OFFSET,1<<15)
    original=bytes(payload)
    plan=prepare(archive,request(['stadium'],team=1),roster_payload=payload)
    updated=EditorModel(load_bytes(plan['replacements']['roster_english.iff']))
    assert updated.rows['teams'][1]['team_type_code']==1
    assert arena_selector(updated,updated.rows['teams'][1])==(900,0)
    assert arena_selector(updated,updated.rows['teams'][0])==(77,0)
    assert bytes(updated.data[off:off+0x44])==original[off:off+0x44]
