import struct
import uuid
from pathlib import Path
import pytest
from support import game_fixture,iff_fixture
from choops_py.archive.usrdir_reader import Archive
from choops_py.archive.manifests import OUTPUT
from choops_py.archive.folder_import import discover,compile_group
from choops_py.formats.standard_iff import StandardIFF
from choops_py.formats.standard_iff_writer import record_blocks,replace_records_expanding
from choops_py.formats.cdf_backed_iff_writer import name_trailer
from choops_py.formats.tool_wrapper import wrap
from choops_py.formats.txtr import TXTR
from choops_py.formats.binary import Binary
from choops_py.texture_tools import dds,gtf,override_import
from choops_py.studio.services import stage_folder


def txtr_header():
    header=bytearray(176)
    struct.pack_into('>4BI3HBBII',header,0x58,0x86,1,2,0,0xaae4,4,4,1,0,0,8,0)
    struct.pack_into('>I',header,0xa4,1)
    return bytes(header)


def named_iff(blocks,records,names):
    return iff_fixture(blocks,records)+name_trailer([{'name':n,'type':t} for n,t in names])


def test_recursive_whole_archives_and_duplicate_targets(tmp_path):
    source=game_fixture(tmp_path/'game',iff_fixture())
    folder=tmp_path/'overrides';nested=folder/'textures'/'courts';nested.mkdir(parents=True)
    (nested/'ua000.iff').write_bytes(iff_fixture([b'new!']))
    (folder/'design.psd').write_bytes(b'ignored')
    mod=OUTPUT/'builds'/('nested_import_test_'+uuid.uuid4().hex)
    report=stage_folder(source,folder,mod)
    assert report['staged']==1 and report['scanned_files']==2
    (folder/'ua000.iff').write_bytes(iff_fixture([b'dup!']))
    with pytest.raises(ValueError,match='Duplicate'):discover(Archive(source),folder)


def test_raw_record_then_dds_takes_priority(tmp_path,monkeypatch):
    payload=named_iff([txtr_header(),b'oldimage'],[(0x5c369069,[0,0])],[('unif','TXTR')])
    source=game_fixture(tmp_path/'game',payload);folder=tmp_path/'overrides'/'ua000';folder.mkdir(parents=True)
    (folder/'unif.txtr').write_bytes(wrap(1,[txtr_header(),b'rawimage']))
    child=folder/'_unif.txtr';child.mkdir();(child/'unif.dds').write_bytes(b'DDS artwork')
    def import_dds(parts,kind,selector,path,job=None):
        assert parts[1]==b'rawimage' and kind=='TXTR'
        return [parts[0],b'DDS wins'],{'width':4,'height':4,'format':'DXT1','mip_count':1}
    monkeypatch.setattr(override_import,'apply_dds',import_dds)
    arc=Archive(source);plan=discover(arc,folder)
    rebuilt,_=compile_group(arc,plan['groups'][0]);iff=StandardIFF(rebuilt)
    assert record_blocks(iff,iff.records[0])[1][3].startswith(b'DDS wins')


def test_expanding_record_preserves_other_records():
    payload=named_iff([txtr_header()*2,b'AAAAAAAA' + b'BBBBBBBB'],
                      [(0x5c369069,[0,0]),(0x5c369069,[176,8])],[('one','TXTR'),('two','TXTR')])
    iff=StandardIFF(payload)
    result=replace_records_expanding(iff,{0:[txtr_header(),b'new pixels'*40]})
    rebuilt=StandardIFF(result)
    assert record_blocks(rebuilt,rebuilt.records[0])[1][3].startswith(b'new pixels'*40)
    assert record_blocks(rebuilt,rebuilt.records[1])[1][3].startswith(b'BBBBBBBB')
    assert rebuilt.records[1]['offsets']==iff.records[1]['offsets']


