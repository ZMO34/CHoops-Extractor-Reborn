# College Hoops 2K8 PS3 Modding Suite — Master AI Agent Handoff

Generated: 2026-06-18  
Project: `ZMO34/CHoops-Extractor-ZMO` / College Hoops Reborn tooling  
Purpose: allow a new AI agent or developer to enter the project, understand the asset formats and tool architecture, and begin safe work without repeating earlier mistakes.

> This file is intentionally extensive. It combines the prior master handoff, roster studio source, standard PS3 IFF report, CDF-backed IFF/CDF report, floor.scne notes, full IFF inventory, standard-IFF CSV summaries, the current GitHub command/package snapshot, and a 2026-06-18 sweep of accessible project-chat details.

---

## 0. Absolute Rules Before Touching Code

1. **Target platform is PS3 College Hoops 2K8.** PC NBA 2K assumptions are references only and must never silently override PS3 behavior.
2. **There are at least two different IFF families.** Standard archive IFF uses magic `0xFF3BEF94`; CDF-backed metadata IFF uses magic `0xF0985030` and must be handled with its paired `.cdf` file.
3. **Uniforms are not CDF-backed.** `ua/uh/ux###.iff` uniforms are standalone standard IFFs. Jersey `names` and `jersey_numbers` are embedded TXTR subfiles inside those standard IFFs, not external `.cdf` payloads.
4. **Preservation-first is mandatory.** Preserve raw compressed blocks, unknown fields, hashes, name tables, padding, file order, segment headers, and original byte ranges unless the writer fully recomputes every affected structure.
5. **Do not treat DDS conversion failures as non-textures.** `gtf2dds` “Bad format” usually means the tool’s GTF/TXTR reconstruction is wrong for that variant, not that the asset is useless.
6. **Do not broad-rewrite the builder without validators.** Rebuild reliability is fragile. Add round-trip tests and validators before allowing size-changing edits.
7. **Separate outer archive identity from inner subfile identity.** Numeric top-level folders come from unresolved archive TOC/hash names; numeric internal subfiles can also happen when an IFF lacks the optional internal name table.
8. **Classify uncertainty clearly.** Mark fields as confirmed, likely, candidate, or unknown. Do not expose red-tier experimental fields as safe editor controls.

---

## 1. Current Goal and Product Direction

The tool is evolving from an extractor into a **College Hoops 2K8 PS3 Modding Suite** supporting:

- full-game ripping with complete canonical names;
- raw-preserving extraction of standard IFF and CDF-backed IFF/CDF assets;
- texture export/import for ordinary textures and hard cases such as uniform names/numbers;
- SCNE court/model research and OBJ export;
- CDF-backed logo and audio research;
- safe rebuild workflows that preserve a vanilla source copy;
- a native/GUI workflow for “build for console” versus “build for emulator” style mod packaging;
- Roster Studio for players, teams, roster slots, school data, asset assignment, existing alternates, arenas, coaches, colors, and research-only unknown fields.

### Important recent product idea: console vs emulator build profiles

The College Hoops Reborn workflow wants two build modes:

- **Build for console:** downsize or validate textures against original vanilla dimensions and likely original payload/format limits.
- **Build for emulator/RPCS3:** allow upscaled textures where RPCS3 can handle them.

The tool already builds from a preserved vanilla copy. That vanilla source should become the authoritative reference for base-game texture dimensions, formats, mip counts, payload sizes, and safe console limits. Do not hardcode default dimensions where the vanilla IFF/CDF can be inspected.

A future profile system should:

```text
vanilla asset index
  -> original texture dimensions/formats/sizes
  -> mod asset scan
  -> profile-specific validation/downscale/conversion
  -> build-copy output
```

For JavaScript-based downsizing of DDS: it is possible if a reliable DDS parser and compressor pipeline is added, but quality/safety depends on preserving compression format, mip layout, alpha, and PS3/GTF expectations. A safer near-term implementation is validation plus calls to known conversion tools, not blind byte resizing.

---

## 2. Current GitHub Repository Snapshot

Repository: `ZMO34/CHoops-Extractor-ZMO`  
Default branch: `master`  
Visibility: public  
Package name: `choops-extractor`  
Current package version seen in `package.json`: `0.7.1`

### Package and build flow

`package.json` exposes:

```json
{
  "bin": {
    "choops-extractor": "./index.js",
    "choops-roster": "./roster.js"
  },
  "scripts": {
    "pack:cli": "pkg -t node18-win-x64 -o dist/choops-extractor.exe --compress GZip index.js && node scripts/copy-native-tools.js",
    "pack:native": "npm run pack:cli && npm run check:dotnet && dotnet publish native-desktop/ChoopsModdingSuite/ChoopsModdingSuite.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishReadyToRun=true -o dist-native",
    "pack": "npm run pack:native",
    "desktop": "npm run pack:cli && npm run check:dotnet && dotnet run --project native-desktop/ChoopsModdingSuite/ChoopsModdingSuite.csproj",
    "gui": "node gui.js",
    "roster": "node roster.js"
  }
}
```

Bundled native texture tools:

```text
2k-tools/lib/gtf2dds.exe
2k-tools/lib/dds2gtf.exe
```

### Important source entry points

```text
index.js                         main CLI
roster.js                        standalone roster CLI
gui.js                           GUI wrapper
src/ripperV3.js                  current ripper entry
src/cache.js                     archive cache / hash resolution
src/builder.js                   direct build into selected game folder
src/buildCopy.js                 safer vanilla-copy build path
src/importerV2.js                mod import path
src/reverter.js                  revert path
src/assetExtractor.js            model/database/roster/animation candidates
src/cdfBackedIffExtractor.js     CDF-backed IFF parser/extractor
src/cdfTextureExtractor.js       CDF texture extraction
src/cdfDecompressor.js           heuristic CDF decompression/chunking
src/teamselectlogoTool.js        teamselectlogo DDS export/import
src/smartAssetScanner.js         recursive structural scan
src/iffResearchTools.js          inspect/scan research utilities
src/scneObjExporterStable.js     SCNE OBJ export
src/scneSplitPartExporter.js     split-part SCNE export
src/scneFloorInspector.js        floor.scne metadata/material/draw inspection
src/rosterTool.js                ROST decode/compare tools
2k-tools/src/parser/IFFReader.js
2k-tools/src/parser/ToolWrappedReader.js
2k-tools/src/parser/choops/ChoopsTextureReader.js
2k-tools/src/parser/choops/ChoopsTextureWriter.js
2k-tools/src/model/general/iff/IFFType.js
2k-tools/src/controller/ChoopsController.js
2k-tools/src/util/gameProfiles.js
```

### Current CLI commands in `index.js`

Commands confirmed in current `index.js` include:

```bat
choops-extractor profiles [--json]
choops-extractor smart-scan <input> <output>
choops-extractor inspect-iff <iffFile> <output> [--dump-subfiles]
choops-extractor scan-refs <input> <output>
choops-extractor rip <USRDIR> <output> [--cache|--build-cache] [--game-name choops2k8]
choops-extractor extract-assets <USRDIR> <output>
choops-extractor decompress-cdf <cdfFile> <output>
choops-extractor extract-cdf-textures <cdfFile> <output> [--iff matching.iff] [--dds]
choops-extractor export-teamselectlogo-dds <cdf> <iff> <output>
choops-extractor import-teamselectlogo-dds <originalCdf> <manifest> <editedDdsDir> <outputCdf>
choops-extractor export-scne-obj <scneFile> <output>
choops-extractor export-scne-split-parts <scneFile> <output>   # verify exact name/options if editing
choops-extractor inspect-floor-scne <scneFile> <output>
choops-extractor probe <iffOrCdfFile>
choops-extractor roster-decode <inputRoster> <output>
choops-extractor roster-compare <baseRoster> <customRoster> <output>
choops-extractor build-cache <USRDIR> [--game-name choops2k8]
choops-extractor import <modDir> <file> -iff <archive.iff> -sub <subfile>
choops-extractor revert <USRDIR> <iffFile>
choops-extractor revert-all <USRDIR>
choops-extractor build <USRDIR> <modFolder>
choops-extractor build-copy <vanillaGameOrUSRDIR> <modFolder> <outputCopiedGamePath> [--overwrite]
```

`roster-decode` and `roster-compare` are now present in the main CLI, which resolves the earlier GUI routing concern where GUI roster jobs were routed through `choops-extractor.exe`.

---

## 3. Asset Namespace and What It Means

The full IFF/CDF inventory proves the archive namespace is finite and enumerable. This is crucial for cache/hash resolution: if an archive TOC entry is unresolved, generate canonical filename candidates and compare their hashes instead of accepting numeric folders.

### Asset family summary from inventory source

| asset family | count from inventory source |
|---|---|
| numeric unresolved or numeric-named IFFs | 640 |
| ua gameplay away uniforms | 452 |
| selua away preview uniforms | 452 |
| seluh home preview uniforms | 452 |
| uh gameplay home uniforms | 452 |
| s arena/court/stadium archives | 384 |
| named miscellaneous IFF/BIN/SCNE | 111 |
| m mascot/model archives | 101 |
| h head model archives | 84 |
| selux alternate preview uniforms | 81 |
| ux gameplay alternate uniforms | 81 |
| coach archives | 50 |
| CDF payload banks | 37 |

### Major families

| Family | Meaning | Tool impact |
| --- | --- | --- |
| `ua###.iff` | Away gameplay uniform | Standard IFF; embedded TXTR + NAME; not CDF-backed |
| `uh###.iff` | Home gameplay uniform | Standard IFF; embedded TXTR + NAME; not CDF-backed |
| `ux###.iff` | Alternate gameplay uniform | Sparse; absence is meaningful |
| `selua###.iff` | Away menu/team-select uniform preview | Separate archive; not generated from gameplay `ua` |
| `seluh###.iff` | Home menu/team-select uniform preview | Separate archive; not generated from gameplay `uh` |
| `selux###.iff` | Alternate menu/team-select preview | Sparse; must be paired with existing `ux` for safe alternate UI |
| `s###.iff` | Stadium/arena/court | Standard IFF; usually SCNE + TXTR + CDAN |
| `m###.iff` | Mascot/model groups | Standard IFF/model research target |
| `h####.iff` | Head models | Player appearance research target |
| `coach###.iff` | Coach models/assets | Appearance/model research target |
| `teamselectlogo.iff/.cdf` | Logo texture bank | CDF-backed TXTR bank |
| `arenapics.iff/.cdf` | Arena/team presentation image bank | CDF-backed candidate |
| `overlaycache.iff/.cdf` | Shared UI overlay cache | CDF-backed candidate |
| `cwd-*.iff/.cdf` | Crowd audio banks | CDF-backed AUDO |
| `gameintro_drums.iff/.cdf` | Intro audio | CDF-backed AUDO |
| `gameintro_playerspeech.iff/.cdf` | Intro speech audio | CDF-backed AUDO |
| `pc*.iff/.cdf` | Player-create shared texture banks | Often CDF-backed |
| `roster_english.iff` | Vanilla roster/database | Standard IFF containing one ROST subfile |
| `frontend*.iff`, `gamedata*.iff`, `loc.iff` | UI/database/localization/presentation | High-priority research banks |

### Hash/name resolution implications

Candidate namespace generation should include at minimum:

```text
ua000-ua999
uh000-uh999
ux000-ux999
selua000-selua999
seluh000-seluh999
selux000-selux999
s000-s999
m000-m999
h0000-h9999
coach001-coach999
known named banks: frontend, frontend_sync, gamedata, gamedataextra, global, loc, fonts, loading, legalpage, overlaycache, arenapics, teamselectlogo, roster_english, playercreate, facegen, jukebox, etc.
special 800-series: ua/uh/selua/seluh/s ranges observed in inventory
```

Do not assume every team has `ux###` or `selux###`. Alternates are sparse. Expose existing alternates safely; creating brand-new alternates requires top-level archive entries and likely frontend/team-select logic, not only ROST editing.

---

## 4. Standard PS3 IFF Format (`0xFF3BEF94`)

### Scope

Standard IFF includes uniforms, menu uniforms, stadium/court files, frontend/UI archives, roster/text/database-like files, studio files, model files, and large global data banks.

### High-level layout

```text
[IFF header: 0x20 bytes]
[block table: blockCount * 0x20 bytes]
[file-record pointer table: fileCount * 0x04 bytes]
[file records: variable length]
[block payload data: usually compressed H7A/CDF-style blocks]
[optional internal name table: AA171516]
[optional zero padding]
```

### Identity systems

```text
outer archive identity
  from game archive TOC/hash resolution
  controls names like ua256, s212, frontend, global

inner IFF subfile identity
  from optional IFF name table
  controls subfile names/types like TXTR, SCNE, LAYT, CDAN
```

Therefore:

- unresolved outer identity -> numeric top-level folder;
- missing inner name table -> numeric internal subfiles even if top-level folder is correct.

Known valid standard IFFs without internal name tables include `ua256.iff` and `s212.iff`. Do not treat them as corrupt.

### Endianness

| Region | Endian / encoding |
| --- | --- |
| Main IFF header | Big-endian u32 |
| Block table | Big-endian u32 |
| File-record pointer table | Big-endian u32 |
| File records | Big-endian u32 |
| Block compression wrapper | Big-endian u32 |
| Name-table magic | Big-endian magic |
| Name-table size/pointers | Little-endian u32 |
| Name-table strings | UTF-16LE |

### Main header

| Offset | Size | Meaning |
| ---: | ---: | --- |
| `0x00` | u32be | magic `0xFF3BEF94` |
| `0x04` | u32be | `headerSize`, absolute offset where first block payload begins |
| `0x08` | u32be | `fileLength`, end of block payload data, excluding name table/padding |
| `0x0C` | u32be | zero |
| `0x10` | u32be | block count |
| `0x14` | u32be | observed `13` |
| `0x18` | u32be | file/subfile count |
| `0x1C` | u32be | observed `0x20 * blockCount + 0x05` |

Invariants observed:

```text
headerSize = 0x20 + blockCount*0x20 + fileCount*0x04 + sum(fileRecordSizes)
fileRecordSize = 0x0C + offsetCount*0x04
firstBlock.startOffset == headerSize
max(block.startOffset + block.compressedLength) == fileLength
```

### Block table entry (`0x20` bytes)

| Offset | Field | Notes |
| ---: | --- | --- |
| `+0x00` | `nameRaw` | hash-like block identifier |
| `+0x04` | `typeRaw` | usually same as `nameRaw` |
| `+0x08` | `unk1` | observed 16, 32, 128 depending family |
| `+0x0C` | `uncompressedLength` | logical decompressed length |
| `+0x10` | `unk2` | often mirrors compression header `unk` |
| `+0x14` | `startOffset` | absolute payload offset in IFF |
| `+0x18` | `compressedLength` | stored payload length; includes wrapper if compressed |
| `+0x1C` | `isIndexed` | observed 0 in analyzed samples |

Common block-bank identifiers:

```text
0xBB05A9C1
0x411536D5
0x76CBC6E7
```

These appear to be block-bank identifiers, not subfile type identifiers.

### Compression wrapper

Most compressed standard IFF blocks begin with:

```text
0x0E4837C3
```

Wrapper layout:

| Offset | Field |
| ---: | --- |
| `+0x00` | magic `0x0E4837C3` |
| `+0x04` | uncompressed length |
| `+0x08` | compressed length, includes `0x14` wrapper |
| `+0x0C` | unk, matches block table `unk2` in samples |
| `+0x10` | shift amount used by H7A decompression |
| `+0x14` | compressed bytes |

Preservation rule:

- If a block is unchanged, write the exact original compressed bytes.
- If changed, either recompress correctly or use a validated uncompressed-block mode. Do not simply dump decompressed bytes into a compressed contract.

### File-record pointer table

Immediately after the block table:

