#!/usr/bin/env python3
"""Submit site HTML and CSS to W3C's public validators (requires internet)."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CSS_NS = "{http://www.w3.org/2005/07/css-validator}"
EXCLUDED = {"_site", "node_modules", "__pycache__"}


def validate(path):
    command = ["curl", "--fail", "--silent", "--show-error", "--max-time", "90"]
    if path.suffix.lower() == ".html":
        command += [
            "-H", "Content-Type: text/html; charset=utf-8",
            "--data-binary", f"@{path}",
            "https://validator.w3.org/nu/?out=json",
        ]
    else:
        command += [
            "--form", f"file=@{path};type=text/css",
            "--form", "output=soap12", "--form", "profile=css3",
            "--form", "warning=2", "--form", "lang=en",
            "https://jigsaw.w3.org/css-validator/validator",
        ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    if path.suffix.lower() == ".html":
        response = json.loads(result.stdout)
        messages = response["messages"]
        return [dict(message, severity=(
            "error" if message["type"] in {"error", "non-document-error"}
            else "warning" if message.get("subType") == "warning" else "info"
        )) for message in messages]

    response = ET.fromstring(result.stdout)
    validity = response.find(f".//{CSS_NS}validity")
    if validity is None or validity.text not in {"true", "false"}:
        raise ValueError("CSS validator did not return a validation result")
    messages = []
    for severity in ("error", "warning"):
        for entry in response.findall(f".//{CSS_NS}{severity}"):
            message = {child.tag.removeprefix(CSS_NS): " ".join(
                "".join(child.itertext()).split()
            ) for child in entry}
            messages.append(dict(message, severity=severity))
    if validity.text == "false" and not any(m["severity"] == "error" for m in messages):
        raise ValueError("CSS validation failed without error details")
    return messages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Site directory; use _site for assembled deployment output")
    parser.add_argument("--report", type=Path, required=True,
                        help="Where to write the full JSON report")
    parser.add_argument("--resume", action="store_true",
                        help="Reuse completed checks in the report; retry service failures")
    args = parser.parse_args()
    root = args.root.resolve()
    files = sorted(path for path in root.rglob("*") if path.is_file()
                   and path.suffix.lower() in {".html", ".css"}
                   and not any(part.startswith(".") or part in EXCLUDED
                               for part in path.relative_to(root).parts))
    if not files:
        parser.error(f"No HTML or CSS files found in {root}")
    report = {"root": str(root), "started_at": datetime.now(timezone.utc).isoformat(),
              "html_validator": "https://validator.w3.org/nu/",
              "css_validator": "https://jigsaw.w3.org/css-validator/",
              "css_profile": "css3", "files": []}
    totals = Counter()
    completed = {}
    if args.resume and args.report.is_file():
        previous = json.loads(args.report.read_text(encoding="utf-8"))
        if previous["root"] != str(root):
            parser.error("Cannot resume a report for a different site root")
        completed = {entry["path"]: entry for entry in previous["files"]
                     if "service_error" not in entry}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    rate_limited = False
    for index, path in enumerate(files):
        name = path.relative_to(root).as_posix()
        if name in completed:
            entry = completed[name]
            report["files"].append(entry)
            totals.update(entry["counts"])
            continue
        try:
            if rate_limited:
                raise ValueError("Not checked: W3C rate-limited this run; retry later with --resume")
            time.sleep(5)  # Pace requests to the shared public services.
            messages = validate(path)
            counts = Counter(message["severity"] for message in messages)
            entry = {"path": name, "messages": messages, "counts": dict(counts)}
            totals.update(counts)
            print(f"[{index + 1}/{len(files)}] {name}: "
                  f"{counts['error']} errors, {counts['warning']} warnings, "
                  f"{counts['info']} notices", flush=True)
        except (OSError, subprocess.CalledProcessError, ValueError, KeyError, ET.ParseError) as exc:
            detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
            if isinstance(exc, subprocess.CalledProcessError) and "429" in detail:
                rate_limited = True
            entry = {"path": name, "service_error": detail}
            totals["service_error"] += 1
            print(f"[{index + 1}/{len(files)}] {name}: CHECK FAILED: {detail}", flush=True)
        report["files"].append(entry)
        report["totals"] = dict(totals)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["totals"] = dict(totals)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {len(files)} files. Totals: {dict(totals)}. Report: {args.report}")
    return 2 if totals["service_error"] else 1 if totals["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