def test_dynamic_dds_changes_descriptor_and_preserves_original_input(tmp_path,monkeypatch):
    image=bytes(range(64));data=bytearray(dds.compressed_preview(8,8,'DXT5',image))
    struct.pack_into('<I',data,24,1)
    source=tmp_path/'art.dds';source.write_bytes(data)
    def convert(name,input_path,output_path,**kw):
        assert struct.unpack_from('<I',Path(input_path).read_bytes(),24)[0]==0
        desc=struct.pack('>4BI3HBBII',0x88,1,2,0,0xaae4,8,8,1,0,0,32,0)
        Path(output_path).write_bytes(gtf.make(desc,image))
    monkeypatch.setattr(override_import.external_converters,'convert',convert)
    changed,info=override_import.apply_dds([txtr_header(),b'oldimage'],'TXTR','unif',source)
    assert TXTR(changed).image()==image and info['width']==8 and info['format']=='DXT5'
    assert source.read_bytes()==bytes(data)


def test_scne_growth_keeps_existing_geometry_bytes(tmp_path,monkeypatch):
    head=bytearray(0x54)+bytearray(txtr_header())
    struct.pack_into('>II',head,0x20,1,0x54-0x24+1)
    old=b'oldimage'+b'VERTEX_AND_INDEX_BYTES'
    image=bytes(range(64));source=tmp_path/'texture_0.dds';source.write_bytes(dds.compressed_preview(8,8,'DXT5',image))
    def convert(name,input_path,output_path,**kw):
        desc=struct.pack('>4BI3HBBII',0x88,1,2,0,0xaae4,8,8,1,0,0,32,0)
        Path(output_path).write_bytes(gtf.make(desc,image))
    monkeypatch.setattr(override_import.external_converters,'convert',convert)
    changed,_=override_import.apply_dds([bytes(head),old],'SCNE','texture_0',source)
    assert changed[1][:len(old)]==old
    assert Binary(changed[0]).u32(0x54+0xa4)>len(old)



def test_nested_growing_scene_build_uses_relocation(tmp_path):
    from choops_py.archive.build_copy import build
    payload=named_iff([b'old head',b'old data'],[(0xe26c9b5d,[0,0])],[('arena','SCNE')])
    source=game_fixture(tmp_path/'game',payload);folder=tmp_path/'overrides'/'ua000';folder.mkdir(parents=True)
    (folder/'arena.scne').write_bytes(wrap(2,[b'new scene header'*100,b'new vertices and textures'*500]))
    mod=OUTPUT/'builds'/('dynamic_scene_mod_'+uuid.uuid4().hex)
    staged=stage_folder(source,folder,mod)
    assert staged['growing_archives']
    output=OUTPUT/'builds'/('dynamic_scene_build_'+uuid.uuid4().hex)
    plan=build(source,mod,output,dry_run=True)
    assert plan['archive_relocation_required']
    result=build(source,mod,output)
    assert result['archive_relocation_required'] and result['validation']['source_unchanged']
    replaced=build(source,mod,output,overwrite=True)
    assert replaced['validation']['source_unchanged']
    new=Archive(output);iff=StandardIFF(new.read(new.entries[0]))
    spans=record_blocks(iff,iff.records[0])
    assert spans[0][3].startswith(b'new scene header'*100) and spans[1][3].startswith(b'new vertices and textures'*500)
    assert Archive(source).read(Archive(source).entries[0]).startswith(payload)


def test_dynamic_texture_editor_import(tmp_path,monkeypatch):
    from choops_py.texture_tools.pipeline import import_texture
    payload=named_iff([txtr_header(),b'oldimage'],[(0x5c369069,[0,0])],[('unif','TXTR')])
    source=tmp_path/'source.iff';source.write_bytes(payload)
    image=bytes(range(64));dds_path=tmp_path/'art.dds';dds_path.write_bytes(dds.compressed_preview(8,8,'DXT5',image))
    def convert(name,input_path,output_path,**kw):
        desc=struct.pack('>4BI3HBBII',0x88,1,2,0,0xaae4,8,8,1,0,0,32,0)
        Path(output_path).write_bytes(gtf.make(desc,image))
    monkeypatch.setattr(override_import.external_converters,'convert',convert)
    output=OUTPUT/'temp'/('dynamic_texture_'+uuid.uuid4().hex+'.iff')
    report=import_texture(source,'unif',dds_path,output,dynamic=True)
    assert report['conversion']['dynamic_layout']
    iff=StandardIFF(output.read_bytes());texture=TXTR([b[3] for b in record_blocks(iff,iff.records[0])])
    assert texture.info()['width']==8 and texture.image()==image



