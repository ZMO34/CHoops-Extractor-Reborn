# Backend research with Ghidra

Use Ghidra regularly for native backend investigations, including scorebug loaders,
text providers, resource selection and roster access. Keep findings in maintained
research docs and publish reviewable updates through the task's GitHub PR.

## Local tools and Research tab

The editor's Research page has **Open backend tools folder (Ghidra / PS3 scripts)**.
It opens `output/research/backend-tools` under the running application's output
root. Downloads are local and are not bundled into editor releases or Git.
The folder contains one portable Ghidra installation, matching Ps3GhidraScripts
extension and portable Java runtime. Retain this folder during future cleanup.

Selected matching pair: Ghidra 12.1.2 and Ps3GhidraScripts 1.0111's 12.1.2 build.
Upstream instructs installing the matching extension through File > Install
Extensions. Do not force a differently versioned extension into a newer Ghidra.
The extension is installed under Ghidra/Extensions/Ps3GhidraScripts; the required
r2 unaffected-register adjustment is applied with a .cspec.original backup.
The launchers also scope XDG_CONFIG_HOME and XDG_CACHE_HOME inside the tools folder.
Official sources:
- https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.2_build
- https://github.com/clienthax/Ps3GhidraScripts/releases/tag/1.0111
- https://github.com/clienthax/Ps3GhidraScripts/blob/1.0111/README.md

The local downloads.json records URLs, byte lengths and SHA-256 values. Validate
archives against upstream digests before extraction. Use a local launcher with
JAVA_HOME scoped to that process; do not change system Java or PATH.

## PS3 analysis sequence

Import an analysis copy of the decoded vanilla ELF using big-endian
PowerISA-Altivec-64-32addr (language ID `PowerPC:BE:64:A2ALT-32addr`,
compiler `default`). Before normal auto-analysis, follow the extension's
AnalyzePs3Binary instructions. The upstream README requires adding r2 to the
unaffected register list in PowerPC/data/languages/ppc_64_32.cspec. Record this
local tool adjustment, retaining a baseline for comparison. Run auto-analysis
then DefinePs3Syscalls. Relocations and some Cell instructions have limitations.

For reconstructed decoded ELFs, independently validate section mapping, OPD and
TOC first; do not assume script success proves correct dataflow. This title has
32-bit address function descriptors and multiple TOCs. Record which TOC belongs
to each investigated function and preserve native calling conventions.

For each finding record function address, callers/callees, relevant field or
resource identity, observed instructions/decompiler reasoning, confidence and
unresolved assumptions. Distinguish static evidence from synthetic harness and
runtime evidence. Keep projects, GZF/GAR exports, raw decompilation, executable
copies and private paths outside Git. Publish authored explanations and bounded
synthetic tests instead of game binaries. No EBOOT edits, emulator or full JB
build is authorized by this workflow.

Current target: cross-check the alternate scorebug loader/provider paths and find
an existing IFF-controlled activation bridge for automatic roster team names.
See SCOREBUG_IFF_ONLY_AUDIT.md; names remain unfinished and packaging is held.

## Setup verification

All three archives matched upstream lengths and SHA-256 digests. Headless startup
discovers the installed PS3 script directory. The decoded vanilla analysis ELF
imports and saves with the specified language and -noanalysis. This establishes
tool startup/import only; PS3 script execution, TOC context and decompiler results
still require separate validation before treating output as backend evidence.
