# Acceptance gates

| Gate | Result / evidence |
|---|---|
| Native Qt source launch | PASS, actual window and synthetic navigation tests |
| Full real archive index/rip | PASS, 3,376/3,376 raw extents with hashes |
| Uniform/court/logo texture export | PASS, 9/9, 9/9, 51/51, 520/520 |
| Sideline export | PARTIAL, 242/248; six raw-preserved unsupported layouts |
| Atlas/roster/court/logo edited copies | PASS structural tests; no gameplay certification |
| Source safety | PASS all ten original SHA-256/size/mtime values unchanged |
| Copied JB build | PASS exact patches, all unpatched bytes, unchanged file sizes |
| Packaged executable | Local prototype built; detailed smoke report under output/reports |
| GitHub Windows/Linux CI | Must be observed on the proposed commit; no fabricated pass |
| Public binary redistribution | BLOCKED: converter redistribution grant absent; Qt notices/source compliance inventory incomplete |
| RPCS3/PS3 runtime | NOT RUN; no configured runtime provided in project settings |
| Advanced geometry/audio/relocation | Read-only research; unresolved format evidence |
| Full requested GUI/CLI parity and UX | INCOMPLETE: see FEATURE_MATRIX.md and RISKS.md |

Do not create tag/release v1.0beta while required product/packaging gates are incomplete. Local development ZIP is not a released beta. Do not merge the PR merely because synthetic CI is green.

Manual runtime checklist: boot a copied JB, inspect edited jersey numbers and court/logo, verify the modified player's jersey value, run a game with affected teams, check logs/load failures, and record emulator/firmware/source version. Never boot a test that modifies original JB files. Structural equality is not runtime compatibility.