def test_linear_compressed_mips_keep_declared_pitch():
    desc=struct.pack('>4BI3HBBII',0xa8,2,2,0,0xaae4,8,8,1,0,0,32,0)
    info=gtf.descriptor_info(desc)
    assert info['image_size']==96  # 2 block rows + 1 block row, all at pitch 32.
    image=bytes(range(64))+bytes(range(16))+b'\0'*16
    assert len(image)==info['image_size']
    header=bytearray(txtr_header());header[0x58:0x70]=desc
    assert TXTR([bytes(header),image]).image()==image



def test_python_texture_manifest_detected_without_archive_folder_name(tmp_path,monkeypatch):
    import json
    payload=named_iff([txtr_header(),b'oldimage'],[(0x5c369069,[0,0])],[('unif','TXTR')])
    source=game_fixture(tmp_path/'game',payload);folder=tmp_path/'renamed_export';folder.mkdir()
    (folder/'source_ua000.iff').write_bytes(payload)
    (folder/'0000_unif.txtr').write_bytes(wrap(1,[txtr_header(),b'rawimage']))
    (folder/'0000_unif.dds').write_bytes(b'DDS')
    metadata={'schema':2,'source':r'Z:\old\ua000.iff','textures':[{'texture_name':'unif','raw_output_path':r'Z:\old\0000_unif.txtr','dds_output_path':r'Z:\old\0000_unif.dds'}]}
    (folder/'manifest.json').write_text(json.dumps(metadata),encoding='utf8')
    def apply(parts,kind,selector,path,job=None):
        assert parts[1]==b'rawimage'
        return [parts[0],b'DDS wins'],{'width':4,'height':4,'format':'DXT1','mip_count':1}
    monkeypatch.setattr(override_import,'apply_dds',apply)
    arc=Archive(source);plan=discover(arc,folder)
    assert plan['detected_formats']==['python-texture-manifest']
    assert plan['dds_files']==1 and plan['groups'][0]['whole'] is None
    result,_=compile_group(arc,plan['groups'][0]);iff=StandardIFF(result)
    assert record_blocks(iff,iff.records[0])[1][3].startswith(b'DDS wins')


def test_python_record_dump_manifest_and_split_blocks(tmp_path):
    import json
    payload=named_iff([b'old head',b'old data'],[(0xe26c9b5d,[0,0])],[('arena','SCNE')])
    source=game_fixture(tmp_path/'game',payload);folder=tmp_path/'dump';parts=folder/'ua000.iff.subfiles';parts.mkdir(parents=True)
    (folder/'ua000.iff').write_bytes(payload)
    iff=StandardIFF(payload);(parts/'manifest.json').write_text(json.dumps(iff.manifest()),encoding='utf8')
    (parts/'0000_arena.scne.block0').write_bytes(b'larger replacement header')
    (parts/'0000_arena.scne.block1').write_bytes(b'larger replacement data'*100)
    arc=Archive(source);plan=discover(arc,folder)
    assert 'python-record-manifest' in plan['detected_formats']
    result,_=compile_group(arc,plan['groups'][0]);new=StandardIFF(result)
    assert record_blocks(new,new.records[0])[1][3].startswith(b'larger replacement data'*100)


def test_legacy_rgba_dds_is_normalized_without_changing_pixels():
    header=bytearray(128);header[:4]=b'DDS '
    for field,value in {4:124,8:0x100f,12:1,16:1,24:1,76:32,80:0x41,88:32,92:0xff,96:0xff00,100:0xff0000,104:0xff000000}.items():struct.pack_into('<I',header,field,value)
    original=bytes(header)+bytes((10,20,30,40))
    normalized=dds.normalized_2d(original)
    assert normalized[128:]==bytes((30,20,10,40))
    assert struct.unpack_from('<I',normalized,24)[0]==0
    assert dds.inspect(normalized)['format']=='ARGB8'


