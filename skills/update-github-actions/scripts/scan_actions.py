#!/usr/bin/env python3
"""Inventory official actions/* references in top-level GitHub workflow files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ACTION_PATTERN = re.compile(
    r"\buses\s*:\s*['\"]?"
    r"(?P<action>actions/(?P<path>[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*))"
    r"@(?!\$\{\{)(?P<ref>[^\s'\"#]+)"
)
OFFICIAL_USES_PATTERN = re.compile(r"\buses\s*:.*\bactions/")


def code_before_comment(line: str) -> str:
    """Return YAML source before the first unquoted comment marker."""
    quote: str | None = None
    escaped = False

    for index, character in enumerate(line):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in {"'", '"'}:
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if character == "#" and quote is None:
            return line[:index]

    return line


def workflow_files(root: Path) -> list[Path]:
    """Return the requested non-recursive workflow YAML files."""
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return []
    return sorted({*workflows.glob("*.yml"), *workflows.glob("*.yaml")})


def scan(root: Path) -> dict[str, Any]:
    """Build a JSON-serializable inventory for a project root."""
    files = workflow_files(root)
    usages: list[dict[str, Any]] = []
    unparsed: list[dict[str, Any]] = []

    for path in files:
        relative_path = path.relative_to(root).as_posix()
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            source = code_before_comment(raw_line)
            matches = list(ACTION_PATTERN.finditer(source))
            for match in matches:
                action_path = match.group("path")
                parts = action_path.split("/")
                usages.append(
                    {
                        "file": relative_path,
                        "line": line_number,
                        "column": match.start("action") + 1,
                        "action": match.group("action"),
                        "repository": f"actions/{parts[0]}",
                        "subpath": "/".join(parts[1:]) or None,
                        "current_ref": match.group("ref"),
                    }
                )

            if OFFICIAL_USES_PATTERN.search(source) and not matches:
                unparsed.append(
                    {
                        "file": relative_path,
                        "line": line_number,
                        "source": source.strip(),
                        "reason": "Official action reference could not be parsed",
                    }
                )

    return {
        "root": str(root),
        "workflow_files": [path.relative_to(root).as_posix() for path in files],
        "usages": usages,
        "unparsed": unparsed,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan (default: current directory)",
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Indent the JSON output for humans"
    )
    return parser.parse_args()


def main() -> None:
    """Run the scanner and print its JSON inventory."""
    args = parse_args()
    root = args.root.expanduser().resolve()
    payload = scan(root)
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
