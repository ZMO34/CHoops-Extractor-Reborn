"""Keep engine-owned gameplay artwork within its existing texture layout."""
import io
import struct
from PIL import Image
from . import dds


def conform(data,layout,job=None):
    source=dds.inspect(data)
    keys=('width','height','format','mip_count','cubemap')
    if all(source[k]==layout[k] for k in keys):return data,False
    if source['cubemap']!=layout['cubemap']:
        raise ValueError('Gameplay texture replacement must preserve its cubemap faces')
    if layout['format'] not in ('DXT1','DXT3','DXT5','ARGB8','L8'):
        raise ValueError('Gameplay texture storage layout cannot be regenerated safely')
    face_size=dds.image_size(source['width'],source['height'],source['format'],source['mip_count'])
    output=[];header=None
    for face in range(6 if source['cubemap'] else 1):
        if job:job.check()
        raw=bytearray(data[:128]);struct.pack_into('<I',raw,112,0)
        raw+=data[128+face*face_size:128+(face+1)*face_size]
        if source['format']=='RGBA16F':
            pixels=bytes(max(0,min(255,round(v*255))) for values in struct.iter_unpack('<4e',raw[128:128+source['width']*source['height']*8]) for v in values)
            image=Image.frombytes('RGBA',(source['width'],source['height']),pixels)
        else:
            with Image.open(io.BytesIO(raw)) as opened:image=opened.convert('RGBA')
        image=image.resize((layout['width'],layout['height']),Image.Resampling.LANCZOS)
        for mip in range(layout['mip_count']):
            if job:job.check()
            width=max(1,layout['width']>>mip);height=max(1,layout['height']>>mip)
            level=image if mip==0 else image.resize((width,height),Image.Resampling.LANCZOS)
            encoded=io.BytesIO()
            if layout['format'].startswith('DXT'):
                # BCN encoders require a complete block at the smallest mips.
                padded=Image.new('RGBA',(max(4,width),max(4,height)));padded.paste(level)
                for x in range(width,padded.width):padded.paste(padded.crop((width-1,0,width,height)),(x,0))
                for y in range(height,padded.height):padded.paste(padded.crop((0,height-1,padded.width,height)),(0,y))
                padded.save(encoded,format='DDS',pixel_format=layout['format'])
                raw_level=encoded.getvalue()
            elif layout['format']=='L8':
                raw_level=dds.linear_l8(width,height,1,level.convert('L').tobytes())
            else:
                level.save(encoded,format='DDS');raw_level=encoded.getvalue()
            if header is None:header=bytearray(raw_level[:128])
            output.append(raw_level[128:])
    struct.pack_into('<II',header,12,layout['height'],layout['width'])
    struct.pack_into('<I',header,20,dds.image_size(layout['width'],layout['height'],layout['format']) if layout['format'].startswith('DXT') else layout['width']*(1 if layout['format']=='L8' else 4))
    struct.pack_into('<I',header,28,layout['mip_count'])
    struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0]|0x20000)
    struct.pack_into('<I',header,108,0x401008 if layout['mip_count']>1 or layout['cubemap'] else 0x1000)
    struct.pack_into('<I',header,112,0xfe00 if layout['cubemap'] else 0)
    result=bytes(header)+b''.join(output);check=dds.inspect(result)
    if any(check[k]!=layout[k] for k in keys):raise ValueError('Gameplay texture layout verification failed')
    return result,True