```text
fileCount * u32be
```

Pointers use relative convention:

```text
fileRecordOffset = pointerEntryOffset + pointerValue - 1
```

A writer must preserve or recompute this table. Recompute formula:

```text
pointerValue = targetFileRecordOffset - pointerEntryOffset + 1
```

### File records

| Offset | Field | Meaning |
| ---: | --- | --- |
| `+0x00` | `idRaw` | internal subfile ID/hash |
| `+0x04` | `typeRaw` | type hash, resolved through name table when present |
| `+0x08` | `offsetCount` | number of block-offset slots |
| `+0x0C` | offsets | u32be offsets into decompressed blocks |

`0xFFFFFFFF` means absent from that block and must be skipped when deriving lengths.

### File data slicing

For each block:

1. collect all file records with a valid offset for that block;
2. exclude `0xFFFFFFFF`;
3. sort offsets;
4. length = next valid offset - current offset;
5. last length = block.uncompressedLength - current offset.

Changing one file’s size shifts every later offset in that block.

### Optional internal name table

Located at `fileLength` when present.

```text
magic: 0xAA171516
size/pointers: little-endian
strings: UTF-16LE
relative pointers: target = pointerFieldOffset + pointerValue - 1
```

Name table contains internal subfile names and type strings. It is outside `fileLength` but still part of the file and must be preserved.

### Observed standard-IFF type map

| typeRawHex | observedNames | totalNamedOccurrences |
|---|---|---|
| 0x047C8C98 | SHAP:7 | 7 |
| 0x070D3D6B | UnAD:1 | 1 |
| 0x0FA31F4D | SCOS:5 | 5 |
| 0x1A511857 | UNLK:1 | 1 |
| 0x1ADE2460 | AOSS:7 | 7 |
| 0x1AEDDA1F | AUDO:26 | 26 |
| 0x249FD2C9 | AMCR:2 | 2 |
| 0x26C22AED | PRIV:1 | 1 |
| 0x4014B412 | SPCI:9 | 9 |
| 0x5C369069 | TXTR:664 | 664 |
| 0x5DBCCA93 | FGCT:179 | 179 |
| 0x60900D71 | Singl:41 | 41 |
| 0x61DF2234 | AUSB:16 | 16 |
| 0x68B693B2 | NAME:8 | 8 |
| 0x6B3AFF68 | HTAJ:1 | 1 |
| 0x7657AB8A | SKEL:1 | 1 |
| 0x79862464 | BLRB:1 | 1 |
| 0x86A1AC9E | LAYT:216 | 216 |
| 0xA7701F00 | CDAN:24 | 24 |
| 0xB69815A5 | FxTwe:24 | 24 |
| 0xBE981E93 | FRFG:7 | 7 |
| 0xC61649B2 | ROST:1 | 1 |
| 0xC6ED33A2 | MRKS:10 | 10 |
| 0xE1124F13 | Clth:2 | 2 |
| 0xE26C9B5D | SCNE:429 | 429 |
| 0xF37C12D9 | STRG:2 | 2 |

### Standard-IFF sample summary

| IFF | blocks | files | name table | compressed blocks | top/observed types |
|---|---|---|---|---|---|
| CH2K8 PS3 ababall.iff | 2 | 1 | yes | 2 | {"SCNE": 1} |
| dornas.iff | 2 | 36 | yes | 2 | {"TXTR": 36} |
| frontend.iff | 3 | 102 | yes | 2 | {"AUDO": 2, "LAYT": 23, "MRKS": 6, "PRIV": 1, "SCNE": 46, "TXTR": 24} |
| gamedata.iff | 2 | 262 | yes | 2 | {"AMCR": 1, "AOSS": 2, "AUSB": 1, "LAYT": 14, "SCNE": 86, "SCOS": 3, "Singl": 1, "TXTR": 154} |
| gamedataextra.iff | 2 | 5 | yes | 2 | {"LAYT": 1, "MRKS": 1, "SCNE": 2, "TXTR": 1} |
| gameintro.iff | 2 | 2 | yes | 2 | {"SCNE": 1, "TXTR": 1} |
| global.iff | 3 | 603 | yes | 3 | {"AMCR": 1, "AOSS": 5, "AUDO": 24, "AUSB": 15, "BLRB": 1, "Clth": 2, "FGCT": 1, "FRFG": 7, "FxTwe": 24, "LAYT": 54, "MRKS": 2, "SCNE": 120, "SCOS": 2, "SHAP": 7, "SKEL": 1, "SPCI": 9, "STRG": 1, "Singl": 2, "TXTR": 323, "UNLK": 1, "UnAD": 1} |
| halftimeadjustments.iff | 2 | 11 | yes | 2 | {"HTAJ": 1, "LAYT": 3, "SCNE": 6, "TXTR": 1} |
| jukebox.iff | 2 | 32 | yes | 2 | {"LAYT": 3, "SCNE": 5, "STRG": 1, "TXTR": 23} |
| legacy.iff | 2 | 143 | yes | 2 | {"LAYT": 51, "SCNE": 78, "TXTR": 14} |
| legalpage.iff | 1 | 3 | yes | 1 | {"TXTR": 3} |
| loading.iff | 2 | 16 | yes | 2 | {"LAYT": 5, "SCNE": 8, "TXTR": 3} |
| m204.iff | 2 | 1 | yes | 2 | {"SCNE": 1} |
| m235.iff | 2 | 1 | yes | 2 | {"SCNE": 1} |
| online.iff | 2 | 94 | yes | 2 | {"LAYT": 40, "SCNE": 37, "TXTR": 17} |
| playeditor.iff | 2 | 4 | yes | 2 | {"LAYT": 1, "SCNE": 3} |
| playercreate.iff | 2 | 62 | yes | 2 | {"LAYT": 2, "SCNE": 6, "Singl": 38, "TXTR": 16} |
| powerbar.iff | 2 | 1 | yes | 2 | {"TXTR": 1} |
| reelmanual.iff | 2 | 1 | yes | 2 | {"SCNE": 1} |
| roster_english.iff | 1 | 1 | yes | 1 | {"ROST": 1} |
| s000.iff | 2 | 11 | yes | 2 | {"CDAN": 8, "SCNE": 2, "TXTR": 1} |
| s211.iff | 2 | 11 | yes | 2 | {"CDAN": 8, "SCNE": 2, "TXTR": 1} |
| s212.iff | 2 | 12 | no | 2 | {"0x5C369069": 1, "0xA7701F00": 9, "0xE26C9B5D": 2} |
| s213.iff | 2 | 11 | yes | 2 | {"CDAN": 8, "SCNE": 2, "TXTR": 1} |
| selua003.iff | 2 | 5 | yes | 2 | {"NAME": 1, "TXTR": 4} |
| selua256.iff | 2 | 5 | yes | 2 | {"NAME": 1, "TXTR": 4} |
| seluh256.iff | 2 | 5 | yes | 2 | {"NAME": 1, "TXTR": 4} |
| selux256.iff | 2 | 5 | yes | 2 | {"NAME": 1, "TXTR": 4} |
| statefarm.iff | 2 | 4 | yes | 2 | {"TXTR": 4} |
| streetdata.iff | 1 | 1 | yes | 1 | {"MRKS": 1} |
| studio.iff | 2 | 179 | yes | 2 | {"FGCT": 178, "SCNE": 1} |
| studio_pontiac.iff | 2 | 3 | yes | 2 | {"TXTR": 3} |
| studio_preview.iff | 2 | 3 | yes | 2 | {"TXTR": 3} |
| ua256.iff | 2 | 11 | no | 2 | {"0x5C369069": 9, "0x68B693B2": 2} |
| uh256.iff | 2 | 11 | yes | 2 | {"NAME": 2, "TXTR": 9} |
| ux256.iff | 2 | 11 | yes | 2 | {"NAME": 2, "TXTR": 9} |
| weeklyshow.iff | 2 | 39 | yes | 2 | {"LAYT": 19, "SCNE": 20} |

### Standard-IFF subfile type counts from CSV

| subfile type | count in standard-IFF CSV |
|---|---|
| TXTR | 664 |
| SCNE | 429 |
| LAYT | 216 |
| FGCT | 179 |
| Singl | 41 |
| AUDO | 26 |
| FxTwe | 24 |
| CDAN | 24 |
| unknown | 23 |
| AUSB | 16 |
| MRKS | 10 |
| SPCI | 9 |
| NAME | 8 |
| AOSS | 7 |
| FRFG | 7 |
| SHAP | 7 |
| SCOS | 5 |
| AMCR | 2 |
| Clth | 2 |
| STRG | 2 |
| PRIV | 1 |
| UnAD | 1 |
| UNLK | 1 |
| BLRB | 1 |
| SKEL | 1 |
| HTAJ | 1 |
| ROST | 1 |

---

## 5. CDF-Backed IFF/CDF Format (`0xF0985030`)

### High-level model

This family is not a normal standalone archive. It is a paired metadata/payload system:

```text
.iff = metadata, names, ids, type hashes, CDF segment table
.cdf = physical payload bank
```

The IFF describes a virtual two-block filesystem over the CDF:

```text
virtual block 0 = per-record CDF headers / metadata side
virtual block 1 = per-record payload side
```

The CDF stores physical bytes as:

```text
[record header][payload][record header][payload]...
```

### Top-level layout

| Offset | Size | Meaning |
| ---: | ---: | --- |
| `0x00` | u32be | magic `0xF0985030` |
| `0x04` | u32be | metadata end / internal name-table offset |
| `0x08` | u32be | duplicate of `0x04` in samples |
| `0x0C` | u32be | zero |
| `0x10` | u32be | virtual block count, observed `2` |
| `0x14` | u32be | constant `0x15` |
| `0x18` | u32be | record/subasset count |
| `0x1C` | u32be | constant `0x4D` |
| `0x20` | u32be relative | pointer to secondary CDF segment table |
| `0x24` | u32be relative | pointer to UTF-16BE CDF filename string |
| `0x28` | 0x20 | virtual block descriptor 0 |
| `0x48` | 0x20 | virtual block descriptor 1 |
| `0x68` | count*4 | primary relative-offset table |

Relative pointers:

```text
segmentTableStart = 0x20 + readU32BE(0x20) - 1
cdfNameString    = 0x24 + readU32BE(0x24) - 1
```

### Primary file record (`0x14` bytes)

| Offset | Field | Meaning |
| ---: | --- | --- |
| `+0x00` | id/name hash | internal subasset id; for teamselectlogo matches CDF header id at `segmentHeaderOffset + 0x15` |
| `+0x04` | type hash | `0x1AEDDA1F = AUDO`, `0x5C36FB69 = TXTR` in CDF-backed samples |
| `+0x08` | offset count | observed `2` |
| `+0x0C` | virtual header offset | into virtual block 0 |
| `+0x10` | virtual payload offset | into virtual block 1 |

### Secondary CDF segment descriptor (`0x10` bytes)

The table pointed to by top-level `0x20` is authoritative for physical extraction/rebuild.

| Offset | Field | Meaning |
| ---: | --- | --- |
| `+0x00` | physical header offset | CDF record header starts here |
| `+0x04` | physical header length | audio observed `0x24`; textures often `0x5E` but varies |
| `+0x08` | physical payload offset | payload starts here |
| `+0x0C` | physical payload length | payload byte length |

### CDF audio records

Audio CDFs are interleaved banks:

```text
segment 0 header 0x24 bytes
segment 0 payload
segment 1 header 0x24 bytes
segment 1 payload
...
```

Audio header fields:

| Offset | Meaning |
| ---: | --- |
| `0x00` | constant `1` |
| `0x04` | constant `5` |
| `0x08` | constant `0x0F` |
| `0x0C` | likely uncompressed/sample-domain size |
| `0x10` | sample rate, observed `48000` |
| `0x14` | zero |
| `0x18` | compressed payload length; matches IFF segment descriptor |
| `0x1C` | zero |
| `0x20` | zero |

Codec is unknown. Extract preservation files, not WAV, until codec is identified.

### CDF texture/GTF records

`teamselectlogo` contains 520 named `TXTR` records.

Texture CDF header observations:

| Offset | Meaning |
| ---: | --- |
| `0x00` | magic `0x0E4837C3` |
| `0x04` | constant `0xB0`, likely logical header size |
| `0x08` | physical header length before embedded GTF; usually `0x5E`, observed `0x5B-0x5F` |
| `0x0C` | small format-like field, observed `7` or `8` |
| `0x10` | constant `8` |
| `0x15` | unaligned u32be subasset id, matches IFF record id |
| `payloadOffset` | embedded GTF starts with `0x0E4837C3` |

Never hardcode CDF texture header length. Read it from the IFF segment descriptor.

### CDF rebuild modes

| Mode | Behavior |
| --- | --- |
| Preserve mode | Reject replacements that change payload length unless explicitly allowed |
| Same-size payload mode | Preserve CDF header and descriptor table; replace only payload bytes |
| Bank rebuild mode | Allow changed sizes; rebuild every CDF segment offset and update matching IFF descriptor table |
| Research mode | Dump every raw table, CDF header, payload, and manifest without conversion |

Size-changing CDF replacement requires rewriting both IFF and CDF together:

```text
read all descriptors
replace selected header/payload
recalculate physical offsets
rewrite CDF
rewrite IFF secondary segment descriptors
preserve name table
preserve CDF filename string
```

---

## 6. Tool Wrapper Format (`2kTl`)

Dumped subfiles often begin with:

```text
0x326B546C  # "2kTl"
```

This is a tool wrapper, not necessarily original game data.

Observed wrapper layout:

| Offset | Field |
| ---: | --- |
| `0x00` | magic `0x326B546C` |
| `0x04` | header length |
| `0x08` | u16be type code |
| `0x0A` | u16be number of blocks |
| `0x0C` | u32be block lengths |
| after header | raw block data concatenated |

When inspecting `.txtr`, `.scne`, `.audo`, etc., first determine whether the file is raw or `2kTl` wrapped. Many texture parsing bugs come from reading descriptor offsets against the wrapper rather than the unwrapped block.

---

## 7. Texture Pipeline and Known Failure Areas

### Standard embedded IFF TXTR vs CDF-backed TXTR

Do not mix these two cases.

| Asset class | Texture storage |
| --- | --- |
| Uniforms `ua/uh/ux###` | Standard IFF embedded TXTRs inside `0xFF3BEF94` blocks |
| Stadiums `s###` | Standard IFF embedded TXTRs and SCNE package textures |
| Teamselect logos | CDF-backed TXTR/GTF records |
| Arenapics/overlaycache/player-create banks | likely/known CDF-backed texture records |

### Uniform names and numbers

Confirmed practical model:

```text
ua256.iff / uh256.iff / ux256.iff
  standard IFF
  compressed blocks
  embedded TXTR subfiles
  NAME metadata subfiles
```

Actual editable atlas targets:

```text
jersey_numbers.txtr
names.txtr
```

Metadata files, not images:

```text
numbers.NAME
names.NAME
```

`NAME` files appear to contain coordinate/layout/glyph metadata, likely 16-bit pair structures. They should be preserved unless the layout is fully decoded.

### Current DDS/GTF conversion behavior

Current path for many normal textures:

```text
TXTR -> tool wrapper/data blocks -> ChoopsTextureReader.toGTFFromFile() -> gtf2dds.exe -> DDS
DDS -> dds2gtf.exe -> ChoopsTextureWriter.toFileFromGtf() -> TXTR -> IFF rebuild
```

Known hard failures:

- repeated `gtf2dds ERROR: Bad format` for `jersey_numbers`;
- no DDS export for uploaded `jersey_numbers.txtr` / `names.txtr` after fallback attempt;
- UI marks/titles such as `mark1`, `mark2`, `mark3`, `titles2` may fail similarly.

Likely causes:

