# Evidence-based feature matrix



Statuses describe this rebuild, not historical proof. “Tested” means structural/local software behavior; no row is in-game verified.



| Feature | Legacy JS | Current Python/native | Evidence | Formats | Access | Risk | Speed | Milestone/status | Blocker |

|---|---|---|---|---|---|---|---|---|---|

| New/open/recent project | Path picker | Game picker + remembered path; profiles absent | Local evidence retained privately; synthetic tests in tests/ | JB | Read | Low | No public timing claim | C: tested partial | Project manifests/profiles/recent list |

| Split TOC/hash identities | Reader/hash cache | Archive reader + chunk iterator | Local evidence retained privately; synthetic tests in tests/ | 0A–0E | Read | Bounds | No public timing claim | B: tested | Persistent SQLite acceleration absent |

| Archive/nested browser | GUI + reader | Virtual Qt table/search + nested records | Local evidence retained privately; synthetic tests in tests/ | IFF/CDF | Read | Low | No public timing claim | C: tested partial | Context menus/history/favorites absent |

| Raw/selective/full extraction | Ripper | Chunked paired raw extraction/cancel | Local evidence retained privately; synthetic tests in tests/ | Split archive | Export | Collision preflight | No public timing claim | B: tested | Resume/retry UI absent |

| Standard IFF | Reader/writer | Bounded writer + precomputed spans | Local evidence retained privately; synthetic tests in tests/ | FF3BEF94 | Bounded write | Aliases/capacity | No public timing claim | B: tested | Arbitrary logical growth blocked |

| CDF pairs | Paired extractor/import | Physical allocation-preserving edit | Local evidence retained privately; synthetic tests in tests/ | F0985030/CDF | Bounded write | Compression allocation | No public timing claim | B/D: tested | Virtual/physical relocation |

| H7A/wrappers | Decode/writer | Bounded token reuse + strict wrapper | Local evidence retained privately; synthetic tests in tests/ | H7A/2kTl | Bounded write | Growth/512MiB cap | No public timing claim | B: tested | General optimizer not implemented |

| Texture pipeline/preview | Converters/TXTR | Shared DDS/GTF, native real preview | Local evidence retained privately; synthetic tests in tests/ | L8/ARGB8/DXT1/3/5 | Read/edit-copy | Layout/mips/capacity | No public timing claim | D: tested partial | PNG import, mip regeneration, cubes unsupported |

| Uniform/atlas | Extract/import | Shared DDS pipeline | Local evidence retained privately; synthetic tests in tests/ | Standard IFF TXTR | Edit-copy | Glyph semantics unknown | No public timing claim | D: tested | No automatic glyph layout editing |

| Team logos | CDF logo workflow | Paired export/import | Local evidence retained privately; synthetic tests in tests/ | IFF/CDF | Edit-copy | Capacity | No public timing claim | D: tested | Not every pixel edit fits compressed allocation |

| Court/arena textures | SCNE texture parser | Shared scene-texture route | Local evidence retained privately; synthetic tests in tests/ | SCNE/TXTR | Edit-copy | Unknown layouts | No public timing claim | D: tested | No unproven resizing/material changes |

| Geometry inspection/export/import | Stable wrapper + experimental scorer | SCNE metadata only | Local evidence retained privately; synthetic tests in tests/ | SCNE | Read-only | Topology/declarations unvalidated | No public timing claim | D: research/read-only | Validated vertex/UV/material decoder/runtime |

| Roster player/team/arena/coach | Roster editor | 4 Qt tables + safe forms/undo/redo | Local evidence retained privately; synthetic tests in tests/ | ROST | Known fields only | Pointer aliases | No public timing claim | D: tested partial | Slot drag/reorder/multi-edit UX |

| Roster adapters/patches | ROST/decrypted inputs | Adapters + source-hashed JSON patch | Local evidence retained privately; synthetic tests in tests/ | IFF/ROST/2kTl/USERDATA/ZIP | Edit-copy | Source mismatch rejected | No public timing claim | D: tested | Encrypted saves unsupported; compare UI absent |

| Palette/conference/prestige/etc | Experimental raw slots | No safe semantic editors | Local evidence retained privately; synthetic tests in tests/ | ROST | Read-only | Unknown semantics | No public timing claim | D: research | Controlled comparisons/runtime evidence |

| Hex/pointer/hash research | Research modules | Bounded hex + CLI hash lookup | Local evidence retained privately; synthetic tests in tests/ | Unknown/raw | Read-only | Low | No public timing claim | D: partial | Full offset/pointer/search/byte-diff tooling |

| Audio/animation/database | Probe/heuristics | Unknown record metadata/raw extraction | Local evidence retained privately; synthetic tests in tests/ | AUDO/CDAN/LAYT | Read-only/raw | Unknown codec | No public timing claim | D: research | Codec/animation schemas not verified |

| Mod workspace/conflicts | Import/revert | Hashed staged overrides + folder preflight | Local evidence retained privately; synthetic tests in tests/ | IFF/CDF/DDS | Stage | Source preconditions | No public timing claim | E: tested partial | Profiles/revert UI; checksum/source conflicts rejected |

| Repack/add/delete/relocate | Writer experiments | Existing extents only | Local evidence retained privately; synthetic tests in tests/ | Archive/IFF/CDF | Conservative | Unproven relocation | No public timing claim | E: limited tested | New/growing entries blocked |

| Dry run/transactional JB | Build-copy | Original protected, copied patched/unpatched bytes verified | Local evidence retained privately; synthetic tests in tests/ | JB split parts | Copy-write | Source safety | No public timing claim | E: tested | Free-space UX incomplete |

| Mod package/folder builder/ISO | Build-copy/ISO ideas | Folder stage/build + bounded XOR patch package | Local evidence retained privately; synthetic tests in tests/ | IFF/CDF folder | Stage/copy | Copyright/source version | No public timing claim | E: partial | Validated ISO remains unavailable |

| Native desktop GUI | Legacy JS/Tk/Web | Functional Qt app + jobs and pickers | Local evidence retained privately; synthetic tests in tests/ | Qt Widgets | Contextual | Read/write services | No public timing claim | C/F: tested partial | Remaining complete UX acceptance gaps |

| Caching/performance/cancel | Cache/profiling ideas | Span index, streaming extraction/cancel | Local evidence retained privately; synthetic tests in tests/ | Archive/IFF | Read/export | Low | No public timing claim | B/F: partial | SQLite cache; parser cancel; peak RSS unmeasured |

| Windows standalone/CI | Old JS package | PyInstaller onedir prototype + safe CI | Local evidence retained privately; synthetic tests in tests/ | Windows x64 ZIP | Distribution | Licensing | No public timing claim | F: partial | Binary notices/redistribution/full acceptance |

| Docs/release/runtime | Historical docs | Current evidence/docs, runtime NOT RUN | Local evidence retained privately; synthetic tests in tests/ | Documentation | Public source | Truthful limits | No public timing claim | F: release withheld | No v1.0beta until gates pass |


New verified capabilities: bounded .chpatch XOR packages export/import, actual five-extent reimport identity, cooperative JB copy/verification cancellation, and native friendly position/reference controls tested through edit/save/reopen.
