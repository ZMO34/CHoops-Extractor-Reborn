"""Application services shared by the native studio and automation."""

from __future__ import annotations

import hashlib
import os
import threading
import uuid
from collections.abc import Callable
from pathlib import Path

from ..archive.manifests import OUTPUT, safe_name, safe_output
from ..archive.usrdir_reader import Archive
from ..core.reports import save_json


class Cancelled(Exception):
    """A cooperative job cancellation; completed exports remain recorded."""


class JobContext:
    def __init__(self, progress: Callable[[int, int, str], None] | None = None):
        self.cancelled = threading.Event()
        self.progress = progress or (lambda current, total, message: None)

    def check(self):
        if self.cancelled.is_set():
            raise Cancelled("Cancelled by user")


def extract(
    archive: Archive, entries: list[dict], output: Path, job: JobContext | None = None
) -> dict:
    """Stream raw extents with collision preflight and per-entry atomic writes."""
    job = job or JobContext()
    out = safe_output(output, [archive.path])
    # Pair known outer IFF/CDF identities; raw data is retained even if decode fails.
    name_index: dict[str, list[dict]] = {}
    for item in archive.entries:
        if item["name"]:
            name_index.setdefault(item["name"].casefold(), []).append(item)
    selected_ids = {e["index"] for e in entries}
    expanded = list(entries)
    for entry in entries:
        name = entry.get("name")
        if name and Path(name).suffix.lower() in (".iff", ".cdf"):
            partner = str(
                Path(name).with_suffix(
                    ".cdf" if name.lower().endswith(".iff") else ".iff"
                )
            )
            matches = name_index.get(partner.casefold(), [])
            if len(matches) == 1 and matches[0]["index"] not in selected_ids:
                expanded.append(matches[0])
                selected_ids.add(matches[0]["index"])
    entries = expanded
    targets = []
    seen = set()
    for entry in entries:
        name = safe_name(entry["name"] or f"hash_{entry['hash']:08x}.bin")
        key = name.casefold()
        if key in seen or (out / name).exists():
            raise ValueError(f"Duplicate or existing extraction target: {name}")
        seen.add(key)
        targets.append((entry, name))
    if not targets:
        raise ValueError("No assets selected")
    if (out / "extraction_manifest.json").exists():
        raise ValueError("Choose a new extraction destination")
    out.mkdir(parents=True, exist_ok=True)
    total = sum(e["size"] for e, _ in targets)
    done = 0
    rows = []
    status = "complete"
    try:
        for entry, name in targets:
            job.check()
            target = out / name
            temporary = out / (".extract_" + uuid.uuid4().hex)
            h = hashlib.sha256()
            try:
                with temporary.open("xb") as stream:
                    for chunk in archive.chunks(entry):
                        job.check()
                        stream.write(chunk)
                        h.update(chunk)
                        done += len(chunk)
                        job.progress(done, total, name)
                # Exclusive target creation avoids overwriting a concurrent export.
                os.link(temporary, target)
                temporary.unlink()
            finally:
                if temporary.exists():
                    temporary.unlink()
            rows.append({**entry, "output": name, "sha256": h.hexdigest()})
    except Cancelled:
        status = "cancelled"
    except KeyboardInterrupt:
        status = "cancelled"
        raise
    except Exception:
        status = "failed"
        raise
    finally:
        result = {
            "schema": 1,
            "status": status,
            "requested": len(targets),
            "completed": len(rows),
            "bytes_written": sum(row["size"] for row in rows),
            "entries": rows,
        }
        save_json(out / "extraction_manifest.json", result, [archive.path])
    return result


def materialize(archive: Archive, entry: dict, directory: Path | None = None) -> Path:
    """Create a private scratch copy for parsers requiring a filesystem input."""
    directory = directory or OUTPUT / "temp" / ("inspect_" + uuid.uuid4().hex)
    selected = [entry]
    if entry["name"] and entry["name"].lower().endswith(".iff"):
        companion = entry["name"][:-4] + ".cdf"
        selected += [e for e in archive.entries if e["name"] == companion]
    extract(archive, selected, directory)
    name = safe_name(entry["name"] or f"hash_{entry['hash']:08x}.bin")
    return directory / name


