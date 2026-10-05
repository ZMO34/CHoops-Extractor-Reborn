import struct
from choops_py.archive.hash_names import namespace,hash_name,lookup
from choops_py.archive.usrdir_reader import Archive
from choops_py.archive import cache
def game(path,payload):
    path.mkdir();data=bytearray(4096);struct.pack_into('>6I',data,0,0xaa00b3bf,2048,1,0,1,0);struct.pack_into('>II8s',data,24,2,0,'0A\0\0'.encode('utf-16-be'));struct.pack_into('>4I',data,40,hash_name('ua000.iff'),1,0,1);data[2048:2048+len(payload)]=payload;(path/'0A').write_bytes(data);return path
def test_names():
    ns=set(namespace());assert 'ua800.iff' in ns and 'h9999.iff' in ns;assert lookup()[hash_name('ua000.iff')]=='ua000.iff';assert hash_name('ua000.iff')==hash_name('UA000.IFF')
def test_archive_cache(workspace,standard):
    p=game(workspace/'source',standard);a=Archive(p);assert a.read(a.entries[0]).startswith(standard);cp=cache.build(p);assert cache.info(p)['schema']==1;cp.unlink()
