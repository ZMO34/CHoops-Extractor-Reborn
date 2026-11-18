"""Apply the selected base JB's texture contract outside stadium archives."""
import re
from ..archive.hash_names import replacement_hash
from ..formats.txtr import TXTR
from ..formats.package import textures, repack_images
from .override_import import apply_dds
from .builtin_converter import to_dds
from .dds import FORMATS


def stadium_archive(group):
    name=group.get('name') or group['entry'].get('name') or ''
    if re.fullmatch(r's\d{3,5}n?\.(?:iff|cdf)',name,re.I):return True
    # Numeric hashes in Python exports must receive the same policy as names.
    return group['entry']['hash'] in _STADIUM_HASHES


_STADIUM_HASHES=frozenset(replacement_hash(f's{i:03d}{suffix}.iff') for i in range(1024) for suffix in ('','n'))


FONT_PALETTE_BYTES=1024


def font_palette(texture):
    """Locate an indexed uniform font's trailing 256-entry ARGB palette.

    Font TXTRs (jersey_numbers/names) are linear L8 with remap 0x5500; the game's
    CPU copy path colours glyphs through this palette, so it is authored artwork,
    not layout. Returns (block, offset, bytes) or None for any other texture.
    """
    info=texture.info()
    if info['format']!='L8' or not info['linear'] or info['cubemap'] or info['remap']!=0x5500:return None
    block=info['payload_block'];data=texture.blocks[block]
    start=(info['payload_offset']+info['image_size']+3)&~3
    if start+FONT_PALETTE_BYTES>len(data):return None
    return block,start,bytes(data[start:start+FONT_PALETTE_BYTES])


def keep_font_palette(result,replacement):
    """Copy a replacement font's palette into the base-layout result."""
    source=font_palette(replacement)
    if source is None:return result,False
    target=font_palette(TXTR(result))
    if target is None or target[2]==source[2]:return result,False
    blocks=list(result);block,start,_=target
    data=bytearray(blocks[block]);data[start:start+FONT_PALETTE_BYTES]=source[2]
    blocks[block]=bytes(data)
    check=font_palette(TXTR(blocks))
    if check is None or check[2]!=source[2]:raise ValueError('Indexed font palette did not survive base-layout normalization')
    return blocks,True


def normalize_record(parts,base,kind,job=None,compact=True):
    """Keep replacement geometry and artwork; restore base image layout."""
    if kind=='TXTR':current=[TXTR(parts)];reference=[TXTR(base)]
    elif kind=='SCNE':
        if len(parts)==1 and len(parts[0])>=0x24 and not int.from_bytes(parts[0][0x20:0x24],'big'):return parts,[]
        current=[TXTR([t.header,t.payload]) for t in textures(parts)]
        candidates=[TXTR([t.header,t.payload]) for t in textures(base)]
        reference=[]
        for texture in current:
            identity=texture.blocks[0][:4]
            matches=[t for t in candidates if t.blocks[0][:4]==identity]
            if len(matches)!=1:raise ValueError('Scene texture has no unique base-JB identity; cannot normalize safely')
            reference.append(matches[0])
    else:return parts,[]
    result=parts;reports=[]
    for index,(texture,target) in enumerate(zip(current,reference)):
        if job:job.check()
        if len(texture.blocks[0])<0x70 or len(target.blocks[0])<0x70:
            raise ValueError('Texture header is truncated; cannot normalize its base-JB layout')
        if texture.blocks[0][0x58]&0x9f not in FORMATS:
            if texture.blocks[0][0x58:0x70]!=target.blocks[0][0x58:0x70]:raise ValueError('Unsupported texture format changed its base-JB layout')
            continue
        # Unchanged render targets can have formats not supported for artwork.
        if texture.blocks[0][0x58:0x70]==target.blocks[0][0x58:0x70] and texture.blocks==target.blocks:continue
        selector=f'texture_{index}' if kind=='SCNE' else 'texture'
        result,report=apply_dds(result,kind,selector,to_dds(texture.gtf()),job,
                                preserve_layout=True,reference=target)
        if kind=='TXTR':
            # DDS round-trips carry pixels only; keep a replacement font's colours.
            result,kept=keep_font_palette(result,texture)
            if kept:report=dict(report,font_palette='replacement')
        reports.append(dict(texture=selector,**report))
    if kind=='SCNE' and reports and compact:result=repack_images(parts,result)
    return result,reports
