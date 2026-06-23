import argparse
import base64
import csv
import os
import platform as _platform_mod
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback
import webbrowser
import zipfile

VERSION = "1.0.0"

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

# Font families per OS
if _is_windows():
    _SANS, _MONO = "DejaVu Sans", "DejaVu Sans Mono"
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
BG_INPUT   = "#030303"
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
    "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"
)

_ICON_ICO_B64 = (
    "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"
)

def _set_window_icon(root):
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
            root._icon_ref = img
    except Exception:
        pass


def _open_folder(path):
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

    # Preserve metadata modification timestamp from TAR header
    try:
        if hasattr(member, "mtime") and member.mtime:
            os.utime(dest_path, (member.mtime, member.mtime))
    except Exception:
        pass

    return dest_path


def safe_zip_extract(zip_archive, member, destination):
    dest_path = safe_archive_dest_path(member.filename, destination)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with zip_archive.open(member) as source, open(dest_path, "wb") as out:
        shutil.copyfileobj(source, out)

    # Preserve metadata modification timestamp from ZIP header
    try:
        zip_time = time.mktime(member.date_time + (0, 0, -1))
        os.utime(dest_path, (zip_time, zip_time))
    except Exception:
        pass 

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

def run_scan(input_path, output_path, src_type_choice, quiet_mode, log_cb, progress_cb, live_count_cb, done_cb):
    base          = "SQLiteWalker_Out_"
    data_list     = []
    error_list    = []
    data_headers  = ("File Name", "File Type", "Export Path", "Tables")
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
    
    # Get the normalized absolute output folder name to trim matches relative to it
    clean_out_root = os.path.abspath(out_folder)
    if _is_windows() and clean_out_root.startswith("\\\\?\\"):
        clean_out_root = clean_out_root[4:]

    if src_type_choice == "archive":
        _, basename = os.path.split(input_path)
        basename_lower = basename.lower()
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
            log_cb("Pre-counting items inside TAR file to synchronize progress bar...\n", "info")
            total = 0
            with tarfile.open(input_path, "r|*") as count_archive:
                for _ in count_archive:
                    total += 1
            
            archive = tarfile.open(input_path, "r|*")
            files = archive

        for idx, entry in enumerate(files, 1):
            progress_cb(idx, total)
            file = entry.filename if archive_type == "zip" else entry.name
            file_name = file.rsplit("/", 1)

            if file.endswith(("-shm", "-wal")):
                try:
                    if archive_type == "zip":
                        if entry.is_dir():
                            continue
                        new_path = safe_zip_extract(archive, entry, out_folder + splitter + "db_out")
                    else:
                        if not entry.isfile():
                            continue
                        f = archive.extractfile(entry)
                        if f is None:
                            continue
                        with f:
                            new_path = safe_tar_write_file(entry, f, out_folder + splitter + "db_out")
                except RuntimeError as e:
                    log_cb(f"  BLOCKED ARCHIVE ENTRY: {e}\n", "error")
                    continue

                if file.startswith("/"):
                    file = file[1:]
                if _is_windows():
                    new_path = new_path.replace("/", "\\")
                
                dest = new_path[4:] if _is_windows() else new_path
                trimmed_dest = os.path.relpath(dest, os.path.dirname(clean_out_root))

                if file.endswith("-shm"):
                    shm_count += 1
                    live_count_cb("shm", shm_count)
                    log_cb(f"  SHM {shm_count}: {file}\n", "shm")
                    f_type = "-SHM"
                else:
                    wal_count += 1
                    live_count_cb("wal", wal_count)
                    log_cb(f"  WAL {wal_count}: {file}\n", "wal")
                    f_type = "-WAL"

                data_list.append((file_name[-1], f_type, trimmed_dest, ""))

            else:
                db = None
                new_path = None

                if archive_type == "zip":
                    if entry.is_dir():
                        continue
                    with archive.open(entry) as f:
                        header = f.read(100)
                    if not header.startswith(b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00"):
                        continue
                    try:
                        new_path = safe_zip_extract(archive, entry, out_folder + splitter + "db_out")
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
                        if not header.startswith(b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00"):
                            continue
                        try:
                            new_path = safe_tar_write_file(entry, f, out_folder + splitter + "db_out", header)
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
                    trimmed_dest = os.path.relpath(dest, os.path.dirname(clean_out_root))
                    
                    count += 1
                    live_count_cb("db", count)
                    data_list.append((file_name[-1], "DB", trimmed_dest, tables_list))
                    log_cb(f"  DB {count}: {file}  [{len(tables_list)} tables]\n", "db")
                except sqlite3.Error as e:
                    dest = new_path[4:] if _is_windows() else new_path
                    trimmed_dest = os.path.relpath(dest, os.path.dirname(clean_out_root))
                    error_count += 1
                    live_count_cb("err", error_count)
                    log_cb(f"  ERROR: {file} - {e}\n", "error")
                    error_list.append((file_name[-1], trimmed_dest, e))
                finally:
                    try: db.close()
                    except Exception: pass

        archive.close()

    elif src_type_choice == "folder":
        log_cb(f"Walking folder: {input_path}\n", "info")
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
                
                clean_dest = dest_file[4:] if _is_windows() and dest_file.startswith("\\\\?\\") else dest_file
                trimmed_dest = os.path.relpath(clean_dest, os.path.dirname(clean_out_root))

                if file.endswith("-shm"):
                    shm_count += 1
                    live_count_cb("shm", shm_count)
                    log_cb(f"  SHM {shm_count}: {file}\n", "shm")
                    f_type = "-SHM"
                else:
                    wal_count += 1
                    live_count_cb("wal", wal_count)
                    log_cb(f"  WAL {wal_count}: {file}\n", "wal")
                    f_type = "-WAL"
                    
                data_list.append((file, f_type, trimmed_dest, ""))
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

                clean_dest = dest_file[4:] if _is_windows() and dest_file.startswith("\\\\?\\") else dest_file
                trimmed_dest = os.path.relpath(clean_dest, os.path.dirname(clean_out_root))

                count += 1
                live_count_cb("db", count)
                data_list.append((file, "DB", trimmed_dest, tables_list))
                log_cb(f"  DB {count}: {file}  [{len(tables_list)} tables]\n", "db")
            except sqlite3.Error as e:
                clean_src = src[4:] if _is_windows() and src.startswith("\\\\?\\") else src
                trimmed_src = os.path.relpath(clean_src, os.path.dirname(clean_out_root))
                error_count += 1
                live_count_cb("err", error_count)
                log_cb(f"  ERROR: {file} - {e}\n", "error")
                error_list.append((file, trimmed_src, e))
            finally:
                try:
                    if db: db.close()
                except Exception: pass

    # Write results TSV
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

    # Write Results to SQLite Database with Indexes on all columns
    sqlite_out_path = out_folder + splitter + "db_list.db"
    try:
        out_db = sqlite3.connect(sqlite_out_path)
        out_curr = out_db.cursor()
        
        out_curr.execute("""
            CREATE TABLE IF NOT EXISTS db_list (
                file_name TEXT,
                file_type TEXT,
                export_path TEXT,
                tables TEXT
            );
        """)
        
        for row in data_list:
            tbls_str = ", ".join(row[3]) if isinstance(row[3], list) else str(row[3])
            out_curr.execute("INSERT INTO db_list VALUES (?, ?, ?, ?);", (row[0], row[1], row[2], tbls_str))
            
        out_curr.execute("CREATE INDEX IF NOT EXISTS idx_filename ON db_list(file_name);")
        out_curr.execute("CREATE INDEX IF NOT EXISTS idx_filetype ON db_list(file_type);")
        out_curr.execute("CREATE INDEX IF NOT EXISTS idx_exportpath ON db_list(export_path);")
        out_curr.execute("CREATE INDEX IF NOT EXISTS idx_tables ON db_list(tables);")
        
        if error_count > 0:
            out_curr.execute("""
                CREATE TABLE IF NOT EXISTS error_list (
                    file_name TEXT,
                    export_path TEXT,
                    error TEXT
                );
            """)
            for row in error_list:
                out_curr.execute("INSERT INTO error_list VALUES (?, ?, ?);", (row[0], row[1], str(row[2])))
            
            out_curr.execute("CREATE INDEX IF NOT EXISTS idx_err_filename ON error_list(file_name);")
            out_curr.execute("CREATE INDEX IF NOT EXISTS idx_err_exportpath ON error_list(export_path);")
            out_curr.execute("CREATE INDEX IF NOT EXISTS idx_err_error ON error_list(error);")
            
        out_db.commit()
        out_db.close()
    except Exception as dbe:
        log_cb(f"  DATABASE WRITE ERROR: Failed compiling db_list.db - {dbe}\n", "error")

    elapsed = round(time.time() - start_time, 2)
    done_cb(count, shm_count, wal_count, error_count, elapsed, out_folder)


# ---------------------------------------------------------------------------
# GUI App Class
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
        self._last_output = None

        self._build_ui()

        self._log(ASCII_BANNER, "banner")
        self._log(f"  Platform : {_SYS}\n", "info")
        self._log(f"  Python   : {sys.version.split()[0]}\n\n", "info")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # Topbar frame row
        self.rowconfigure(1, weight=1) # Main Body frame row
        self.rowconfigure(2, weight=0) # Statusbar frame row

        self._build_topbar()
        self._build_body()
        self._build_statusbar()

    def _build_topbar(self):
        # Frame container configured to grid title text components and the right-aligned halved logo
        bar = tk.Frame(self, bg=BG_PANEL, pady=10, padx=18)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)

        # Left Column Stack for Application Labels & Repositioned About Button
        title_frame = tk.Frame(bar, bg=BG_PANEL)
        title_frame.grid(row=0, column=0, sticky="nw")
        
        tk.Label(title_frame, text="SQLiteWalker", font=HEADER,
                 bg=BG_PANEL, fg=ACCENT).grid(row=0, column=0, sticky="w")
        tk.Label(title_frame, text=f"v{VERSION}  ",
                 font=SANS_SM, bg=BG_PANEL, fg=FG_DIM).grid(row=0, column=1, sticky="w", padx=(6, 0))
                 
        # Repositioned About Button beneath Title string metadata stack
        tk.Button(title_frame, text="About", font=SANS_SM,
                  bg=BG_PANEL, fg=ACCENT, activebackground=BG_PANEL, activeforeground=ACCENT_DIM,
                  relief="flat", bd=0, cursor="hand2", anchor="w",
                  command=self._show_about).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        # Right Column Layout checking for external asset availability
        script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
        logo_path = os.path.join(script_dir, "logo.png")

        if os.path.exists(logo_path):
            try:
                # Load external photo reference and divide layout dimensions strictly by 3
                full_img = tk.PhotoImage(file=logo_path)
                self._main_logo_img = full_img.subsample(3, 3)
                
                logo_label = tk.Label(bar, image=self._main_logo_img, bg=BG_PANEL, cursor="hand2")
                logo_label.grid(row=0, column=2, sticky="e")
                
                # Double feature: clicking logo opens script repository hub
                logo_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/stark4n6/SQLiteWalker"))
            except Exception:
                pass

    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)

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

        opts = tk.Frame(body, bg=BG)
        opts.grid(row=3, column=0, sticky="ew", pady=(4, 10))

        self.quiet_var = tk.BooleanVar(value=True)

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

        hdr = tk.Frame(frame, bg=BG_PANEL, padx=10, pady=6)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="Log", font=SANS_SM, bg=BG_PANEL, fg=FG_DIM).pack(side="left")
        tk.Button(hdr, text="Clear", font=SANS_SM,
                  bg=BG_PANEL, fg=FG_DIM, relief="flat", bd=0,
                  activebackground=BG_PANEL, activeforeground=ACCENT,
                  cursor="hand2", command=self._clear_log).pack(side="right")

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
            ("wal", "WALs",   YELLOW),
            ("shm", "SHMs",   YELLOW),
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

    def _on_src_type_change(self):
        ph = "Path to scan"
        if self.input_path.get() not in (ph, ""):
            self.input_path.delete(0, "end")
            self.input_path.insert(0, ph)
            self.input_path.config(fg=FG_DIM)

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
            path = filedialog.askdirectory(title="Select source folder")
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

    def _show_about(self, *args):
        # 1. Check if an active instance already exists in memory
        if hasattr(self, "_about_window") and self._about_window and tk.Toplevel.winfo_exists(self._about_window):
            self._about_window.lift()
            self._about_window.focus_set()
            return

        # 2. Hard execution gate check to stop instantaneous double-firing
        if hasattr(self, "_building_about") and self._building_about:
            return
        self._building_about = True

        try:
            self._about_window = tk.Toplevel(self)
            win = self._about_window
            
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

            tk.Frame(content, bg=BG_PANEL, height=1).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

            rows = [
                ("Version", VERSION, False),
                ("Author", "@KevinPagano3 | @stark4n6", False),
                ("GitHub", "https://github.com/stark4n6/SQLiteWalker", True),
                ("Website", "https://startme.stark4n6.com", True),
                ("GUI contributor", "@Mipa97", False),
                ("Runtime", f"{_SYS} | Python {sys.version.split()[0]}", False),
            ]

            def _open_url(url):
                try:
                    webbrowser.open_new_tab(url)
                except Exception:
                    pass

            for row_idx, (label, value, is_url) in enumerate(rows, 3):
                tk.Label(content, text=label, font=SANS_SM, bg=BG, fg=FG_DIM,
                         width=15, anchor="w").grid(row=row_idx, column=0, sticky="nw", pady=2)
                
                if is_url:
                    lbl_val = tk.Label(content, text=value, font=SANS_SM, bg=BG, fg=ACCENT,
                                       anchor="w", wraplength=340, justify="left", cursor="hand2")
                    lbl_val.grid(row=row_idx, column=1, sticky="w", pady=2)
                    
                    lbl_val.bind("<Button-1>", lambda e, url=value: _open_url(url))
                    lbl_val.bind("<Enter>", lambda e, lbl=lbl_val: lbl.config(font=(_SANS, 9, "underline")))
                    lbl_val.bind("<Leave>", lambda e, lbl=lbl_val: lbl.config(font=SANS_SM))
                else:
                    tk.Label(content, text=value, font=SANS_SM, bg=BG, fg=FG,
                             anchor="w", wraplength=340, justify="left").grid(row=row_idx, column=1, sticky="w", pady=2)

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

        finally:
            self._building_about = False

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

    def _thread_live_count(self, key, current_val):
        def _up():
            if key in self._stat_vars:
                self._stat_vars[key].set(str(current_val))
        self.after(0, _up)

    def _open_last_output(self):
        if self._last_output and os.path.isdir(self._last_output):
            _open_folder(self._last_output)

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
            v.set("0")

        self._log("\n" + "-" * 60 + "\n", "info")
        self._log(f"Source  : {inp}\n", "info")
        self._log(f"Dest    : {out}\n", "info")
        self._log("-" * 60 + "\n", "info")

        def _run_scan_safely():
            try:
                run_scan(
                    input_path=inp,
                    output_path=out,
                    src_type_choice=self.src_type.get(),
                    quiet_mode=self.quiet_var.get(),
                    log_cb=self._thread_log,
                    progress_cb=self._thread_progress,
                    live_count_cb=self._thread_live_count,
                    done_cb=self._scan_done
                )
            except Exception as e:
                self._thread_log(f"\nERROR: Scan failed: {e}\n", "error")
                self._thread_log(traceback.format_exc(), "error")
                self._scan_failed(str(e))

        threading.Thread(target=_run_scan_safely, daemon=True).start()

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
                self._log(f"   Errors   : {error_count}  (see error_list.tsv / db_list.db)\n", "error")
            self._log(f"   Output   : {out_folder}\n", "done")
            self._log("-" * 60 + "\n", "info")
        self.after(0, _update)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Setup argument parser to support standard execution or headless CLI sweeps
    # Disable automatic -h handling so we can intercept it cleanly
    parser = argparse.ArgumentParser(
        description=f"SQLiteWalker {VERSION} | https://github.com/stark4n6/SQLiteWalker | https://startme.stark4n6.com",
        add_help=False 
    )
    parser.add_argument("-i", "--source", help="Path to input file or directory to scan.")
    parser.add_argument("-o", "--output", help="Path to base output directory where compilation directory is written.")
    parser.add_argument("-t", "--type",   choices=["folder", "archive"], help="Specify source target mapping context.")
    parser.add_argument("-h", "--help",   action="store_true", help="Show this help message and exit.")

    # Check for CLI switches explicitly
    cli_switches = ["-i", "--source", "-o", "--output", "-t", "--type", "-h", "--help"]
    
    if any(arg in sys.argv for arg in cli_switches):
        args = parser.parse_args()
        
        # If help is requested, print it and exit immediately before GUI initialization
        if args.help:
            parser.print_help()
            sys.exit(0)
        
        # If they didn't ask for help but missed a required parameter
        if not args.source or not args.output or not args.type:
            print("ERROR: When utilizing CLI switches, all arguments (-i, -o, -t) must be specified.\n")
            parser.print_help()
            sys.exit(1)
            
        run_in_cli_mode(args)
    else:
        # No switches provided; fallback to initializing interactive graphical loop cleanly
        app = SQLiteWalkerApp()
        app.mainloop()


if __name__ == "__main__":
    main()