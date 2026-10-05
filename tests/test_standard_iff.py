import pytest,struct
from choops_py.formats.standard_iff import StandardIFF,decompress
def test_parse_replace(standard,workspace):
    iff=StandardIFF(standard);assert iff.records[0]['type']=='TXTR';assert iff.raw==standard
    result=iff.replace('0',b'WXYZ');assert result[84:88]==b'WXYZ';assert result[88:]==b'PAD'
    iff.dump(workspace/'dump');assert (workspace/'dump'/'0000_0.txtr.block0').read_bytes()==b'abcd'
    with pytest.raises(ValueError):iff.replace('0',b'x')
def test_bounds(standard):
    damaged=bytearray(standard);struct.pack_into('>I',damaged,64,0xffffffff)
    with pytest.raises(ValueError):StandardIFF(bytes(damaged))
def test_h7a():
    raw=struct.pack('>5I',0x0e4837c3,4,25,0,8)+b'\0abcd';assert decompress(raw,4)==b'abcd'
    with pytest.raises(ValueError):decompress(raw[:-1],4)
