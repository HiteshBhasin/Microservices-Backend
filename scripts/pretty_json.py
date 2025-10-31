#!/usr/bin/env python3
"""Simple JSON pretty-printer.
Usage:
  python scripts/pretty_json.py input.json
  cat raw.json | python scripts/pretty_json.py
  curl ... | python scripts/pretty_json.py

Reads from a file (first arg) or stdin if no args are provided.
Prints formatted JSON (indent=2, ensure_ascii=False) to stdout.
"""
import sys
import json
from pathlib import Path

def pprint_from_text(text: str) -> None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON input: {e}\n")
        sys.exit(2)
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if not p.exists():
            sys.stderr.write(f"File not found: {p}\n")
            sys.exit(2)
        text = p.read_text(encoding="utf-8")
        pprint_from_text(text)
    else:
        # read from stdin
        text = sys.stdin.read()
        if not text.strip():
            sys.stderr.write("No input provided on stdin. Provide a file path or pipe JSON into this script.\n")
            sys.exit(2)
        pprint_from_text(text)

if __name__ == '__main__':
    main()
