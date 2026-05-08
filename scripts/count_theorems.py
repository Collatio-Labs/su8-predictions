#!/usr/bin/env python3
"""
count_theorems.py — Count theorem-grade Lean 4 declarations.

Methodology:
  1. Find all .lean files under proofs/ (excluding .lake/ and lake-packages/).
  2. For each file, strip:
     - Block comments:  /- ... -/  (nested)
     - Line comments:   -- ... EOL
     - String literals: "..."      (with backslash escapes)
  3. Count lines matching theorem/lemma declarations at line start, allowing
     optional modifiers: private, protected, noncomputable, @[...] attributes.

Pattern (on stripped source):
  ^(private\\s+|protected\\s+|noncomputable\\s+)*(@\\[.*?\\]\\s+)*(theorem|lemma)\\s+

Reports Collatio side, UFT side, and combined total.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
COLLATIO_ROOT = os.path.join(REPO_ROOT, "proofs", "Collatio")
UFT_ROOT = os.path.join(REPO_ROOT, "proofs", "UFT", "lean")

EXCLUDE_DIRS = {".lake", "lake-packages", "build"}

DECL_RE = re.compile(
    r"^(?:(?:private|protected|noncomputable)\s+)*"
    r"(?:@\[.*?\]\s+)*"
    r"(?:theorem|lemma)\s+",
)


def find_lean_files(root):
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(".lean"):
                result.append(os.path.join(dirpath, fn))
    return sorted(result)


def strip_comments_and_strings(source):
    out = []
    i = 0
    n = len(source)
    depth = 0

    while i < n:
        if depth > 0:
            if i + 1 < n and source[i] == "/" and source[i + 1] == "-":
                depth += 1
                i += 2
            elif i + 1 < n and source[i] == "-" and source[i + 1] == "/":
                depth -= 1
                i += 2
            else:
                i += 1
            continue

        if i + 1 < n and source[i] == "/" and source[i + 1] == "-":
            depth = 1
            i += 2
            continue

        if i + 1 < n and source[i] == "-" and source[i + 1] == "-":
            while i < n and source[i] != "\n":
                i += 1
            continue

        if source[i] == '"':
            i += 1
            while i < n and source[i] != '"':
                if source[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            continue

        out.append(source[i])
        i += 1

    return "".join(out)


def count_in_files(files):
    total = 0
    per_file = {}
    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        stripped = strip_comments_and_strings(source)
        count = 0
        for line in stripped.splitlines():
            line_s = line.lstrip()
            if DECL_RE.match(line_s):
                count += 1
        per_file[fp] = count
        total += count
    return total, per_file


def main():
    collatio_files = find_lean_files(COLLATIO_ROOT)
    uft_files = find_lean_files(UFT_ROOT)

    collatio_count, collatio_detail = count_in_files(collatio_files)
    uft_count, uft_detail = count_in_files(uft_files)

    combined = collatio_count + uft_count

    print(f"Collatio ({len(collatio_files)} files): {collatio_count:,} theorem/lemma declarations")
    print(f"UFT      ({len(uft_files)} files): {uft_count:,} theorem/lemma declarations")
    print(f"Combined:                    {combined:,} theorem-grade declarations")
    print()

    if "--detail" in sys.argv:
        print("=== Collatio detail ===")
        for fp, c in sorted(collatio_detail.items()):
            if c > 0:
                print(f"  {c:4d}  {fp}")
        print()
        print("=== UFT detail ===")
        for fp, c in sorted(uft_detail.items()):
            if c > 0:
                print(f"  {c:4d}  {fp}")


if __name__ == "__main__":
    main()
