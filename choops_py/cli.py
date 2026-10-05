import argparse,json,sys
from pathlib import Path
from .archive.manifests import OUTPUT,safe_output,write_bytes,report
from .archive import cache
from .archive.hash_names import resolve
from .archive.ripper import rip
from .formats.standard_iff import StandardIFF
from .formats.cdf_backed_iff import CDFPair
from .formats.tool_wrapper import unwrap,wrap
from .formats import txtr,roster,scne,audio
from .modding import overrides,build_copy
from .validation import standard_iff_validator,cdf_pair_validator,build_validator,rip_audit
# Registry is also the GUI's command schema. Outputs are identified for preflight.
SPECS={
'build-cache':['source'],'cache-info':['source'],'resolve-name':['value'],
'rip':['source','output'],'inspect-iff':['input','output'],'validate-iff':['input','output'],'round-trip-iff':['input','output'],'dump-iff-subfiles':['input','output'],'replace-iff-subfile':['input','selector','replacement','output'],
'inspect-cdf-pair':['input','cdf','output'],'validate-cdf-pair':['input','cdf','output'],'dump-cdf-pair':['input','cdf','output'],'round-trip-cdf-pair':['input','cdf','output'],'replace-cdf-payload':['input','cdf','selector','replacement','output'],
'inspect-tool-wrapper':['input'],'unwrap-tool-file':['input','output'],'wrap-tool-file':['type','blocks','output'],
'inspect-txtr':['input','output'],'extract-textures':['input','output'],'inspect-uniform-atlas':['input','output'],
'import':['mod','input'],'list-overrides':['mod'],'validate-mod':['mod'],'build-copy':['source','mod','output'],'validate-build':['source','modded','output'],'audit-rip':['inventory','rip_output','output'],
'roster-detect':['input'],'roster-decode':['input','output'],'roster-compare':['input','custom','output'],'roster-validate':['input'],
'inspect-floor-scne':['input','output'],'inspect-audo':['input','output'],'extract-audio-payloads':['input','cdf','output']}
def parser():
    p=argparse.ArgumentParser(description='PS3 CHoops preservation tools; all writes under project output/')
    subs=p.add_subparsers(dest='command',required=True);subs.add_parser('gui')
    for command,fields in SPECS.items():
        s=subs.add_parser(command)
        for field in fields:
            kwargs={}
            if field=='blocks':kwargs['nargs']='+'
            if command=='extract-audio-payloads' and field=='cdf':kwargs['nargs']='?'
            s.add_argument(field,**kwargs)
        if command in ('build-cache','rip'):s.add_argument('--game-name',choices=['choops2k8'],default='choops2k8')
        if command=='rip':
            group=s.add_mutually_exclusive_group();group.add_argument('--cache',action='store_true');group.add_argument('--build-cache',action='store_true')
            s.add_argument('--index',type=int);s.add_argument('--file');s.add_argument('--iff-only',action='store_true');s.add_argument('--raw-iff',action='store_true');s.add_argument('--type',nargs='+',default=[]);s.add_argument('--log-output');s.add_argument('--strict',action='store_true')
        if command=='inspect-iff':s.add_argument('--dump-subfiles',action='store_true')
        if command.startswith('round-trip'):s.add_argument('--compare',action='store_true')
        if command.startswith('replace-'):s.add_argument('--same-size-only',action='store_true',required=True)
        if command=='extract-textures':s.add_argument('--raw',action='store_true')
        if command=='import':s.add_argument('--iff',required=True);s.add_argument('--sub')
        if command=='build-copy':s.add_argument('--overwrite',action='store_true');s.add_argument('--dry-run',action='store_true')
    return p
