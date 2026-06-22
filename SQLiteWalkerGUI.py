import csv
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile  # ZIP File support
import base64
import platform as _platform_mod
import tempfile
import tarfile  # TAR File Support
import re

VERSION = "0.6.0"

ASCII_BANNER = (
    "  SQLiteWalker  v" + VERSION + "\n"
    "  https://github.com/stark4n6/SQLiteWalker\n"
    "  @KevinPagano3 | @stark4n6\n"
)

# ---------------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------------

_SYS = _platform_mod.system()  # "Windows", "Darwin", or "Linux"

def _is_windows(): return _SYS == "Windows"
def _is_mac():     return _SYS == "Darwin"
def _is_linux():   return _SYS == "Linux"

# Font families per OS - Segoe/Courier don't exist on macOS or Linux
if _is_windows():
    _SANS, _MONO = "Segoe UI",    "Courier New"
elif _is_mac():
    _SANS, _MONO = "SF Pro Text", "Menlo"       # SF Pro falls back to Helvetica Neue
else:
    _SANS, _MONO = "DejaVu Sans", "DejaVu Sans Mono"

MONO    = (_MONO,  9)
SANS_SM = (_SANS,  9)
SANS_MD = (_SANS, 10)
HEADER  = (_MONO, 14, "bold")

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

BG         = "#1a1d23"
BG_PANEL   = "#21252e"
BG_INPUT   = "#161920"
ACCENT     = "#00d4aa"
ACCENT_DIM = "#007a63"
FG         = "#d0d6e0"
FG_DIM     = "#6b7280"
RED        = "#f87171"
YELLOW     = "#fbbf24"

# ---------------------------------------------------------------------------
# Embedded icon - 32x32 "SW" PNG + ICO, no external files needed
# ---------------------------------------------------------------------------

_ICON_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAC70lEQVR4nM2XTUgUYRjHfzPOzLru"
    "ru4mfh78oA5+XbqI2KXoEGL0QWCXIIIiQokOHRI6VAR18GSHDhUEWZBR0CkijIiITlGQeihl19QN"
    "dW21VdfZ3ZkOs6677exX7KrPZWffeeb9/57/O8z7vLDNIeT8xLdhPe39tp6c5sw+OZPwf4JkTvpH"
    "uLarP2367KtbOYGkB4gTzyScFiQNRGqAqHiuwilBUkCIhRRPmCPFO5QMkEfxbCASAQogngnCfAm2"
    "MDYBClj9Rpi5IKVKjlS5WDrXjdrWgGa3IgZViub9uG4MIXl9LJ85RKBnPyUjn3EOPANgqe8oK90d"
    "yJNeKnoHAVjtasd/8TiWr5OUX7mXpCPGE8VXv3j1FMHOFnbdHKLmxDXK+x8gTXjRLTIAyqgHALWl"
    "PvaM2mxchxqr0UssxlirMaaMuU1dMH0HtFIboT21COEI8qQXYT2E/H0a18AwsvtXdEIP6DrhmnI0"
    "lwPdaiHUWI00NQeCgNpUlwCojHlMnTYFENQQaBq6LDF39xJL5w8TbG9CVzZXTAysIf2cj1WpNteB"
    "IGB//j4mrLkchGvKQdeRx6dyAAiqOJ68BSBS6WTl2D4Wr59m7v5lwg1VsbyNqtSW+lilxZ/GkWYW"
    "jLGo/ZJnDnElmD0AgOPxCBV9d7A/fYc86TVgKsr4c/LAJsCoOwFAmp5HXF5FGXWjNtWx3tYIgCW6"
    "/jkBAMgTs5Q+fE1F7yD2Fx8A0K2WJAdCu2tRm+pi/5VRN7pVYe3gXmOeMXP7UwJotmJ8t88S7GhG"
    "c9nRbMVEKp1GNV9+xPKkWR/i7wC6VIRuVeIAjF/Nbk0ANQvT74AQikAozNKFI2hlNhAEiub9OB69"
    "wfbyY0KuMu4h2NkaFTIqlWYWEP0BNKcd0R9A8vpSAmxukVvwJYTk7XkH7QVRoqSWKo9h1pzsIAeg"
    "oC6kas2SHSgARLq+0HwJ8giRqSndwW25CUQ2IPk9mKQByRh5O5rlCpLj4XTb4y/cQz1QNZiA/wAA"
    "AABJRU5ErkJggg=="
)