1. incorrect GTF header reconstruction;
2. wrong descriptor offsets after `2kTl` unwrap;
3. mismatched payload size;
4. broken mip offsets;
5. endian mistakes;
6. swizzled/tiled payload not described correctly;
7. assuming every TXTR variant has the same header layout.

### Required next texture command: `inspect-txtr`

Add a command that:

```text
choops-extractor inspect-txtr <txtrFile> <outputFolder>
```

It should:

- detect raw vs `2kTl` wrapped;
- print block count and block lengths;
- dump header bytes and key descriptor fields;
- scan for `0x0E4837C3` candidate GTF headers;
- infer width/height/format/mip candidates;
- dump raw payload candidates;
- generate candidate DDS variants independent of `gtf2dds`;
- compare against vanilla dimensions and payload sizes;
- produce JSON manifest for future agents.

### Interim texture import safety

Until the problematic TXTR variants are decoded:

- allow normal DDS import only for known-good textures;
- reject or research-gate uniform name/number imports;
- require same dimensions/format/mip count first;
- preserve NAME metadata;
- preserve original payload length unless using a validated writer.

---

## 8. SCNE / Models / Court Floor

`SCNE` packages are used for courts, stadiums, UI scenes, overlays, and presentation systems.

Ripped `floor.scne` is normally a two-block `2kTl` file:

```text
block 0 = package header, texture headers, model-part records, materials, draw runs, vertex descriptors, declarations, names
block 1 = texture payloads followed by geometry payloads such as index and vertex buffers
```

### Package header highlights

| Offset | Meaning |
| ---: | --- |
| `0x00` | package name offset + 1 |
| `0x20` | texture count |
| `0x24` | texture table pointer; actual offset = value + `0x23` |
| `0x44` | model-part count |
| `0x48` | model-part table pointer; actual offset = value + `0x47` |

### Texture headers

Each texture header is `0xB0` bytes.

Important fields:

| Offset | Meaning |
| ---: | --- |
| `0x58` | GTF/texture format word copied during DDS->GTF import |
| `0x5C` | remap/control word |
| `0x60` | packed dimensions, usually width high 16 bits / height low 16 bits |
| `0x64` | mip/count or related parameter |
| `0x68` | pitch/linear-size-like field |
| `0x6C` | additional GTF parameter |
| `0x90` | repeated packed dimensions |
| `0xA4` | texture data offset + 1 into block 1 |

### Known floor model parts

| Part | Role |
| --- | --- |
| `floor` | base floor and apron route |
| `paint` | key/paint colorized regions |
| `centerlogo` | center logo and center circle |
| `lines` | court line overlays and colorized line regions |

### Model-part record (`0xB0` bytes)

Important fields:

| Offset | Meaning |
| ---: | --- |
| `0x00` | UTF-16BE part name pointer, relative |
| `0x04` | hash/id |
| `0x08` | enabled/visibility flag |
| `0x30..0x38` | bounds center X/Y/Z |
| `0x4C..0x54` | scale X/Y/Z |
| `0x60/0x64` | material record count/pointer |
| `0x7C/0x80` | draw-run count/pointer |
| `0x84/0x88` | vertex-buffer descriptor count/pointer |
| `0x94/0x9C` | vertex declaration count/pointer |
| `0xA4` | index flags / primitive flags, often `0x20000010` |
| `0xA8` | index count, not flags |
| `0xAC` | index buffer offset + 1 into block 1 |

### Vertex layout for known floor vertices

Stride: `0x24` / 36 bytes.

| Offset | Type | Meaning |
| ---: | --- | --- |
| `0x00` | float32 BE x3 | position X/Y/Z |
| `0x0C` | float32 BE x4 | auxiliary/tangent/material data |
| `0x1C` | half-float BE x2 | UV0 U/V |
| `0x20` | 4 bytes | packed auxiliary/color/render attribute |

UV edit point:

```text
vertexBufferDataOffset + vertexIndex * 0x24 + 0x1C
```

### Full-court texture strategy

Safest current strategy:

1. Use the `floor` model part.
2. Route through glossy/non-colorized floor material path, preferably draw/pass id `0`.
3. Put full-court diffuse art into `texture_0`.
4. Preserve or regenerate matching normal/gloss partner in `texture_2`.
5. Remap part 0 UV0 values to 0..1 from vertex X/Z bounds.
6. Avoid `paint`, `key_hash_*`, and line material routes for full-court diffuse art because those are tied to Edit School color controls.

Known floor bounds from samples:

```text
X ≈ -1132.8995 .. 1132.8994
Z ≈ -1829.0146 .. 1829.0150
```

UV remap formula:

```text
U = (X - minX) / (maxX - minX)
V = (Z - minZ) / (maxZ - minZ)
```

---

## 9. Audio / AUDO

### CDF-backed audio

Known examples:

```text
gameintro_drums.iff + gameintro_drums.cdf
gameintro_playerspeech.iff + gameintro_playerspeech.cdf
cwd-cheer-*.iff + cwd-cheer-*.cdf
cwd-boo-*.iff + cwd-boo-*.cdf
cwd-ahh-*.iff + cwd-ahh-*.cdf
cwd-freethrow-*.iff + cwd-freethrow-*.cdf
```

`AUDO` CDF records are structurally mapped:

```text
0x24-byte audio header + compressed/encoded payload
sample rate observed 48000
```

The codec is unknown. Do not claim playable audio decode. Current safe output:

```text
.audio_header.bin
.audio_payload.bin
manifest.json
```

### Standard IFF AUDO

Some standard IFFs such as `frontend.iff` and `global.iff` contain `AUDO` subfiles directly. They still require preservation extraction and codec research.

Future audio work:

1. inspect headers and frame candidates;
2. identify codec;
3. decode to WAV;
4. implement encode or size-preserving replacement.

---

## 10. ROST / Roster Structure

### Supported sources

Roster Studio must treat roster input as a format family, not only `roster_english.iff`.

| Input type | Detection | Payload source | Write-back rule |
| --- | --- | --- | --- |
| `roster_english.iff` | standard IFF magic `0xFF3BEF94`, one ROST subfile | extract ROST from decompressed block | rebuild through preservation-safe IFF writer |
| decrypted PS3 save ZIP | ZIP contains USERDATA/PARAM/etc. | USERDATA first u32be length + raw ROST | patch USERDATA in copied ZIP, preserve other files |
| raw USERDATA | first u32be length equals file size - 4 | bytes after first 4 bytes | write length + payload |
| raw ROST payload | table probes validate offsets | whole file | write raw payload |
| workbook/CSV patch | manifest/schema | apply edits to base payload | export through chosen adapter |

The editor should show source type and signing boundary clearly. It can edit decrypted USERDATA/save ZIP contents but should not claim to produce a console-ready signed PS3 save unless save resigning is implemented and tested.

### Adapter architecture

Recommended module layout:

```text
src/roster/io/
  detectRosterSource.js
  RosterSource.js
  StandardIffRosterAdapter.js
  Ps3SaveZipRosterAdapter.js
  UserdataRosterAdapter.js
  RawRostAdapter.js
  WorkbookRosterPatchAdapter.js
```

Main editor should receive only:

```text
payloadBytes
sourceMetadata
validationReport
writeBack(edits, outputPath)
```

### Known ROST tables

| Table | Start | Count | Row size | End |
| --- | ---: | ---: | ---: | ---: |
| Players | `0x0271AC` | 5685 | 308 | `0x1D2970` |
| Arenas | `0x1D5C84` | 379 | 28 | `0x1D85F8` |
| Teams | `0x1D85E0` | 443 | 704 | `0x224820` |
| Coaches | `0x23F78C` | 1373 | 44 | `0x24E388` |

Vanilla ROST payload size observed: `3,981,216` bytes.  
Custom save payload observed: `4,061,184` bytes (`0x3DF800`), four-byte USERDATA wrapper plus payload.

### String pointer rule

```text
string_offset = field_offset + read_s32_be(field_offset)
strings are UTF-16LE
```

### Confirmed player fields

| Offset | Type | Meaning | Editor control |
| ---: | --- | --- | --- |
| `+0x10` | s32be relative ptr | last name | same-length/shorter text first |
| `+0x14` | s32be relative ptr | first name | same-length/shorter text first |
| `+0x18` | u32be | high 16 bits player/index id, low 16 bits jersey number | jersey editable; id read-only |
| `+0x3A` | u8 | height in inches | feet/inches picker |
| `+0x3B` | u8 enum | position: 0 PG, 1 SG, 2 SF, 3 PF, 4 C | dropdown |

Candidate appearance bytes:

```text
player row +0x00..+0x03
```

These vary across players and are zero in many unused rows, but are **not confirmed skin tone**. Label as Appearance Byte 0..3 until controlled one-change skin-tone saves prove meaning.

### Confirmed team fields

| Offset | Type | Meaning | Editor control |
| ---: | --- | --- | --- |
| `+0x30` | s32be ptr | short/team name | text |
| `+0x34` | s32be ptr | abbreviation | text |
| `+0x38` | s32be ptr | school/full name | text |
| `+0x3C` | s32be ptr | mascot plural | text |
| `+0x40` | s32be ptr | mascot name | text |
| `+0x44` | s32be ptr | arena pointer | arena dropdown |
| `+0x4C/+0x50/+0x54` | s32be ptrs | rivals | team dropdowns |
| `+0x60/+0x64/+0x68` | s32be ptrs | coach and assistants | coach dropdowns |
| `+0x6C..+0xA8` | 16 x s32be ptrs | roster slots into player table | drag/drop or dropdown slots |
| `+0x18C` | u16 + u16 | asset_id + team row/check | asset assignment |
| `+0x190` | u16 + u16 | asset_id repeat + mascot id or `FFFF` | asset/mascot validation |
| `+0x194` | u16 + u16 | asset_id repeat + zero | validation field |
| `+0x198` | s32be ptr | student section name | text |
| `+0x19C` | s32be ptr | Midnight Madness/event name | text |
| `+0x1A0..+0x218` | 31 u32-like color words | school/court/material palette candidate | experimental palette editor |

### Team asset IDs

Asset ID connects database team rows to art families.

Example:

```text
Georgia team row index: 313
Georgia asset_id: 256
assets: uh256, ua256, ux256, seluh256, selua256, selux256, s256, m256
```

Team row index, asset ID, and original linked identity/check are distinct. Community rosters can reorder or replace team rows while still using existing assets.

### Roster Studio tabs

| Tab | Purpose | Fields |
| --- | --- | --- |
| Players | player editing | names, jersey, position, height, team assignment, appearance research |
| Teams / School Data | school identity | names, abbreviation, mascot, arena, rivals, coaches, student section, event |
| Roster Slots | team composition | 16 slots per team, drag/drop/dropdowns |
| Assets | art assignment | asset ID, home/away/alt availability, arena, mascot/model |
| Alternates | existing alt management | expose existing `ux/selux` only when files exist |
| Colors / Court Palette | school/court/material colors | team `+0x1A0..+0x218`, labels graduate from candidate to confirmed |
| Conferences | conference/prestige research | disabled/research-only until confirmed |
| Unknown Fields | raw diff research | hex/byte/u16/u32 with diff labels |

### Write safety tiers

| Tier | Examples | Behavior |
| --- | --- | --- |
| Green | jersey number, height, position, roster slots, arena/rival/coach pointers, asset ID, same-length strings | normal editing with validation |
| Yellow | palette region, existing alternate assignment, student/event strings, appearance candidates | experimental editing with backup/report |
| Red | skin tone labels, conference affiliation/prestige, longer string heap rebuild, brand-new alternate archive creation | research-only until proven |

### Roster validation rules

Every export should produce a validation report checking:

- string pointers resolve in bounds;
- roster slot pointers target valid players or safe empty values;
- team/arena/coach/rival pointers target valid rows;
- asset IDs match across `+0x18C/+0x190/+0x194`;
- asset IDs correspond to available `uh/ua/ux/seluh/selua/selux/s/m` files when possible;
- color words preserved unless intentionally changed;
- unknown bytes preserved exactly;
- string edits do not exceed original storage unless string heap rebuild mode is enabled.

---

## 11. Rebuild / Import / Binary Preservation

### Current build concepts

`build` modifies a selected game folder. `build-copy` is safer: it copies a vanilla extracted game folder first, then applies a mod to the copy.

Recommended user-facing default:

```text
vanilla source folder stays untouched
build-copy creates modded output folder
profile validates/downscales as needed
post-build validator checks archive consistency
```

### Standard IFF rebuild rules

- Preserve raw compressed blocks when unchanged.
- Preserve name table and padding after `fileLength`.
- Preserve or recompute file-record pointer table.
- Skip `0xFFFFFFFF` sentinel offsets when slicing/rebuilding.
- Recompute all later offsets in a block if any earlier file length changes.
- Keep unknown type hashes round-trippable.
- Do not drop unknown types from `IFFType`; preserve raw `typeRaw`, `idRaw`, offset slots, and payload bytes.

### CDF rebuild rules

- Treat `.iff` and `.cdf` as a pair.
- Preserve CDF segment headers unless fully understood.
- Same-size payload edits are safest.
- Size-changing edits require bank rebuild and IFF descriptor updates.

### Mod build profiles

Suggested future profile object:

```json
{
  "id": "console",
  "description": "PS3 console-safe build",
  "texturePolicy": "match-vanilla-or-downscale",
  "allowUpscale": false,
  "requireSameFormat": true,
  "requireMipCompatibility": true,
  "sizeChangingIffEdits": "reject-unless-safe-writer",
  "sizeChangingCdfEdits": "bank-rebuild-only"
}
```

```json
{
  "id": "emulator",
  "description": "RPCS3/upscaled texture build",
  "texturePolicy": "allow-upscale-with-validation",
  "allowUpscale": true,
  "requireSameFormat": false,
  "requireMipCompatibility": true,
  "sizeChangingIffEdits": "validator-required",
  "sizeChangingCdfEdits": "bank-rebuild-only"
}
```

### Validator commands to add

```bat
choops-extractor validate-iff <iffFile> <report.json>
choops-extractor round-trip-iff <iffFile> <output.iff> --compare
choops-extractor validate-cdf-pair <iffFile> <cdfFile> <report.json>
choops-extractor validate-build <vanillaUSRDIR> <moddedUSRDIR> <reportFolder>
choops-extractor asset-index <vanillaUSRDIR> <output.json>
choops-extractor compare-texture-profile <vanillaAsset> <modAsset> <report.json>
```

---

## 12. Known Bugs / Debugging Targets

### A. Numeric folders / incomplete hash resolution

Evidence: auto-resolution worked at least once, but only one auto-resolved hash was observed. The mechanism exists; the candidate namespace is incomplete.

Fix:

- generate full canonical filename candidates;
- compare candidate hash to archive TOC hash;
- log unresolved entries with index, hash, size, magic, structural fingerprint;
- infer from internal IFF structure only as fallback.

### B. Clamped invalid archive reads

Observed warnings involved archive parts like `0A`, `0B`, `0C` with huge offsets/lengths. Clamping avoids crashes but can silently produce corrupt/truncated files.

Fix diagnostics:

- log archive part name;
- entry index;
- hash/name if known;
- requested offset/length;
- part size;
- adjacent TOC entries;
- whether entry spans archive parts;
- whether reader incorrectly assumes single-part containment.

### C. `gtf2dds` failures for `jersey_numbers` and `names`

Do not redirect this to CDF logic. Uniform names/numbers are embedded standard IFF TXTRs. Build `inspect-txtr`, compare many home/away samples, and implement a variant-aware DDS export path.

### D. CDF extraction/rebuild not fully validated

`teamselectlogo` is structurally mapped, but `arenapics`, `overlaycache`, player-create CDF banks, and size-changing imports still need controlled tests.

### E. Audio extraction is preservation-only

AUDO payloads are not decoded to WAV. Keep them binary-preserved until codec is identified.

