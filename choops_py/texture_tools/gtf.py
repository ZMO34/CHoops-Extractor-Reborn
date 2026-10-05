import struct
from ..formats.binary import Binary
from ..core.errors import ToolError
from .dds import FORMATS,image_size

def descriptor_info(descriptor):
    b=Binary(descriptor);b.slice(0,24)
    code=descriptor[0];fmt=FORMATS.get(code&0x9f)
    if not fmt:raise ToolError('unsupported_texture_format',f'PS3 format 0x{code:02x}')
    width,height,mips=b.u16(8),b.u16(10),descriptor[1]
    if descriptor[2]!=2 or descriptor[3] or b.u16(12)!=1:raise ToolError('unsupported_texture_layout','Only single 2D non-cube textures are writable')
    size=image_size(width,height,fmt,mips)
    pitch=b.u32(16)
    if code&0x20 and fmt in ('L8','ARGB8') and pitch!=width*(1 if fmt=='L8' else 4):raise ToolError('unsupported_texture_pitch',f'Padded pitch {pitch} is not validated')
    return dict(width=width,height=height,format=fmt,mip_count=mips,image_size=size,ps3_format=code,linear=bool(code&0x20),pitch=pitch)

def make(descriptor,payload):
    descriptor_info(descriptor)
    return struct.pack('>6I',0x01080000,len(payload)+48,1,0,48,len(payload))+descriptor+payload

def parse(data):
    b=Binary(data);b.slice(0,48)
    if b.u32(0)!=0x01080000 or b.u32(8)!=1:raise ToolError('invalid_gtf','Expected one-texture GTF')
    offset,size=b.u32(16),b.u32(20);payload=b.slice(offset,size)
    if offset<48 or offset+size>len(data):raise ToolError('invalid_gtf','Invalid GTF payload range')
    info=descriptor_info(data[24:48]);info.update(payload_offset=offset,payload_size=size)
    return info,data[24:48],payload
