import pytest
from choops_py.cli import main,parser,SPECS
from choops_py.archive.manifests import safe_output,OUTPUT
def test_commands():
    subs=next(a for a in parser()._actions if getattr(a,'choices',None));assert set(SPECS)|{'gui'}==set(subs.choices)
def test_help():
    with pytest.raises(SystemExit) as e:main(['--help'])
    assert e.value.code==0
def test_roundtrip(standard,workspace):
    p=workspace/'in.iff';p.write_bytes(standard);out=workspace/'out.iff';assert main(['round-trip-iff',str(p),str(out),'--compare'])==0;assert out.read_bytes()==standard
def test_safety(workspace):
    with pytest.raises(ValueError):safe_output(workspace/'source'/'out',[workspace/'source'])
    with pytest.raises(ValueError):safe_output(OUTPUT.parent/'unsafe')
    assert safe_output(workspace/'safe')==workspace/'safe'
