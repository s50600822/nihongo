#!/usr/bin/env python3
"""Count Japanese character frequencies across a directory tree and write a Markdown table.

Usage examples:
    python freq.py                         # scan ./ recursively, write Readme.md
    python freq.py lyrics md -o freq.md    # scan only these dirs, custom output
    python freq.py -o -                    # print the table to stdout
    python freq.py --scripts kanji         # kanji only
"""
from __future__ import annotations

import argparse
import html
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
DEFAULT_EXTS = {".md", ".txt", ".html", ".htm"}
# Characters that are valid kana/kanji but pure noise for this corpus
NOISE = {"啊"}  # Chinese filler, e.g. 啊啊啊啊...


def script_of(ch: str) -> str | None:
    """Return 'hiragana' / 'katakana' / 'kanji', or None for anything else."""
    cp = ord(ch)
    if 0x3041 <= cp <= 0x3096 or cp in (0x309D, 0x309E):
        return "hiragana"
    if 0x30A1 <= cp <= 0x30FA or 0x30FC <= cp <= 0x30FF:  # excludes ・ (U+30FB)
        return "katakana"
    if (ch == "々" or 0x3400 <= cp <= 0x4DBF or 0x4E00 <= cp <= 0x9FFF
            or 0xF900 <= cp <= 0xFAFF or 0x20000 <= cp <= 0x2FA1F):
        return "kanji"
    return None


def iter_files(roots, exts, exclude: set[Path]):
    for root in roots:
        if root.is_file():
            candidates = [root]
        else:
            candidates = sorted(root.rglob("*"))
        for p in candidates:
            if not p.is_file() or p.resolve() in exclude:
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if exts and p.suffix.lower() not in exts:
                continue
            yield p


def read_text(path: Path) -> str | None:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:  # binary file
        return None
    text = data.decode("utf-8-sig", errors="replace")  # utf-8-sig strips the BOM
    if path.suffix.lower() in {".html", ".htm"}:
        text = html.unescape(text)
    # NFKC: half-width katakana -> full-width, decomposed dakuten (か+゛) -> が
    return unicodedata.normalize("NFKC", text)


def count_chars(files, scripts: set[str]) -> tuple[Counter, int]:
    counter: Counter = Counter()
    n_files = 0
    for path in files:
        try:
            text = read_text(path)
        except OSError as e:
            print(f"skip {path}: {e}", file=sys.stderr)
            continue
        if text is None:
            continue
        n_files += 1
        counter.update(ch for ch in text if ch not in NOISE and script_of(ch) in scripts)
    return counter, n_files


def build_markdown(counter: Counter, n_files: int, min_count: int) -> str:
    items = sorted(((c, n) for c, n in counter.items() if n >= min_count),
                   key=lambda kv: (-kv[1], kv[0]))  # deterministic tie-break
    total = sum(counter.values())
    lines = [
        "# Character frequency",
        "",
        f"{len(items)} distinct characters, {total} total, from {n_files} files.",
        "",
        "| Rank | Character | Frequency | % | Cumulative % |",
        "|-----:|:---------:|----------:|--:|-------------:|",
    ]
    running = 0
    for rank, (ch, n) in enumerate(items, 1):
        running += n
        lines.append(f"| {rank} | {ch} | {n} "
                     f"| {n / total:.2%} | {running / total:.2%} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, default=[Path(".")], help="dirs/files to scan (default: .)")
    ap.add_argument("-o", "--output", default="Readme.md", help="output file, or '-' for stdout")
    ap.add_argument("--ext", nargs="*", default=sorted(DEFAULT_EXTS),
                    help="file extensions to scan (default: %(default)s); pass none to scan everything text-like")
    ap.add_argument("--scripts", nargs="+", default=["hiragana", "katakana", "kanji"],
                    choices=["hiragana", "katakana", "kanji"])
    ap.add_argument("--min-count", type=int, default=1)
    args = ap.parse_args()

    exts = {e if e.startswith(".") else f".{e}" for e in args.ext}
    exclude = set() if args.output == "-" else {Path(args.output).resolve()}  # never read our own output
    counter, n_files = count_chars(iter_files(args.paths, exts, exclude), set(args.scripts))
    md = build_markdown(counter, n_files, args.min_count)

    if args.output == "-":
        sys.stdout.write(md)
    else:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Wrote {len(counter)} characters from {n_files} files to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
