"""Automatically recognize Python exports and nested binary/DDS overrides."""
from pathlib import Path
import json
import re
import struct
from collections import defaultdict
from .hash_names import replacement_hash as hash_name

RECORD_TYPES={'.txtr':'TXTR','.scne':'SCNE','.name':'NAME','.cdan':'CDAN','.layt':'LAYT','.rost':'ROST'}


def discover(archive,folder,job=None):
    folder=Path(folder)
    def linked(p):return p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction())
    if linked(folder):raise ValueError('Linked override folders are blocked')
    folder=folder.resolve();files=[];pending=[folder]
    while pending:
        parent=pending.pop()
        for p in sorted(parent.iterdir(),key=lambda p:p.name.casefold()):
            if job:job.check()
            if linked(p):raise ValueError('Linked replacement path: '+str(p.relative_to(folder)))
            if p.is_dir():pending.append(p)
            elif p.is_file():files.append(p)
    hashes={e['hash']:e for e in archive.entries};groups=defaultdict(lambda:{'whole':None,'records':{},'dds':{},'dds_rank':{},'package_records':{}})
    ignored=0;issues=[];shadowed=[]
    def identity_name(entry,fallback):
        if entry['name']:return entry['name']
        if next(archive.chunks(entry,4),b'')==bytes.fromhex('ff3bef94'):return f"hash_{entry['hash']:08x}.iff"
        return fallback
    def owner(file):
        for parent in file.parents:
            parent_name=parent.name.removesuffix('.subfiles')
            name=parent_name if Path(parent_name).suffix.lower() in ('.iff','.bin') else parent_name+'.iff'
            e=hashes.get(hash_name(name)) if name.isascii() else None
            if e:return e,identity_name(e,name)
            if parent==folder:break
        return None,None
    def add(group,kind,key,file):
        if key in group[kind]:issues.append('Duplicate target: '+str(file.relative_to(folder)))
        else:group[kind][key]=file
    consumed=set();formats=set()
    for marker in files:
        if marker.name in ('rip_report.json','extraction_manifest.json'):
            formats.add('python-archive-export');consumed.add(marker)
    def local_file(manifest,value):
        if not isinstance(value,str):return None
        candidate=manifest.parent/Path(value.replace('\\','/')).name
        return candidate if candidate in files else None
    for manifest in [p for p in files if p.name=='manifest.json']:
        if manifest.stat().st_size>16*1024*1024:continue
        try:metadata=json.loads(manifest.read_text(encoding='utf-8-sig'))
        except (ValueError,OSError):continue
        if not isinstance(metadata,dict):continue
        if isinstance(metadata.get('textures'),list) and isinstance(metadata.get('source'),str):
            source_name=Path(metadata['source'].replace('\\','/')).name
            entry=hashes.get(hash_name(source_name)) if source_name.isascii() else None
            if entry is None:entry,source_name=owner(manifest)
            if entry is None:issues.append('Unresolved Python export source: '+manifest.name);continue
            group=groups[entry['hash']];group['entry']=entry;group['name']=identity_name(entry,source_name)
            formats.add('python-texture-manifest');consumed.add(manifest)
            for ref in manifest.parent.glob('source_*'):
                if ref in files:consumed.add(ref)
            for texture in metadata['textures']:
                if not isinstance(texture,dict):raise ValueError('Invalid Python texture manifest entry')
                selector=texture.get('texture_name')
                if not isinstance(selector,str):continue
                raw=local_file(manifest,texture.get('raw_output_path'));dds_file=local_file(manifest,texture.get('dds_output_path'))
                if raw:
                    consumed.add(raw)
                    if '/texture_' in selector:add(group,'package_records',selector,raw)
                    else:
                        with raw.open('rb') as stream:prefix=stream.read(12)
                        typ='SCNE' if prefix[:4]==b'2kTl' and struct.unpack_from('>H',prefix,8)[0]==2 else 'TXTR'
                        add(group,'records',(selector,typ),raw)
                if dds_file:
                    consumed.add(dds_file)
                    if selector in group['dds']:issues.append('Duplicate manifest DDS: '+selector)
                    group['dds'][selector]=dds_file;group['dds_rank'][selector]=3
                ref=local_file(manifest,texture.get('gtf_output_path'))
                if ref:consumed.add(ref)
        elif metadata.get('family')=='standard-iff' and isinstance(metadata.get('records'),list):
            name=manifest.parent.name.removesuffix('.subfiles')
            entry=hashes.get(hash_name(name)) if name.isascii() else None
            if entry is None:continue
            group=groups[entry['hash']];group['entry']=entry;group['name']=identity_name(entry,name)
            formats.add('python-record-manifest');consumed.add(manifest)
            for record in metadata['records']:
                paths=sorted(manifest.parent.glob(str(record['index']).zfill(4)+'_*.'+record['type'].lower()+'.block*'),key=lambda p:int(p.suffix.removeprefix('.block')))
                if paths:
                    add(group,'records',(record['name'],record['type']),paths);consumed.update(paths)
    for i,file in enumerate(sorted(files,key=lambda p:str(p.relative_to(folder)).casefold())):
        if file in consumed:continue
        if job and i%100==0:job.check();job.progress(i,len(files),'Scanning nested overrides')
        ext=file.suffix.lower()
        if ext in ('.iff','.cdf','.bin'):
            e=hashes.get(hash_name(file.name)) if file.name.isascii() else None
            if not e:issues.append('Unknown archive filename: '+str(file.relative_to(folder)));continue
            group=groups[e['hash']];group['entry']=e;group['name']=identity_name(e,file.name)
            if group['whole']:issues.append('Duplicate archive replacement: '+file.name)
            group['whole']=file;continue
        if ext not in RECORD_TYPES and ext!='.dds':ignored+=1;continue
        e,name=owner(file)
        if e is None:issues.append('No archive folder for '+str(file.relative_to(folder)));continue
        group=groups[e['hash']];group['entry']=e;group['name']=name
        if ext in RECORD_TYPES:
            formats.add('legacy-record-folders')
            add(group,'records',(file.stem,RECORD_TYPES[ext]),file)
        else:
            formats.add('legacy-record-folders')
            context=next((p for p in file.parents if p.suffix.lower() in RECORD_TYPES),None)
            if context:
                record_name=context.stem.removeprefix('_');typ=RECORD_TYPES[context.suffix.lower()]
                if typ=='SCNE':selector=record_name+'/'+file.stem
                elif typ=='TXTR':selector=record_name
                else:ignored+=1;continue
            else:selector=file.stem
            rank=2 if context else 1
            previous=group['dds'].get(selector)
            if previous:
                old_rank=group['dds_rank'][selector]
                if rank==old_rank:issues.append('Duplicate DDS target: '+str(file.relative_to(folder)))
                elif rank>old_rank:
                    shadowed.append(str(previous.relative_to(folder)));group['dds'][selector]=file;group['dds_rank'][selector]=rank
                else:shadowed.append(str(file.relative_to(folder)))
            else:group['dds'][selector]=file;group['dds_rank'][selector]=rank
    if issues:raise ValueError('Override discovery failed: '+'; '.join(issues[:8]))
    if not groups:raise ValueError('Folder and subfolders contain no supported replacements or DDS textures')
    return dict(groups=list(groups.values()),detected_formats=sorted(formats),scanned_files=len(files),ignored_files=ignored,shadowed_dds=shadowed,
                dds_files=sum(len(g['dds']) for g in groups.values()),binary_records=sum(len(g['records'])+len(g['package_records']) for g in groups.values()))



