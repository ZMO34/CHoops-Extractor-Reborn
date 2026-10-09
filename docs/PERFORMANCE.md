# Workstation performance — 2026-10-09

Windows 11 build 26200, Python 3.12.14, 8 physical/16 logical CPUs, approximately 16 GiB RAM. Read-only JB: 4,862,682,189 bytes across ten files. Five archive parts, 3,376 entries. Single observations from time.perf_counter; no invented before/after comparisons.

| Operation | Seconds |
|---|---:|
| index_seconds | 0.065 |
| selective_seconds | 0.0769 |
| ua000.iff_export_seconds | 3.0413 |
| atlas_import_seconds | 2.9672 |
| uh000.iff_export_seconds | 3.1148 |
| s000.iff_export_seconds | 6.652 |
| teamselectlogo.iff_export_seconds | 25.5603 |
| sideline_items.iff_export_seconds | 15.3035 |
| roster_load_seconds | 0.6675 |
| roster_edit_seconds | 0.0961 |
| roster_save_seconds | 5.0765 |
| full_rip_seconds | 35.5861 |
| stage_seconds | 0.0836 |
| dry_run_seconds | 0.0224 |
| build_seconds | 28.8679 |

Full raw rip completed 3,376/3,376. Eight representative selective extents: 29,169,664 bytes. Texture exports: 831/837 candidates. Initial build measurement predates addition of exhaustive unpatched-byte comparison, so it must not be represented as the final stronger builder timing. Cold/warm startup, peak resident memory, full-cache acceleration, cancellation latency and model viewport are not measured yet.

Targeted synthetic before/after benchmark: 5,000 IFF records, all spans enumerated once. Baseline source 2.532895s; precomputed spans 0.003778s. Same generated file, final spans checked. This is a synthetic parser comparison, not a real-game overall speedup claim.