### F. Native/GUI workflow must stay aligned with CLI

`package.json` now includes native desktop packaging. Keep GUI command routing aligned with current CLI, especially `build-copy`, `roster-decode`, `roster-compare`, and future profile builds.

---

## 13. Recommended Workstreams for Split Chats / Agents

### Workstream A — Extraction Accuracy and Cache/Hash Debugging

Goal: full rip completes accurately with canonical names and no corrupt/truncated reads.

Focus:

- cache build;
- hash candidate namespace;
- numeric folders;
- clamped read diagnostics;
- full-rip summaries;
- nonfatal texture conversion failures;
- raw asset preservation.

Starter prompt:

```text
We are continuing the College Hoops 2K8 PS3 Modding Suite. Use the master handoff. Focus only on extraction accuracy, cache/hash resolution, numeric folders, full-rip errors, and clamped archive reads. Inspect the GitHub repo and implement safe fixes without changing texture decoding logic except for crash prevention.
```

### Workstream B — Uniform Names/Numbers TXTR Reverse Engineering

Goal: export/import `jersey_numbers` and `names` DDS atlases from standard embedded uniform TXTRs.

Focus:

- `inspect-txtr`;
- `2kTl` unwrap;
- standard embedded TXTR descriptor layouts;
- `jersey_numbers.txtr` and `names.txtr`;
- `numbers.NAME` / `names.NAME` metadata;
- synthetic DDS fallback;
- safe same-size import.

Starter prompt:

```text
Use the master handoff. Focus only on standard IFF embedded TXTRs for uniform jersey_numbers and names. Do not use CDF assumptions for uniforms. Analyze uploaded home/away jersey samples, reverse the TXTR layout, and implement inspect/export/import support for editable DDS atlases.
```

### Workstream C — Roster Studio / ROST Editor

Goal: build a safe Roster Studio supporting vanilla IFF rosters, decrypted save ZIPs, raw USERDATA, and raw ROST payloads.

Focus:

- source adapters;
- players/teams/arenas/coaches tables;
- roster slots;
- asset assignment;
- same-length string editing;
- palette research;
- workbook/CSV import/export;
- validation reports.

Starter prompt:

```text
Use the master handoff. Focus only on ROST parsing/writing, multi-source roster adapters, Roster Studio UI, safe editable fields, asset assignment, and validation. Do not change texture or IFF rebuild logic.
```

### Workstream D — Rebuild / Binary Preservation / Build Profiles

Goal: make rebuilds safe, deterministic, and profile-aware.

Focus:

- standard IFF round-trip;
- CDF pair validation;
- unchanged compressed block preservation;
- same-size texture replacement;
- build-copy default;
- console vs emulator texture profiles;
- post-build validation.

Starter prompt:

```text
Use the master handoff. Focus only on rebuild correctness: standard IFF round-trip, validation, compressed block preservation, size-preserving texture replacement, CDF pair rebuild rules, console/emulator build profiles, and preventing crashes/corrupt output.
```

### Workstream E — SCNE Court/Model Tools

Goal: make SCNE export/inspection reliable and progress toward safe court-floor material/UV editing.

Focus:

- floor.scne inspector;
- draw runs/material route mapping;
- OBJ export validation;
- full-court UV remap;
- texture_0/texture_2 diffuse/gloss pairing;
- court color palette mapping against ROST.

Starter prompt:

```text
Use the master handoff. Focus only on SCNE/floor court model research: part tables, material records, draw runs, vertex buffers, UV remapping, and full-court texture routing. Do not modify roster or CDF logic except to document references.
```

### Workstream F — Formal Format Docs and Research Manifests

Goal: keep repo docs and machine-readable manifests authoritative.

Focus:

- `docs/ps3_standard_iff.md`;
- `docs/ps3_cdf_backed_iff.md`;
- `docs/txtr_standard.md`;
- `docs/scne_floor.md`;
- `docs/roster_rost.md`;
- JSON schemas and command outputs for future agents.

Starter prompt:

```text
Use the master handoff. Focus only on documenting and formalizing the PS3 standard IFF, CDF-backed IFF/CDF, TXTR, NAME, SCNE, AUDO, and ROST formats into repo docs and machine-readable specs.
```

---

## 14. Immediate Priority Order

1. **Fix full-rip extraction accuracy.** Add namespace generation and clamped-read diagnostics.
2. **Add validators and round-trip checks.** Especially standard IFF and CDF pair validation.
3. **Build `inspect-txtr`.** Target uniform `jersey_numbers` and `names` first.
4. **Implement Roster Studio green-tier edits.** Players, teams, roster slots, asset IDs, same-length strings.
5. **Add build profiles.** Console vs emulator texture policy using vanilla source asset metadata.
6. **Document formats in repo.** Keep docs tied to sample outputs.

---

## 15. Do-Not-Do List

- Do not treat every `.iff` as `0xFF3BEF94` standard archive.
- Do not treat every texture as CDF-backed.
- Do not assume uniforms have paired `.cdf` files.
- Do not skip raw export when DDS conversion fails.
- Do not sort `0xFFFFFFFF` offsets as real file offsets.
- Do not drop name tables because they are after `fileLength`.
- Do not hardcode CDF texture header length as `0x5E`.
- Do not rewrite CDF payload sizes without updating the matching IFF descriptor table.
- Do not expose skin tone, conference, prestige, or longer string heap edits as confirmed until controlled diffs prove them.
- Do not modify the vanilla source game in default workflows; use `build-copy`.
- Do not present brand-new `ux###`, brand-new teams, or brand-new cyberface slots as safe normal edits until archive injection and references are solved.
- Do not treat scorebug layout work as simple texture replacement; it is a `gamedata` SCNE/LAYT/layout problem.
- Do not claim audio can decode to WAV yet.

---

## 16. Minimum Test Matrix

Use small known assets before full-game writes:

| Test asset | Why |
| --- | --- |
| `uh256.iff` | standard uniform with known successful rip behavior |
| `ua256.iff` | standard uniform missing name table case |
| `ux256.iff` | alternate uniform path |
| `selua256/seluh256/selux256.iff` | preview uniform path |
| `s212.iff` | stadium/court missing name table case |
| `s256.iff` / `floor.scne` | Georgia court/floor target |
| `teamselectlogo.iff/.cdf` | CDF-backed TXTR bank with 520 records |
| `gameintro_drums.iff/.cdf` | CDF-backed AUDO bank |
| `roster_english.iff` | vanilla ROST standard IFF |
| custom decrypted USERDATA/save ZIP | larger ROST payload and community roster support |
| `frontend.iff` / `global.iff` | 3-block standard IFF with many types and sentinel offsets |

Validation success means:

- unmodified parse -> write either byte-identical or structurally equivalent with explicit expected differences;
- no out-of-bounds offsets;
- name tables preserved;
- unknown subfiles preserved;
- raw assets exported even if conversion fails;
- rebuild does not corrupt archive TOC/cache.

---

## 17. Suggested Repo Documentation Layout

```text
docs/
  MASTER_HANDOFF.md
  ps3_standard_iff.md
  ps3_cdf_backed_iff.md
  txtr_standard_and_uniform_atlas.md
  cdf_texture_banks.md
  scne_floor.md
  roster_rost.md
  rebuild_preservation.md
  asset_namespace.md
  build_profiles.md
  known_bugs.md
  test_matrix.md
schemas/
  standard_iff_manifest.schema.json
  cdf_pair_manifest.schema.json
  txtr_inspect_manifest.schema.json
  roster_schema.json
  build_validation_report.schema.json
```

---

## 18. Source Material Incorporated

Local project sources integrated into this handoff:

```text
/mnt/data/choops_master_handoff.md
/mnt/data/CHoops_Roster_Studio_Master_Source_v2.md
/mnt/data/ps3_standard_iff_format_report.md
/mnt/data/ps3_cdf_iff_format_report.md
/mnt/data/floor_scne_format.md
/mnt/data/comprehensive list of EVERY iff file intended to be dumped by the Choops-Extractor tool.txt
/mnt/data/ps3_standard_iff_file_summary.csv
/mnt/data/ps3_standard_iff_subfiles.csv
/mnt/data/ps3_standard_iff_type_map.csv
```

Current GitHub snapshot consulted:

```text
ZMO34/CHoops-Extractor-ZMO
package.json as of 2026-06-18
index.js as of 2026-06-17
```

Accessible project-chat sweep incorporated on 2026-06-18:

```text
Build profiles for console vs RPCS3/emulator
Adding new IFF/cache entries and alternate UX constraints
Custom cyberfaces/head-model discussion
Adding more teams / team-count limits
Roster Studio editor design requests
ESPN-style scorebug and gamedata SCNE/TXTR layout work
Full-rip skipped/missing file debugging
floor.scne full-court texture remap discussion
```

---

## 19. Project Chat Sweep Addendum — Smaller Details That Were Easy To Miss

This section captures project-chat details that were not always formalized in the earlier format reports. These are not all equally proven. Treat them as design constraints, hypotheses, or workflow requirements depending on the confidence notes below.

### 19.1 Console vs RPCS3/emulator build profiles came from real mod workflow pain

The College Hoops Reborn workflow currently tends to require two separate builds:

```text
console build = default/original-ish texture resolution and stricter safety
RPCS3 build = upscaled textures allowed where emulator memory/performance can handle them
```

The desired UX is explicitly a “Build for Console” and “Build for Emulator” style button layout. The important implementation detail from the build-profile discussion is that the tool already works from a preserved vanilla source copy. That vanilla copy should become the authoritative reference for original asset dimensions, texture formats, mip counts, payload lengths, and likely console-safe limits.

Do **not** hardcode a table of default texture sizes if the vanilla game source is available. Instead:

```text
vanilla USRDIR / source copy
  -> scan every original IFF/CDF texture
  -> build vanilla asset profile index
  -> compare modded replacement textures against the vanilla profile
  -> for console: reject/downscale/reformat to match vanilla constraints
  -> for emulator: allow selected upscales with validation warnings
```

For DDS downsizing in JavaScript: it is possible only if the tool can safely parse/decode the DDS, resize the image, regenerate mipmaps, and write the correct compression format expected by the DDS->GTF import path. Blind byte resizing or canvas-based conversion of compressed DDS files is unsafe. A good near-term implementation can call external texture tools behind a profile manager while keeping the source mod textures unchanged.

### 19.2 Build-copy should remain the default mental model

The project direction is not “modify the only game dump in place.” The safer workflow is:

```text
vanilla extracted game folder stays untouched
mod source folder contains edited assets
build-copy creates a new output game folder
profile step validates or transforms assets
builder applies overrides only to the copied game
validator checks the result
```

Any future native GUI should make this obvious with source/output labels so users do not accidentally damage their vanilla base.

### 19.3 “Adding a new IFF to the cache” is not the same as making the game load it

A prior discussion asked whether the tool could add new IFF files to the College Hoops 2K8 cache, for example giving a team a new `ux###` alternate uniform when that team does not currently have one.

Important distinction:

```text
cache/index awareness in the tool
  !=
actual game archive TOC entry
  !=
roster/team reference
  !=
frontend/team-select logic knowing the asset exists
```

Safe current assumption:

- Replacing an existing archive is feasible.
- Reassigning a team to an already existing asset ID is a roster/editor target.
- Exposing an already existing `ux###` / `selux###` alternate is plausible if the roster and UI already know how to reference it.
- Creating a brand-new top-level `ux###.iff` for a team with no alternate is a separate archive-injection problem.

A future “new archive entry” system must solve:

1. where the archive TOC lives;
2. how filenames are hashed;
3. how cache/archive offsets and sizes are written;
4. whether archives can grow or must fit existing slots;
5. how roster/team data references the new asset;
6. how frontend/team-select screens discover or unlock the new uniform;
7. how console/RPCS3 react to changed archive layout.

Until that exists, do not let the UI present “add new alternate jersey” as a normal safe edit. Present only “assign existing alternate asset” or “replace existing alternate archive.”

### 19.4 Alternate jerseys are sparse by design

The inventory proves `ux###` and `selux###` are sparse, while `ua/uh` and `selua/seluh` are broad team families. Absence of `ux###` is meaningful. The tool should never generate alternate slots for all teams just because every team has home/away files.

Practical rule for Roster Studio:

```text
if ux### and selux### exist:
    show as existing alternate-capable asset
else:
    show alternate slot as unavailable / advanced archive-injection only
```

The special `800` ranges may be tournament/legacy/extra presentation assets, but that must remain research-labeled until mapped.

### 19.5 Adding brand-new teams is probably harder than replacing teams

A prior question asked whether more teams can be added beyond the game’s current roster. Current best model:

- The known team table has a fixed decoded count of 443 rows.
- UI, schedules, conference logic, tournament logic, commentary, art assets, and save structures likely assume fixed counts or fixed table sizes.
- Adding a brand-new row is not the same as editing an existing row.
- The practical first editor should replace or repurpose existing teams/unused rows, not expand the table.

Future “add team” support would require:

```text
ROST table expansion
string heap rebuild
all pointers after the expansion fixed
schedule/conference/menu systems audited
asset IDs assigned
archive assets present
frontend lists and selection screens tested
save compatibility tested
```

Treat “replace an existing team” as green/yellow depending on fields. Treat “increase team count” as red/research.

### 19.6 Custom cyberfaces/head models are likely replacement-first

Another prior thread asked how to add custom cyberfaces. Current safe interpretation:

- Head assets are likely in `h####.iff` archives and/or player-create face-related CDF/IFF banks.
- Replacing an existing head/cyberface asset is the first safe modding route.
- Assigning a player to an existing head/appearance ID is a roster-field research target.
- Adding a brand-new head archive has the same archive-injection problem as new alternates.

Do not promise unlimited new cyberface slots until the relevant roster appearance fields, `h####` namespace, and archive-entry system are proven.

### 19.7 UI/scorebug work is a distinct SCNE/LAYT/gamedata workstream

Prior scorebug work centered on files inside `gamedata`, including examples such as:

```text
scorebug_bloom.txtr
scorebug_bottombar.scne
```

The practical lesson was that the scorebug is not solved by texture editing alone. It likely requires editing layout/scene containers, spacing, anchors, model parts, texture placements, and possibly LAYT/SCNE routing inside `gamedata.iff`.

Specific desired scorebug/editor goals from the chat history:

- rearrange the scorebug to mimic a modern ESPN-style layout;
- move team logos correctly;
- ensure scores sit beside the correct team/logo rather than drifting separately;
- center the College Hoops 2K8 logo while keeping its existing height;
- center the “6th Man” element below the scorebug bars;
- rearrange timers, period/quarter/half labels, possession/bonus indicators, and other game-state widgets accurately;
- optionally place a 2K/broadcast logo in the top-right corner;
- optionally create a player-info card on the black bar with stats such as fouls, assists, or related live-game fields.

This should become its own workstream:

```text
Workstream G — UI / Scorebug / Gamedata SCNE-LAYT Editing
```

Do not mix it with uniform texture work. It needs an inspector for `gamedata.iff` internal `SCNE`, `LAYT`, and `TXTR` subfiles, plus a visual/layout manifest.

Useful commands to keep documented for this area:

```bat
choops-extractor rip <USRDIR> <output> --build-cache --game-name choops2k8
choops-extractor inspect-iff <path-to-gamedata.iff> <output-folder>
choops-extractor export-scne-obj <scorebug_bottombar.scne> <output-folder>
```

If exact command names change in the repo, update this section rather than letting agents invent one-off scripts.

### 19.8 Full-rip completeness needs an expected-vs-actual inventory audit

One project problem was that a recent rip extracted only part of the expected files. The comprehensive file list should be used not only for hash resolution but also for rip completeness.

Add a post-rip audit command:

```bat
choops-extractor audit-rip <expectedInventory.txt> <ripOutputFolder> <reportFolder>
```

