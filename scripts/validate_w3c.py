#!/usr/bin/env python3
"""Validate site HTML and CSS locally using the installed W3C Nu checker (vnu)."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"_site", "node_modules", "__pycache__"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Site directory; use _site for assembled deployment output")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    files = sorted(path for path in root.rglob("*") if path.is_file()
                   and path.suffix.lower() in {".html", ".css"}
                   and not any(part.startswith(".") or part in EXCLUDED
                               for part in path.relative_to(root).parts))
    if not files:
        parser.error(f"No HTML or CSS files found in {root}")
    executable = shutil.which("vnu")
    if not executable:
        parser.error("Local vnu is required. Install it or add it to PATH; no online fallback is used.")
    report = {"root": str(root), "started_at": datetime.now(timezone.utc).isoformat(),
              "validator": executable, "files": [str(p.relative_to(root)) for p in files]}
    try:
        result = subprocess.run(
            [executable, "--also-check-css", "--format", "json", "--stdout", *map(str, files)],
            capture_output=True, text=True, check=False,
        )
        report["result"] = json.loads(result.stdout)
        report["exit_code"] = result.returncode
        report["diagnostics"] = result.stderr
    except (OSError, ValueError) as exc:
        report["execution_error"] = str(exc)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Validation incomplete: {exc}. Report: {args.report}")
        return 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    messages = report["result"].get("messages", [])
    for message in messages:
        print(f"{message.get('url', '')}:{message.get('lastLine', '')}: "
              f"{message.get('type', '')}: {message.get('message', '')}")
    print(f"Locally checked {len(files)} HTML/CSS files; vnu exit {result.returncode}. Report: {args.report}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
