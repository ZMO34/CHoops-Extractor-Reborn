import struct
import zlib
import uuid
from pathlib import Path
from support import game_fixture,iff_fixture,literal,txtr_fixture
from choops_py.archive.add_assets import build
from choops_py.archive.manifests import OUTPUT
from choops_py.archive.usrdir_reader import Archive
from choops_py.archive.hash_names import hash_name
from choops_py.archive.folder_import import discover,compile_group
from choops_py.formats.cdf_backed_iff import CDFPair
from choops_py.formats.cdf_backed_iff_writer import name_trailer,replace_texture_records
from choops_py.formats.compression import decode
from choops_py.formats.txtr import TXTR
from choops_py.texture_tools.dds import compressed_preview


def logo_pair():
    name='logos.cdf';end=148+len(name.encode('utf-16-be'))+2
    header=bytearray(end);parts=txtr_fixture(format=0x86,split=True)
    stored=[literal(p) for p in parts]
    struct.pack_into('>10I',header,0,0xf0985030,end,end,0,2,21,1,77,97,113)
    for j,p in enumerate(parts):
        struct.pack_into('>8I',header,40+j*32,1,1,16 if j==0 else 128,len(p),0,end+j*176,len(p),0)
    struct.pack_into('>I',header,104,5)
    struct.pack_into('>5I',header,108,zlib.crc32(b'logo001'),0x5c369069,2,0,0)
    struct.pack_into('>I',header,128,5)
    struct.pack_into('>4I',header,132,0,len(stored[0]),len(stored[0]),len(stored[1]))
    header[148:]=name.encode('utf-16-be')+b'\0\0'
    return bytes(header)+name_trailer([{'name':'logo001','type':'TXTR'}]),b''.join(stored)


def test_cdf_dds_discovery_and_growing_paired_import(tmp_path):
    metadata,cdf=logo_pair()
    source=game_fixture(tmp_path/'source',iff_fixture())
    jb=OUTPUT/'builds'/('logo_source_'+uuid.uuid4().hex)
    build(source,{'logos.iff':metadata,'logos.cdf':cdf},jb)
    folder=tmp_path/'overrides'/'logos'/'_logo001.txtr';folder.mkdir(parents=True)
    image=b'\x12'*64
    (folder/'logo001.dds').write_bytes(compressed_preview(8,8,'DXT5',image))
    archive=Archive(jb);groups=discover(archive,tmp_path/'overrides')['groups']
    assert len(groups)==1
    rebuilt,details=compile_group(archive,groups[0])
    _,name,payload=groups[0]['compiled_companion']
    assert name=='logos.cdf' and details[0]['width']==8
    pair=CDFPair(rebuilt,payload);r=pair.records[0]
    parts=[decode(payload[r[k+'_offset']:r[k+'_offset']+r[k+'_length']]) for k in ('header','payload')]
    assert TXTR(parts).image()==image
    assert struct.unpack_from('>I',rebuilt,84)[0]>=64
    import shutil
    shutil.rmtree(jb)


def test_cdf_writer_preserves_unchanged_record_content():
    metadata,payload=logo_pair()
    rebuilt,cdf=replace_texture_records(metadata,payload,{})
    before=CDFPair(metadata,payload);after=CDFPair(rebuilt,cdf)
    for old,new in zip(before.records,after.records):
        for k in ('header','payload'):
            assert decode(payload[old[k+'_offset']:old[k+'_offset']+old[k+'_length']])==decode(cdf[new[k+'_offset']:new[k+'_offset']+new[k+'_length']])