def compile_group(archive,group,job=None):
    from ..formats.standard_iff import StandardIFF
    from ..formats.standard_iff_writer import replace_records_expanding
    from ..formats.compression import decode
    from ..formats.tool_wrapper import unwrap
    from ..texture_tools.override_import import apply_dds
    original=archive.read(group['entry'])
    data=group['whole'].read_bytes() if group['whole'] else original
    if not group['records'] and not group['dds'] and not group['package_records']:return data,[]
    iff=StandardIFF(data);decoded={};changes={};details=[]
    def find(name,typ=None):
        matches=[r for r in iff.records if r['name'].casefold()==name.casefold() and (typ is None or r['type']==typ)]
        if len(matches)!=1:raise ValueError('Unknown/ambiguous record '+name+' in '+group['name'])
        return matches[0]
    def parts(rec):
        if rec['index'] in changes:return changes[rec['index']]
        result=[]
        for block,start,end in iff.spans(rec):
            if block not in decoded:
                b=iff.blocks[block];decoded[block]=decode(iff.raw[b['start']:b['start']+b['size']],b['logical_size'])
            result.append(decoded[block][start:end])
        return result
    for (name,typ),file in group['records'].items():
        if job:job.check()
        rec=find(name,typ)
        if isinstance(file,list):changes[rec['index']]=[p.read_bytes() for p in file]
        else:
            raw=file.read_bytes();changes[rec['index']]=unwrap(raw)[1] if raw[:4]==b'2kTl' else [raw]
    from ..texture_tools.override_import import apply_raw_texture
    for selector,file in group['package_records'].items():
        if selector in group['dds']:continue
        name,texture=selector.split('/',1);rec=find(name,'SCNE')
        raw=file.read_bytes();replacement=unwrap(raw)[1] if raw[:4]==b'2kTl' else [raw]
        changes[rec['index']]=apply_raw_texture(parts(rec),texture,replacement)
    for i,(selector,file) in enumerate(group['dds'].items()):
        if job:job.check();job.progress(i,len(group['dds']),'DDS priority: '+group['name']+'/'+selector)
        if '/' in selector:name,texture=selector.split('/',1);rec=find(name,'SCNE')
        else:texture=selector;rec=find(selector,'TXTR')
        try:changed,info=apply_dds(parts(rec),rec['type'],texture,file,job)
        except (ValueError,OSError) as error:raise ValueError(selector+': '+str(error)) from error
        changes[rec['index']]=changed
        details.append(dict(selector=selector,**info))
    return replace_records_expanding(iff,changes),details