_ICON_ICO_B64 = (
    "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"
)


def _set_window_icon(root):
    # Windows needs a real .ico file on disk; write to temp and clean up immediately
    # macOS/Linux accept a PhotoImage via iconphoto()
    try:
        if _is_windows():
            tmp = tempfile.NamedTemporaryFile(suffix=".ico", delete=False)
            tmp.write(base64.b64decode(_ICON_ICO_B64))
            tmp.close()
            root.iconbitmap(tmp.name)
            os.unlink(tmp.name)
        else:
            img = tk.PhotoImage(data=_ICON_PNG_B64)
            root.iconphoto(True, img)
            root._icon_ref = img  # keep ref so GC doesn't collect it
    except Exception:
        pass  # icon is cosmetic - never crash over it


def _open_folder(path):
    # Each OS has its own "open folder" verb
    try:
        if _is_windows():
            os.startfile(path)
        elif _is_mac():
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

# Windows long-path prefix: paths >260 chars need the \\?\ URI escape
def open_sqlite_db_readonly(path):
    if _is_windows():
        if path.startswith("\\\\?\\UNC\\"):
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith("\\\\?\\"):
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith("\\\\"):
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)

WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def sanitize_archive_member_name(member_name):
    member_name = member_name.replace("\\", "/")

    if member_name.startswith("/") or re.match(r"^[A-Za-z]:", member_name):
        raise RuntimeError(
            f"Unsafe absolute archive path blocked: {member_name}"
        )

    safe_parts = []
    for part in member_name.split("/"):
        if part in ("", ".", ".."):
            raise RuntimeError(
                f"Unsafe archive path component blocked: {member_name}"
            )

        safe_part = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", part)
        safe_part = safe_part.rstrip(" .")

        if not safe_part:
            safe_part = "_"

        stem = safe_part.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_NAMES:
            safe_part = f"_{safe_part}"

        safe_parts.append(safe_part)

    return os.path.join(*safe_parts)


def unique_dest_path(dest_path):
    if not os.path.exists(dest_path):
        return dest_path

    folder, filename = os.path.split(dest_path)
    stem, ext = os.path.splitext(filename)

    for suffix_num in range(1, 1000):
        candidate = os.path.join(folder, f"{stem}-{suffix_num:03d}{ext}")
        if not os.path.exists(candidate):
            return candidate

    raise RuntimeError(
        f"Could not create a unique output path for {filename}"
    )


def safe_archive_dest_path(member_name, destination):
    dest_root = os.path.abspath(destination)
    safe_member_name = sanitize_archive_member_name(member_name)
    dest_path = os.path.abspath(os.path.join(dest_root, safe_member_name))

    try:
        common_path = os.path.commonpath([dest_root, dest_path])
    except ValueError:
        common_path = ""

    if common_path != dest_root:
        raise RuntimeError(
            f"Unsafe archive path blocked: {member_name}"
        )

    return unique_dest_path(dest_path)


def safe_tar_write_file(member, source, destination, initial_data=b""):
    if member.islnk() or member.issym():
        raise RuntimeError(
            f"Unsafe TAR link blocked: {member.name}"
        )

    dest_path = safe_archive_dest_path(member.name, destination)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as out:
        if initial_data:
            out.write(initial_data)
        shutil.copyfileobj(source, out)

    return dest_path


def safe_zip_extract(zip_archive, member, destination):
    dest_path = safe_archive_dest_path(member.filename, destination)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with zip_archive.open(member) as source, open(dest_path, "wb") as out:
        shutil.copyfileobj(source, out)

    return dest_path


def create_output_folder(output_path, base, splitter):
    output_ts = time.strftime("%Y%m%d-%H%M%S")

    for suffix_num in range(1000):
        suffix = "" if suffix_num == 0 else f"-{suffix_num:03d}"
        out_folder = output_path + base + output_ts + suffix

        try:
            os.makedirs(out_folder + splitter + "db_out")
            return out_folder
        except FileExistsError:
            continue

    raise RuntimeError(
        f"Could not create a unique output folder for {base}{output_ts}"
    )

