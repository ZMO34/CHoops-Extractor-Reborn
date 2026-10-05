import struct
import pytest
from pathlib import Path
from choops_py.archive.manifests import OUTPUT
@pytest.fixture
def workspace():
    import tempfile,shutil
    (OUTPUT/'temp').mkdir(parents=True,exist_ok=True)
    p=Path(tempfile.mkdtemp(prefix='pytest_',dir=OUTPUT/'temp'))
    yield p
    shutil.rmtree(p)
@pytest.fixture
def standard():
    return struct.pack('>8I',0xff3bef94,84,88,0,1,13,1,37)+struct.pack('>8I',1,1,16,4,0,84,4,0)+struct.pack('>I',5)+struct.pack('>4I',7,0x5c369069,1,0)+b'abcd'+b'PAD'
@pytest.fixture
def pair():
    iff=bytearray(180)
    def u(off,val):struct.pack_into('>I',iff,off,val)
    u(0,0xf0985030);u(4,180);u(16,1);u(24,1);u(32,76-32+1);u(36,48-36+1)
    iff[48:60]='x.cdf\0'.encode('utf-16-be');u(76,140-76+1);u(104,120-104+1)
    for off,val in zip(range(120,140,4),[1,0x1aedda1f,2,0,0]):u(off,val)
    for off,val in zip(range(140,156,4),[0,4,4,4]):u(off,val)
    return bytes(iff),b'HEADdataTAIL'
