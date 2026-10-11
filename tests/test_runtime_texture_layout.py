import io
import struct
from PIL import Image
from choops_py.texture_tools import dds
from choops_py.texture_tools.runtime_layout import conform
from choops_py.texture_tools.override_import import apply_dds
from choops_py.formats.txtr import TXTR
from support import txtr_fixture


def artwork(width,height,color):
    output=io.BytesIO();Image.new('RGBA',(width,height),color).save(output,format='DDS')
    return output.getvalue()


def test_core_artwork_keeps_storage_dimensions_and_complete_small_mips():
    source=artwork(32,16,(0,0,255,255))
    layout=dict(width=8,height=4,format='DXT5',mip_count=4,cubemap=False)
    result,changed=conform(source,layout)
    assert changed and all(dds.inspect(result)[k]==v for k,v in layout.items())
    with Image.open(io.BytesIO(result)) as image:
        assert image.convert('RGBA').getpixel((0,0))==(0,0,255,255)
    assert len(result)==128+dds.image_size(8,4,'DXT5',4)


def test_matching_layout_keeps_artwork_bytes_exact():
    source=artwork(8,4,(11,22,33,44));layout=dds.inspect(source)
    assert conform(source,layout)==(source,False)


def test_core_dds_import_preserves_entire_header_and_payload_capacity(tmp_path):
    parts=txtr_fixture(format=0x86,split=True)
    header=bytearray(parts[0]);struct.pack_into('>3H',header,0x90,4,4,1)
    parts=[bytes(header),parts[1]]
    path=tmp_path/'replacement.dds';source=artwork(32,32,(0,0,255,255));path.write_bytes(source)
    result,report=apply_dds(parts,'TXTR','artwork',path,preserve_layout=True)
    assert result[0]==parts[0]
    assert list(map(len,result))==list(map(len,parts))
    assert TXTR(result).info()['format']=='DXT1'
    assert report['storage_layout_preserved'] and report['artwork_resampled']
    assert report['input_layout']['width']==32 and report['width']==4
    assert path.read_bytes()==source
