from pathlib import Path
import json
from ..archive.manifests import safe_output,write_bytes,report,digest
from ..formats.standard_iff import StandardIFF
from ..formats.tool_wrapper import unwrap
def relative_asset(name):
    p=Path(name)
    if p.is_absolute() or len(p.parts)!=1 or p.name in ('.','..') or ':' in name or '/' in name or '\\' in name:raise ValueError("Archive name must be a plain filename")
    return p.name
def listing(mod):
    p=Path(mod)/'overrides.json'
    return json.loads(p.read_text()) if p.exists() else []
def stage(mod,file,iff,sub=None):
    mod=safe_output(mod,[file]);name=relative_asset(iff);data=Path(file).read_bytes();rows=listing(mod)
    if any(r['archive']==name and r['subfile']==sub for r in rows):raise ValueError("Override already staged")
    target=f"assets/{len(rows):04d}.bin";write_bytes(mod/target,data,[file]);rows.append(dict(archive=name,subfile=sub,path=target,sha256=digest(data),size=len(data)))
    manifest=safe_output(mod/'overrides.json',[file])
    if manifest.exists():manifest.unlink()
    report(manifest,rows);return rows[-1]
def validate(mod):
    mod=Path(mod).resolve();rows=listing(mod)
    for r in rows:
        relative_asset(r['archive']);p=(mod/r['path']).resolve()
        if not p.is_relative_to(mod):raise ValueError("Override escapes mod directory")
        data=p.read_bytes()
        if digest(data)!=r['sha256'] or len(data)!=r['size']:raise ValueError("Staged asset changed; reimport required")
        if r['subfile'] is None and r['archive'].lower().endswith('.iff'):
            magic=data[:4]
            if magic==bytes.fromhex('ff3bef94'):StandardIFF(data)
            elif magic==bytes.fromhex('f0985030'):raise ValueError("CDF whole-pair staging not yet validated")
            else:raise ValueError("Invalid IFF override")
    return rows