It should report:

- expected archive names missing from the rip;
- numeric folders that likely correspond to unresolved expected names;
- duplicate/resolved collisions;
- IFF/CDF pairs where one side is missing;
- texture-conversion failures where raw asset was still preserved;
- archives skipped because of clamped reads or invalid TOC entries;
- skipped counts by family (`ua`, `uh`, `ux`, `s`, `m`, `h`, CDF-backed banks, frontend/UI, roster/database).

This is separate from “does the program exit without crashing.” A successful extraction must be complete, named, and auditable.

### 19.9 Roster Studio should feel like a database editor, not just CSV export

Earlier roster-editor design requests emphasized:

- dropdown editing;
- fill-in-the-blank text editing;
- player row editing;
- skin tone / appearance editing once confirmed;
- team assignments;
- asset assignment;
- alternate assignment;
- conference affiliation;
- conference prestige;
- school data in separate tabs;
- roster fill-in workflow for building a mod season quickly.

The current safety mapping still applies:

```text
confirmed fields = normal editor controls
candidate fields = research controls with warnings
unknown fields = hex/diff viewer only
```

A good UI mental model:

```text
Players tab
Teams / School Data tab
Roster Slots tab
Assets tab
Existing Alternates tab
Colors / Court Palette tab
Conferences tab, research-only until mapped
Appearance tab, research-only until skin tone and face fields are confirmed
Unknown Fields / Diff Lab tab
```

The editor should not require the user to manually manage relative string pointers or row offsets. That should be handled by source adapters and validators.

### 19.10 Conference affiliation and prestige are specifically requested but not mapped

Conference affiliation and prestige should be visible in the roadmap, but they are not confirmed fields yet. Do not guess offsets from intuition.

Recommended discovery method:

1. Identify in-game or save-editable conference/prestige changes if possible.
2. Make one-change saves.
3. Diff normalized ROST payloads.
4. Cross-check with `gamedata`, `frontend`, `loc`, and any schedule/conference-related tables.
5. Only then promote fields from research-only to editable.

### 19.11 Floor SCNE “stretch texture across the entire court” means UV/material routing, not just making a bigger texture

A prior floor task asked to stretch a texture container across the entire court floor and apron, with the modding plan of making other textures transparent and using one full-court template.

Important correction:

```text
texture header/payload size alone does not decide coverage
coverage is controlled by geometry, draw runs, material route, and UVs
```

The parser-informed route remains:

- use the `floor` model part;
- keep the non-colorized/glossy floor draw/pass route where possible;
- put full-court art in the correct diffuse texture slot, likely `texture_0` for the floor route;
- preserve a matching normal/gloss partner where needed;
- remap UV0 coordinates across the actual X/Z court bounds;
- do not route full-court art through paint/key/line material paths unless intentionally using Edit School color controls.

If the modding workflow eventually uses a transparent-overlay template, the tool should still preserve SCNE material expectations and avoid breaking gloss/shadow behavior.

### 19.12 Scorebug, floor, and uniform texture problems all look similar to users but are different technically

Future agents should classify any graphics issue by storage and render route before editing:

| User-visible task | Likely technical family |
| --- | --- |
| Jersey body texture edit | Standard IFF embedded TXTR |
| Jersey numbers/names edit | Standard IFF embedded TXTR variant + NAME metadata |
| Team-select uniform preview | Separate `selu*` standard IFF |
| Full-court texture template | Stadium `s###.iff` SCNE geometry/UV/material route |
| Team logos in selection screens | CDF-backed `teamselectlogo` TXTR/GTF bank |
| Scorebug layout | `gamedata.iff` SCNE/LAYT/TXTR layout system |
| Arena presentation images | likely CDF-backed `arenapics` |
| Crowd/intro audio | CDF-backed AUDO |
| Player cyberface | `h####.iff` / face/player-create asset research |

The same DDS file extension can appear in very different rebuild contexts. Always identify the archive family first.

### 19.13 Existing source-file handoff is now meant to be added to project sources

The user intends to add this master file to the project sources. Future chats should treat it as the first read, not as a casual summary. When updating the repo, prefer a stable path such as:

```text
docs/MASTER_HANDOFF.md
```

or:

```text
docs/AI_AGENT_HANDOFF.md
```

Keep future corrections additive and dated so older claims can be corrected without losing the historical reasoning.

### 19.14 Accessible chat-history limitation

This addendum is based on the project conversation summaries and uploaded source files currently surfaced in this workspace. If older chats exist outside the surfaced project context, they are not guaranteed to be represented here. Future agents should add dated deltas when the user recalls or uploads another missed thread.


---

## Appendix A — Full Extracted Asset Inventory Names From Provided Source

This appendix preserves the filename inventory extracted from the provided comprehensive list. It is useful for hash candidate generation and unresolved numeric-folder elimination.

