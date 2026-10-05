import os
from pathlib import Path
import pytest
from choops_py.archive.usrdir_reader import Archive
from choops_py.formats.standard_iff import StandardIFF
JB=Path(os.environ.get('CHOOPS_JB',str(Path(__file__).resolve().parents[2]/'College Hoops 2K8 (USA)')))
@pytest.mark.skipif(not JB.exists(),reason='Optional proprietary JB fixture absent')
def test_real_iff():
    a=Archive(JB);e=next(e for e in a.entries if e['name']=='ua000.iff');iff=StandardIFF(a.read(e));assert iff.records
