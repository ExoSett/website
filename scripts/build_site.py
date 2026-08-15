#!/usr/bin/env python3
"""Assemble the ExoSett website with a built ExoSett Sketch bundle."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sketch-dist", required=True, type=Path)
    parser.add_argument("--output", default=ROOT / "_site", type=Path)
    return parser.parse_args()


def ignored(_directory: str, names: list[str]) -> set[str]:
    excluded = {".git", ".vscode", "_site", "__pycache__", ".DS_Store"}
    return set(names) & excluded


def main() -> int:
    args = arguments()
    sketch_dist = args.sketch_dist.resolve()
    output = args.output.resolve()
    expected = [sketch_dist / "sketch.js", sketch_dist / "sketch.css"]

    missing = [path for path in expected if not path.is_file()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise SystemExit(f"Sketch build is incomplete; missing: {names}")
    if output == ROOT or output in ROOT.parents:
        raise SystemExit("Output must not be the website source directory or one of its parents.")

    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT, output, ignore=ignored)

    assets = output / "design" / "sketch" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for source in expected:
        shutil.copy2(source, assets / source.name)

    print(f"Combined website assembled at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
