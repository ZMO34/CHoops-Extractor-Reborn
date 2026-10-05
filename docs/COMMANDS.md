# Commands

Run from the project folder. All destination paths must be under output/. Use each command's --help for flags. Numeric wrapper type IDs preserve the legacy wrapper contract. Replacement commands require --same-size-only.

```text
usage: bootstrap_docs.py gui [-h]
usage: bootstrap_docs.py build-cache [-h] [--game-name {choops2k8}] source
usage: bootstrap_docs.py cache-info [-h] source
usage: bootstrap_docs.py resolve-name [-h] value
usage: bootstrap_docs.py rip [-h] [--game-name {choops2k8}] [--cache |
                             --build-cache] [--index INDEX] [--file FILE]
                             [--iff-only] [--raw-iff] [--type TYPE [TYPE ...]]
                             [--log-output LOG_OUTPUT] [--strict]
                             source output
usage: bootstrap_docs.py inspect-iff [-h] [--dump-subfiles] input output
usage: bootstrap_docs.py validate-iff [-h] input output
usage: bootstrap_docs.py round-trip-iff [-h] [--compare] input output
usage: bootstrap_docs.py dump-iff-subfiles [-h] input output
usage: bootstrap_docs.py replace-iff-subfile [-h] --same-size-only
                                             input selector replacement output
usage: bootstrap_docs.py inspect-cdf-pair [-h] input cdf output
usage: bootstrap_docs.py validate-cdf-pair [-h] input cdf output
usage: bootstrap_docs.py dump-cdf-pair [-h] input cdf output
usage: bootstrap_docs.py round-trip-cdf-pair [-h] [--compare] input cdf output
usage: bootstrap_docs.py replace-cdf-payload [-h] --same-size-only
                                             input cdf selector replacement
                                             output
usage: bootstrap_docs.py inspect-tool-wrapper [-h] input
usage: bootstrap_docs.py unwrap-tool-file [-h] input output
usage: bootstrap_docs.py wrap-tool-file [-h] type blocks [blocks ...] output
usage: bootstrap_docs.py inspect-txtr [-h] input output
usage: bootstrap_docs.py extract-textures [-h] [--raw] input output
usage: bootstrap_docs.py inspect-uniform-atlas [-h] input output
usage: bootstrap_docs.py import [-h] --iff IFF [--sub SUB] mod input
usage: bootstrap_docs.py list-overrides [-h] mod
usage: bootstrap_docs.py validate-mod [-h] mod
usage: bootstrap_docs.py build-copy [-h] [--overwrite] [--dry-run]
                                    source mod output
usage: bootstrap_docs.py validate-build [-h] source modded output
usage: bootstrap_docs.py audit-rip [-h] inventory rip_output output
usage: bootstrap_docs.py roster-detect [-h] input
usage: bootstrap_docs.py roster-decode [-h] input output
usage: bootstrap_docs.py roster-compare [-h] input custom output
usage: bootstrap_docs.py roster-validate [-h] input
usage: bootstrap_docs.py inspect-floor-scne [-h] input output
usage: bootstrap_docs.py inspect-audo [-h] input output
usage: bootstrap_docs.py extract-audio-payloads [-h] input [cdf] output
```
