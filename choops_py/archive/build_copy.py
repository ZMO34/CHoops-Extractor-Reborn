"""Transactional modded JB folder builds. Vanilla is always read-only."""
import json
import os
import shutil
import uuid
from pathlib import Path
from .importer import validate
from .usrdir_reader import Archive,usrdir
from .manifests import OUTPUT,safe_output,digest
from ..core.reports import save_json
from ..core.paths import reject_links
from ..core.errors import ToolError
from ..formats.standard_iff import StandardIFF
from ..formats.standard_iff_writer import record,record_blocks,replace_records
from ..formats.tool_wrapper import unwrap
from ..formats.cdf_backed_iff import CDFPair
from ..texture_tools.pipeline import Container,imported_image

def jb_root(source):
    source=Path(source).resolve()
    for p in [source,*source.parents]:
        if (p/'PS3_GAME'/'USRDIR'/'0A').is_file():return p
    raise ToolError('jb_folder_required','Select a vanilla JB folder containing PS3_GAME/USRDIR/0A')

def inventory(source):
    return {str(p.relative_to(source)):{'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in source.rglob('*') if p.is_file()}

def preflight(source,mod):
    archive=Archive(source);rows=validate(mod);grouped={};patches=[]
    conditions=Path(mod)/'source_preconditions.json'
    if conditions.exists():
        document=json.loads(conditions.read_text(encoding='utf-8'))
        if document.get('schema')!=1:raise ToolError('invalid_source_preconditions','Unsupported schema')
        for expected in document['entries']:
            index=expected['index']
            if not isinstance(index,int) or not 0<=index<len(archive.entries):raise ToolError('source_version_mismatch','TOC index differs')
            entry=archive.entries[index]
            if entry['hash']!=expected['hash'] or digest(archive.read(entry))!=expected['sha256']:
                raise ToolError('source_version_mismatch','Original archive asset changed since staging')
    for row in rows:grouped.setdefault(row['archive'].lower(),[]).append(row)
    for name,group in grouped.items():
        matches=[e for e in archive.entries if e['name'] and e['name'].lower()==name]
        if len(matches)!=1:raise ToolError('unresolved_archive_identity',name)
        entry=matches[0];original=archive.read(entry);data=original
        for row in group:
            path=Path(mod)/row['path'];replacement=path.read_bytes()
            if row.get('kind')=='dds':
                # Reuse the same import pipeline, using an output/temp copy as the
                # evolving source. Nothing is written into vanilla.
                work=safe_output(OUTPUT/'temp'/('build_preflight_'+uuid.uuid4().hex));work.mkdir()
                input_file=work/entry['name'];input_file.write_bytes(data)
                c=Container(input_file)
                asset=c.select(row['subfile']);image,_=imported_image(asset,path);data=c.replacement(asset,image)
            elif row['subfile'] is not None:
                iff=StandardIFF(data);rec=record(iff,row['subfile'])
                parts=unwrap(replacement)[1] if replacement[:4]==b'2kTl' else [replacement]
                data=replace_records(iff,{rec['index']:parts})
            else:data=replacement
        if len(data)>len(original):raise ToolError('archive_extent_capacity_exceeded',f'{name} needs {len(data)} bytes; allocation {len(original)}')
        if len(data)<len(original):
            if data[:4]!=bytes.fromhex('ff3bef94'):raise ToolError('archive_size_change_blocked',name)
            StandardIFF(data);data+=b'\0'*(len(original)-len(data))
        if data[:4]==bytes.fromhex('ff3bef94'):StandardIFF(data)
        patches.append((entry,data))
    final={e['name'].lower():data for e,data in patches if e['name']}
    for entry,data in patches:
        if data[:4]==bytes.fromhex('f0985030'):
            partner=entry['name'][:-4]+'.cdf';matches=[e for e in archive.entries if e['name'] and e['name'].lower()==partner.lower()]
            if len(matches)!=1:raise ToolError('cdf_pair_required',partner)
            CDFPair(data,final.get(partner.lower(),archive.read(matches[0])))
        elif entry['name'].lower().endswith('.cdf'):
            partner=entry['name'][:-4]+'.iff';matches=[e for e in archive.entries if e['name'] and e['name'].lower()==partner.lower()]
            if len(matches)!=1:raise ToolError('cdf_pair_required',partner)
            CDFPair(final.get(partner.lower(),archive.read(matches[0])),data)
    return archive,patches

def patch_parts(archive,directory,entry,data):
    start=entry['offset'];remaining=len(data);position=0;base=0
    for part in archive.parts:
        end=base+part['size']
        if base<=start<end and remaining:
            n=min(remaining,end-start);path=directory/part['name']
            with path.open('r+b') as stream:stream.seek(start-base);stream.write(data[position:position+n])
            remaining-=n;position+=n;start+=n
        base=end
    if remaining:raise ToolError('incomplete_archive_patch','Split archive write did not consume all data')

def verify_preserved_ranges(source, copied, archive, patches):
    """Prove every byte outside staged logical extents equals the source."""
    source=Path(source);copied=Path(copied)
    ranges={};base=0
    for part in archive.parts:
        intervals=[]
        for entry,data in patches:
            lo=max(base,entry['offset']);hi=min(base+part['size'],entry['offset']+len(data))
            if lo<hi:intervals.append((lo-base,hi-base))
        ranges[str((archive.path/part['name']).relative_to(source))]=intervals
        base+=part['size']
    for relative in inventory(source):
        excluded=ranges.get(relative,[]);position=0
        with (source/relative).open('rb') as left,(copied/relative).open('rb') as right:
            while True:
                old=left.read(1024*1024);new=right.read(1024*1024)
                if not old:
                    if new:raise ToolError('build_validation_failed','Copied file grew')
                    break
                if len(old)!=len(new):raise ToolError('build_validation_failed','Copied file resized')
                cursor=0
                for lo,hi in sorted(excluded):
                    if lo>=position+len(old) or hi<=position:continue
                    start=max(0,lo-position);end=min(len(old),hi-position)
                    if old[cursor:start]!=new[cursor:start]:raise ToolError('build_validation_failed','Untouched bytes changed')
                    cursor=end
                if old[cursor:]!=new[cursor:]:raise ToolError('build_validation_failed','Untouched bytes changed')
                position+=len(old)


def build(source,mod,output,overwrite=False,dry_run=False):
    src=jb_root(source);out=safe_output(output,[src,mod])
    if not out.is_relative_to((OUTPUT/'builds').resolve()) or out==(OUTPUT/'builds').resolve():raise ToolError('unsafe_build_output','Build destinations must be output/builds/<build_name>/')
    reject_links(src)
    if out.exists() and any(out.iterdir()):
        marker=out/'build_manifest.json'
        if not overwrite:raise ToolError('output_exists','Use --overwrite for an existing generated JB build')
        if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('project_kind')!='choops-jb-copy':raise ToolError('unowned_build_output',"Refusing to overwrite a folder without this tool's build manifest")
        reject_links(out)
    archive,patches=preflight(src,mod);plan=[{'archive':e['name'],'index':e['index'],'size':len(data),'sha256':digest(data)} for e,data in patches]
    if dry_run:return {'dry_run':True,'source':str(src),'output':str(out),'patches':plan}
    before=inventory(src);out.parent.mkdir(parents=True,exist_ok=True)
    staging=safe_output(out.parent/('.jb_build_'+uuid.uuid4().hex),[src,mod]);backup=None
    print('Copying vanilla JB into a separate output build...',flush=True)
    try:
        shutil.copytree(src,staging)
        copied_usrdir=staging/archive.path.relative_to(src)
        for entry,data in patches:patch_parts(archive,copied_usrdir,entry,data)
        copied=Archive(copied_usrdir)
        for entry,data in patches:
            if copied.read(copied.entries[entry['index']])!=data:raise ToolError('build_validation_failed',f"Written archive differs: {entry['name']}")
        for relative,metadata in before.items():
            path=staging/relative
            if not path.is_file() or path.stat().st_size!=metadata['size']:raise ToolError('build_validation_failed',f'Copied file missing or resized: {relative}')
        verify_preserved_ranges(src,staging,archive,patches)
        if inventory(src)!=before:raise ToolError('vanilla_changed_during_build','Vanilla source inventory changed during copying; discard build and retry')
        manifest={'project_kind':'choops-jb-copy','source':str(src),'mod':str(Path(mod).resolve()),'output':str(out),'patches':plan,'file_count':len(before),'vanilla_inventory_unchanged':True,'validation':{'inventory_and_sizes':True,'patched_extents_byte_exact':True,'all_unpatched_bytes_exact':True,'console_gameplay':'not tested'}}
        save_json(staging/'build_manifest.json',manifest,[src,mod])
        if out.exists():
            backup=safe_output(out.parent/('.jb_previous_'+uuid.uuid4().hex));out.rename(backup)
        staging.rename(out)
        if backup:shutil.rmtree(backup)
        return manifest
    except Exception:
        if staging.exists():shutil.rmtree(safe_output(staging))
        if backup and backup.exists() and not out.exists():backup.rename(out)
        raise
