param()
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { $pythonExe = (Get-Command python).Source }
Push-Location $projectRoot
try {
    & $pythonExe -m PyInstaller --noconfirm --onedir --console --name CHoops-Studio --add-data 'choops_py/archive/names.json;choops_py/archive' --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtPdf --exclude-module PySide6.QtQml --exclude-module tkinter tools/rebuild/studio_entry.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    # Converters must be supplied separately until redistribution is established.
    Copy-Item -LiteralPath README.md, docs/USER_GUIDE.md, docs/rebuild/CONVERTER_PROVENANCE.md -Destination dist/CHoops-Studio
    Set-Content -LiteralPath dist/CHoops-Studio/README-START-HERE.txt -Value 'Development prototype. Run CHoops-Studio.exe. CLI: CHoops-Studio.exe --cli --help. See USER_GUIDE.md. DDS tools require separately authorized local converters; no game assets included. This build is not a published v1.0beta release.'
    & dist/CHoops-Studio/CHoops-Studio.exe --smoke
    if ($LASTEXITCODE -ne 0) { throw 'Packaged Qt smoke failed' }
} finally { Pop-Location }
