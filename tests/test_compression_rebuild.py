import struct
from choops_py.formats.compression import MAGIC, decode, encode_greedy, encode_like


def literal(data,shift=12):
    body=b''.join(b'\0'+data[i:i+8] for i in range(0,len(data),8))
    return struct.pack('>5I',MAGIC,len(data),20+len(body),123,shift)+body


def test_changed_repetition_is_recompressed_instead_of_literal_inflation():
    baseline=literal(b'A'*8192)
    original=encode_greedy(baseline,b'A'*8192)
    edited=b'ABCD'*(8192//4)
    result=encode_like(original,edited)
    assert decode(result)==edited
    assert len(result)<1200
    assert result[12:20]==original[12:20]
    assert encode_like(original,b'A'*8192)==original


def test_greedy_distance_overlap_and_incompressible_tail():
    for shift in (4,8,12,16):
        data=bytes(range(256))*3+b'ABC'*101+b'last'
        result=encode_greedy(literal(data,shift),data)
        assert decode(result)==data