def test_hashed_python_rip_relocates_existing_unknown_asset(tmp_path):
    from choops_py.archive.build_copy import build
    payload=named_iff([b'old head',b'old data'],[(0xe26c9b5d,[0,0])],[('arena','SCNE')])
    source=game_fixture(tmp_path/'game',payload)
    bank=source/'PS3_GAME'/'USRDIR'/'0A';raw=bytearray(bank.read_bytes())
    struct.pack_into('>I',raw,40,0x13579bdf);bank.write_bytes(raw)
    folder=tmp_path/'hash_13579bdf.iff.subfiles';folder.mkdir()
    import json
    (folder/'manifest.json').write_text(json.dumps(StandardIFF(payload).manifest()),encoding='utf8')
    (folder/'0000_arena.scne.block0').write_bytes(b'expanded head'*100)
    (folder/'0000_arena.scne.block1').write_bytes(b'expanded mesh'*500)
    mod=OUTPUT/'builds'/('hashed_import_'+uuid.uuid4().hex)
    stage_folder(source,folder,mod)
    output=OUTPUT/'builds'/('hashed_build_'+uuid.uuid4().hex)
    report=build(source,mod,output)
    assert report['validation']['source_unchanged']
    archive=Archive(output);assert archive.entries[0]['hash']==0x13579bdf
    iff=StandardIFF(archive.read(archive.entries[0]))
    assert record_blocks(iff,iff.records[0])[1][3].startswith(b'expanded mesh'*500)


def test_python_raw_package_texture_keeps_mesh_and_runtime_identity():
    head=bytearray(0x54)+bytearray(txtr_header())
    struct.pack_into('>II',head,0x20,1,0x54-0x24+1)
    header=bytearray(txtr_header())
    struct.pack_into('>HH',header,0x60,8,8)
    image=bytes(range(32));mesh=b'oldimageGEOMETRY'
    result=override_import.apply_raw_texture([bytes(head),mesh],'texture_0',[bytes(header),image])
    from choops_py.formats.package import textures
    texture=textures(result)[0]
    assert result[1][:len(mesh)]==mesh
    assert TXTR([texture.header,texture.payload]).image()==image


def test_half_float_dds_metadata():
    header=bytearray(128);header[:4]=b'DDS '
    for field,value in {4:124,8:0x1007,12:2,16:2,76:32,80:4,84:113}.items():struct.pack_into('<I',header,field,value)
    info=dds.inspect(bytes(header)+b'\0'*32)
    assert info['format']=='RGBA16F' and info['payload_size']==32


def test_legacy_cube_marker_and_native_face_alignment():
    header=bytearray(128);header[:4]=b'DDS '
    for field,value in {4:124,8:0x1007,12:2,16:2,76:32,80:4,84:113,112:0xfc00}.items():struct.pack_into('<I',header,field,value)
    cube=bytes(header)+bytes(range(32))*6
    assert dds.inspect(cube)['cubemap']
    assert dds.normalized_2d(cube)[128:]==cube[128:]
    assert struct.unpack_from('<I',dds.normalized_2d(cube),112)[0]==0xfe00
    descriptor=struct.pack('>4BI3HBBII',0x9a,1,2,1,0xaae4,2,2,1,0,0,0,0)
    assert gtf.descriptor_info(descriptor)['image_size']==128*5+32


def test_bad_dds_never_falls_back_to_raw_txtr(tmp_path):
    payload=named_iff([txtr_header(),b'oldimage'],[(0x5c369069,[0,0])],[('unif','TXTR')])
    source=game_fixture(tmp_path/'game',payload);folder=tmp_path/'ua000';folder.mkdir()
    (folder/'unif.txtr').write_bytes(wrap(1,[txtr_header(),b'rawimage']))
    (folder/'unif.dds').write_bytes(b'broken DDS')
    mod=OUTPUT/'builds'/('invalid_dds_'+uuid.uuid4().hex)
    with pytest.raises(ValueError):stage_folder(source,folder,mod)
    assert not mod.exists()
    archive=Archive(source);assert archive.read(archive.entries[0]).startswith(payload)
