"""Content-addressed builtin texture conversion cache with corruption checks."""
import hashlib
import os
import uuid
import re
from pathlib import Path
from ..archive.manifests import OUTPUT


def cached_conversion(name,source,swizzle,convert,root=None):
    folder=Path(root) if root is not None else OUTPUT/'cache'/'texture_conversions'
    identity=hashlib.sha256(b'choops-conversion-cache-1')
    for module in ('builtin_converter.py','dds.py','gtf.py','runtime_layout.py'):
        identity.update(Path(__file__).with_name(module).read_bytes())
    from PIL import __version__
    identity.update(__version__.encode())
    identity.update(name.encode());identity.update(bytes([bool(swizzle)]));identity.update(source)
    key=identity.hexdigest();target=folder/(key+'.bin')
    try:
        cached=target.read_bytes()
        if len(cached)>=32 and hashlib.sha256(cached[32:]).digest()==cached[:32]:
            target.touch()
            return cached[32:],True
    except OSError:pass
    result=convert()
    # Cache failures never prevent conversion; cap any one stored entry.
    if len(result)<=128*1024*1024:
        temporary=folder/('.'+uuid.uuid4().hex)
        try:
            folder.mkdir(parents=True,exist_ok=True)
            entries=[p for p in folder.glob('*.bin') if re.fullmatch(r'[0-9a-f]{64}\.bin',p.name) and not p.is_symlink() and p.resolve().is_relative_to(folder.resolve())]
            sizes={p:p.stat().st_size for p in entries};total=sum(sizes.values())
            for old in sorted(entries,key=lambda p:p.stat().st_mtime_ns):
                if total+len(result)+32<=512*1024*1024:break
                total-=sizes[old];old.unlink()
            temporary.write_bytes(hashlib.sha256(result).digest()+result)
            os.replace(temporary,target)
        except OSError:pass
        finally:
            if temporary.exists():temporary.unlink()
    return result,False
