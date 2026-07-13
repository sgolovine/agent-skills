#!/usr/bin/env python3
"""Validate common Conventional Commits 1.0.0 message structure."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADER_RE = re.compile(
    r"^(?P<type>[A-Za-z][A-Za-z0-9-]*)(?:\((?P<scope>[^()\r\n]+)\))?"
    r"(?P<breaking>!)?: (?P<description>\S.*)$"
)
FOOTER_RE = re.compile(
    r"^(?P<token>[A-Za-z0-9-]+|BREAKING CHANGE|BREAKING-CHANGE)(?:: | #)(?P<value>\S.*)$"
)
BREAKING_FOOTER_RE = re.compile(r"^BREAKING(?: |-)?CHANGE: \S.*$")


def _read_message(args: argparse.Namespace) -> str:
    if args.message_file:
        return Path(args.message_file).read_text(encoding="utf-8")
    if args.message is not None:
        return args.message
    raise SystemExit("provide --message or --message-file")


def _footer_start(lines: list[str]) -> int | None:
    index = len(lines) - 1
    while index >= 0 and lines[index] == "":
        index -= 1
    if index < 0 or not FOOTER_RE.match(lines[index]):
        return None

    start = index
    index -= 1
    while index >= 0:
        line = lines[index]
        if line == "":
            return start
        if FOOTER_RE.match(line):
            start = index
        index -= 1
    return start


def validate(message: str) -> list[str]:
    normalized = message.replace("\r\n", "\n").rstrip("\n")
    if not normalized.strip():
        return ["commit message is empty"]

    lines = normalized.split("\n")
    errors: list[str] = []

    header = lines[0]
    match = HEADER_RE.match(header)
    if not match:
        errors.append("header must match '<type>[optional scope][optional !]: <description>'")
    elif match.group("type") != match.group("type").lower():
        errors.append("type should be lowercase for repository consistency")

    if len(lines) > 1 and lines[1] != "":
        errors.append("body or footers must begin one blank line after the description")

    footer_start = _footer_start(lines)
    if footer_start is not None:
        if footer_start > 0 and lines[footer_start - 1] != "":
            errors.append("footers must be separated from the body by one blank line")
        for line in lines[footer_start:]:
            if line and FOOTER_RE.match(line):
                token = line.split(":", 1)[0]
                if " " in token and token != "BREAKING CHANGE":
                    errors.append("footer tokens must use '-' instead of spaces, except BREAKING CHANGE")

    for line in lines:
        if line.upper().startswith("BREAKING CHANGE") or line.upper().startswith("BREAKING-CHANGE"):
            if not BREAKING_FOOTER_RE.match(line):
                errors.append("breaking-change footer must be 'BREAKING CHANGE: <description>'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--message")
    source.add_argument("--message-file")
    args = parser.parse_args()

    errors = validate(_read_message(args))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: Conventional Commit structure looks valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
