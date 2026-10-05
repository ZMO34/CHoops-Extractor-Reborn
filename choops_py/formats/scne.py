from .binary import Binary
from .tool_wrapper import unwrap
def inspect(data):
    blocks=unwrap(data)[1] if data[:4]==b'2kTl' else [data];b=Binary(blocks[0]);b.slice(0,0x54)
    count=b.u32(0x44);table=b.relative(0x48);b.slice(table,count*0xb0);parts=[]
    for i in range(count):
        off=table+i*0xb0;parts.append(dict(index=i,name=b.utf16(b.relative(off),'be'),index_flags=b.u32(off+0xa4),index_count=b.u32(off+0xa8),index_offset_plus_one=b.u32(off+0xac),raw_words=[b.u32(off+j*4) for j in range(44)]))
    return dict(mode='read-only',texture_count=b.u32(0x20),parts=parts,block_sizes=[len(x) for x in blocks])