def inspect_asset(path: Path) -> dict:
    """Return nested records and texture candidates without guessing writers."""
    from ..formats.cdf_backed_iff import CDFPair
    from ..formats.standard_iff import StandardIFF
    from ..texture_tools.pipeline import Container

    if path.stat().st_size > 128 * 1024 * 1024:
        with path.open("rb") as stream:
            header = stream.read(4096)
        return {
            "path": path,
            "records": [],
            "textures": [],
            "hex": header,
            "warning": "Interactive decode limit is 128 MiB; streamed raw extraction remains available.",
        }
    raw = path.read_bytes()
    records = []
    cdf = path.with_suffix(".cdf")
    if raw[:4] == bytes.fromhex("ff3bef94"):
        records = StandardIFF(raw).records
    elif raw[:4] == bytes.fromhex("f0985030") and cdf.exists():
        records = CDFPair(raw, cdf.read_bytes()).records
    assets = []
    warning = ""
    try:
        container = Container(path, cdf if cdf.exists() else None)
        for asset in container.assets:
            try:
                info = asset.texture.info() if asset.texture else {}
            except ValueError as error:
                info = {"reason": str(error)}
            assets.append(
                {
                    "name": asset.name,
                    "kind": asset.kind,
                    "metadata": info,
                    "warnings": asset.warnings,
                    "editable": asset.texture is not None,
                }
            )
    except ValueError as error:
        warning = str(error)
    return {
        "path": path,
        "records": records,
        "textures": assets,
        "hex": raw[:4096],
        "warning": warning,
    }


def stage_folder(source: Path, folder: Path, mod: Path) -> dict:
    """Match extracted filenames to TOC identities, then preflight paired edits."""
    import shutil

    from ..archive.build_copy import preflight
    from ..archive.importer import stage

    archive = Archive(source)
    folder = folder.resolve()
    mod = safe_output(mod, [source, folder])
    if mod.exists():
        raise ValueError("Choose a new mod directory")
    files = [
        p for p in folder.iterdir() if p.suffix.lower() in (".iff", ".cdf", ".bin")
    ]
    if not files:
        raise ValueError("Folder contains no IFF/CDF/BIN replacements")
    matches = []
    for file in files:
        if file.is_symlink() or (hasattr(file, "is_junction") and file.is_junction()):
            raise ValueError("Linked replacements are blocked")
        candidates = [
            e
            for e in archive.entries
            if e["name"] and e["name"].casefold() == file.name.casefold()
        ]
        if len(candidates) != 1:
            raise ValueError(f"Unknown or ambiguous archive filename: {file.name}")
        matches.append((file, candidates[0]))
    work = mod.parent / (".mod_" + uuid.uuid4().hex)
    try:
        for file, entry in matches:
            stage(work, file, entry["name"])
        _, patches = preflight(source, work)
        # Store source preconditions beside the established override format.
        save_json(
            work / "source_preconditions.json",
            {
                "schema": 1,
                "entries": [
                    {
                        "index": e["index"],
                        "hash": e["hash"],
                        "sha256": hashlib.sha256(archive.read(e)).hexdigest(),
                    }
                    for _, e in matches
                ],
            },
        )
        work.rename(mod)
        return {"staged": len(patches), "mod": str(mod)}
    except Exception:
        if work.exists():
            shutil.rmtree(work)
        raise


def decode_texture_preview(source: Path, selector: str):
    from ..texture_tools.pipeline import Container
    cdf = source.with_suffix('.cdf')
    asset = Container(source, cdf if cdf.exists() else None).select(selector)
    return decode_preview_asset(asset)


