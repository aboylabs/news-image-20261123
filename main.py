#!/usr/bin/env python3
"""Entrypoint for the news-image-20261123 entry.

The front page for Monday 23 November 2026 is drawn by render23.py and
shipped in this repository as entry/entry.png. This program, standard
library only with no network access, copies that image to the grader's
output directory, so the two runs the grader makes write identical bytes.
The copy is byte for byte: nothing is re-encoded, so the judged image is
exactly the one rendered and verified during the build.
"""
import hashlib
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry" / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def destination():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    return Path(outdir) / "entry.png"


def main():
    data = SOURCE.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("entry.png is not a PNG file")
    target = destination()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target)
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {target} ({len(data)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
