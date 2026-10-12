param()
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { $pythonExe = (Get-Command python).Source }
Push-Location $projectRoot
try {
    $nativeArgs = @()
    if (Test-Path -LiteralPath 'choops_py/formats/_h7a.dll') { $nativeArgs = @('--add-binary', 'choops_py/formats/_h7a.dll;choops_py/formats') }
    & $pythonExe -m PyInstaller --noconfirm --onedir --console --name CHoops-Studio --add-data 'choops_py/archive/names.json;choops_py/archive' --add-data 'choops_py/archive/verified_names.json;choops_py/archive' --add-data 'choops_py/audio_tools/soundtrack_names.json;choops_py/audio_tools' --add-data 'choops_py/formats/native/LICENSE.txt;choops_py/formats/native' @nativeArgs --exclude-module av --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtPdf --exclude-module PySide6.QtQml --exclude-module tkinter tools/rebuild/studio_entry.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    # Recent Qt uses Windows' unversioned ICU API. An unrelated ICU on PATH
    # can be collected by PyInstaller and shadow that API with suffixed exports.
    $bundleIcu = Join-Path $projectRoot 'dist/CHoops-Studio/_internal/icuuc.dll'
    if (Test-Path -LiteralPath $bundleIcu) {
        $icuImport = & $pythonExe -c "from pathlib import Path; import pefile; p=pefile.PE(str(Path(r'dist/CHoops-Studio/_internal/PySide6/Qt6Core.dll'))); print(int(any(i.dll.lower()==b'icuuc.dll' and any(s.name==b'ucnv_open' for s in i.imports) for i in p.DIRECTORY_ENTRY_IMPORT)))"
        $icuExport = & $pythonExe -c "from pathlib import Path; import pefile; p=pefile.PE(str(Path(r'dist/CHoops-Studio/_internal/icuuc.dll'))); print(int(any(s.name==b'ucnv_open' for s in p.DIRECTORY_ENTRY_EXPORT.symbols)))"
        if ($icuImport -eq '1' -and $icuExport -eq '0') { Remove-Item -LiteralPath $bundleIcu }
    }
    # Independent DDS conversion is included. Legacy converters are not bundled.
    Copy-Item -LiteralPath README.md, docs/USER_GUIDE.md, docs/rebuild/CONVERTER_PROVENANCE.md -Destination dist/CHoops-Studio
    Copy-Item -LiteralPath docs/AUDIO_WORKFLOW.md -Destination dist/CHoops-Studio
    Set-Content -LiteralPath dist/CHoops-Studio/README-START-HERE.txt -Value 'Run CHoops-Studio.exe. CLI: CHoops-Studio.exe --cli --help. DDS conversion is built in. The Audio workspace is experimental; WAV decode/encode needs the Python workspace and codec prerequisites because native codecs are not bundled here. External texture converters and game assets are not included. See USER_GUIDE.md and AUDIO_WORKFLOW.md. Gameplay is unverified.'
    & dist/CHoops-Studio/CHoops-Studio.exe --smoke
    if ($LASTEXITCODE -ne 0) { throw 'Packaged Qt smoke failed' }
} finally { Pop-Location }
