import pytest
from choops_py.formats.tool_wrapper import wrap,unwrap
def test_wrapper():
    data=wrap('7',[b'abc',b'def']);assert unwrap(data)==(7,[b'abc',b'def']);assert wrap(0,[])==wrap('0',[])
    with pytest.raises(ValueError):unwrap(data[:-1])
