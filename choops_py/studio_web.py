"""Three-tab localhost dashboard for native Python rip/build/roster workflows."""
import json, logging, subprocess, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .archive.manifests import OUTPUT, safe_output
from .roster.editor_model import EditorModel
from .roster.workflow import save_model
from .studio_fields import apply_studio_field, team_colors

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
LOGGER = logging.getLogger("choops.studio")
LOCK = threading.RLock()
STATE = {"roster": None, "jobs": {}, "next": 0}


def job_args(action, params):
    src_text = str(params.get("source", "")).strip()
    dst_text = str(params.get("target", "")).strip()
    if not src_text or not dst_text:
        raise ValueError("Source and output folders are required")
    src = Path(src_text).expanduser().resolve()
    dst = safe_output(dst_text, [src])
    if not src.is_dir() or src == dst:
        raise ValueError("Source directory does not exist or overlaps output")
    command = [sys.executable, "-u", "-m", "choops_py.cli"]
    if action == "rip":
        usrdir = src / "PS3_GAME" / "USRDIR" if (src / "PS3_GAME" / "USRDIR" / "0A").is_file() else src
        if not (usrdir / "0A").is_file():
            raise ValueError("Select a PS3 USRDIR folder containing part 0A, or its JB root")
        if dst.exists() and any(dst.iterdir()):
            raise ValueError("Choose an empty rip destination")
        return command + ["rip", str(usrdir), str(dst), "--build-cache", "--iff-only"]
    if action == "build":
        mods_text = str(params.get("mods", "")).strip()
        if not mods_text:
            raise ValueError("Select the staged mods folder")
        mods = Path(mods_text).expanduser().resolve()
        if not mods.is_dir():
            raise ValueError("Staged mods folder does not exist")
        builds = (OUTPUT / "builds").resolve()
        if dst == builds or not dst.is_relative_to(builds):
            raise ValueError("Build destination must be output/builds/<name>")
        command += ["build-copy", str(src), str(mods), str(dst)]
        if params.get("overwrite") is True:
            command.append("--overwrite")
        return command
    raise ValueError("Only rip and build are accepted job actions")


def run_job(action, params):
    argv = job_args(action, params)
    with LOCK:
        STATE["next"] += 1
        ident = STATE["next"]
        job = {"id": ident, "action": action, "status": "queued",
               "exit_code": None, "command": argv[3:], "log": []}
        STATE["jobs"][ident] = job
    def work():
        try:
            job["status"] = "running"
            with subprocess.Popen(argv, cwd=str(PROJECT), stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                  errors="replace", bufsize=1) as process:
                for line in process.stdout:
                    with LOCK:
                        job["log"].append(line.rstrip())
                        if len(job["log"]) > 800:
                            del job["log"][:-800]
                job["exit_code"] = process.wait()
                job["status"] = "completed" if job["exit_code"] == 0 else "failed"
        except Exception as error:
            with LOCK:
                job["status"] = "failed"
                job["log"].append(repr(error))
            LOGGER.exception("Background job failed")
    threading.Thread(target=work, daemon=True, name=f"choops-{action}-{ident}").start()
    return dict(job)


def summary(model):
    return {"source": model.source.source_path, "kind": model.source.kind,
            "payload_size": len(model.data), "queued": len(model.edits),
            "teams": [{"index": t["index"], "name": t["school_name"], "asset": t["asset_id"]}
                      for t in model.rows["teams"]]}


