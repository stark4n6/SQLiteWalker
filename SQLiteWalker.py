import csv
import argparse
import os
import re
import shutil
import sqlite3
import sys
import time
import tarfile
import zipfile
from zipfile import ZipFile

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

VERSION = "0.6.0"

ascii_art = rf'''
        _______.  ______      __       __  .___________. _______        
       /       | /  __  \    |  |     |  | |           ||   ____|       
      |   (----`|  |  |  |   |  |     |  | `---|  |----`|  |__          
       \   \    |  |  |  |   |  |     |  |     |  |     |   __|         
   .----)   |   |  `--'  '--.|  `----.|  |     |  |     |  |____        
   |_______/     \_____\_____\_______||__|     |__|     |_______| 
____    __    ____  ___       __       __  ___  _______ .______      
\   \  /  \  /   / /   \     |  |     |  |/  / |   ____||   _  \     
 \   \/    \/   / /  ^  \    |  |     |  '  /  |  |__   |  |_)  |    
  \            / /  /_\  \   |  |     |    <   |   __|  |      /     
   \    /\    / /  _____  \  |  `----.|  .  \  |  |____ |  |\  \----.
    \__/  \__/ /__/     \__\ |_______||__|\__\ |_______|| _| `._____|
    
                SQLiteWalker v{VERSION}
                https://github.com/stark4n6/SQLiteWalker
                @KevinPagano3 | @stark4n6 | startme.stark4n6.com
                                                                     '''

# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

def is_platform_windows():
    return os.name == 'nt'

# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

def open_sqlite_db_readonly(path):
    '''Opens a SQLite db read-only so the original file and its -wal/-shm are never modified.'''
    if is_platform_windows():
        # Encode the \\?\ long-path prefix into its percent-encoded form for the URI
        if path.startswith('\\\\?\\UNC\\'):   # UNC long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\?\\'):       # normal long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\'):          # plain UNC
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                                  # normal drive path
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)

# ---------------------------------------------------------------------------
# Archive safety
# ---------------------------------------------------------------------------

# Device names that are illegal as file/folder names on Windows regardless of extension
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def sanitize_archive_member_name(member_name):
    '''
    Validates and cleans an archive member path before extraction.

    Raises RuntimeError for:
      - absolute paths  (/etc/passwd, C:\\Windows\\...)
      - directory traversal  (../../secret)
      - empty components after normalization

    Strips illegal characters on Windows and handles reserved device names.
    Returns an OS-appropriate relative path string.
    '''
    member_name = member_name.replace("\\", "/")

    # Block absolute paths — both POSIX-style and Windows drive-letter style
    if member_name.startswith("/") or re.match(r"^[A-Za-z]:", member_name):
        raise RuntimeError(f"Unsafe absolute archive path blocked: {member_name}")

    safe_parts = []
    for part in member_name.split("/"):
        # Empty segments, current-dir dots, and parent-dir traversal are all unsafe
        if part in ("", ".", ".."):
            raise RuntimeError(f"Unsafe archive path component blocked: {member_name}")

        # Replace characters that are illegal in Windows filenames
        safe_part = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", part)
        # Windows also forbids trailing spaces and dots on file/folder names
        safe_part = safe_part.rstrip(" .")

        if not safe_part:
            safe_part = "_"

        # Prefix reserved device names so they can't be created on Windows
        stem = safe_part.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_NAMES:
            safe_part = f"_{safe_part}"

        safe_parts.append(safe_part)

    return os.path.join(*safe_parts)


def unique_dest_path(dest_path):
    '''Returns dest_path unchanged if it doesn't exist, otherwise appends -001, -002, etc.'''
    if not os.path.exists(dest_path):
        return dest_path

    folder, filename = os.path.split(dest_path)
    stem, ext = os.path.splitext(filename)

    for n in range(1, 1000):
        candidate = os.path.join(folder, f"{stem}-{n:03d}{ext}")
        if not os.path.exists(candidate):
            return candidate

    raise RuntimeError(f"Could not create a unique output path for {filename}")