# ---------------------------------------------------------------------------
# Core scan - runs entirely in a worker thread, never touches tkinter directly
# ---------------------------------------------------------------------------

def run_scan(input_path, output_path, quiet_mode, log_cb, progress_cb, done_cb):
    base          = "SQLiteWalker_Out_"
    data_list     = []
    error_list    = []
    data_headers  = ("File Name", "Export Path", "Tables")
    error_headers = ("File Name", "Export Path", "Error")
    count = error_count = wal_count = shm_count = 0
    splitter = "\\" if _is_windows() else "/"

    start_time = time.time()

    # Prefix Windows paths to handle >260-char paths
    if _is_windows():
        if len(input_path) > 1 and input_path[1] == ":":
            input_path  = "\\\\?\\" + input_path.replace("/", "\\")
        if len(output_path) > 1 and output_path[1] == ":":
            output_path = "\\\\?\\" + output_path.replace("/", "\\")
        if not output_path.endswith("\\"):
            output_path += "\\"

    out_folder = create_output_folder(output_path, base, splitter)

    _, basename = os.path.split(input_path)
    basename_lower = basename.lower()

    if os.path.isfile(input_path):
        if basename_lower.endswith(".zip"):
            archive_type = "zip"

        elif basename_lower.endswith((".tar", ".tar.gz", ".tgz")):
            archive_type = "tar"

        else:
            log_cb("Input file is not a supported archive (.zip / .tar / .tar.gz / .tgz). Aborting.\n", "error")
            done_cb(0, 0, 0, 0, 0, out_folder)
            return

        log_cb(f"Opening {archive_type.upper()}: {input_path}\n", "info")
        if archive_type == "zip":
            archive = zipfile.ZipFile(input_path, "r")
            files = archive.infolist()
            total = len(files)

        else:
            archive = tarfile.open(input_path, "r|*")
            files = archive
            total = 0

        for idx, entry in enumerate(files, 1):
            progress_cb(idx, total)
            file = entry.filename if archive_type == "zip" else entry.name
            file_name = file.rsplit("/", 1)

            if file.endswith(("-shm", "-wal")):
                try:
                    if archive_type == "zip":
                        if entry.is_dir():
                            continue
                        new_path = safe_zip_extract(
                            archive,
                            entry,
                            out_folder + splitter + "db_out"
                        )
                    else:
                        if not entry.isfile():
                            continue

                        f = archive.extractfile(entry)

                        if f is None:
                            continue

                        with f:
                            new_path = safe_tar_write_file(
                                entry,
                                f,
                                out_folder + splitter + "db_out"
                            )

                except RuntimeError as e:
                    log_cb(f"  BLOCKED ARCHIVE ENTRY: {e}\n", "error")
                    continue

                if file.startswith("/"):
                    file = file[1:]
                if _is_windows():
                    new_path = new_path.replace("/", "\\")
                if file.endswith("-shm"):
                    shm_count += 1
                    log_cb(f"  SHM {shm_count}: {file}\n", "shm")
                else:
                    wal_count += 1
                    log_cb(f"  WAL {wal_count}: {file}\n", "wal")
                dest = new_path[4:] if _is_windows() else new_path
                data_list.append((file_name[-1], dest, ""))

            else:
                db = None
                new_path = None

                if archive_type == "zip":
                    if entry.is_dir():
                        continue

                    with archive.open(entry) as f:
                        header = f.read(100)

                    # SQLite magic bytes: "SQLite format 3\x00"
                    if not header.startswith(b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00"):
                        continue

                    try:
                        new_path = safe_zip_extract(
                            archive,
                            entry,
                            out_folder + splitter + "db_out"
                        )

                    except RuntimeError as e:
                        log_cb(f"  BLOCKED ZIP ENTRY: {e}\n", "error")
                        continue

                else:
                    if not entry.isfile():
                        continue

                    f = archive.extractfile(entry)

                    if f is None:
                        continue

                    with f:
                        header = f.read(100)

                        # SQLite magic bytes: "SQLite format 3\x00"
                        if not header.startswith(b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00"):
                            continue

                        try:
                            new_path = safe_tar_write_file(
                                entry,
                                f,
                                out_folder + splitter + "db_out",
                                header
                            )

                        except RuntimeError as e:
                            log_cb(f"  BLOCKED TAR ENTRY: {e}\n", "error")
                            continue

                try:
                    if file.startswith("/"):
                        file = file[1:]
                    if _is_windows():
                        new_path = new_path.replace("/", "\\")
                    db = open_sqlite_db_readonly(new_path)
                    cursor = db.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables_list = [r[0] for r in cursor.fetchall()]
                    dest = new_path[4:] if _is_windows() else new_path
                    data_list.append((file_name[-1], dest, tables_list))
                    count += 1
                    log_cb(f"  DB {count}: {file}  [{len(tables_list)} tables]\n", "db")
                except sqlite3.Error as e:
                    log_cb(f"  ERROR: {file} - {e}\n", "error")
                    dest = new_path[4:] if _is_windows() else new_path
                    error_list.append((file_name[-1], dest, e))
                    error_count += 1
                finally:
                    try: db.close()
                    except Exception: pass

        archive.close()

    elif os.path.isdir(input_path):
        log_cb(f"Walking folder: {input_path}\n", "info")
        # Collect all paths up front so we have a real total for the progress bar
        all_files = [(r, fn) for r, _, fns in os.walk(input_path) for fn in fns]
        total = max(len(all_files), 1)

        for idx, (root, file) in enumerate(all_files, 1):
            progress_cb(idx, total)
            src = os.path.join(root, file)

            if file.endswith(("-shm", "-wal")):
                rel_path = os.path.relpath(root, input_path)
                if rel_path == ".":
                    dest_dir = out_folder
                else:
                    dest_dir = os.path.join(out_folder, rel_path)
                
                dest_file = os.path.join(dest_dir, file)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src, dest_file)
                if file.endswith("-shm"):
                    shm_count += 1
                    log_cb(f"  SHM {shm_count}: {file}\n", "shm")
                else:
                    wal_count += 1
                    log_cb(f"  WAL {wal_count}: {file}\n", "wal")
                data_list.append((file, dest_file, ""))
                continue

            if not os.path.isfile(src) or os.path.getsize(src) <= 100:
                continue
            try:
                with open(src, "r", encoding="ISO-8859-1") as f:
                    hdr = f.read(100)
            except Exception:
                continue
            if not hdr.startswith("SQLite format 3"):
                continue

            db = None
            try:
                db = open_sqlite_db_readonly(src)
                cursor = db.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables_list = [r[0] for r in cursor.fetchall()]

                rel_path = os.path.relpath(root, input_path)
                if rel_path == ".":
                    dest_dir = out_folder
                else:
                    dest_dir = os.path.join(out_folder, rel_path)
                dest_file = os.path.join(dest_dir, file)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src, dest_file)

                data_list.append((file, dest_file, tables_list))
                count += 1
                log_cb(f"  DB {count}: {file}  [{len(tables_list)} tables]\n", "db")
            except sqlite3.Error as e:
                log_cb(f"  ERROR: {file} - {e}\n", "error")
                error_list.append((file, src, e))
                error_count += 1
            finally:
                try:
                    if db: db.close()
                except Exception: pass

    else:
        log_cb("Input path is not a file or folder. Aborting.\n", "error")
        done_cb(0, 0, 0, 0, 0, out_folder)
        return

    # Write results TSV; errors get a separate file only when there are any
    tsv_path = out_folder + splitter + "db_list.tsv"
    with open(tsv_path, "w", newline="") as f_out:
        w = csv.writer(f_out, delimiter="\t")
        w.writerow(data_headers)
        for row in data_list:
            w.writerow(row)

    if error_count > 0:
        err_path = out_folder + splitter + "error_list.tsv"
        with open(err_path, "w", newline="") as f_out:
            w = csv.writer(f_out, delimiter="\t")
            w.writerow(error_headers)
            for row in error_list:
                w.writerow(row)

    elapsed = round(time.time() - start_time, 2)
    done_cb(count, shm_count, wal_count, error_count, elapsed, out_folder)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class SQLiteWalkerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"SQLiteWalker  v{VERSION}")
        self.configure(bg=BG)
        self.minsize(780, 580)
        self.resizable(True, True)

        _set_window_icon(self)

        self._scanning    = False
        self._last_output = None  # set after each successful scan

        self._build_ui()

        self._log(ASCII_BANNER, "banner")
        self._log(f"  Platform : {_SYS}\n", "info")
        self._log(f"  Python   : {sys.version.split()[0]}\n\n", "info")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_body()
        self._build_statusbar()

    def _build_topbar(self):
        bar = tk.Frame(self, bg=BG_PANEL, pady=10, padx=18)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)

        tk.Label(bar, text="SQLiteWalker", font=HEADER,
                 bg=BG_PANEL, fg=ACCENT).grid(row=0, column=0, sticky="w")
        tk.Label(bar, text=f"v{VERSION}  ",
                 font=SANS_SM, bg=BG_PANEL, fg=FG_DIM).grid(row=0, column=1, sticky="w", padx=(10, 0))
        tk.Button(bar, text="About", font=SANS_SM,
                  bg=BG_PANEL, fg=FG_DIM,
                  activebackground=BG_PANEL, activeforeground=ACCENT,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._show_about).grid(row=0, column=2, sticky="e")

    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)  # row 4 = log panel, stretches with window

        # Source type: radio pair avoids the old "are you picking a zip?" messagebox
        src_row = tk.Frame(body, bg=BG)
        src_row.grid(row=0, column=0, sticky="w", pady=(0, 4))
        tk.Label(src_row, text="Source type", font=SANS_MD,
                 bg=BG, fg=FG, width=12, anchor="w").pack(side="left")
        self.src_type = tk.StringVar(value="folder")
        for val, lbl in [
            ("folder", "Folder"),
            ("archive", "Archive (.zip / .tar / .tar.gz / .tgz)"),
        ]:
            tk.Radiobutton(src_row, text=lbl,
                        variable=self.src_type,
                        value=val,
                        font=SANS_SM,
                        bg=BG,
                        fg=FG,
                        selectcolor=BG_INPUT,
                        activebackground=BG,
                        activeforeground=ACCENT,
                        relief="flat",
                        bd=0,
                        command=self._on_src_type_change).pack(
                            side="left", padx=(0, 14))

        self._build_path_row(body, 1, "Source",        "input_path",  self._browse_source, "Path to scan")
        self._build_path_row(body, 2, "Output Folder", "output_path", self._browse_output, "Folder where results will be saved")

        # Options row - quiet mode on the left, action buttons on the right
        opts = tk.Frame(body, bg=BG)
        opts.grid(row=3, column=0, sticky="ew", pady=(4, 10))

        self.quiet_var = tk.BooleanVar(value=True)  # always quiet; only hits are logged

        # "Open Output" is disabled until at least one scan completes
        self.open_btn = tk.Button(opts, text="Open Output",
                                  font=SANS_SM, bg=BG_PANEL, fg=FG_DIM,
                                  activebackground=ACCENT_DIM, activeforeground=BG,
                                  relief="flat", bd=0, padx=12, pady=5,
                                  cursor="hand2", state="disabled",
                                  command=self._open_last_output)
        self.open_btn.pack(side="right", padx=(6, 0))

        self.scan_btn = tk.Button(opts, text="Run Scan",
                                  font=(_SANS, 10, "bold"),
                                  bg=ACCENT, fg=BG,
                                  activebackground=ACCENT_DIM, activeforeground=BG,
                                  disabledforeground=BG,
                                  relief="flat", bd=0, padx=18, pady=5,
                                  cursor="hand2", command=self._start_scan)
        self.scan_btn.pack(side="right")

        self._build_log_panel(body)

    def _build_log_panel(self, parent):
        frame = tk.Frame(parent, bg=BG_PANEL)
        frame.grid(row=4, column=0, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Header row with "Log" label and a Clear button
        hdr = tk.Frame(frame, bg=BG_PANEL, padx=10, pady=6)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="Log", font=SANS_SM, bg=BG_PANEL, fg=FG_DIM).pack(side="left")
        tk.Button(hdr, text="Clear", font=SANS_SM,
                  bg=BG_PANEL, fg=FG_DIM, relief="flat", bd=0,
                  activebackground=BG_PANEL, activeforeground=ACCENT,
                  cursor="hand2", command=self._clear_log).pack(side="right")

        # Text widget + scrollbars
        txt_frame = tk.Frame(frame, bg=BG_PANEL)
        txt_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 4))
        txt_frame.rowconfigure(0, weight=1)
        txt_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(txt_frame, bg=BG_INPUT, fg=FG, font=MONO,
                                wrap="none", relief="flat", bd=0,
                                insertbackground=ACCENT, state="disabled", spacing1=1)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        sb_y = ttk.Scrollbar(txt_frame, orient="vertical",   command=self.log_text.yview)
        sb_x = ttk.Scrollbar(txt_frame, orient="horizontal", command=self.log_text.xview)
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        self.log_text.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self.log_text.tag_config("banner", foreground=ACCENT)
        self.log_text.tag_config("info",   foreground=FG_DIM)
        self.log_text.tag_config("db",     foreground=ACCENT)
        self.log_text.tag_config("shm",    foreground=YELLOW)
        self.log_text.tag_config("wal",    foreground=YELLOW)
        self.log_text.tag_config("error",  foreground=RED)
        self.log_text.tag_config("done",   foreground=ACCENT)
        self.log_text.tag_config("normal", foreground=FG)

        # Progress bar - determinate because we pre-count files before walking
        # NOTE: pady=(0,6) on a Frame() constructor triggers "bad screen distance"
        # on some Tk versions - use grid(pady=...) instead
        prog_frame = tk.Frame(frame, bg=BG_PANEL)
        prog_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 6))
        prog_frame.columnconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Scan.Horizontal.TProgressbar",
                        troughcolor=BG_INPUT, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT,
                        bordercolor=BG_INPUT, troughrelief="flat", relief="flat")
        style.configure("Vertical.TScrollbar",
                        troughcolor=BG_INPUT, background=BG_PANEL,
                        arrowcolor=FG_DIM,   bordercolor=BG_INPUT)
        style.configure("Horizontal.TScrollbar",
                        troughcolor=BG_INPUT, background=BG_PANEL,
                        arrowcolor=FG_DIM,   bordercolor=BG_INPUT)

        self.progress = ttk.Progressbar(prog_frame, style="Scan.Horizontal.TProgressbar",
                                        orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")

        self.prog_label = tk.Label(prog_frame, text="", font=SANS_SM,
                                   bg=BG_PANEL, fg=FG_DIM, width=14, anchor="e")
        self.prog_label.grid(row=0, column=1, padx=(8, 0))

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG_PANEL, padx=18, pady=6)
        bar.grid(row=2, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var,
                 font=SANS_SM, bg=BG_PANEL, fg=FG_DIM, anchor="w").grid(row=0, column=0, sticky="w")

        pills = tk.Frame(bar, bg=BG_PANEL)
        pills.grid(row=0, column=1, sticky="e")

        self._stat_vars = {}
        for key, label, color in [
            ("db",  "DBs",    ACCENT),
            ("wal", "WALs",   ACCENT),
            ("shm", "SHMs",   ACCENT),
            ("err", "Errors", RED),
        ]:
            v = tk.StringVar(value="-")
            self._stat_vars[key] = v
            pill = tk.Frame(pills, bg=BG, padx=8, pady=2)
            pill.pack(side="left", padx=3)
            tk.Label(pill, textvariable=v, font=(_MONO, 10, "bold"),
                     bg=BG, fg=color).pack(side="left")
            tk.Label(pill, text=f" {label}", font=SANS_SM,
                     bg=BG, fg=FG_DIM).pack(side="left")

    def _build_path_row(self, parent, row, label_text, attr, browse_cmd, placeholder):
        row_frame = tk.Frame(parent, bg=BG)
        row_frame.grid(row=row, column=0, sticky="ew", pady=(0, 6))
        row_frame.columnconfigure(1, weight=1)

        tk.Label(row_frame, text=label_text, font=SANS_MD,
                 bg=BG, fg=FG, width=12, anchor="w").grid(row=0, column=0, sticky="w")

        entry = tk.Entry(row_frame, font=MONO, bg=BG_INPUT, fg=FG,
                         insertbackground=ACCENT, relief="flat", bd=0,
                         highlightthickness=1,
                         highlightcolor=ACCENT, highlightbackground=BG_PANEL)
        entry.grid(row=0, column=1, sticky="ew", ipady=5, padx=(6, 6))
        entry.insert(0, placeholder)
        entry.config(fg=FG_DIM)

        # Placeholder behaviour: clear on focus, restore if left empty
        def _focus_in(e, ph=placeholder, en=entry):
            if en.get() == ph:
                en.delete(0, "end")
                en.config(fg=FG)

        def _focus_out(e, ph=placeholder, en=entry):
            if not en.get():
                en.insert(0, ph)
                en.config(fg=FG_DIM)

        entry.bind("<FocusIn>",  _focus_in)
        entry.bind("<FocusOut>", _focus_out)
        setattr(self, attr, entry)

        tk.Button(row_frame, text="Browse...", font=SANS_SM,
                  bg=BG_PANEL, fg=ACCENT,
                  activebackground=ACCENT_DIM, activeforeground=BG,
                  relief="flat", bd=0, padx=10, pady=5,
                  cursor="hand2", command=browse_cmd).grid(row=0, column=2, sticky="e")

    # ------------------------------------------------------------------
    # Source type toggle
    # ------------------------------------------------------------------

    def _on_src_type_change(self):
        # Clear the path field when the user switches between folder/archive
        ph = "Path to scan"
        if self.input_path.get() not in (ph, ""):
            self.input_path.delete(0, "end")
            self.input_path.insert(0, ph)
            self.input_path.config(fg=FG_DIM)

    # ------------------------------------------------------------------
    # Browse dialogs
    # ------------------------------------------------------------------

    def _browse_source(self):
        if self.src_type.get() == "archive":
            path = filedialog.askopenfilename(
                title="Select archive",
                filetypes=[
                    ("Supported archives", "*.zip *.tar *.tar.gz *.tgz"),
                    ("All files", "*.*"),
                ]
            )
        else:
            path = filedialog.askdirectory(
                title="Select source folder"
            )
        if path:
            self.input_path.delete(0, "end")
            self.input_path.insert(0, path)
            self.input_path.config(fg=FG)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_path.delete(0, "end")
            self.output_path.insert(0, path)
            self.output_path.config(fg=FG)

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title("About SQLiteWalker")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self)
        _set_window_icon(win)

        content = tk.Frame(win, bg=BG, padx=26, pady=22)
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(1, weight=1)

        tk.Label(content, text="SQLiteWalker", font=HEADER,
                 bg=BG, fg=ACCENT).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(content, text="Python script to walk a folder, zip or tar file looking for SQLite databases",
                 font=SANS_MD, bg=BG, fg=FG).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 12))

        tk.Frame(content, bg=BG_PANEL, height=1).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12)
        )

        rows = [
            ("Version", VERSION),
            ("Author", "@KevinPagano3 | @stark4n6"),
            ("GitHub", "https://github.com/stark4n6/SQLiteWalker"),
            ("Website", "startme.stark4n6.com"),
            ("GUI contributor", "@Mipa97"),
            ("Runtime", f"{_SYS} | Python {sys.version.split()[0]}"),
        ]

        for row_idx, (label, value) in enumerate(rows, 3):
            tk.Label(content, text=label, font=SANS_SM, bg=BG, fg=FG_DIM,
                     width=15, anchor="w").grid(row=row_idx, column=0, sticky="nw", pady=2)
            tk.Label(content, text=value, font=SANS_SM, bg=BG, fg=FG,
                     anchor="w", wraplength=340, justify="left").grid(
                         row=row_idx, column=1, sticky="w", pady=2
                     )

        btn_row = tk.Frame(content, bg=BG)
        btn_row.grid(row=3 + len(rows), column=0, columnspan=2, sticky="e", pady=(16, 0))
        tk.Button(btn_row, text="Close", font=SANS_SM,
                  bg=BG_PANEL, fg=ACCENT,
                  activebackground=ACCENT_DIM, activeforeground=BG,
                  relief="flat", bd=0, padx=18, pady=5,
                  cursor="hand2", command=win.destroy).pack()

        win.bind("<Escape>", lambda _e: win.destroy())
        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        win.grab_set()
        win.focus_set()

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _log(self, text, tag="normal"):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text, tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self._log(ASCII_BANNER, "banner")

    # Thread-safe: worker calls these, .after() marshals to the main thread
    def _thread_log(self, text, tag="normal"):
        self.after(0, self._log, text, tag)

    def _thread_progress(self, current, total):
        def _up():
            if total:
                pct = int(current / total * 100)
                self.progress["value"] = pct
                self.prog_label.config(text=f"{current} / {total}")
            else:
                self.progress["value"] = 0
                self.prog_label.config(text=f"{current} scanned")
        self.after(0, _up)

    # ------------------------------------------------------------------
    # Open output folder
    # ------------------------------------------------------------------

    def _open_last_output(self):
        if self._last_output and os.path.isdir(self._last_output):
            _open_folder(self._last_output)

    # ------------------------------------------------------------------
    # Scan lifecycle
    # ------------------------------------------------------------------

    def _start_scan(self):
        if self._scanning:
            return

        placeholders = {"Path to scan", "Folder where results will be saved"}
        inp = self.input_path.get().strip()
        out = self.output_path.get().strip()

        if inp in placeholders or not inp:
            messagebox.showerror("Missing input", "Please select a source file or folder.")
            return
        if out in placeholders or not out:
            messagebox.showerror("Missing output", "Please select an output folder.")
            return
        if not os.path.exists(inp):
            messagebox.showerror("Not found", f"Source path does not exist:\n{inp}")
            return
        if not os.path.exists(out):
            messagebox.showerror("Not found", f"Output folder does not exist:\n{out}")
            return

        self._scanning = True
        self.open_btn.config(state="disabled")
        self.scan_btn.config(state="disabled", text="Scanning...", bg=ACCENT_DIM, fg=BG)
        self.status_var.set("Scanning...")
        self.progress["value"] = 0
        self.prog_label.config(text="")
        for v in self._stat_vars.values():
            v.set("-")

        self._log("\n" + "-" * 60 + "\n", "info")
        self._log(f"Source  : {inp}\n", "info")
        self._log(f"Dest    : {out}\n", "info")
        self._log("-" * 60 + "\n", "info")

        def _run_scan_safely():
            try:
                run_scan(
                    inp,
                    out,
                    self.quiet_var.get(),
                    self._thread_log,
                    self._thread_progress,
                    self._scan_done
                )
            except Exception as e:
                self._thread_log(f"\nERROR: Scan failed: {e}\n", "error")
                self._thread_log(traceback.format_exc(), "error")
                self._scan_failed(str(e))

        threading.Thread(
            target=_run_scan_safely,
            daemon=True,
        ).start()

    def _scan_failed(self, message):
        def _update():
            self._scanning = False
            self.scan_btn.config(state="normal", text="Run Scan", bg=ACCENT, fg=BG)
            self.open_btn.config(state="disabled", fg=FG_DIM)
            self.progress["value"] = 0
            self.prog_label.config(text="Failed")
            self.status_var.set(f"Scan failed: {message}")

        self.after(0, _update)

    def _scan_done(self, count, shm_count, wal_count, error_count, elapsed, out_folder):
        # Called from the worker thread - must schedule UI updates via after()
        def _update():
            self._scanning    = False
            self._last_output = out_folder

            self.scan_btn.config(state="normal", text="Run Scan", bg=ACCENT, fg=BG)
            self.open_btn.config(state="normal", fg=ACCENT)
            self.progress["value"] = 100
            self.prog_label.config(text="Done")

            self._stat_vars["db"].set(str(count))
            self._stat_vars["wal"].set(str(wal_count))
            self._stat_vars["shm"].set(str(shm_count))
            self._stat_vars["err"].set(str(error_count))
            self.status_var.set(f"Scan complete  |  {elapsed}s  |  {out_folder}")

            self._log("\n" + "-" * 60 + "\n", "info")
            self._log("JOB FINISHED\n", "done")
            self._log(f"   Runtime  : {elapsed}s\n", "done")
            self._log(f"   DBs      : {count}\n",    "done")
            self._log(f"   SHMs     : {shm_count}\n","done")
            self._log(f"   WALs     : {wal_count}\n","done")
            if error_count:
                self._log(f"   Errors   : {error_count}  (see error_list.tsv)\n", "error")
            self._log(f"   Output   : {out_folder}\n", "done")
            self._log("-" * 60 + "\n", "info")

        self.after(0, _update)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = SQLiteWalkerApp()
    app.mainloop()


if __name__ == "__main__":
    main()