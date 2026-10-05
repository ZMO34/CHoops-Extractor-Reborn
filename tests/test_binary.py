import pytest
from choops_py.formats.binary import Binary,relative_target,relative_value
def test_binary():
    b=Binary(b'\0\0\0\5A\0\0\0');assert b.u32(0)==5;assert b.utf16(4)=='A';assert b.relative(0)==4
    assert relative_target(10,relative_value(10,100))==100
    with pytest.raises(ValueError):b.slice(-1,1)
    with pytest.raises(ValueError):b.slice(0,20)
    with pytest.raises(ValueError):Binary(b'\0\0\0\0').relative(0)