def safe_archive_dest_path(member_name, destination):
    '''
    Resolves the final extraction path for an archive member and verifies it
    stays inside the destination directory (guards against path traversal
    even after sanitization).
    '''
    dest_root   = os.path.abspath(destination)
    safe_name   = sanitize_archive_member_name(member_name)
    dest_path   = os.path.abspath(os.path.join(dest_root, safe_name))

    # commonpath() raises ValueError when the paths are on different drives (Windows)
    try:
        common = os.path.commonpath([dest_root, dest_path])
    except ValueError:
        common = ""

    if common != dest_root:
        raise RuntimeError(f"Unsafe archive path blocked after resolution: {member_name}")

    return unique_dest_path(dest_path)


def safe_zip_extract(zip_archive, member, destination):
    '''Extracts one ZIP member to destination using the safe path helpers above.'''
    dest_path = safe_archive_dest_path(member.filename, destination)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with zip_archive.open(member) as src, open(dest_path, "wb") as out:
        shutil.copyfileobj(src, out)
    return dest_path


def safe_tar_write_file(member, source, destination, initial_data=b""):
    '''
    Writes one TAR member to destination.
    Hard and symbolic links are blocked outright — they can point outside the
    destination tree and cannot be made safe by path sanitization alone.
    initial_data lets the caller prepend bytes already read (e.g. the magic-byte
    header we consumed to identify the file type).
    '''
    if member.islnk() or member.issym():
        raise RuntimeError(f"Unsafe TAR link blocked: {member.name}")

    dest_path = safe_archive_dest_path(member.name, destination)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as out:
        if initial_data:
            out.write(initial_data)
        shutil.copyfileobj(source, out)

    return dest_path

# ---------------------------------------------------------------------------
# Output folder creation
# ---------------------------------------------------------------------------

def create_output_folder(output_path, base, splitter):
    '''
    Creates the timestamped output folder.  If a folder with that timestamp
    already exists (two scans fired within the same second) it appends -001,
    -002, etc. rather than crashing.
    '''
    output_ts = time.strftime("%Y%m%d-%H%M%S")

    for n in range(1000):
        suffix     = "" if n == 0 else f"-{n:03d}"
        out_folder = output_path + base + output_ts + suffix
        try:
            os.makedirs(out_folder + splitter + "db_out")
            return out_folder
        except FileExistsError:
            continue

    raise RuntimeError(f"Could not create a unique output folder for {base}{output_ts}")

# ---------------------------------------------------------------------------
# Core scan
# ---------------------------------------------------------------------------

SQLITE_MAGIC = b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00"


