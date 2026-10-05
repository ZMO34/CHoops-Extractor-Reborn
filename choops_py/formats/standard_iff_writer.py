"""Preserve all logical offsets; rebuild only changed stored blocks."""
import struct
from .standard_iff import StandardIFF
from .compression import decode, encode_like
from .binary import Binary
from ..core.errors import ToolError

def record(iff, selector, expected_type=None):
    selector = str(selector)
    candidates = [r for r in iff.records if (str(r['index'])==selector or r['name']==selector or f"{r['name']}.{r['type'].lower()}"==selector) and (not expected_type or r['type']==expected_type)]
    if len(candidates)!=1: raise ToolError('ambiguous_subfile','Select a unique name/index and type')
    return candidates[0]

def record_blocks(iff, rec):
    blocks = []
    for index,start,end in iff.spans(rec):
        block=iff.blocks[index]
        logical=decode(iff.raw[block['start']:block['start']+block['size']],block['logical_size'])
        blocks.append((index,start,end,logical[start:end]))
    return blocks

def replace_records(iff, changes):
    """changes maps record index to complete block slices (same logical size).

    Physical block positions/lengths, fileLength and H7A lengths are recomputed.
    Internal record offsets stay unchanged. The name table is moved byte-exactly.
    Only identified trailing zero padding may absorb compressed growth.
    """
    changed = {}; touched = []
    for index, replacements in changes.items():
        rec=record(iff,index); spans=record_blocks(iff,rec)
        if len(spans)!=len(replacements): raise ToolError('block_count_mismatch','Replacement must preserve each subfile block')
        for (block_index,start,end,old),new in zip(spans,replacements):
            if len(old)!=len(new): raise ToolError('payload_size_mismatch','Replacement changes logical subfile size')
            if old==new: continue
            for other in iff.records:
                if other['index']==rec['index']: continue
                for bj,bs,be in iff.spans(other):
                    if bj==block_index and start<be and bs<end: raise ToolError('aliased_subfile','Replacement overlaps another subfile')
            for bj,bs,be in touched:
                if bj==block_index and start<be and bs<end: raise ToolError('overlapping_edits','Changes overlap')
            touched.append((block_index,start,end))
            if block_index not in changed:
                block=iff.blocks[block_index];changed[block_index]=bytearray(decode(iff.raw[block['start']:block['start']+block['size']],block['logical_size']))
            changed[block_index][start:end]=new
    if not changed: return iff.raw
    header=bytearray(iff.raw[:iff.header_size]);payload=bytearray();cursor=iff.header_size
    for block in sorted(iff.blocks,key=lambda b:b['start']):
        if block['start']<cursor: raise ToolError('overlapping_blocks','Stored block ranges overlap')
        payload.extend(iff.raw[cursor:block['start']])
        original=iff.raw[block['start']:block['start']+block['size']]
        replacement=bytes(changed[block['index']]) if block['index'] in changed else None
        stored=encode_like(original,replacement) if replacement is not None and block['compressed'] else replacement if replacement is not None else original
        new_start=iff.header_size+len(payload)
        entry=32+block['index']*32
        struct.pack_into('>I',header,entry+20,new_start);struct.pack_into('>I',header,entry+24,len(stored))
        payload.extend(stored);cursor=block['start']+block['size']
    payload.extend(iff.raw[cursor:iff.file_length]);new_end=len(header)+len(payload)
    struct.pack_into('>I',header,8,new_end)
    trailer=iff.raw[iff.file_length:];meaningful=0
    if trailer[:4]==bytes.fromhex('aa171516'):
        meaningful=8+Binary(trailer).u32(4,'<')
        if meaningful>len(trailer):raise ToolError('invalid_name_table','Name table exceeds trailer')
    elif any(trailer):meaningful=len(trailer)
    core=bytes(header)+bytes(payload)+trailer[:meaningful]
    if len(core)>len(iff.raw):
        raise ToolError('archive_extent_capacity_exceeded',f'Rebuilt IFF needs {len(core)} bytes; original extent is {len(iff.raw)}. Size-changing archive relocation is blocked.')
    padding=trailer[meaningful:]
    if any(padding):raise ToolError('unknown_trailer','Cannot resize unknown trailing bytes')
    result=core+b'\0'*(len(iff.raw)-len(core))
    rebuilt=StandardIFF(result)
    for index,logical in changed.items():
        b=rebuilt.blocks[index]
        if decode(result[b['start']:b['start']+b['size']],b['logical_size'])!=bytes(logical):raise ToolError('writer_validation_failed','Rebuilt logical block mismatch')
    return result
