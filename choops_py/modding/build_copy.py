import shutil
from pathlib import Path
from .overrides import validate
from ..archive.usrdir_reader import Archive,usrdir
from ..archive.manifests import safe_output,source_root,report
from ..formats.standard_iff import StandardIFF
def build(source,mod,output,overwrite=False,dry_run=False):
    src=Path(source).resolve();out=safe_output(output,[src,mod]);rows=validate(mod);a=Archive(src);plan=[];patches=[]
    if out.exists() and any(out.iterdir()):raise ValueError("Build output must be empty; --overwrite never deletes an existing game")
    grouped={}
    for row in rows:grouped.setdefault(row['archive'],[]).append(row)
    for name,group in grouped.items():
        matches=[e for e in a.entries if e['name']==name]
        if len(matches)!=1:raise ValueError(f"Archive identity unresolved: {name}")
        e=matches[0];original=a.read(e);data=original
        for row in group:
            payload=(Path(mod)/row['path']).read_bytes()
            data=StandardIFF(data).replace(row['subfile'],payload) if row['subfile'] is not None else payload
        if len(data)!=len(original):raise ValueError("Build requires same-size archive replacements")
        patches.append((e,data));plan.append(dict(archive=name,index=e['index'],size=len(data)))
    if dry_run:return dict(dry_run=True,patches=plan)
    # Reject symlinks/junctions before copying or patching.
    for p in src.rglob('*'):
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):raise ValueError("Linked source entries are not supported")
    shutil.copytree(src,out,dirs_exist_ok=True)
    copied_usrdir=out/a.path.relative_to(src)
    for e,data in patches:
        start=e['offset'];remaining=len(data);pos=0;base=0
        for part in a.parts:
            end=base+part['size']
            if base<=start<end and remaining:
                n=min(remaining,end-start)
                with (copied_usrdir/part['name']).open('r+b') as f:f.seek(start-base);f.write(data[pos:pos+n])
                start+=n;remaining-=n;pos+=n
            base=end
        if remaining:raise ValueError("Incomplete patch")
    report(out/'build_manifest.json',dict(source=str(src),patches=plan),[src]);return plan
