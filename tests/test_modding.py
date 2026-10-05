import pytest
from choops_py.modding.overrides import stage,validate
from choops_py.modding.build_copy import build
from test_cache import game
def test_staging_build(workspace,standard):
    src=game(workspace/'source',standard);payload=workspace/'payload';payload.write_bytes(b'WXYZ');mod=workspace/'mod';stage(mod,payload,'ua000.iff','0');assert len(validate(mod))==1
    before=(src/'0A').read_bytes();plan=build(src,mod,workspace/'build',dry_run=True);assert plan['dry_run'];assert not (workspace/'build').exists()
    build(src,mod,workspace/'build');assert (src/'0A').read_bytes()==before;assert (workspace/'build'/'0A').read_bytes()[2048+84:2048+88]==b'WXYZ'
    with pytest.raises(ValueError):stage(workspace/'bad',payload,'../oops')
    with pytest.raises(ValueError):build(src,mod,src/'output',dry_run=True)
