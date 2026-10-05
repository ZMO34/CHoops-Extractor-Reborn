"""Bundled converter discovery, readiness checks, execution and reporting."""
import hashlib
import json
import shutil
import uuid
from pathlib import Path
from ..archive.manifests import ROOT, OUTPUT, safe_output, write_bytes
from ..core.reports import save_json
from ..core.command_runner import run_tool
from ..core.errors import ToolError
CONFIG=OUTPUT/'config'/'texture_tools.json'
TOOLS=('gtf2dds','dds2gtf')

def configured():
    return json.loads(CONFIG.read_text(encoding='utf-8')) if CONFIG.is_file() else {}

def find(name,override=None):
    if name not in TOOLS:raise ToolError('unknown_converter',name)
    bundled=ROOT/'tools'/(name+'.exe')
    if bundled.is_file():return bundled.resolve()
    config=configured()
    candidates=[Path(config[name])] if config.get(name) else []
    if override:candidates.append(Path(override))
    candidates.extend(ROOT/folder/(name+'.exe') for folder in ('external','output/tools'))
    return next((p.resolve() for p in candidates if p.is_file()),None)

def executable_check(path):
    path=Path(path)
    if not path.is_file():return {'ready':False,'reason':'converter_missing'}
    data=path.read_bytes()
    if data[:2]!=b'MZ':return {'ready':False,'reason':'invalid_windows_executable'}
    import os
    if os.name!='nt':return {'ready':False,'reason':'windows_converter_requires_windows'}
    try:
        result=run_tool([path,'-h'],OUTPUT/'temp'/'converter_check',timeout=10)
        text=result['stdout']+result['stderr']
        # gtf2dds reports unknown -h but reaching its option parser proves execution.
        ready=bool(text.strip()) and ('Usage' in text or 'option' in text.lower() or 'gtf' in text.lower())
        return dict(ready=ready,reason='ready' if ready else 'execution_check_failed',execution=result)
    except ToolError as error:return dict(ready=False,reason=error.code,detail=error.detail)

def status(check=True):
    result={}
    for name in TOOLS:
        bundled=ROOT/'tools'/(name+'.exe');path=find(name)
        health=executable_check(bundled) if check else {'ready':False,'reason':'not_checked'}
        result[name]={'bundled_found':bundled.is_file(),'bundled_path':str(bundled),'selected_path':str(path) if path else None,**health}
    result['export_dds_ready']=result['gtf2dds']['ready']
    result['import_dds_ready']=result['dds2gtf']['ready']
    previous=OUTPUT/'reports'/'texture_tools_test.json'
    result['test_conversion_result']=json.loads(previous.read_text(encoding='utf-8')).get('status') if previous.exists() else 'not_run'
    return result

def configure(gtf2dds=None,dds2gtf=None):
    config=configured()
    for name,value in [('gtf2dds',gtf2dds),('dds2gtf',dds2gtf)]:
        if value:
            path=Path(value).resolve()
            if not path.is_file():raise ToolError('converter_missing',str(path))
            config[name]=str(path)
    save_json(CONFIG,config);return status()

def setup():
    # Installation is the one intentional write to the tracked tools directory.
    from ..archive.manifests import digest
    sources=[ROOT.parent/'UNFINISHEDBPHIT CHoops-Extractor-master'/'2k-tools'/'lib', ROOT.parent/'CHoops-Extractor-Reborn-master'/'2k-tools'/'lib', ROOT.parent/'CHoops-Extractor-Reborn-master'/'CHoops-Extractor-Reborn-master'/'2k-tools'/'lib']
    (ROOT/'tools').mkdir(exist_ok=True)
    for name in TOOLS:
        dest=ROOT/'tools'/(name+'.exe');found=next((p/(name+'.exe') for p in sources if (p/(name+'.exe')).is_file()),None)
        if not found:raise ToolError('converter_missing',f'No old-source copy of {name}.exe found')
        if dest.exists() and digest(dest.read_bytes())!=digest(found.read_bytes()):raise ToolError('converter_conflict',f'Refusing to overwrite a different bundled {name}')
        if not dest.exists():shutil.copyfile(found,dest)
    return status()

def convert(name,input_path,output_path,override=None,swizzle=False):
    exe=find(name,override)
    if not exe:raise ToolError('converter_missing',f'DDS editing requires bundled tools/{name}.exe')
    output_path=safe_output(output_path,[input_path]);output_path.parent.mkdir(parents=True,exist_ok=True)
    if output_path.exists():raise ToolError('output_exists',str(output_path))
    args=[exe,'-v','-z']
    if name=='dds2gtf' and swizzle:args.append('-s')
    args.extend(['-o',output_path,Path(input_path).resolve()])
    result=run_tool(args,output_path.parent)
    result['status']='success' if result['returncode']==0 and output_path.is_file() else 'conversion_failed'
    save_json(output_path.with_suffix(output_path.suffix+'.conversion.json'),result,[input_path])
    if result['status']!='success':
        if output_path.is_file():output_path.unlink()
        raise ToolError('conversion_failed',f"{name} exit {result['returncode']}: {result['stdout']} {result['stderr']}")
    return result

def test_tools():
    import struct
    from . import dds,gtf
    root=OUTPUT/'temp';root.mkdir(parents=True,exist_ok=True)
    out=root/('converter_test_'+uuid.uuid4().hex);out.mkdir();desc=bytearray(24)
    desc[0:4]=bytes([0xa1,1,2,0]);struct.pack_into('>HHH',desc,8,4,4,1);struct.pack_into('>I',desc,16,4)
    input_dds=out/'input.dds';write_bytes(input_dds,dds.linear_l8(4,4,1,bytes(range(16))))
    report={'status':'failed','directory':str(out),'tools':status()}
    try:
        report['import']=convert('dds2gtf',input_dds,out/'converted.gtf')
        info,descriptor,payload=gtf.parse((out/'converted.gtf').read_bytes())
        # A DXT1 synthetic texture is supported by both original converter executables.
        compressed=bytearray(128);compressed[:4]=b'DDS '
        for off,value in {4:124,8:0x81007,12:4,16:4,20:8,28:1,76:32,80:4,108:0x1000}.items():struct.pack_into('<I',compressed,off,value)
        compressed[84:88]=b'DXT1';compressed.extend(bytes.fromhex('00f8e00700000000'))
        write_bytes(out/'dxt1.dds',bytes(compressed));convert('dds2gtf',out/'dxt1.dds',out/'dxt1.gtf',swizzle=True)
        report['export']=convert('gtf2dds',out/'dxt1.gtf',out/'roundtrip.dds')
        roundtrip=(out/'roundtrip.dds').read_bytes();report['dds_metadata']=dds.inspect(roundtrip)
        if roundtrip[128:]!=bytes(compressed)[128:]:raise ToolError('converter_roundtrip_mismatch','DXT1 image bytes changed')
        report['status']='passed'
    except (ToolError,OSError,ValueError) as error:report['reason']=str(error)
    save_json(OUTPUT/'reports'/'texture_tools_test.json',report)
    return report
