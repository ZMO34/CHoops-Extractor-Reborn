import pytest
from choops_py.formats.cdf_backed_iff import CDFPair
def test_pair(pair,workspace):
    iff,cdf=pair;p=CDFPair(iff,cdf);assert p.records[0]['type']=='AUDO';assert p.cdf_name=='x.cdf'
    assert p.replace('0',b'MODS')==b'HEADMODSTAIL';p.dump(workspace/'pair')
    with pytest.raises(ValueError):p.replace('0',b'x')
    with pytest.raises(ValueError):CDFPair(iff,cdf[:6])
