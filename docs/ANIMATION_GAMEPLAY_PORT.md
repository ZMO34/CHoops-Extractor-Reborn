# Cross-game animation and controls implementation ledger

Owner scope (2026-10-20): research and implement as much NBA 2K11/14 on-court
animation/control behavior as evidence supports, preserve the College Hoops 2K8
backend, keep original controls in preset A and make a modern right-stick layout
the default. Do not open RPCS3. Original game files remain immutable; separate
experimental local outputs are authorized. No blanket gameplay claim follows from
an IFF parser, successful build or executable decompilation.

## What is implemented in the editor

- Archive discovery resolves 21 additional animation/graph bank filenames. Each
  matches a literal filename in a supplied executable and an actual archive CRC;
  these banks appear in Explorer's Animation banks category.
- Animation inventory validates record counts against actual header bounds. The
  previous arbitrary 10,000-record check silently skipped NBA 2K14's main bank.
  Inventory now includes 22,139 SingleMoCap records across standard IFFs, including
  14,679 in nba_animations.iff. Its 4,226 companion 0x39F61D57 records are separate.
- Read-only motion envelope profiles follow confirmed native pointer fixups for
  CH2K8 and NBA 2K11. Reference IDs are distinguished from payload pointers;
  the NBA event-entry list is bounded and checked for its native sentinel.
- The alias inspector reports local source-ID candidates, missing/external IDs,
  ambiguities and cycles without calling them resolved gameplay dependencies.
- Motion selection collection envelopes have distinct observed strides: NBA
  2K11 uses 20 bytes; NBA 2K14 uses 28. Neither profile enables an import writer.
- Seven prior PR branches (#31–#37) are consolidated with ancestry retained.
  Legacy saves, override compatibility checks, faces, SDAT v3 reads, scorebug
  contracts, executable research documentation and uniform editing are preserved.
  The renamed roster-open button's GUI regression expectation is updated; added
  synthetic Legacy tests cover layout rejection, truncation and outer-byte
  preservation. A draft Legacy PR is not treated as gameplay-certified save use.

## Native evidence from supplied Ghidra and original disassembly

Focused Ghidra projects use PowerPC big-endian 64-bit/32-bit addresses, OPD-derived
TOC contexts and the supplied PS3 script conventions. Direct disassembly verifies
function starts and import calls; the nearest OPD alone is insufficient because
local functions do not all have OPD entries. Game code/project exports remain
private and are not bundled with the editor.

| Revision | Confirmed native route | Consequence |
| --- | --- | --- |
| CH2K8 | Motion relocation at 0x1E9C0 touches +0x30/+0x34/+0x38/+0x3C and a pointer tail at +0x40 sized by +0x10 & 0x3F | The older envelope cannot be populated using NBA offsets. |
| CH2K8 | Resource reference resolver/handler at 0x241E0/0x24478 uses +0x30 as source identity for an unresolved +0x38 | Mirror/reference rows are not standalone packed pose streams. |
| NBA 2K11 | Relocation at 0x15F24 touches +4/+0x24/+0x28/+0x2C/+0x30/+0x34, tail +0x38, plus 12-byte entries through an INT_MIN sentinel | Added pointer/event dependencies must be converted, not copied. Event meanings are unresolved. |
| NBA 2K11 | Reference handler at 0x1C604 uses source identity +0x28 and resolution field +0x30 | Old CH alias offsets would read the wrong source key. |
| NBA 2K14 | Native 0x74A41C dispatch distinguishes 0x60900D71 from 0x449E4AC7 and iterates the latter with a 28-byte stride | Shared type hashes do not establish identical collection layouts. |
| CH2K8 | Imported cellPadGetData (NID 0x8B72CDA1) reaches poller 0x7B2358 via call 0x7B26F0 | Raw analog decoding is established; gameplay action mapping remains downstream. |
| NBA 2K11 | Same authenticated import reaches poller 0x861454 via call 0x8617C0 | This is an input-device boundary, not a portable dribble implementation. |
| NBA 2K14 | Same import reaches poller 0xB5DAF0 via call 0xB5DC00 | Copying this poller would not supply the Pro Stick gameplay system. |

The native relative-pointer helper adds signed field value minus one to the
field address, leaving zero null. In unresolved motion records the source-ID field
must be handled before treating that location as a pointer. Actual CH crowd
samples yielded 125 packed records and 125 aliases with local candidates; NBA
2K11 siganims_generic yielded 333 packed and 333 aliases. Both produced zero
envelope errors/cycles. This does not establish compatible skeletons or poses.

Native dribble graphs are separate 0x0D53D4B3 resources. The supplied 2K11 dribbler
graph decodes to 770,144 bytes; 2K14 to 2,611,944 bytes, with different contents and
header organization. The exact-name CRC of `animgraph` matches this type hash,
and each executable contains ANIMGRAPHRESOURCEHANDLER metadata. Graph opcode,
transition/blending and contact semantics are not decoded. NBA 2K14's motion.iff
also has three unresolved 0x9D34E89E resources; these are not relabeled skeletons.

Control-menu reflection was traced at CH 0x6BC12C. Its localized entries include
Controller Setup, and a native menu descriptor names ControllerConfigMenu. This
is menu registration rather than the downstream dribble/shooting action map.
Stock tutorial text explicitly warns that some drills depend on Default controls;
changing a preset requires checking those consumers as well. A global left/right
axis swap is not an implementation of the requested controls.

## Explicit remaining implementation

**No donor animation is yet playable in CH2K8. No new default/control preset is
installed. No smoother gameplay or entire on-court system port is claimed.**

Remaining dependencies are packed rotation/translation/time decoding and encoding,
per-bone names/order/bind poses and retargeting, root motion, ball/hand/foot contacts,
paired interaction events, animation ID/variant selection, blend/transition graph
execution, shooting/defense/AI consumers and memory limits. Players/teams BIN
payloads remain opaque and must not be confused with an already decoded clip bank.

For controls, trace the gameplay-specific dribble and shooting consumers after
analog normalization, map preset save/load and reset/default paths, implement a
context-aware modern layout, retain original behavior in preset A and account for
training/post/defensive/menu consumers. No speculative executable patch is enabled.

## Reproduce supported investigation

```
python -m choops_py.research.animation_compat CH_JB NBA11_JB NBA14_JB --output output/research/animation-current.json
python -m choops_py.cli rip NBA14_JB output/rips/nba14 --file nba_animations.iff --raw-iff
python -m choops_py.cli inspect-animation-links EXTRACTED_BANK.iff college-hoops-2k8 output/research/ch-links.json
python -m choops_py.cli inspect-animation-links EXTRACTED_BANK.iff nba-2k11 output/research/nba11-links.json
```

Use the matching profile. The links command rejects NBA 2K14 because its packed
motion envelope is not established. It reports local candidates rather than
silently resolving cross-bank references. Source assets, reports and executable
analysis copies are local, excluded from Git. No RPCS3 or testing JB is used.
