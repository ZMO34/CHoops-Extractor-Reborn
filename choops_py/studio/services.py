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
            matches = [
                e
                for e in archive.entries
                if e["name"] and e["name"].casefold() == partner.casefold()
            ]
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
