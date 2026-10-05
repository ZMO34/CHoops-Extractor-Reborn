"""Focused CLI schema also consumed by the GUI; one registration source."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Command:
    fields: tuple
    options: tuple = ()
    output_file: bool = False
COMMANDS={
    'build-cache':Command(('source',)), 'cache-info':Command(('source',)), 'resolve-name':Command(('value',)),
    'rip':Command(('source','output'),('rip',)),
    'texture-tools-status':Command(()), 'setup-texture-tools':Command((),('copy-tools',)),
    'test-texture-tools':Command(()), 'configure-texture-tools':Command((),('converter-config',)),
    'inspect-txtr':Command(('input','output')), 'export-dds':Command(('input','output'),('export',)),
    'export-iff-textures':Command(('input','output'),('export',)),
    'export-cdf-textures':Command(('input','cdf','output'),('export',)),
    'export-teamselectlogo-dds':Command(('input','cdf','output'),('export',)),
    'export-uniform-atlas-dds':Command(('input','output'),('export',)),
    'export-scne-textures':Command(('input','output'),('export',)),
    'export-court-textures':Command(('input','output'),('export',)),
    'import-dds':Command(('input','dds_file','output'),('import-format',),True),
    'replace-iff-texture':Command(('input','selector','dds_file','output'),('import-format',),True),
    'replace-cdf-texture':Command(('input','cdf','selector','dds_file','output'),('import-size',)),
    'import-teamselectlogo-dds':Command(('input','cdf','manifest','edited','output'),('import-size',)),
    'import-uniform-atlas-dds':Command(('input','selector','dds_file','output'),('import-format',),True),
    'import-scne-texture':Command(('input','selector','dds_file','output'),('import-format',),True),
    'replace-court-texture':Command(('input','selector','dds_file','output'),('import-format',),True),
    'import':Command(('mod','input'),('staging',)), 'list-overrides':Command(('mod',)), 'validate-mod':Command(('mod',)),
    'build-copy':Command(('source','mod','output'),('build',)),
    'validate-build':Command(('source','modded','output')),
    'roster-detect':Command(('input',)), 'roster-decode':Command(('input','output')),
    'roster-export-json':Command(('input','output')), 'roster-validate':Command(('input',)),
    'roster-save':Command(('input','patch','output'),('safe-roster',),True),
    'inspect-iff':Command(('input','output'),('inspect-iff',)),
    'validate-iff':Command(('input','output'),(),True),
    'round-trip-iff':Command(('input','output'),('compare',),True),
    'inspect-cdf-pair':Command(('input','cdf','output')),
    'validate-cdf-pair':Command(('input','cdf','output'),(),True),
    'inspect-tool-wrapper':Command(('input',)),
}
SPECS={name:list(command.fields) for name,command in COMMANDS.items()}
