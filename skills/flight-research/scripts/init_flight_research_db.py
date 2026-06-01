#!/usr/bin/env python3
"""Initialize a flight research SQLite database from the bundled schema."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a flight research SQLite database.")
    parser.add_argument("--output", required=True, help="Path to the SQLite database to create.")
    parser.add_argument(
        "--schema",
        default=str(Path(__file__).resolve().parents[1] / "references" / "schema.sql"),
        help="Path to schema.sql. Defaults to the schema bundled with this skill.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing database. By default, existing files are refused.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output).expanduser().resolve()
    schema = Path(args.schema).expanduser().resolve()

    if output.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing database: {output}")
    if not schema.exists():
        raise SystemExit(f"Schema file not found: {schema}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    schema_sql = schema.read_text(encoding="utf-8")
    with sqlite3.connect(output) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_sql)
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
            ("sqlite_version", sqlite3.sqlite_version),
        )
        conn.commit()

    print(output)


if __name__ == "__main__":
    main()