def decode_preview_asset(asset, max_size=2048):
    import shutil
    from PIL import Image
    from ..texture_tools.dds import linear_l8, compressed_preview
    from ..texture_tools.external_converters import convert
    info = asset.texture.info()
    work = OUTPUT / 'temp' / ('preview_' + uuid.uuid4().hex)
    work.mkdir(parents=True)
    try:
        dds = work / 'texture.dds'
        if info['format'] in ('DXT1','DXT3','DXT5') and (info['width'] & (info['width']-1) or info['height'] & (info['height']-1)):
            dds.write_bytes(compressed_preview(info['width'],info['height'],info['format'],asset.texture.image()))
        elif info['format'] == 'L8' and info['linear']:
            dds.write_bytes(linear_l8(info['width'], info['height'], info['mip_count'], asset.texture.image()))
        else:
            gtf = work / 'texture.gtf'
            gtf.write_bytes(asset.texture.gtf())
            convert('gtf2dds', gtf, dds)
        with Image.open(dds) as image:
            image.load()
            image.thumbnail((max_size, max_size))
            image = image.convert('RGBA')
            return image.size, image.tobytes()
    finally:
        shutil.rmtree(work)


def inspect_scene_preview(source: Path, record_index: int, include_all=False, job=None):
    from ..texture_tools.pipeline import Container
    from ..formats.standard_iff_writer import record_blocks
    from ..formats.compression import decode
    from ..formats.tool_wrapper import unwrap
    from ..formats.scne import preview_meshes
    job = job or JobContext()
    if source.stat().st_size > 128 * 1024 * 1024:
        raise ValueError('Interactive scene decode limit is 128 MiB')
    cdf = source.with_suffix('.cdf')
    container = Container(source, cdf if cdf.exists() else None)
    records = container.iff.records if container.iff else container.pair.records if container.pair else []
    scenes = [r for r in records if r['type'] == 'SCNE' and (include_all or r['index'] == record_index)]
    if not scenes and container.wrapper_type == 2:
        scenes = [{'index': 0, 'name': source.stem}]
    if not scenes:
        raise ValueError('Select a SCNE record in an IFF or open a SCNE wrapper')
    result = {'meshes': [], 'warnings': [], 'textures': [], 'images': {}}
    for rec in scenes:
        job.check()
        if container.iff:
            blocks = [b[3] for b in record_blocks(container.iff, rec)]
        elif container.pair:
            blocks = [decode(container.pair.cdf[rec[k+'_offset']:rec[k+'_offset']+rec[k+'_length']]) for k in ('header','payload')]
        else:
            blocks = unwrap(container.raw)[1]
        scene = preview_meshes(blocks)
        assets = [a for a in container.assets if (a.record_index == rec['index'] or container.wrapper_type == 2) and a.texture]
        by_index = {a.package_index: a.name for a in assets}
        result['textures'].extend(a.name for a in assets)
        for mesh in scene['meshes']:
            mesh['court_surface'] = rec['name'].lower() == 'floor'
            mesh['name'] = rec['name'] + '/' + mesh['name']
            for batch in mesh['batches']:
                batch['texture'] = by_index.get(batch['texture_index'])
                # This runtime-injected court pass repeats the wood geometry;
                # a neutral diffuse fallback would cover every court decal.
                if mesh['court_surface'] and batch.get('material_hash') == 0xe16ecb73 and batch['texture'] is None:
                    batch['omit_preview'] = True
                    scene['warnings'].append('Court runtime-only material 0xe16ecb73 omitted from color preview')
        result['meshes'].extend(scene['meshes'])
        result['warnings'].extend(scene['warnings'])
    needed = {batch['texture'] for mesh in result['meshes'] for batch in mesh['batches'] if batch['texture']}
    assets = {a.name:a for a in container.assets if a.texture}
    decoded_bytes = 0
    for i, name in enumerate(sorted(needed)):
        job.check()
        job.progress(i, len(needed), 'Loading material texture ' + name)
        try:
            image = decode_preview_asset(assets[name], max_size=1024)
            decoded_bytes += len(image[1])
            if decoded_bytes > 128 * 1024 * 1024:
                result['warnings'].append('Scene texture memory limit reached')
                break
            result['images'][name] = image
        except ValueError as error:
            result['warnings'].append(name + ': ' + str(error))
    job.progress(len(needed), len(needed), 'Scene loaded')
    return result