class Handler(BaseHTTPRequestHandler):
    server_version = "CHoopsNativeStudio/1.0"

    def log_message(self, fmt, *args):
        LOGGER.debug(fmt, *args)

    def respond(self, status, value):
        body = json.dumps(value, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def roster(self):
        if STATE["roster"] is None:
            raise ValueError("Open a roster file first")
        return STATE["roster"]

    def do_GET(self):
        path = urlparse(self.path)
        try:
            if path.path == "/":
                body = (ROOT / "studio.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)
            elif path.path == "/api/status":
                with LOCK:
                    self.respond(200, {"native_python": True, "output": str(OUTPUT),
                                       "roster": summary(STATE["roster"]) if STATE["roster"] else None,
                                       "jobs": [dict(j) for j in STATE["jobs"].values()]})
            elif path.path == "/api/team":
                with LOCK:
                    m = self.roster()
                    index = int(parse_qs(path.query).get("index", ["0"])[0])
                    m.row_offset("teams", index)
                    self.respond(200, {**m.rows["teams"][index], "colors": team_colors(m, index)})
            elif path.path == "/api/player":
                with LOCK:
                    m = self.roster()
                    index = int(parse_qs(path.query).get("index", ["0"])[0])
                    m.row_offset("players", index)
                    self.respond(200, m.rows["players"][index])
            else:
                self.respond(404, {"error": "Not found"})
        except (ValueError, KeyError, IndexError) as error:
            self.respond(400, {"error": str(error)})
        except Exception as error:
            LOGGER.exception("GET failure")
            self.respond(500, {"error": str(error)})

    def do_POST(self):
        origin = self.headers.get("Origin")
        allowed = f"http://127.0.0.1:{self.server.server_port}"
        if origin and origin != allowed:
            return self.respond(403, {"error": "Cross-origin requests blocked"})
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return self.respond(415, {"error": "JSON requests only"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 <= length <= 1_000_000:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(length) or "{}")
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")
            path = urlparse(self.path).path
            if path == "/api/open":
                value = str(data.get("path", "")).strip()
                if not value or not Path(value).is_file():
                    raise ValueError("Select an existing roster file")
                model = EditorModel.open(value)
                if not model.validate()["valid"]:
                    raise ValueError("Roster references invalid; unsafe to edit")
                with LOCK:
                    if STATE["roster"] and STATE["roster"].edits and not data.get("discard"):
                        raise ValueError("Save, revert, or explicitly discard unsaved edits")
                    STATE["roster"] = model
                    self.respond(200, summary(model))
            elif path == "/api/edit":
                with LOCK:
                    m = self.roster()
                    table, field, index = data["table"], data["field"], int(data["index"])
                    if table == "teams" and (field.startswith("color_") or field in (
                        "short_name", "abbreviation", "school_name", "mascot_plural", "mascot_name"
                    )):
                        apply_studio_field(m, index, field, data.get("value"), bool(data.get("research_ack")))
                    else:
                        m.edit(table, index, field, data.get("value"), data.get("slot"))
                    self.respond(200, {"queued": len(m.edits)})
            elif path == "/api/save":
                with LOCK:
                    m = self.roster()
                    destination = str(data.get("path", "")).strip()
                    if not destination:
                        raise ValueError("Select a copy destination")
                    result = save_model(m, destination)
                    self.respond(200, {"saved": str(Path(destination).resolve()), "report": result})
            elif path == "/api/undo":
                with LOCK:
                    m = self.roster()
                    m.undo()
                    self.respond(200, {"queued": len(m.edits)})
            elif path == "/api/revert":
                with LOCK:
                    m = self.roster()
                    m.revert()
                    self.respond(200, {"queued": 0})
            elif path == "/api/job":
                self.respond(200, run_job(data.get("action"), data))
            elif path == "/api/browse":
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                try:
                    chosen = filedialog.askdirectory() if data.get("folder") else filedialog.askopenfilename()
                finally:
                    root.destroy()
                self.respond(200, {"path": chosen})
            else:
                self.respond(404, {"error": "Not found"})
        except (ValueError, KeyError, IndexError, OSError) as error:
            self.respond(400, {"error": str(error)})
        except Exception as error:
            LOGGER.exception("POST failure")
            self.respond(500, {"error": str(error)})


def launch(port=8788, browser=True):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{server.server_port}"
    print("CHoops Python Studio: " + url, flush=True)
    if browser:
        threading.Timer(.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    p = argparse.ArgumentParser(description="Three-tab College Hoops native Python studio")
    p.add_argument("--port", type=int, default=8788)
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()
    launch(args.port, not args.no_browser)


if __name__ == "__main__":
    main()
