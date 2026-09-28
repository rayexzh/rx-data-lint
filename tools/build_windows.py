"""Build an unsigned Windows portable ZIP using the current Python environment."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if sys.platform != "win32":
    raise SystemExit("Build this package on Windows.")
subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
    "--onedir", "--name", "RxDataLint", "--paths", str(ROOT / "src"),
    "--distpath", str(ROOT / "dist"), "--workpath", str(ROOT / "build"),
    "--specpath", str(ROOT / "build"), str(ROOT / "tools" / "desktop_entry.py")], check=True, cwd=ROOT)
bundle = ROOT / "dist" / "RxDataLint"
# Python builds with Tcl/Tk 9 can store their scripts in separate ZIPs that
# PyInstaller does not collect. Populate the standard runtime-hook directories.
for prefix, inner, folder in (("libtcl", "tcl_library", "_tcl_data"), ("libtk", "tk_library", "_tk_data")):
    target = bundle / "_internal" / folder
    if not target.exists():
        archives = list((Path(sys.base_prefix) / "tcl").glob(prefix + "*.zip"))
        if len(archives) == 1:
            with zipfile.ZipFile(archives[0]) as archive:
                for name in archive.namelist():
                    if not name.startswith(inner + "/") or name.endswith("/"):
                        continue
                    output = target / name[len(inner) + 1:]
                    if not output.resolve().is_relative_to(target.resolve()):
                        raise ValueError("Invalid Tcl/Tk archive path")
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(archive.read(name))
(bundle / "examples").mkdir(exist_ok=True)
shutil.copy2(ROOT / "examples" / "sample_scmd.csv", bundle / "examples")
for source in ("LICENSE", "README.md", "README.zh-CN.md", "CHANGELOG.md"):
    shutil.copy2(ROOT / source, bundle)
python_license = Path(sys.base_prefix) / "LICENSE.txt"
if python_license.exists():
    shutil.copy2(python_license, bundle / "PYTHON-LICENSE.txt")
shutil.copytree(ROOT / "docs", bundle / "docs", dirs_exist_ok=True)
diagnostic = ROOT / "build" / "packaged-smoke.json"
if diagnostic.exists():
    diagnostic.unlink()
subprocess.run([str(bundle / "RxDataLint.exe"), "--self-test", str(bundle / "examples" / "sample_scmd.csv"),
                str(diagnostic)], check=True, timeout=60, cwd=bundle)
if not diagnostic.exists():
    raise SystemExit("Packaged smoke test did not produce a result.")
print(diagnostic.read_text(encoding="utf-8"))
archive = Path(shutil.make_archive(str(ROOT / "dist" / "RxDataLint-Windows-x64"), "zip", ROOT / "dist", "RxDataLint"))
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix(".zip.sha256").write_text(checksum + "  " + archive.name + "\n", encoding="utf-8")
print(archive)