def execute(a):
    c=a.command
    if c=='gui':
        from .gui import launch
        return launch()
    sources=[getattr(a,f) for f in ('source','input','cdf','replacement','custom','mod','modded','inventory','rip_output') if getattr(a,f,None)]
    if hasattr(a,'output'):a.output=safe_output(a.output,sources)
    read=lambda f:Path(getattr(a,f)).read_bytes()
    if c=='build-cache':return str(cache.build(a.source))
    if c=='cache-info':return cache.info(a.source)
    if c=='resolve-name':return resolve(a.value)
    if c=='rip':
        if a.build_cache:cache.build(a.source)
        if a.cache:cache.info(a.source)
        return rip(a.source,a.output,a.index,a.file,a.iff_only,a.raw_iff,a.type,a.strict,a.log_output)
    if c in ('inspect-iff','validate-iff','dump-iff-subfiles','round-trip-iff','replace-iff-subfile'):
        data=read('input');iff=StandardIFF(data)
        if c=='validate-iff':result=standard_iff_validator.validate(data);report(a.output,result,sources);return result
        if c=='round-trip-iff':write_bytes(a.output,iff.raw,sources);return dict(equal=Path(a.output).read_bytes()==data)
        if c=='replace-iff-subfile':write_bytes(a.output,iff.replace(a.selector,read('replacement')),sources);return str(a.output)
        if c=='dump-iff-subfiles' or a.dump_subfiles:iff.dump(a.output)
        else:report(a.output/'inspection.json',iff.manifest(),sources)
        return iff.manifest()
    if 'cdf-pair' in c or c=='replace-cdf-payload':
        iff=read('input');cdf=read('cdf');pair=CDFPair(iff,cdf)
        if c=='validate-cdf-pair':result=cdf_pair_validator.validate(iff,cdf);report(a.output,result,sources);return result
        if c=='replace-cdf-payload':cdf=pair.replace(a.selector,read('replacement'))
        if c in ('round-trip-cdf-pair','replace-cdf-payload'):
            write_bytes(a.output/Path(a.input).name,iff,sources);write_bytes(a.output/Path(a.cdf).name,cdf,sources)
            return dict(iff_equal=(a.output/Path(a.input).name).read_bytes()==iff,cdf_equal=(a.output/Path(a.cdf).name).read_bytes()==cdf)
        if c=='dump-cdf-pair':pair.dump(a.output)
        else:report(a.output/'inspection.json',pair.manifest(),sources)
        return pair.manifest()
    if c in ('inspect-tool-wrapper','unwrap-tool-file'):
        typ,blocks=unwrap(read('input'))
        if c=='unwrap-tool-file':
            for i,b in enumerate(blocks):write_bytes(a.output/f'block{i}.bin',b,sources)
        return dict(type=typ,block_sizes=[len(b) for b in blocks])
    if c=='wrap-tool-file':write_bytes(a.output,wrap(a.type,[Path(p).read_bytes() for p in a.blocks]),a.blocks);return str(a.output)
    if c=='import':return overrides.stage(a.mod,a.input,a.iff,a.sub)
    if c=='list-overrides':return overrides.listing(a.mod)
    if c=='validate-mod':return overrides.validate(a.mod)
    if c=='build-copy':return build_copy.build(a.source,a.mod,a.output,a.overwrite,a.dry_run)
    if c=='validate-build':result=build_validator.validate(a.source,a.modded);report(a.output/'build_validation.json',result,sources);return result
    if c=='audit-rip':result=rip_audit.audit(a.inventory,a.rip_output);report(a.output/'audit.json',result,sources);return result
    if c=='extract-textures':return StandardIFF(read('input')).dump(a.output,['TXTR'])
    if c=='extract-audio-payloads':
        if a.cdf:
            pair=CDFPair(read('input'),read('cdf'))
            for r in pair.records:
                if r['type']=='AUDO':write_bytes(a.output/f"audio_{r['index']:04d}.bin",pair.cdf[r['payload_offset']:r['payload_offset']+r['payload_length']],sources)
            return pair.manifest()
        return StandardIFF(read('input')).dump(a.output,['AUDO'])
    if c=='roster-compare':result=roster.compare(read('input'),read('custom'))
    elif c.startswith('roster-'):result=roster.inspect(read('input'))
    elif c=='inspect-floor-scne':result=scne.inspect(read('input'))
    elif c=='inspect-audo':result=audio.inspect(read('input'))
    elif c in ('inspect-txtr','inspect-uniform-atlas'):
        data=read('input')
        result=StandardIFF(data).manifest() if data[:4]==bytes.fromhex('ff3bef94') else txtr.inspect(data)
        if c=='inspect-uniform-atlas':result['atlas_mapping']='candidate only; no automatic glyph editing'
    else:raise ValueError('Unsupported command')
    if hasattr(a,'output'):report(a.output/'inspection.json',result,sources)
    return result
def main(argv=None):
    p=parser();a=p.parse_args(argv)
    try:
        result=execute(a)
        if result is not None:print(json.dumps(result,indent=2))
        return 0
    except (ValueError,OSError,KeyError) as error:print(f'Error: {error}',file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