```text
2560.iff
frontend.iff
frontend_sync.iff
loc.iff
fonts.iff
gamedata.iff
gamedataextra.iff
roster_english.iff
jukebox.iff
overlaycache.cdf
overlaycache.iff
arenapics.cdf
arenapics.iff
ua256.iff
teamselectlogo.iff
teamselectlogo.cdf
0.iff
8.iff
39.iff
45.iff
47.iff
53.iff
55.iff
64.iff
71.iff
77.iff
78.iff
79.iff
80.iff
87.iff
91.iff
94.iff
96.iff
97.iff
100.iff
105.iff
106.iff
111.iff
117.iff
119.iff
124.iff
131.iff
138.iff
143.iff
147.iff
149.iff
152.iff
154.iff
155.iff
158.iff
165.iff
171.iff
178.iff
183.iff
202.iff
203.iff
208.iff
213.iff
220.iff
223.iff
230.iff
231.iff
236.iff
239.iff
241.iff
246.iff
247.iff
258.iff
272.iff
278.iff
280.iff
291.iff
296.iff
298.iff
303.iff
304.iff
309.iff
314.iff
318.iff
330.iff
337.iff
344.iff
352.iff
356.iff
357.iff
358.iff
368.iff
373.iff
381.iff
385.iff
394.iff
401.iff
403.iff
412.iff
416.iff
424.iff
432.iff
440.iff
451.iff
459.iff
466.iff
471.iff
486.iff
493.iff
499.iff
506.iff
513.iff
516.iff
521.iff
526.iff
533.iff
537.iff
541.iff
543.iff
551.iff
556.iff
560.iff
570.iff
572.iff
576.iff
587.iff
596.iff
609.iff
616.iff
625.iff
626.iff
628.iff
632.iff
642.iff
645.iff
649.iff
653.iff
656.iff
662.iff
666.iff
675.iff
685.iff
688.iff
690.iff
691.iff
700.iff
701.iff
705.iff
708.iff
711.iff
713.iff
718.iff
719.iff
723.iff
725.iff
731.iff
738.iff
742.iff
743.iff
751.iff
754.iff
758.iff
761.iff
762.iff
765.iff
770.iff
774.iff
776.iff
778.iff
784.iff
793.iff
802.iff
808.iff
820.iff
825.iff
829.iff
832.iff
840.iff
842.iff
844.iff
853.iff
859.iff
861.iff
866.iff
868.iff
876.iff
884.iff
887.iff
890.iff
893.iff
896.iff
902.iff
909.iff
915.iff
926.iff
928.iff
932.iff
935.iff
941.iff
948.iff
951.iff
955.iff
958.iff
969.iff
972.iff
975.iff
978.iff
982.iff
985.iff
991.iff
994.iff
996.iff
999.iff
1004.iff
1005.iff
1015.iff
1021.iff
1029.iff
1030.iff
1038.iff
1045.iff
1051.iff
1055.iff
1056.iff
1060.iff
1065.iff
1073.iff
1078.iff
1084.iff
1093.iff
1102.iff
1112.iff
1120.iff
1125.iff
1126.iff
1131.iff
1133.iff
1138.iff
1140.iff
1144.iff
1149.iff
1152.iff
1157.iff
1163.iff
1172.iff
1175.iff
1180.iff
1181.iff
1185.iff
1191.iff
1197.iff
1202.iff
1204.iff
1206.iff
1211.iff
1218.iff
1251.iff
1255.iff
1260.iff
1263.iff
1272.iff
1275.iff
1280.iff
1288.iff
1296.iff
1300.iff
1318.iff
1320.iff
1323.iff
1330.iff
1332.iff
1334.iff
1342.iff
1347.iff
1349.iff
1354.iff
1359.iff
1365.iff
1368.iff
1370.iff
1376.iff
1380.iff
1385.iff
1387.iff
1390.iff
1397.iff
1403.iff
1407.iff
1412.iff
1413.iff
1421.iff
1428.iff
1432.iff
1440.iff
1453.iff
1459.iff
1468.iff
1469.iff
1474.iff
1478.iff
1479.iff
1489.iff
1496.iff
1498.iff
1501.iff
1509.iff
1516.iff
1521.iff
1527.iff
1532.iff
1534.iff
1535.iff
1540.iff
1543.iff
1544.iff
1547.iff
1554.iff
1556.iff
1557.iff
1560.iff
1564.iff
1565.iff
1567.iff
1569.iff
1571.iff
1584.iff
1585.iff
1593.iff
1596.iff
1603.iff
1605.iff
1611.iff
1613.iff
1615.iff
1618.iff
1620.iff
1621.iff
1625.iff
1628.iff
1636.iff
1641.iff
1646.iff
1657.iff
1658.iff
1660.iff
1662.iff
1670.iff
1676.iff
1681.iff
1687.iff
1688.iff
1692.iff
1693.iff
1696.iff
1700.iff
1712.iff
1718.iff
1721.iff
1723.iff
1726.iff
1735.iff
1739.iff
1743.iff
1749.iff
1756.iff
1760.iff
1763.iff
1764.iff
1771.iff
1773.iff
1778.iff
1786.iff
1797.iff
1801.iff
1807.iff
1813.iff
1815.iff
1817.iff
1822.iff
1834.iff
1836.iff
1839.iff
1850.iff
1856.iff
1857.iff
1858.iff
1861.iff
1865.iff
1880.iff
1884.iff
1886.iff
1891.iff
1895.iff
1902.iff
1904.iff
1908.iff
1914.iff
1919.iff
1924.iff
1929.iff
1939.iff
1948.iff
1977.iff
1985.iff
1992.iff
2000.iff
2014.iff
2018.iff
2028.iff
2036.iff
2042.iff
2046.iff
2050.iff
2059.iff
2063.iff
2064.iff
2071.iff
2075.iff
2080.iff
2087.iff
2089.iff
2095.iff
2101.iff
2106.iff
2110.iff
2114.iff
2116.iff
2129.iff
2133.iff
2135.iff
2137.iff
2141.iff
2152.iff
2162.iff
2169.iff
2179.iff
2186.iff
2189.iff
2216.iff
2223.iff
2231.iff
2238.iff
2253.iff
2257.iff
2262.iff
2263.iff
2269.iff
2271.iff
2277.iff
2287.iff
2289.iff
2294.iff
2298.iff
2304.iff
2305.iff
2311.iff
2316.iff
2321.iff
2323.iff
2325.iff
2333.iff
2339.iff
2347.iff
2354.iff
2359.iff
2362.iff
2366.iff
2372.iff
2384.iff
2385.iff
2395.iff
2400.iff
2402.iff
2408.iff
2413.iff
2419.iff
2422.iff
2430.iff
2433.iff
2436.iff
2438.iff
2440.iff
2441.iff
2446.iff
2452.iff
2459.iff
2465.iff
2466.iff
2469.iff
2472.iff
2477.iff
2485.iff
2486.iff
2490.iff
2492.iff
2497.iff
2500.iff
2503.iff
2507.iff
2510.iff
2521.iff
2523.iff
2525.iff
2527.iff
2534.iff
2535.iff
2537.iff
2543.iff
2546.iff
2548.iff
2550.iff
2555.iff
2565.iff
2567.iff
2577.iff
2581.iff
2585.iff
2586.iff
2588.iff
2592.iff
2618.iff
2623.iff
2627.iff
2631.iff
2634.iff
2643.iff
2652.iff
2655.iff
2681.iff
2682.iff
2688.iff
2692.iff
2695.iff
2697.iff
2700.iff
2706.iff
2708.iff
2713.iff
2717.iff
2722.iff
2723.iff
2732.iff
2734.iff
2735.iff
2738.iff
2743.iff
2746.iff
2752.iff
2757.iff
2762.iff
2777.iff
2782.iff
2799.iff
2807.iff
2815.iff
2820.iff
2827.iff
2829.iff
2836.iff
2848.iff
2864.iff
2869.iff
2875.iff
2877.iff
2880.iff
2882.iff
2886.iff
2888.iff
2903.iff
2907.iff
2912.iff
2919.iff
2923.iff
2924.iff
2929.iff
2934.iff
2940.iff
2948.iff
2951.iff
2954.iff
2960.iff
2965.iff
2972.iff
2979.iff
2981.iff
2989.iff
2990.iff
2995.iff
3002.iff
3008.iff
3029.iff
3032.iff
3033.iff
3034.iff
3039.iff
3044.iff
3051.iff
3064.iff
3067.iff
3077.iff
3086.iff
3092.iff
3093.iff
3098.iff
3100.iff
3104.iff
3107.iff
3112.iff
3124.iff
3129.iff
3132.iff
3140.iff
3156.iff
3157.iff
3161.iff
3163.iff
3165.iff
3168.iff
3171.iff
3172.iff
3181.iff
3182.iff
3185.iff
3191.iff
3196.iff
3202.iff
3203.iff
3214.iff
3222.iff
3236.iff
3244.iff
3248.iff
3258.iff
3260.iff
3264.iff
3267.iff
3275.iff
3279.iff
3286.iff
3289.iff
3294.iff
3296.iff
3306.iff
3308.iff
3309.iff
3322.iff
3330.iff
3336.iff
3341.iff
3343.iff
3344.iff
3348.iff
3349.iff
3353.iff
3354.iff
3356.iff
3361.iff
3368.iff
3369.iff
3375.iff
ababall.iff
ao_tri.iff
ao_vtri.iff
ao_wishbone.iff
basket.cdf
basket.iff
chantcreate_drums.iff
chantcreate_sounds.iff
chantcreate.iff
cloth_shorts.iff
cloth_tri.iff
cloth_u.iff
cloth_v.iff
cloth_vtri.iff
cloth_wishbone.iff
coach001.iff
coach002.iff
coach003.iff
coach004.iff
coach005.iff
coach006.iff
coach007.iff
coach008.iff
coach009.iff
coach010.iff
coach011.iff
coach012.iff
coach013.iff
coach014.iff
coach015.iff
coach016.iff
coach017.iff
coach018.iff
coach019.iff
coach020.iff
coach021.iff
coach022.iff
coach023.iff
coach024.iff
coach025.iff
coach026.iff
coach027.iff
coach028.iff
coach029.iff
coach030.iff
coach031.iff
coach032.iff
coach033.iff
coach034.iff
coach035.iff
coach036.iff
coach037.iff
coach038.iff
coach039.iff
coach040.iff
coach041.iff
coach042.iff
coach043.iff
coach044.iff
coach045.iff
coach046.iff
coach047.iff
coach048.iff
coach049.iff
coach050.iff
coachmode.iff
createpholder.iff
crowd.iff
crowdloops_inside_large.iff
crowdloops_inside_small.iff
cwd-ahh-front_large.cdf
cwd-ahh-front_large.iff
cwd-ahh-front_small.cdf
cwd-ahh-front_small.iff
cwd-ahh-rear_large.cdf
cwd-ahh-rear_large.iff
cwd-ahh-rear_small.cdf
cwd-ahh-rear_small.iff
cwd-boo-front_large.cdf
cwd-boo-front_large.iff
cwd-boo-front_small.cdf
cwd-boo-front_small.iff
cwd-boo-rear_large.cdf
cwd-boo-rear_large.iff
cwd-boo-rear_small.cdf
cwd-boo-rear_small.iff
cwd-cheer-lrg-front_large.cdf
cwd-cheer-lrg-front_large.iff
cwd-cheer-lrg-front_small.cdf
cwd-cheer-lrg-front_small.iff
cwd-cheer-lrg-rear_large.cdf
cwd-cheer-lrg-rear_large.iff
cwd-cheer-lrg-rear_small.cdf
cwd-cheer-lrg-rear_small.iff
cwd-cheer-med-front_large.cdf
cwd-cheer-med-front_large.iff
cwd-cheer-med-front_small.cdf
cwd-cheer-med-front_small.iff
cwd-cheer-med-rear_large.cdf
cwd-cheer-med-rear_large.iff
cwd-cheer-med-rear_small.cdf
cwd-cheer-med-rear_small.iff
cwd-cheer-sml-front_large.cdf
cwd-cheer-sml-front_large.iff
cwd-cheer-sml-front_small.cdf
cwd-cheer-sml-front_small.iff
cwd-cheer-sml-rear_large.cdf
cwd-cheer-sml-rear_large.iff
cwd-cheer-sml-rear_small.cdf
cwd-cheer-sml-rear_small.iff
cwd-freethrow-front_large.cdf
cwd-freethrow-front_large.iff
cwd-freethrow-front_small.cdf
cwd-freethrow-front_small.iff
cwd-freethrow-rear_large.cdf
cwd-freethrow-rear_large.iff
cwd-freethrow-rear_small.cdf
cwd-freethrow-rear_small.iff
Director.iff
dornas.iff
drilldata.iff
drillschallenge_attackbasket.iff
drillschallenge_denyposition.iff
drillschallenge_dribblecourse.iff
drillschallenge_linecourse.iff
drillschallenge_shooting.iff
drillschallenge.iff
facegen.iff
floor.scne
gameintro_cameras.iff
gameintro_drums.cdf
gameintro_drums.iff
gameintro_playerspeech.cdf
gameintro_playerspeech.iff
gameintro.iff
global.iff
gumbel.iff
h0001.iff
h0002.iff
h0003.iff
h0004.iff
h0005.iff
h0006.iff
h0007.iff
h0008.iff
h0009.iff
h0010.iff
h0011.iff
h0012.iff
h0013.iff
h0014.iff
h0015.iff
h0016.iff
h0017.iff
h0018.iff
h0019.iff
h0020.iff
h0021.iff
h0022.iff
h0023.iff
h0024.iff
h0025.iff
h0026.iff
h0027.iff
h0028.iff
h0029.iff
h0030.iff
h0031.iff
h0032.iff
h0033.iff
h0034.iff
h0035.iff
h0036.iff
h0037.iff
h0038.iff
h0039.iff
h0040.iff
h0041.iff
h0042.iff
h0043.iff
h0044.iff
h0045.iff
h0046.iff
h0047.iff
h0048.iff
h0049.iff
h0050.iff
h0051.iff
h0052.iff
h0053.iff
h0054.iff
h0055.iff
h0056.iff
h0057.iff
h0058.iff
h0059.iff
h0060.iff
h0061.iff
h0062.iff
h0063.iff
h0064.iff
h0065.iff
h0066.iff
h0067.iff
h0068.iff
h0069.iff
h0070.iff
h0071.iff
h0072.iff
h0073.iff
h0074.iff
h0075.iff
h0076.iff
h0077.iff
h0078.iff
h0079.iff
h0080.iff
h0081.iff
h0082.iff
h0083.iff
h0084.iff
halftimeadjustments.iff
kellogg.iff
legacy.iff
legalpage.iff
loading_drillschallenge.iff
loading.iff
loadm.bin
m010.iff
m011.iff
m013.iff
m014.iff
m015.iff
m016.iff
m017.iff
m018.iff
m021.iff
m030.iff
m033.iff
m035.iff
m036.iff
m040.iff
m042.iff
m043.iff
m044.iff
m045.iff
m046.iff
m047.iff
m049.iff
m052.iff
m053.iff
m054.iff
m055.iff
m072.iff
m075.iff
m077.iff
m078.iff
m079.iff
m080.iff
m081.iff
m082.iff
m083.iff
m084.iff
m085.iff
m086.iff
m087.iff
m089.iff
m090.iff
m092.iff
m093.iff
m095.iff
m119.iff
m120.iff
m121.iff
m122.iff
m123.iff
m124.iff
m127.iff
m129.iff
m130.iff
m131.iff
m147.iff
m149.iff
m161.iff
m162.iff
m164.iff
m167.iff
m168.iff
m172.iff
m173.iff
m187.iff
m199.iff
m204.iff
m205.iff
m207.iff
m209.iff
m210.iff
m211.iff
m234.iff
m235.iff
m236.iff
m237.iff
m238.iff
m239.iff
m240.iff
m241.iff
m242.iff
m243.iff
m245.iff
m251.iff
m253.iff
m254.iff
m255.iff
m256.iff
m257.iff
m258.iff
m261.iff
m262.iff
m263.iff
m265.iff
m270.iff
m303.iff
m307.iff
m308.iff
m309.iff
m315.iff
m317.iff
m318.iff
m321.iff
online.iff
pcaatface.cdf
pcaatface.iff
pcarmtats.cdf
pcarmtats.iff
pcchest.cdf
pcchest.iff
pcfacehair.cdf
pcfacehair.iff
pcfacenormal.cdf
pcfacenormal.iff
pchair.cdf
pchair.iff
playeditor.iff
playercreate.iff
powerbar.iff
reelmanual.iff
s000.iff
s001.iff
s002.iff
s003.iff
s004.iff
s005.iff
s006.iff
s007.iff
s008.iff
s009.iff
s010.iff
s011.iff
s012.iff
s013.iff
s014.iff
s015.iff
s016.iff
s017.iff
s018.iff
s019.iff
s020.iff
s021.iff
s022.iff
s023.iff
s024.iff
s025.iff
s026.iff
s027.iff
s028.iff
s029.iff
s030.iff
s031.iff
s032.iff
s033.iff
s034.iff
s035.iff
s036.iff
s037.iff
s038.iff
s039.iff
s040.iff
s041.iff
s042.iff
s043.iff
s044.iff
s045.iff
s046.iff
s047.iff
s048.iff
s049.iff
s050.iff
s051.iff
s052.iff
s053.iff
s054.iff
s055.iff
s056.iff
s057.iff
s058.iff
s059.iff
s060.iff
s061.iff
s062.iff
s063.iff
s064.iff
s065.iff
s066.iff
s067.iff
s068.iff
s069.iff
s070.iff
s071.iff
s072.iff
s073.iff
s074.iff
s075.iff
s076.iff
s077.iff
s078.iff
s079.iff
s080.iff
s081.iff
s082.iff
s083.iff
s084.iff
s085.iff
s086.iff
s087.iff
s088.iff
s089.iff
s090.iff
s091.iff
s092.iff
s093.iff
s094.iff
s095.iff
s096.iff
s097.iff
s098.iff
s099.iff
s100.iff
s101.iff
s102.iff
s103.iff
s104.iff
s105.iff
s106.iff
s107.iff
s108.iff
s109.iff
s110.iff
s111.iff
s112.iff
s113.iff
s114.iff
s115.iff
s116.iff
s117.iff
s118.iff
s119.iff
s120.iff
s121.iff
s122.iff
s123.iff
s124.iff
s125.iff
s126.iff
s127.iff
s128.iff
s129.iff
s130.iff
s131.iff
s132.iff
s133.iff
s134.iff
s135.iff
s136.iff
s137.iff
s138.iff
s139.iff
s140.iff
s141.iff
s142.iff
s143.iff
s144.iff
s145.iff
s146.iff
s147.iff
s148.iff
s149.iff
s150.iff
s151.iff
s152.iff
s153.iff
s154.iff
s155.iff
s156.iff
s157.iff
s158.iff
s159.iff
s160.iff
s161.iff
s162.iff
s163.iff
s164.iff
s165.iff
s166.iff
s167.iff
s168.iff
s169.iff
s170.iff
s171.iff
s172.iff
s173.iff
s174.iff
s175.iff
s176.iff
s177.iff
s178.iff
s179.iff
s180.iff
s181.iff
s182.iff
s183.iff
s184.iff
s185.iff
s186.iff
s187.iff
s188.iff
s189.iff
s190.iff
s191.iff
s192.iff
s193.iff
s194.iff
s195.iff
s196.iff
s197.iff
s198.iff
s199.iff
s200.iff
s201.iff
s202.iff
s203.iff
s204.iff
s205.iff
s206.iff
s207.iff
s208.iff
s209.iff
s210.iff
s211.iff
s212.iff
s213.iff
s214.iff
s215.iff
s216.iff
s217.iff
s218.iff
s219.iff
s220.iff
s221.iff
s222.iff
s223.iff
s224.iff
s225.iff
s226.iff
s227.iff
s228.iff
s229.iff
s230.iff
s231.iff
s232.iff
s233.iff
s234.iff
s235.iff
s236.iff
s237.iff
s238.iff
s239.iff
s240.iff
s241.iff
s242.iff
s243.iff
s244.iff
s245.iff
s246.iff
s247.iff
s248.iff
s249.iff
s250.iff
s251.iff
s252.iff
s253.iff
s254.iff
s255.iff
s256.iff
s257.iff
s258.iff
s259.iff
s260.iff
s261.iff
s262.iff
s263.iff
s264.iff
s265.iff
s266.iff
s267.iff
s268.iff
s269.iff
s270.iff
s271.iff
s272.iff
s273.iff
s274.iff
s275.iff
s276.iff
s277.iff
s278.iff
s279.iff
s280.iff
s281.iff
s282.iff
s283.iff
s284.iff
s285.iff
s286.iff
s287.iff
s288.iff
s289.iff
s290.iff
s291.iff
s292.iff
s293.iff
s294.iff
s295.iff
s296.iff
s297.iff
s298.iff
s299.iff
s300.iff
s301.iff
s302.iff
s303.iff
s304.iff
s305.iff
s306.iff
s307.iff
s308.iff
s309.iff
s310.iff
s311.iff
s312.iff
s313.iff
s314.iff
s315.iff
s316.iff
s317.iff
s318.iff
s319.iff
s320.iff
s321.iff
s322.iff
s323.iff
s324.iff
s325.iff
s326.iff
s332.iff
s333.iff
s334.iff
s337.iff
s338.iff
s340.iff
s342.iff
s343.iff
s345.iff
s346.iff
s347.iff
s349.iff
s350.iff
s351.iff
s352.iff
s353.iff
s354.iff
s355.iff
s356.iff
s357.iff
s358.iff
s361.iff
s365.iff
s368.iff
s369.iff
s370.iff
s371.iff
s372.iff
s373.iff
s375.iff
s377.iff
s379.iff
s381.iff
s382.iff
s383.iff
s384.iff
s421.iff
s422.iff
s429.iff
s430.iff
s431.iff
s432.iff
s451.iff
s452.iff
s800.iff
s801.iff
s802.iff
s803.iff
s804.iff
s805.iff
s806.iff
s807.iff
s808.iff
s809.iff
s810.iff
s811.iff
s812.iff
selua000.iff
selua001.iff
selua002.iff
selua003.iff
selua004.iff
selua005.iff
selua006.iff
selua007.iff
selua008.iff
selua009.iff
selua010.iff
selua011.iff
selua012.iff
selua013.iff
selua014.iff
selua015.iff
selua016.iff
selua017.iff
selua018.iff
selua019.iff
selua020.iff
selua021.iff
selua022.iff
selua023.iff
selua024.iff
selua025.iff
selua026.iff
selua027.iff
selua028.iff
selua029.iff
selua030.iff
selua031.iff
selua032.iff
selua033.iff
selua034.iff
selua035.iff
selua036.iff
selua037.iff
selua038.iff
selua039.iff
selua040.iff
selua041.iff
selua042.iff
selua043.iff
selua044.iff
selua045.iff
selua046.iff
selua047.iff
selua048.iff
selua049.iff
selua050.iff
selua051.iff
selua052.iff
selua053.iff
selua054.iff
selua055.iff
selua056.iff
selua057.iff
selua058.iff
selua059.iff
selua060.iff
selua061.iff
selua062.iff
selua063.iff
selua064.iff
selua065.iff
selua066.iff
selua067.iff
selua068.iff
selua069.iff
selua070.iff
selua071.iff
selua072.iff
selua073.iff
selua074.iff
selua075.iff
selua076.iff
selua077.iff
selua078.iff
selua079.iff
selua080.iff
selua081.iff
selua082.iff
selua083.iff
selua084.iff
selua085.iff
selua086.iff
selua087.iff
selua088.iff
selua089.iff
selua090.iff
selua091.iff
selua092.iff
selua093.iff
selua094.iff
selua095.iff
selua096.iff
selua097.iff
selua098.iff
selua099.iff
selua100.iff
selua101.iff
selua102.iff
selua103.iff
selua104.iff
selua105.iff
selua106.iff
selua107.iff
selua108.iff
selua109.iff
selua110.iff
selua111.iff
selua112.iff
selua113.iff
selua114.iff
selua115.iff
selua116.iff
selua117.iff
selua118.iff
selua119.iff
selua120.iff
selua121.iff
selua122.iff
selua123.iff
selua124.iff
selua125.iff
selua126.iff
selua127.iff
selua128.iff
selua129.iff
selua130.iff
selua131.iff
selua132.iff
selua133.iff
selua134.iff
selua135.iff
selua136.iff
selua137.iff
selua138.iff
selua139.iff
selua140.iff
selua141.iff
selua142.iff
selua143.iff
selua144.iff
selua145.iff
selua146.iff
selua147.iff
selua148.iff
selua149.iff
selua150.iff
selua151.iff
selua152.iff
selua153.iff
selua154.iff
selua155.iff
selua156.iff
selua157.iff
selua158.iff
selua159.iff
selua160.iff
selua161.iff
selua162.iff
selua163.iff
selua164.iff
selua165.iff
selua166.iff
selua167.iff
selua168.iff
selua169.iff
selua170.iff
selua171.iff
selua172.iff
selua173.iff
selua174.iff
selua175.iff
selua176.iff
selua177.iff
selua178.iff
selua179.iff
selua180.iff
selua181.iff
selua182.iff
selua183.iff
selua184.iff
selua185.iff
selua186.iff
selua187.iff
selua188.iff
selua189.iff
selua190.iff
selua191.iff
selua192.iff
selua193.iff
selua194.iff
selua195.iff
selua196.iff
selua197.iff
selua198.iff
selua199.iff
selua200.iff
selua201.iff
selua202.iff
selua203.iff
selua204.iff
selua205.iff
selua206.iff
selua207.iff
selua208.iff
selua209.iff
selua210.iff
selua211.iff
selua212.iff
selua213.iff
selua214.iff
selua215.iff
selua216.iff
selua217.iff
selua218.iff
selua219.iff
selua220.iff
selua221.iff
selua222.iff
selua223.iff
selua224.iff
selua225.iff
selua226.iff
selua227.iff
selua228.iff
selua229.iff
selua230.iff
selua231.iff
selua232.iff
selua233.iff
selua234.iff
selua235.iff
selua236.iff
selua237.iff
selua238.iff
selua239.iff
selua240.iff
selua241.iff
selua242.iff
selua243.iff
selua244.iff
selua245.iff
selua246.iff
selua247.iff
selua248.iff
selua249.iff
selua250.iff
selua251.iff
selua252.iff
selua253.iff
selua254.iff
selua255.iff
selua256.iff
selua257.iff
selua258.iff
selua259.iff
selua260.iff
selua261.iff
selua262.iff
selua263.iff
selua264.iff
selua265.iff
selua266.iff
selua267.iff
selua268.iff
selua269.iff
selua270.iff
selua271.iff
selua272.iff
selua273.iff
selua274.iff
selua275.iff
selua276.iff
selua277.iff
selua278.iff
selua279.iff
selua280.iff
selua281.iff
selua282.iff
selua283.iff
selua284.iff
selua285.iff
selua286.iff
selua287.iff
selua288.iff
selua289.iff
selua290.iff
selua291.iff
selua292.iff
selua293.iff
selua294.iff
selua295.iff
selua296.iff
selua297.iff
selua298.iff
selua299.iff
selua300.iff
selua301.iff
selua302.iff
selua303.iff
selua304.iff
selua305.iff
selua306.iff
selua307.iff
selua308.iff
selua309.iff
selua310.iff
selua311.iff
selua312.iff
selua313.iff
selua314.iff
selua315.iff
selua316.iff
selua317.iff
selua318.iff
selua319.iff
selua320.iff
selua321.iff
selua322.iff
selua323.iff
selua324.iff
selua325.iff
selua326.iff
selua327.iff
selua328.iff
selua329.iff
selua330.iff
selua331.iff
selua332.iff
selua333.iff
selua334.iff
selua335.iff
selua336.iff
selua337.iff
selua338.iff
selua339.iff
selua340.iff
selua341.iff
selua342.iff
selua343.iff
selua344.iff
selua345.iff
selua346.iff
selua347.iff
selua348.iff
selua349.iff
selua350.iff
selua351.iff
selua352.iff
selua353.iff
selua354.iff
selua355.iff
selua356.iff
selua357.iff
selua358.iff
selua359.iff
selua360.iff
selua361.iff
selua362.iff
selua363.iff
selua364.iff
selua365.iff
selua366.iff
selua367.iff
selua368.iff
selua369.iff
selua370.iff
selua371.iff
selua372.iff
selua373.iff
selua374.iff
selua375.iff
selua376.iff
selua377.iff
selua378.iff
selua379.iff
selua380.iff
selua381.iff
selua382.iff
selua383.iff
selua384.iff
selua385.iff
selua386.iff
selua387.iff
selua388.iff
selua389.iff
selua390.iff
selua391.iff
selua392.iff
selua393.iff
selua394.iff
selua395.iff
selua396.iff
selua397.iff
selua398.iff
selua400.iff
selua401.iff
selua403.iff
selua404.iff
selua405.iff
selua406.iff
selua407.iff
selua408.iff
selua409.iff
selua410.iff
selua411.iff
selua412.iff
selua413.iff
selua414.iff
selua415.iff
selua416.iff
selua417.iff
selua418.iff
selua421.iff
selua422.iff
selua423.iff
selua424.iff
selua425.iff
selua426.iff
selua427.iff
selua428.iff
selua429.iff
selua430.iff
selua448.iff
selua449.iff
selua450.iff
selua451.iff
selua452.iff
selua800.iff
selua801.iff
selua802.iff
selua803.iff
selua804.iff
selua805.iff
selua806.iff
selua807.iff
selua808.iff
selua809.iff
selua810.iff
selua811.iff
selua812.iff
selua813.iff
selua814.iff
selua815.iff
selua816.iff
selua817.iff
selua818.iff
selua819.iff
seluh000.iff
seluh001.iff
seluh002.iff
seluh003.iff
seluh004.iff
seluh005.iff
seluh006.iff
seluh007.iff
seluh008.iff
seluh009.iff
seluh010.iff
seluh011.iff
seluh012.iff
seluh013.iff
seluh014.iff
seluh015.iff
seluh016.iff
seluh017.iff
seluh018.iff
seluh019.iff
seluh020.iff
seluh021.iff
seluh022.iff
seluh023.iff
seluh024.iff
seluh025.iff
seluh026.iff
seluh027.iff
seluh028.iff
seluh029.iff
seluh030.iff
seluh031.iff
seluh032.iff
seluh033.iff
seluh034.iff
seluh035.iff
seluh036.iff
seluh037.iff
seluh038.iff
seluh039.iff
seluh040.iff
seluh041.iff
seluh042.iff
seluh043.iff
seluh044.iff
seluh045.iff
seluh046.iff
seluh047.iff
seluh048.iff
seluh049.iff
seluh050.iff
seluh051.iff
seluh052.iff
seluh053.iff
seluh054.iff
seluh055.iff
seluh056.iff
seluh057.iff
seluh058.iff
seluh059.iff
seluh060.iff
seluh061.iff
seluh062.iff
seluh063.iff
seluh064.iff
seluh065.iff
seluh066.iff
seluh067.iff
seluh068.iff
seluh069.iff
seluh070.iff
seluh071.iff
seluh072.iff
seluh073.iff
seluh074.iff
seluh075.iff
seluh076.iff
seluh077.iff
seluh078.iff
seluh079.iff
seluh080.iff
seluh081.iff
seluh082.iff
seluh083.iff
seluh084.iff
seluh085.iff
seluh086.iff
seluh087.iff
seluh088.iff
seluh089.iff
seluh090.iff
seluh091.iff
seluh092.iff
seluh093.iff
seluh094.iff
seluh095.iff
seluh096.iff
seluh097.iff
seluh098.iff
seluh099.iff
seluh100.iff
seluh101.iff
seluh102.iff
seluh103.iff
seluh104.iff
seluh105.iff
seluh106.iff
seluh107.iff
seluh108.iff
seluh109.iff
seluh110.iff
seluh111.iff
seluh112.iff
seluh113.iff
seluh114.iff
seluh115.iff
seluh116.iff
seluh117.iff
seluh118.iff
seluh119.iff
seluh120.iff
seluh121.iff
seluh122.iff
seluh123.iff
seluh124.iff
seluh125.iff
seluh126.iff
seluh127.iff
seluh128.iff
seluh129.iff
seluh130.iff
seluh131.iff
seluh132.iff
seluh133.iff
seluh134.iff
seluh135.iff
seluh136.iff
seluh137.iff
seluh138.iff
seluh139.iff
seluh140.iff
seluh141.iff
seluh142.iff
seluh143.iff
seluh144.iff
seluh145.iff
seluh146.iff
seluh147.iff
seluh148.iff
seluh149.iff
seluh150.iff
seluh151.iff
seluh152.iff
seluh153.iff
seluh154.iff
seluh155.iff
seluh156.iff
seluh157.iff
seluh158.iff
seluh159.iff
seluh160.iff
seluh161.iff
seluh162.iff
seluh163.iff
seluh164.iff
seluh165.iff
seluh166.iff
seluh167.iff
seluh168.iff
seluh169.iff
seluh170.iff
seluh171.iff
seluh172.iff
seluh173.iff
seluh174.iff
seluh175.iff
seluh176.iff
seluh177.iff
seluh178.iff
seluh179.iff
seluh180.iff
seluh181.iff
seluh182.iff
seluh183.iff
seluh184.iff
seluh185.iff
seluh186.iff
seluh187.iff
seluh188.iff
seluh189.iff
seluh190.iff
seluh191.iff
seluh192.iff
seluh193.iff
seluh194.iff
seluh195.iff
seluh196.iff
seluh197.iff
seluh198.iff
seluh199.iff
seluh200.iff
seluh201.iff
seluh202.iff
seluh203.iff
seluh204.iff
seluh205.iff
seluh206.iff
seluh207.iff
seluh208.iff
seluh209.iff
seluh210.iff
seluh211.iff
seluh212.iff
seluh213.iff
seluh214.iff
seluh215.iff
seluh216.iff
seluh217.iff
seluh218.iff
seluh219.iff
seluh220.iff
seluh221.iff
seluh222.iff
seluh223.iff
seluh224.iff
seluh225.iff
seluh226.iff
seluh227.iff
seluh228.iff
seluh229.iff
seluh230.iff
seluh231.iff
seluh232.iff
seluh233.iff
seluh234.iff
seluh235.iff
seluh236.iff
seluh237.iff
seluh238.iff
seluh239.iff
seluh240.iff
seluh241.iff
seluh242.iff
seluh243.iff
seluh244.iff
seluh245.iff
seluh246.iff
seluh247.iff
seluh248.iff
seluh249.iff
seluh250.iff
seluh251.iff
seluh252.iff
seluh253.iff
seluh254.iff
seluh255.iff
seluh256.iff
seluh257.iff
seluh258.iff
seluh259.iff
seluh260.iff
seluh261.iff
seluh262.iff
seluh263.iff
seluh264.iff
seluh265.iff
seluh266.iff
seluh267.iff
seluh268.iff
seluh269.iff
seluh270.iff
seluh271.iff
seluh272.iff
seluh273.iff
seluh274.iff
seluh275.iff
seluh276.iff
seluh277.iff
seluh278.iff
seluh279.iff
seluh280.iff
seluh281.iff
seluh282.iff
seluh283.iff
seluh284.iff
seluh285.iff
seluh286.iff
seluh287.iff
seluh288.iff
seluh289.iff
seluh290.iff
seluh291.iff
seluh292.iff
seluh293.iff
seluh294.iff
seluh295.iff
seluh296.iff
seluh297.iff
seluh298.iff
seluh299.iff
seluh300.iff
seluh301.iff
seluh302.iff
seluh303.iff
seluh304.iff
seluh305.iff
seluh306.iff
seluh307.iff
seluh308.iff
seluh309.iff
seluh310.iff
seluh311.iff
seluh312.iff
seluh313.iff
seluh314.iff
seluh315.iff
seluh316.iff
seluh317.iff
seluh318.iff
seluh319.iff
seluh320.iff
seluh321.iff
seluh322.iff
seluh323.iff
seluh324.iff
seluh325.iff
seluh326.iff
seluh327.iff
seluh328.iff
seluh329.iff
seluh330.iff
seluh331.iff
seluh332.iff
seluh333.iff
seluh334.iff
seluh335.iff
seluh336.iff
seluh337.iff
seluh338.iff
seluh339.iff
seluh340.iff
seluh341.iff
seluh342.iff
seluh343.iff
seluh344.iff
seluh345.iff
seluh346.iff
seluh347.iff
seluh348.iff
seluh349.iff
seluh350.iff
seluh351.iff
seluh352.iff
seluh353.iff
seluh354.iff
seluh355.iff
seluh356.iff
seluh357.iff
seluh358.iff
seluh359.iff
seluh360.iff
seluh361.iff
seluh362.iff
seluh363.iff
seluh364.iff
seluh365.iff
seluh366.iff
seluh367.iff
seluh368.iff
seluh369.iff
seluh370.iff
seluh371.iff
seluh372.iff
seluh373.iff
seluh374.iff
seluh375.iff
seluh376.iff
seluh377.iff
seluh378.iff
seluh379.iff
seluh380.iff
seluh381.iff
seluh382.iff
seluh383.iff
seluh384.iff
seluh385.iff
seluh386.iff
seluh387.iff
seluh388.iff
seluh389.iff
seluh390.iff
seluh391.iff
seluh392.iff
seluh393.iff
seluh394.iff
seluh395.iff
seluh396.iff
seluh397.iff
seluh398.iff
seluh400.iff
seluh401.iff
seluh403.iff
seluh404.iff
seluh405.iff
seluh406.iff
seluh407.iff
seluh408.iff
seluh409.iff
seluh410.iff
seluh411.iff
seluh412.iff
seluh413.iff
seluh414.iff
seluh415.iff
seluh416.iff
seluh417.iff
seluh418.iff
seluh421.iff
seluh422.iff
seluh423.iff
seluh424.iff
seluh425.iff
seluh426.iff
seluh427.iff
seluh428.iff
seluh429.iff
seluh430.iff
seluh448.iff
seluh449.iff
seluh450.iff
seluh451.iff
seluh452.iff
seluh800.iff
seluh801.iff
seluh802.iff
seluh803.iff
seluh804.iff
seluh805.iff
seluh806.iff
seluh807.iff
seluh808.iff
seluh809.iff
seluh810.iff
seluh811.iff
seluh812.iff
seluh813.iff
seluh814.iff
seluh815.iff
seluh816.iff
seluh817.iff
seluh818.iff
seluh819.iff
selux007.iff
selux011.iff
selux012.iff
selux013.iff
selux014.iff
selux017.iff
selux018.iff
selux031.iff
selux035.iff
selux037.iff
selux041.iff
selux042.iff
selux043.iff
selux044.iff
selux045.iff
selux046.iff
selux047.iff
selux048.iff
selux049.iff
selux052.iff
selux053.iff
selux054.iff
selux055.iff
selux058.iff
selux066.iff
selux073.iff
selux075.iff
selux076.iff
selux077.iff
selux078.iff
selux080.iff
selux082.iff
selux086.iff
selux087.iff
selux088.iff
selux089.iff
selux091.iff
selux092.iff
selux093.iff
selux095.iff
selux114.iff
selux117.iff
selux119.iff
selux121.iff
selux122.iff
selux123.iff
selux135.iff
selux171.iff
selux183.iff
selux191.iff
selux207.iff
selux208.iff
selux211.iff
selux228.iff
selux231.iff
selux234.iff
selux235.iff
selux236.iff
selux237.iff
selux238.iff
selux241.iff
selux242.iff
selux246.iff
selux252.iff
selux254.iff
selux255.iff
selux256.iff
selux257.iff
selux258.iff
selux261.iff
selux263.iff
selux266.iff
selux278.iff
selux300.iff
selux305.iff
selux307.iff
selux308.iff
selux309.iff
selux312.iff
selux322.iff
selux408.iff
sfx_inside.iff
shoe_101_06.iff
shoe_102_04.iff
shoe_500_00.iff
shrine_trophies.iff
shrine.iff
sideline_items_crowd01.iff
sideline_items_crowd01a.iff
sideline_items_crowd01b.iff
sideline_items_crowd01c.iff
sideline_items_crowd02.iff
sideline_items_crowd03.iff
sideline_items.cdf
sideline_items.iff
statefarm.iff
streetdata.iff
studio_pontiac.iff
studio_preview.iff
studio_sfch2nite.iff
studio_sfsunday.iff
studio.iff
tutorial.iff
ua000.iff
ua001.iff
ua002.iff
ua003.iff
ua004.iff
ua005.iff
ua006.iff
ua007.iff
ua008.iff
ua009.iff
ua010.iff
ua011.iff
ua012.iff
ua013.iff
ua014.iff
ua015.iff
ua016.iff
ua017.iff
ua018.iff
ua019.iff
ua020.iff
ua021.iff
ua022.iff
ua023.iff
ua024.iff
ua025.iff
ua026.iff
ua027.iff
ua028.iff
ua029.iff
ua030.iff
ua031.iff
ua032.iff
ua033.iff
ua034.iff
ua035.iff
ua036.iff
ua037.iff
ua038.iff
ua039.iff
ua040.iff
ua041.iff
ua042.iff
ua043.iff
ua044.iff
ua045.iff
ua046.iff
ua047.iff
ua048.iff
ua049.iff
ua050.iff
ua051.iff
ua052.iff
ua053.iff
ua054.iff
ua055.iff
ua056.iff
ua057.iff
ua058.iff
ua059.iff
ua060.iff
ua061.iff
ua062.iff
ua063.iff
ua064.iff
ua065.iff
ua066.iff
ua067.iff
ua068.iff
ua069.iff
ua070.iff
ua071.iff
ua072.iff
ua073.iff
ua074.iff
ua075.iff
ua076.iff
ua077.iff
ua078.iff
ua079.iff
ua080.iff
ua081.iff
ua082.iff
ua083.iff
ua084.iff
ua085.iff
ua086.iff
ua087.iff
ua088.iff
ua089.iff
ua090.iff
ua091.iff
ua092.iff
ua093.iff
ua094.iff
ua095.iff
ua096.iff
ua097.iff
ua098.iff
ua099.iff
ua100.iff
ua101.iff
ua102.iff
ua103.iff
ua104.iff
ua105.iff
ua106.iff
ua107.iff
ua108.iff
ua109.iff
ua110.iff
ua111.iff
ua112.iff
ua113.iff
ua114.iff
ua115.iff
ua116.iff
ua117.iff
ua118.iff
ua119.iff
ua120.iff
ua121.iff
ua122.iff
ua123.iff
ua124.iff
ua125.iff
ua126.iff
ua127.iff
ua128.iff
ua129.iff
ua130.iff
ua131.iff
ua132.iff
ua133.iff
ua134.iff
ua135.iff
ua136.iff
ua137.iff
ua138.iff
ua139.iff
ua140.iff
ua141.iff
ua142.iff
ua143.iff
ua144.iff
ua145.iff
ua146.iff
ua147.iff
ua148.iff
ua149.iff
ua150.iff
ua151.iff
ua152.iff
ua153.iff
ua154.iff
ua155.iff
ua156.iff
ua157.iff
ua158.iff
ua159.iff
ua160.iff
ua161.iff
ua162.iff
ua163.iff
ua164.iff
ua165.iff
ua166.iff
ua167.iff
ua168.iff
ua169.iff
ua170.iff
ua171.iff
ua172.iff
ua173.iff
ua174.iff
ua175.iff
ua176.iff
ua177.iff
ua178.iff
ua179.iff
ua180.iff
ua181.iff
ua182.iff
ua183.iff
ua184.iff
ua185.iff
ua186.iff
ua187.iff
ua188.iff
ua189.iff
ua190.iff
ua191.iff
ua192.iff
ua193.iff
ua194.iff
ua195.iff
ua196.iff
ua197.iff
ua198.iff
ua199.iff
ua200.iff
ua201.iff
ua202.iff
ua203.iff
ua204.iff
ua205.iff
ua206.iff
ua207.iff
ua208.iff
ua209.iff
ua210.iff
ua211.iff
ua212.iff
ua213.iff
ua214.iff
ua215.iff
ua216.iff
ua217.iff
ua218.iff
ua219.iff
ua220.iff
ua221.iff
ua222.iff
ua223.iff
ua224.iff
ua225.iff
ua226.iff
ua227.iff
ua228.iff
ua229.iff
ua230.iff
ua231.iff
ua232.iff
ua233.iff
ua234.iff
ua235.iff
ua236.iff
ua237.iff
ua238.iff
ua239.iff
ua240.iff
ua241.iff
ua242.iff
ua243.iff
ua244.iff
ua245.iff
ua246.iff
ua247.iff
ua248.iff
ua249.iff
ua250.iff
ua251.iff
ua252.iff
ua253.iff
ua254.iff
ua255.iff
ua257.iff
ua258.iff
ua259.iff
ua260.iff
ua261.iff
ua262.iff
ua263.iff
ua264.iff
ua265.iff
ua266.iff
ua267.iff
ua268.iff
ua269.iff
ua270.iff
ua271.iff
ua272.iff
ua273.iff
ua274.iff
ua275.iff
ua276.iff
ua277.iff
ua278.iff
ua279.iff
ua280.iff
ua281.iff
ua282.iff
ua283.iff
ua284.iff
ua285.iff
ua286.iff
ua287.iff
ua288.iff
ua289.iff
ua290.iff
ua291.iff
ua292.iff
ua293.iff
ua294.iff
ua295.iff
ua296.iff
ua297.iff
ua298.iff
ua299.iff
ua300.iff
ua301.iff
ua302.iff
ua303.iff
ua304.iff
ua305.iff
ua306.iff
ua307.iff
ua308.iff
ua309.iff
ua310.iff
ua311.iff
ua312.iff
ua313.iff
ua314.iff
ua315.iff
ua316.iff
ua317.iff
ua318.iff
ua319.iff
ua320.iff
ua321.iff
ua322.iff
ua323.iff
ua324.iff
ua325.iff
ua326.iff
ua327.iff
ua328.iff
ua329.iff
ua330.iff
ua331.iff
ua332.iff
ua333.iff
ua334.iff
ua335.iff
ua336.iff
ua337.iff
ua338.iff
ua339.iff
ua340.iff
ua341.iff
ua342.iff
ua343.iff
ua344.iff
ua345.iff
ua346.iff
ua347.iff
ua348.iff
ua349.iff
ua350.iff
ua351.iff
ua352.iff
ua353.iff
ua354.iff
ua355.iff
ua356.iff
ua357.iff
ua358.iff
ua359.iff
ua360.iff
ua361.iff
ua362.iff
ua363.iff
ua364.iff
ua365.iff
ua366.iff
ua367.iff
ua368.iff
ua369.iff
ua370.iff
ua371.iff
ua372.iff
ua373.iff
ua374.iff
ua375.iff
ua376.iff
ua377.iff
ua378.iff
ua379.iff
ua380.iff
ua381.iff
ua382.iff
ua383.iff
ua384.iff
ua385.iff
ua386.iff
ua387.iff
ua388.iff
ua389.iff
ua390.iff
ua391.iff
ua392.iff
ua393.iff
ua394.iff
ua395.iff
ua396.iff
ua397.iff
ua398.iff
ua400.iff
ua401.iff
ua403.iff
ua404.iff
ua405.iff
ua406.iff
ua407.iff
ua408.iff
ua409.iff
ua410.iff
ua411.iff
ua412.iff
ua413.iff
ua414.iff
ua415.iff
ua416.iff
ua417.iff
ua418.iff
ua421.iff
ua422.iff
ua423.iff
ua424.iff
ua425.iff
ua426.iff
ua427.iff
ua428.iff
ua429.iff
ua430.iff
ua448.iff
ua449.iff
ua450.iff
ua451.iff
ua452.iff
ua800.iff
ua801.iff
ua802.iff
ua803.iff
ua804.iff
ua805.iff
ua806.iff
ua807.iff
ua808.iff
ua809.iff
ua810.iff
ua811.iff
ua812.iff
ua813.iff
ua814.iff
ua815.iff
ua816.iff
ua817.iff
ua818.iff
ua819.iff
uh000.iff
uh001.iff
uh002.iff
uh003.iff
uh004.iff
uh005.iff
uh006.iff
uh007.iff
uh008.iff
uh009.iff
uh010.iff
uh011.iff
uh012.iff
uh013.iff
uh014.iff
uh015.iff
uh016.iff
uh017.iff
uh018.iff
uh019.iff
uh020.iff
uh021.iff
uh022.iff
uh023.iff
uh024.iff
uh025.iff
uh026.iff
uh027.iff
uh028.iff
uh029.iff
uh030.iff
uh031.iff
uh032.iff
uh033.iff
uh034.iff
uh035.iff
uh036.iff
uh037.iff
uh038.iff
uh039.iff
uh040.iff
uh041.iff
uh042.iff
uh043.iff
uh044.iff
uh045.iff
uh046.iff
uh047.iff
uh048.iff
uh049.iff
uh050.iff
uh051.iff
uh052.iff
uh053.iff
uh054.iff
uh055.iff
uh056.iff
uh057.iff
uh058.iff
uh059.iff
uh060.iff
uh061.iff
uh062.iff
uh063.iff
uh064.iff
uh065.iff
uh066.iff
uh067.iff
uh068.iff
uh069.iff
uh070.iff
uh071.iff
uh072.iff
uh073.iff
uh074.iff
uh075.iff
uh076.iff
uh077.iff
uh078.iff
uh079.iff
uh080.iff
uh081.iff
uh082.iff
uh083.iff
uh084.iff
uh085.iff
uh086.iff
uh087.iff
uh088.iff
uh089.iff
uh090.iff
uh091.iff
uh092.iff
uh093.iff
uh094.iff
uh095.iff
uh096.iff
uh097.iff
uh098.iff
uh099.iff
uh100.iff
uh101.iff
uh102.iff
uh103.iff
uh104.iff
uh105.iff
uh106.iff
uh107.iff
uh108.iff
uh109.iff
uh110.iff
uh111.iff
uh112.iff
uh113.iff
uh114.iff
uh115.iff
uh116.iff
uh117.iff
uh118.iff
uh119.iff
uh120.iff
uh121.iff
uh122.iff
uh123.iff
uh124.iff
uh125.iff
uh126.iff
uh127.iff
uh128.iff
uh129.iff
uh130.iff
uh131.iff
uh132.iff
uh133.iff
uh134.iff
uh135.iff
uh136.iff
uh137.iff
uh138.iff
uh139.iff
uh140.iff
uh141.iff
uh142.iff
uh143.iff
uh144.iff
uh145.iff
uh146.iff
uh147.iff
uh148.iff
uh149.iff
uh150.iff
uh151.iff
uh152.iff
uh153.iff
uh154.iff
uh155.iff
uh156.iff
uh157.iff
uh158.iff
uh159.iff
uh160.iff
uh161.iff
uh162.iff
uh163.iff
uh164.iff
uh165.iff
uh166.iff
uh167.iff
uh168.iff
uh169.iff
uh170.iff
uh171.iff
uh172.iff
uh173.iff
uh174.iff
uh175.iff
uh176.iff
uh177.iff
uh178.iff
uh179.iff
uh180.iff
uh181.iff
uh182.iff
uh183.iff
uh184.iff
uh185.iff
uh186.iff
uh187.iff
uh188.iff
uh189.iff
uh190.iff
uh191.iff
uh192.iff
uh193.iff
uh194.iff
uh195.iff
uh196.iff
uh197.iff
uh198.iff
uh199.iff
uh200.iff
uh201.iff
uh202.iff
uh203.iff
uh204.iff
uh205.iff
uh206.iff
uh207.iff
uh208.iff
uh209.iff
uh210.iff
uh211.iff
uh212.iff
uh213.iff
uh214.iff
uh215.iff
uh216.iff
uh217.iff
uh218.iff
uh219.iff
uh220.iff
uh221.iff
uh222.iff
uh223.iff
uh224.iff
uh225.iff
uh226.iff
uh227.iff
uh228.iff
uh229.iff
uh230.iff
uh231.iff
uh232.iff
uh233.iff
uh234.iff
uh235.iff
uh236.iff
uh237.iff
uh238.iff
uh239.iff
uh240.iff
uh241.iff
uh242.iff
uh243.iff
uh244.iff
uh245.iff
uh246.iff
uh247.iff
uh248.iff
uh249.iff
uh250.iff
uh251.iff
uh252.iff
uh253.iff
uh254.iff
uh255.iff
uh256.iff
uh257.iff
uh258.iff
uh259.iff
uh260.iff
uh261.iff
uh262.iff
uh263.iff
uh264.iff
uh265.iff
uh266.iff
uh267.iff
uh268.iff
uh269.iff
uh270.iff
uh271.iff
uh272.iff
uh273.iff
uh274.iff
uh275.iff
uh276.iff
uh277.iff
uh278.iff
uh279.iff
uh280.iff
uh281.iff
uh282.iff
uh283.iff
uh284.iff
uh285.iff
uh286.iff
uh287.iff
uh288.iff
uh289.iff
uh290.iff
uh291.iff
uh292.iff
uh293.iff
uh294.iff
uh295.iff
uh296.iff
uh297.iff
uh298.iff
uh299.iff
uh300.iff
uh301.iff
uh302.iff
uh303.iff
uh304.iff
uh305.iff
uh306.iff
uh307.iff
uh308.iff
uh309.iff
uh310.iff
uh311.iff
uh312.iff
uh313.iff
uh314.iff
uh315.iff
uh316.iff
uh317.iff
uh318.iff
uh319.iff
uh320.iff
uh321.iff
uh322.iff
uh323.iff
uh324.iff
uh325.iff
uh326.iff
uh327.iff
uh328.iff
uh329.iff
uh330.iff
uh331.iff
uh332.iff
uh333.iff
uh334.iff
uh335.iff
uh336.iff
uh337.iff
uh338.iff
uh339.iff
uh340.iff
uh341.iff
uh342.iff
uh343.iff
uh344.iff
uh345.iff
uh346.iff
uh347.iff
uh348.iff
uh349.iff
uh350.iff
uh351.iff
uh352.iff
uh353.iff
uh354.iff
uh355.iff
uh356.iff
uh357.iff
uh358.iff
uh359.iff
uh360.iff
uh361.iff
uh362.iff
uh363.iff
uh364.iff
uh365.iff
uh366.iff
uh367.iff
uh368.iff
uh369.iff
uh370.iff
uh371.iff
uh372.iff
uh373.iff
uh374.iff
uh375.iff
uh376.iff
uh377.iff
uh378.iff
uh379.iff
uh380.iff
uh381.iff
uh382.iff
uh383.iff
uh384.iff
uh385.iff
uh386.iff
uh387.iff
uh388.iff
uh389.iff
uh390.iff
uh391.iff
uh392.iff
uh393.iff
uh394.iff
uh395.iff
uh396.iff
uh397.iff
uh398.iff
uh400.iff
uh401.iff
uh403.iff
uh404.iff
uh405.iff
uh406.iff
uh407.iff
uh408.iff
uh409.iff
uh410.iff
uh411.iff
uh412.iff
uh413.iff
uh414.iff
uh415.iff
uh416.iff
uh417.iff
uh418.iff
uh421.iff
uh422.iff
uh423.iff
uh424.iff
uh425.iff
uh426.iff
uh427.iff
uh428.iff
uh429.iff
uh430.iff
uh448.iff
uh449.iff
uh450.iff
uh451.iff
uh452.iff
uh800.iff
uh801.iff
uh802.iff
uh803.iff
uh804.iff
uh805.iff
uh806.iff
uh807.iff
uh808.iff
uh809.iff
uh810.iff
uh811.iff
uh812.iff
uh813.iff
uh814.iff
uh815.iff
uh816.iff
uh817.iff
uh818.iff
uh819.iff
ux007.iff
ux011.iff
ux012.iff
ux013.iff
ux014.iff
ux017.iff
ux018.iff
ux031.iff
ux035.iff
ux037.iff
ux041.iff
ux042.iff
ux043.iff
ux044.iff
ux045.iff
ux046.iff
ux047.iff
ux048.iff
ux049.iff
ux052.iff
ux053.iff
ux054.iff
ux055.iff
ux058.iff
ux066.iff
ux073.iff
ux075.iff
ux076.iff
ux077.iff
ux078.iff
ux080.iff
ux082.iff
ux086.iff
ux087.iff
ux088.iff
ux089.iff
ux091.iff
ux092.iff
ux093.iff
ux095.iff
ux114.iff
ux117.iff
ux119.iff
ux121.iff
ux122.iff
ux123.iff
ux135.iff
ux171.iff
ux183.iff
ux191.iff
ux207.iff
ux208.iff
ux211.iff
ux228.iff
ux231.iff
ux234.iff
ux235.iff
ux236.iff
ux237.iff
ux238.iff
ux241.iff
ux242.iff
ux246.iff
ux252.iff
ux254.iff
ux255.iff
ux256.iff
ux257.iff
ux258.iff
ux261.iff
ux263.iff
ux266.iff
ux278.iff
ux300.iff
ux305.iff
ux307.iff
ux308.iff
ux309.iff
ux312.iff
ux322.iff
ux408.iff
weeklyshow.iff
```

---

## Appendix B — Notes for Future AI Agents

When starting a new chat, paste this file first or attach it as the source. Then state exactly which workstream applies. The safest pattern is:

1. Read this file.
2. Inspect current repo files before editing.
3. State which format family is involved.
4. Add or update tests/validators before broad writer changes.
5. Keep raw-preserving output even if conversion/export fails.
6. Mark unknown fields as unknown.
7. Use small known samples before full-game rebuilds.

The most common historical mistake was applying a correct idea from one format family to the wrong family. The biggest example: treating uniform names/numbers as CDF-backed when inventory and format reports indicate they are standard embedded TXTRs.