def run_scan(input_path, output_path, quiet_mode):
    base          = "SQLiteWalker_Out_"
    data_list     = []
    error_list    = []
    data_headers  = ('File Name', 'Export Path', 'Tables')
    error_headers = ('File Name', 'Export Path', 'Error')
    count = error_count = wal_count = shm_count = 0
    splitter = "\\" if is_platform_windows() else "/"

    start_time = time.time()

    # Prefix Windows paths to handle >260-char paths
    if is_platform_windows():
        if len(input_path) > 1 and input_path[1] == ":":
            input_path  = "\\\\?\\" + input_path.replace("/", "\\")
        if len(output_path) > 1 and output_path[1] == ":":
            output_path = "\\\\?\\" + output_path.replace("/", "\\")

    # Trailing separator required so base concatenates into the right directory
    if not output_path.endswith(splitter):
        output_path += splitter

    out_folder = create_output_folder(output_path, base, splitter)

    _, basename     = os.path.split(input_path)
    basename_lower  = basename.lower()

    # ------------------------------------------------------------------
    # Archive branch  (.zip / .tar / .tar.gz / .tgz)
    # ------------------------------------------------------------------
    if os.path.isfile(input_path):

        if basename_lower.endswith(".zip"):
            archive_type = "zip"
        elif basename_lower.endswith((".tar", ".tar.gz", ".tgz")):
            archive_type = "tar"
        else:
            print("Input file is not a supported archive (.zip / .tar / .tar.gz / .tgz). Exiting.")
            sys.exit(1)

        print(f"Opening {archive_type.upper()}: {input_path}")

        if archive_type == "zip":
            archive = zipfile.ZipFile(input_path, "r")
            entries = archive.infolist()
            total   = len(entries)
        else:
            # r|* = streaming read, works on .tar.gz without seeking
            archive = tarfile.open(input_path, "r|*")
            entries = archive      # iterator — no random access, total unknown up front
            total   = 0

        for idx, entry in enumerate(entries, 1):
            file      = entry.filename if archive_type == "zip" else entry.name
            file_name = file.rsplit("/", 1)

            # ----- WAL / SHM companion files -----
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
                    print(f"  BLOCKED ARCHIVE ENTRY: {e}")
                    continue

                if file.startswith("/"):
                    file = file[1:]
                if is_platform_windows():
                    new_path = new_path.replace("/", "\\")

                if file.endswith("-shm"):
                    shm_count += 1
                    if not quiet_mode:
                        print(f"  SHM {shm_count}: {file}")
                else:
                    wal_count += 1
                    if not quiet_mode:
                        print(f"  WAL {wal_count}: {file}")

                dest = new_path[4:] if is_platform_windows() else new_path
                data_list.append((file_name[-1], dest, ""))

            # ----- Potential SQLite database files -----
            else:
                db       = None
                new_path = None

                if archive_type == "zip":
                    if entry.is_dir():
                        continue
                    with archive.open(entry) as f:
                        header = f.read(100)
                    if not header.startswith(SQLITE_MAGIC):
                        continue
                    try:
                        new_path = safe_zip_extract(archive, entry, out_folder + splitter + "db_out")
                    except RuntimeError as e:
                        print(f"  BLOCKED ZIP ENTRY: {e}")
                        continue

                else:
                    if not entry.isfile():
                        continue
                    f = archive.extractfile(entry)
                    if f is None:
                        continue
                    with f:
                        header = f.read(100)
                        if not header.startswith(SQLITE_MAGIC):
                            continue
                        try:
                            # Pass header back in — it was consumed during identification
                            new_path = safe_tar_write_file(
                                entry, f, out_folder + splitter + "db_out", header
                            )
                        except RuntimeError as e:
                            print(f"  BLOCKED TAR ENTRY: {e}")
                            continue

                try:
                    if file.startswith("/"):
                        file = file[1:]
                    if is_platform_windows():
                        new_path = new_path.replace("/", "\\")
                    db = open_sqlite_db_readonly(new_path)
                    cursor = db.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables_list = [r[0] for r in cursor.fetchall()]
                    dest = new_path[4:] if is_platform_windows() else new_path
                    data_list.append((file_name[-1], dest, tables_list))
                    count += 1
                    if not quiet_mode:
                        print(f"  DB {count}: {file}  [{len(tables_list)} tables]")
                except sqlite3.Error as e:
                    print(f"  ERROR: {file} — {e}")
                    dest = new_path[4:] if is_platform_windows() else new_path
                    error_list.append((file_name[-1], dest, e))
                    error_count += 1
                finally:
                    try:
                        if db: db.close()
                    except Exception:
                        pass

        archive.close()

    # ------------------------------------------------------------------
    # Folder walk branch
    # ------------------------------------------------------------------
    elif os.path.isdir(input_path):
        print(f"Walking folder: {input_path}")

        for root, dirs, files in os.walk(input_path):
            for file in files:

                # ----- WAL / SHM companion files -----
                if file.endswith(("-shm", "-wal")):
                    src_path = os.path.join(root, file)
                    rel      = os.path.relpath(root, input_path)
                    dest_dir = out_folder if rel == "." else os.path.join(out_folder, rel)
                    dest_file = os.path.join(dest_dir, file)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(src_path, dest_file)

                    if file.endswith("-shm"):
                        shm_count += 1
                        if not quiet_mode:
                            print(f"  SHM {shm_count}: {file}")
                    else:
                        wal_count += 1
                        if not quiet_mode:
                            print(f"  WAL {wal_count}: {file}")

                    data_list.append((file, dest_file, ""))
                    continue

                # ----- Potential SQLite database files -----
                src_path = os.path.join(root, file)
                if not os.path.isfile(src_path) or os.path.getsize(src_path) <= 100:
                    continue

                try:
                    with open(src_path, "r", encoding="ISO-8859-1") as f:
                        hdr = f.read(100)
                except Exception:
                    continue

                if not hdr.startswith("SQLite format 3"):
                    continue

                db = None
                try:
                    db = open_sqlite_db_readonly(src_path)
                    cursor = db.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables_list = [r[0] for r in cursor.fetchall()]

                    rel       = os.path.relpath(root, input_path)
                    dest_dir  = out_folder if rel == "." else os.path.join(out_folder, rel)
                    dest_file = os.path.join(dest_dir, file)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(src_path, dest_file)

                    data_list.append((file, dest_file, tables_list))
                    count += 1
                    if not quiet_mode:
                        print(f"  DB {count}: {src_path}  [{len(tables_list)} tables]")
                except sqlite3.Error as e:
                    print(f"  ERROR: {file} — {e}")
                    error_list.append((file, src_path, e))
                    error_count += 1
                finally:
                    try:
                        if db: db.close()
                    except Exception:
                        pass

    else:
        print("Input path is not a file or folder. Exiting.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Write TSV output(s)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    elapsed = round(time.time() - start_time, 2)
    print()
    print("****JOB FINISHED****")
    print(f"Runtime     : {elapsed}s")
    print(f"DBs Found   : {count}")
    print(f"SHMs Found  : {shm_count}")
    print(f"WALs Found  : {wal_count}")
    print(f"Error Count : {error_count}")
    if error_count > 0:
        print("Check error_list.tsv for details")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=f"SQLiteWalker v{VERSION} by @KevinPagano3 | @stark4n6 | https://github.com/stark4n6/SQLiteWalker"
    )
    parser.add_argument('-i', '--input_path',  required=True,  type=str, action="store",
                        help='Input path: folder, .zip, .tar, .tar.gz, or .tgz')
    parser.add_argument('-o', '--output_path', required=True,  type=str, action="store",
                        help='Output folder path')
    parser.add_argument('-q', '--quiet_mode',  required=False, action="store_true",
                        help='Suppress per-file console output')
    args = parser.parse_args()

    input_path  = args.input_path
    output_path = os.path.abspath(args.output_path)
    quiet_mode  = args.quiet_mode

    if not os.path.exists(input_path):
        parser.error("INPUT path does not exist.")
    if not os.path.exists(output_path):
        parser.error("OUTPUT folder does not exist.")

    # Windows: prefix paths to handle >260-char paths (done again inside run_scan,
    # but doing it here ensures the argparse validation above works on long paths too)
    if is_platform_windows():
        if len(input_path) > 1 and input_path[1] == ":":
            input_path = "\\\\?\\" + input_path.replace("/", "\\")

    print(ascii_art)
    print()
    print(f"Source      : {input_path}")
    print(f"Destination : {output_path}")
    print("-" * max(len(f"Source      : {input_path}"), 40))

    if quiet_mode:
        print("Quiet mode enabled.")
        print("These aren't the logs you're looking for.")
    print()

    run_scan(input_path, output_path, quiet_mode)


if __name__ == "__main__":
    main()