"""Build and verify an unsigned two-program Windows portable release."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rxdatalint import __version__

TAG = "v" + __version__.replace("a", "-alpha.")
NAME = "RxDataLint-" + TAG.removeprefix("v")


def collect_tk(bundle):
    # Some Python builds keep Tcl/Tk scripts in ZIPs missed by PyInstaller.
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


def smoke(suite, results):
    results.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME"):
        env.pop(name, None)
    env["PATH"] = os.pathsep.join((str(Path(os.environ["SystemRoot"]) / "System32"), os.environ["SystemRoot"]))
    report = {}
    for folder, exe in (("Checker", "RxDataLint.exe"), ("Analysis", "RxDataLintAnalysis.exe")):
        diagnostic = (results / f"{folder}.json").resolve()
        if diagnostic.exists():
            raise ValueError("Choose a fresh smoke output folder.")
        subprocess.run([str((suite / folder / exe).resolve()), "--self-test",
                        str((suite / "examples/sample_scmd.csv").resolve()), str(diagnostic)],
                       check=True, timeout=60, cwd=results, env=env)
        data = json.loads(diagnostic.read_text(encoding="utf-8"))
        if data.get("ok") is not True or data.get("rows") != 8:
            raise ValueError(f"Packaged {folder} smoke test failed.")
        report[folder] = data
    return report


def main():
    if sys.platform != "win32" or sys.maxsize <= 2**32:
        raise SystemExit("Build with 64-bit Python on Windows.")
    suite = ROOT / "dist" / NAME
    workspace = ROOT / "build" / NAME
    archive = ROOT / "dist" / f"RxDataLint-Windows-x64-{TAG}.zip"
    if suite.exists() or workspace.exists() or archive.exists():
        raise SystemExit("Output already exists. Preserve it and use a fresh version/build location.")
    suite.mkdir(parents=True)
    workspace.mkdir(parents=True)
    env = os.environ.copy()
    env["PYINSTALLER_CONFIG_DIR"] = str(workspace / "pyinstaller-config")
    for folder, name, entry in (("Checker", "RxDataLint", "desktop_entry.py"),
                                ("Analysis", "RxDataLintAnalysis", "analysis_entry.py")):
        args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed", "--onedir",
                "--name", name, "--paths", str(ROOT / "src"), "--paths", str(ROOT / "analysis"),
                "--distpath", str(suite), "--workpath", str(workspace / folder), "--specpath", str(workspace)]
        if folder == "Analysis":
            args += ["--add-data", str(ROOT / "analysis/schema.sql") + ":.",
                     "--add-data", str(ROOT / "analysis/sql") + ":sql"]
        subprocess.run(args + [str(ROOT / "tools" / entry)], check=True, cwd=ROOT, env=env)
        bundle = suite / name
        collect_tk(bundle)
        bundle.rename(suite / folder)
    (suite / "examples").mkdir()
    shutil.copy2(ROOT / "examples/sample_scmd.csv", suite / "examples")
    shutil.copy2(ROOT / "docs/WINDOWS-SUITE.md", suite / "START-HERE.md")
    shutil.copy2(ROOT / "LICENSE", suite)
    shutil.copy2(ROOT / "CHANGELOG.md", suite)
    (suite / "docs").mkdir()
    for name in ("QUICKSTART.md", "RULES.md", "WINDOWS-SUITE.md"):
        shutil.copy2(ROOT / "docs" / name, suite / "docs")
    for folder in ("Checker", "Analysis"):
        (suite / folder / "examples").mkdir()
        shutil.copy2(ROOT / "examples/sample_scmd.csv", suite / folder / "examples")
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, suite / "PYTHON-LICENSE.txt")
    for folder, exe in (("Checker", "RxDataLint.exe"), ("Analysis", "RxDataLintAnalysis.exe")):
        (suite / f"Start-{folder}.bat").write_bytes(
            f'@echo off\r\nstart "" /D "%~dp0{folder}" "%~dp0{folder}\\{exe}"\r\n'.encode("ascii"))
    first = smoke(suite, workspace / "smoke-built")
    shutil.make_archive(str(archive.with_suffix("")), "zip", suite.parent, suite.name)
    extracted = workspace / "extracted suite 中文"
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError("ZIP integrity check failed.")
        zipped.extractall(extracted)
    second = smoke(extracted / suite.name, workspace / "smoke-extracted")
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(checksum + "  " + archive.name + "\n", encoding="utf-8")
    validation = {"tag": TAG, "python_version": platform.python_version(), "platform": platform.platform(),
                  "machine": platform.machine(), "archive": archive.name, "sha256": checksum,
                  "built": first, "extracted": second,
                  "scope": "Tested on the build machine with Python environment variables removed and a system-only PATH. No independent clean Windows VM/other-machine test. Report-button handlers checked with an intercepted open call."}
    (ROOT / "dist" / f"validation-{TAG}.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    print(archive)


if __name__ == "__main__":
    main()
