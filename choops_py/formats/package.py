"""Shared SCNE package texture layout; geometry remains byte-preserved."""
from dataclasses import dataclass
from .binary import Binary
from ..core.errors import ToolError
@dataclass
class PackageTexture:
    index: int
    header_offset: int
    payload_offset: int
    payload_end: int
    header: bytes
    payload: bytes

def textures(blocks):
    if len(blocks)!=2: raise ToolError('package_layout_not_supported','SCNE texture package requires header and data blocks')
    head,data=blocks; b=Binary(head);b.slice(0,0x54)
    count=b.u32(0x20)
    if count>4096:raise ToolError('invalid_package','Texture count exceeds limit')
    if not count:return []
    table=b.relative(0x24);b.slice(table,count*0xb0)
    offsets=[b.u32(table+i*0xb0+0xa4)-1 for i in range(count)]
    if any(o<0 or o>=len(data) for o in offsets):raise ToolError('invalid_package','Texture payload pointer outside data block')
    result=[]
    for i,start in enumerate(offsets):
        end=min([o for o in offsets if o>start],default=len(data));off=table+i*0xb0
        result.append(PackageTexture(i,off,start,end,head[off:off+0xb0],data[start:end]))
    return result

def replace_texture(blocks,index,image,logical_length):
    items=textures(blocks);matches=[t for t in items if t.index==index]
    if len(matches)!=1:raise ToolError('texture_not_found',str(index))
    t=matches[0]
    if logical_length>len(t.payload) or len(image)!=logical_length:raise ToolError('payload_size_mismatch','Texture image must fit original slice')
    for other in items:
        if other.index!=index and other.payload_offset==t.payload_offset:raise ToolError('aliased_texture','Shared package payload')
    data=bytearray(blocks[1]);data[t.payload_offset:t.payload_offset+logical_length]=image
    return [blocks[0],bytes(data)]
