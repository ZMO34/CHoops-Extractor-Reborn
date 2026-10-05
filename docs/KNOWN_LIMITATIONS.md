# Known limitations

- Roster detect/decode/validate provides raw wrapper/size/hash evidence; semantic decoding, save-container recognition and field editing are blocked. It never labels unvalidated fields safe.
- TXTR dimensions/format words are candidates; DDS conversion and uniform glyph mapping are not implemented.
- Standard compressed replacement and multi-block replacement are blocked. No recompression or size-changing archive writer.
- CDF physical same-size replacement preserves bytes but does not certify payload codec semantics. Whole-pair build staging is blocked.
- Floor SCNE exposes header/model records; no mesh export, material rewrite or UV editing. Audio stays raw; inspect-audo inspects one raw file, not an automatically resolved pair.
- Cache is reproducible and fingerprint checked, but reparses the TOC. Namespace resolution is extensive rather than guaranteed complete; hash collisions need future explicit handling.
- validate-build checks file existence, sizes and hashes; console boot/gameplay testing remains required. No ISO authoring or texture resizing profiles.
- Full-game rip has not been run. Real-game smoke tests cover one standard uniform and one CDF pair.
- Existing output files/builds are refused. GUI has live jobs but no cancellation. Use numeric wrapper type IDs.

Publication and test environment blockers are recorded in CODEX_UPDATE_SUMMARY.md.
