"""Read-only cross-game animation evidence; no animation replacement or porting."""
import argparse
from collections import Counter
from contextlib import ExitStack

from ..archive.usrdir_reader import Archive
from ..archive.build_io import BankReader
from ..archive.manifests import safe_output
from ..formats.binary import Binary
from ..formats.standard_iff import StandardIFF
from ..formats.standard_iff_writer import record_blocks
from ..core.reports import save_json

TRACK_TYPES = {0x60900d71:'SingleMoCap',0x7657ab8a:'SKEL',0x9d34e89e:'unresolved motion.iff record family'}


def inspect(source,job=None):
    archive=Archive(source)
    before=[(archive.path/p['name']).stat() for p in archive.parts]
    found=[];counts=Counter()
    with ExitStack() as stack:
        reader=BankReader(archive,stack)
        for i,entry in enumerate(sorted(archive.entries,key=lambda e:e['offset'])):
            if job:job.check();job.progress(i,len(archive.entries),'Inspecting animation record headers')
            raw=reader.read(entry['offset'],min(32,entry['size']))
            if raw[:4]!=bytes.fromhex('ff3bef94'):continue
            b=Binary(raw);size,bc,fc=b.u32(4),b.u32(16),b.u32(24)
            if not 32<=size<=min(entry['size'],4*1024*1024) or bc>10000 or fc>10000:continue
            header=Binary(reader.read(entry['offset'],size))
            for record in range(fc):
                field=header.relative(28)+record*4
                at=header.relative(field);typ=header.u32(at+4)
                if typ in TRACK_TYPES:
                    counts[TRACK_TYPES[typ]]+=1
                    found.append(dict(archive_index=entry['index'],archive=entry['name'] or f"hash_{entry['hash']:08x}",record=record,type=TRACK_TYPES[typ]))
    samples=[];seen=Counter()
    for item in found:
        if seen[item['type']]>=5:continue
        iff=StandardIFF(archive.read(archive.entries[item['archive_index']]))
        record=iff.records[item['record']];blocks=record_blocks(iff,record)
        samples.append({**item,'name':record['name'],'decoded_block_sizes':[len(b[3]) for b in blocks],
                        'header_prefixes':[b[3][:32].hex() for b in blocks]})
        seen[item['type']]+=1
    after=[(archive.path/p['name']).stat() for p in archive.parts]
    if any((a.st_size,a.st_mtime_ns,a.st_ino)!=(b.st_size,b.st_mtime_ns,b.st_ino) for a,b in zip(before,after)):
        raise ValueError('Source changed during animation inspection')
    return dict(game=archive.game_info,record_counts=dict(counts),records=found,samples=samples,
                source_unchanged=True,mode='read-only',tracks_decoded=False,port_implemented=False)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources',nargs='+');parser.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    output=safe_output(args.output,args.sources)
    if output.exists():raise ValueError('Choose a new animation report path')
    result=dict(games=[inspect(s) for s in args.sources],direct_swap_certified=False,
                conclusion='A shared type hash is not a compatibility guarantee. Bone IDs/order, bind pose, packed tracks, root motion, events and gameplay lookup tables require independent verification. No animation writer or port is enabled.')
    save_json(output,result)
    print(output)


if __name__=='__main__':main()
