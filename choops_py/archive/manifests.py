from pathlib import Path
import json, hashlib, sys
ROOT=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]
OUTPUT=ROOT/"output"
def source_root(path):
    p=Path(path).resolve()
    for candidate in [p,*p.parents]:
        if (candidate/"PS3_GAME").is_dir(): return candidate
    return p if p.is_dir() else p.parent
def safe_output(path, sources=()):
    p=Path(path).resolve()
    if not p.is_relative_to(OUTPUT.resolve()): raise ValueError("All outputs must be under project output/")
    for s in sources:
        source=Path(s).resolve()
        protected=source_root(s)
        if source.is_file() and protected==source.parent:
            if p==source: raise ValueError("Output would overwrite input")
        elif p.is_relative_to(protected): raise ValueError("Output is inside input/source folder")
    return p

def build_destination(path, sources=()):
    """User-chosen JB destination, including other drives; never a source tree."""
    raw=Path(path).absolute()
    for parent in (raw,*raw.parents):
        if parent.is_symlink() or (hasattr(parent,'is_junction') and parent.is_junction()):
            raise ValueError('Build destination must not traverse links or junctions')
    p=raw.resolve()
    if p==Path(p.anchor) or p==ROOT.resolve() or ROOT.resolve().is_relative_to(p):
        raise ValueError('Choose a separate named build folder')
    for value in sources:
        source=source_root(value).resolve()
        if p.is_relative_to(source) or source.is_relative_to(p):
            raise ValueError('Build destination overlaps an input/source folder')
    return p
def write_bytes(path,data,sources=()):
    p=safe_output(path,sources)
    if p.exists(): raise ValueError(f"Output exists: {p}")
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(data)
    return p
def report(path,data,sources=()): return write_bytes(path,(json.dumps(data,indent=2)+"\n").encode(),sources)
def digest(data): return hashlib.sha256(data).hexdigest()
def safe_name(name):
    import re
    return re.sub(r'[^A-Za-z0-9_.-]', '_',str(name)).strip('.') or 'unnamed'
