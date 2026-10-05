from .binary import Binary
from .tool_wrapper import unwrap
def inspect(data):
    blocks=unwrap(data)[1] if data[:4]==b'2kTl' else [data]
    b=Binary(blocks[0]);result={'mode':'read-only raw preservation','block_sizes':[len(x) for x in blocks],'dds_conversion':'not implemented; failure does not invalidate asset'}
    if len(blocks[0])>=0x70:
        dims=b.u32(0x60);result.update(candidate_width=dims>>16,candidate_height=dims&65535,format_word=b.u32(0x58),confidence='candidate; layout must be validated for this variant')
    return result
