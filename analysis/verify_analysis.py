"""Verify generated analysis files against their recorded SHA-256 hashes."""
import argparse
import hashlib
import json
from pathlib import Path
from html_report import REPORT_FILES


def verify(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError("No artifact hashes. Regenerate this analysis with the current pipeline.")
    required = {"medicines.sqlite", "SUMMARY.md"} | {
        f"{p.stem}.csv" for p in (Path(__file__).parent / "sql").glob("*.sql")
    }
    if manifest.get("analysis_format_version", 1) >= 2:
        required.update(REPORT_FILES)
    failures = [f"Not recorded: {name}" for name in sorted(required - artifacts.keys())]
    for name, expected in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name or name in (".", "..", "manifest.json"):
            raise ValueError("Invalid artifact name in manifest.")
        path = folder / name
        if path.is_symlink() or not path.is_file():
            failures.append(f"Missing or unsupported file: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(f"Changed: {name}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    try:
        failures = verify(args.folder)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Verification failed: {exc}\n")
    if failures:
        parser.exit(1, "Verification failed:\n" + "\n".join(failures) + "\n")
    print("PASS: all recorded analysis files match their hashes. / 分析文件校验通过。")


if __name__ == "__main__":
    main()
