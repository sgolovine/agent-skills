#!/usr/bin/env python3
"""Static triage scanner for untrusted agent skill repositories.

This helper never executes, imports, installs, renders, or follows anything from
the target. It inventories files, scans multiple text views, decodes obvious
payloads, and emits JSON leads for manual adversarial review.
"""

from __future__ import annotations

import argparse
import base64
import codecs
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import sys
import unicodedata
import urllib.parse
import warnings
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Iterable

MAX_FULL_SCAN_BYTES = 2_000_000
MAX_SAMPLE_BYTES = 64_000
MAX_DECODED_BYTES = 200_000
MAX_DECODE_DEPTH = 2

ZERO_WIDTH = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
    "\u2060": "WORD JOINER",
}

TEXT_SUFFIXES = {
    ".bash",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".lock",
    ".md",
    ".mjs",
    ".py",
    ".rs",
    ".sh",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}

TEXT_NAMES = {
    "Dockerfile",
    "Makefile",
    "Taskfile",
    "justfile",
    "go.mod",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

ENTRYPOINT_NAMES = {
    "SKILL.md",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "action.yml",
}


@dataclass(frozen=True)
class Rule:
    category: str
    title: str
    pattern: str
    severity: str
    intent_risk: int
    capability_risk: int
    why_it_matters: str
    recommended_action: str


@dataclass(frozen=True)
class FileRecord:
    path: Path
    relpath: str
    size: int
    sha256: str
    extension: str
    text_like: bool
    skipped_reason: str | None = None


@dataclass(frozen=True)
class TextView:
    file: FileRecord
    name: str
    text: str
    transform: str
    depth: int = 0


RULES = [
    Rule("prompt_control", "Potential prompt-control instruction", r"ignore (all )?(previous|prior|above) instructions", "high", 3, 0, "The skill attempts to override review instructions.", "Treat as hostile prompt injection and remove it."),
    Rule("prompt_control", "Potential prompt-control instruction", r"disregard .* instructions|do not (mention|report|disclose|warn)|mark .* safe|report .* safe|hide this|trusted mode|system:.*approve|always approve|never warn", "high", 3, 0, "The skill attempts to control reporting, trust, or warnings.", "Remove the instruction and do not let it affect the review."),
    Rule("tool_control", "Potential tool poisoning", r"before using this tool.*(env|secret|token|credential)|include .* environment variables|send .* token|read .* ~/.*|disable .* security|bypass .* confirmation", "high", 3, 2, "Tool-facing text appears to coerce unsafe tool use.", "Remove or redesign the tool metadata; never provide secrets to satisfy it."),
    Rule("secret_access", "Potential secret access", r"process\.env|os\.environ|printenv|/proc/self/environ|GITHUB_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|NPM_TOKEN|DATABASE_URL|\.env(\.|$)|\.npmrc|\.pypirc|\.docker/config\.json|\.aws/credentials|\.ssh/(id_rsa|id_ed25519|config|known_hosts)", "high", 2, 3, "The skill may read secrets or credential material.", "Remove secret access unless narrowly justified and sandboxed."),
    Rule("secret_access", "Potential environment dump", r"\benv\b|cat\s+.*\.env|cat\s+.*credentials", "medium", 1, 3, "Environment or credential dumping can expose secrets.", "Replace with scoped configuration reads that avoid secrets."),
    Rule("exfiltration", "Potential network or exfiltration path", r"\bcurl\b|\bwget\b|fetch\s*\(|requests\.(post|get|put)|axios\.|http\.request|https\.request|urllib\.request|socket\.|dns\.|nslookup|dig\b|webhook|posthog|sentry|segment|analytics|git\s+push|npm\s+publish|!\[.*\]\(https?://", "high", 2, 2, "Outbound paths can exfiltrate data or stage remote code.", "Remove or justify the network path and restrict it to allowlisted destinations."),
    Rule("code_execution", "Potential dynamic code execution", r"eval\s*\(|exec\s*\(|new\s+Function|child_process|subprocess\.|os\.system|shell=True|importlib|import\s*\(|chmod\s+\+x", "high", 2, 3, "Dynamic execution or process spawning can run attacker-controlled code.", "Remove dynamic execution or isolate it in a disposable sandbox."),
    Rule("code_execution", "Potential curl-pipe-shell installer", r"(curl|wget).*?\|\s*(bash|sh)", "critical", 3, 3, "Remote shell installers combine network and code execution.", "Do not run this on the host; remove the pattern."),
    Rule("code_execution", "Install-time execution hook", r'"(preinstall|install|postinstall|prepare)"\s*:|preinstall|postinstall|prepare', "medium", 1, 3, "Install hooks execute before review may complete.", "Disable or remove install hooks unless essential and reviewed."),
    Rule("persistence", "Potential persistence or instruction tampering", r"AGENTS\.md|CLAUDE\.md|\.cursor/rules|\.github/copilot-instructions\.md|\.git/hooks|git\s+config\s+--global|~/.bashrc|~/.zshrc|~/.profile|crontab|systemd|LaunchAgents|authorized_keys|remember that .* trusted|always trust|store .* safe", "high", 2, 3, "Persistence or instruction tampering can affect future agent behavior.", "Remove persistence and avoid writes to global or agent instruction files."),
    Rule("ci_compromise", "Potential CI compromise", r"\.github/workflows|permissions:\s*write-all|id-token:\s*write|secrets:\s*inherit|secrets\.|actions/.*@(main|master|HEAD)|run:.*(env|printenv|curl|wget)", "high", 2, 3, "CI changes can expose secrets or expand deployment authority.", "Pin actions, reduce permissions, and remove secret-exposing commands."),
    Rule("sandbox_escape", "Potential sandbox escape or host access", r"docker\.sock|--privileged|--network\s+host|-v\s*/:|--mount.*source=/|\.\./\.\./|~/\.| /etc/| /usr/local/bin|ln\s+-s|os\.symlink", "high", 2, 3, "Host mounts, traversal, and symlinks can escape review boundaries.", "Remove host access or run only in an isolated disposable environment."),
    Rule("supply_chain", "Potential supply-chain risk", r"git\+https?|https?://.*\.(tgz|tar\.gz|zip)|npm:.*@|actions/.*@(main|master)|[<>=~^*]\s*$", "medium", 1, 2, "Remote or loosely pinned dependencies can execute unexpected code.", "Pin dependencies and verify provenance."),
    Rule("obfuscation", "Potential obfuscation", r"Buffer\.from\([^)]*,\s*['\"]base64['\"]|base64\s+(-d|--decode)|fromhex\s*\(|\\x[0-9a-fA-F]{2}|atob\s*\(|gzip|zlib|[\"']cu[\"']\s*\+\s*[\"']rl[\"']", "medium", 2, 1, "Obfuscation can hide malicious behavior from casual review.", "Decode and explain or remove the obfuscated content."),
    Rule("dos", "Potential DoS or cost bomb", r"while\s+true|for\s*\(\s*;\s*;\s*\)|:\(\)\s*\{|yes\s+>|fork\s*\(|os\.walk\([\"']/|find\s+/|max_tokens.*[1-9][0-9]{5,}", "medium", 1, 2, "Unbounded work can waste compute, disk, money, or tokens.", "Add strict bounds or remove the behavior."),
    Rule("social_engineering", "Potential social engineering", r"false positive|officially approved|scanner.*wrong|do not report|expected warning|compliance requires", "low", 1, 0, "Claims inside the skill are not evidence of safety.", "Verify provenance independently and ignore pressure to suppress warnings."),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(root: Path) -> list[FileRecord]:
    paths: Iterable[Path] = [root] if root.is_file() else root.rglob("*")
    records = []
    for path in paths:
        if not path.is_file():
            continue
        resolved = path.resolve()
        if ".git/objects/" in resolved.as_posix():
            continue
        relpath = resolved.name if root.is_file() else str(resolved.relative_to(root.resolve()))
        size = resolved.stat().st_size
        text_like = resolved.suffix in TEXT_SUFFIXES or resolved.name in TEXT_NAMES or resolved.name.startswith("README")
        skipped_reason = "large_file_sampled" if size > MAX_FULL_SCAN_BYTES else None
        records.append(
            FileRecord(
                path=resolved,
                relpath=relpath,
                size=size,
                sha256=sha256_file(resolved),
                extension=resolved.suffix,
                text_like=text_like,
                skipped_reason=skipped_reason,
            )
        )
    return sorted(records, key=lambda item: item.relpath)


def read_text(record: FileRecord) -> str | None:
    if not record.text_like:
        return None
    data = record.path.read_bytes()
    if record.skipped_reason:
        data = data[:MAX_SAMPLE_BYTES] + b"\n...[static scan sampled large file]...\n" + data[-MAX_SAMPLE_BYTES:]
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def reveal_hidden(text: str) -> str:
    return "".join(f"<{ZERO_WIDTH[char]}>" if char in ZERO_WIDTH else char for char in text)


def extract_comments(text: str) -> str:
    parts = []
    patterns = [
        r"<!--(.*?)-->",
        r"\[//\]: # \((.*?)\)",
        r"/\*(.*?)\*/",
        r"^\s*#(.*)$",
        r"^\s*//(.*)$",
    ]
    for pattern in patterns:
        parts.extend(match.group(1) for match in re.finditer(pattern, text, re.DOTALL | re.MULTILINE))
    return "\n".join(parts)


def split_string_view(text: str) -> str:
    text = re.sub(r"(['\"])([^'\"]{1,24})\1\s*\+\s*(['\"])([^'\"]{1,24})\3", lambda m: m.group(2) + m.group(4), text)
    return re.sub(r"(['\"])([^'\"]{1,24})\1\s+(['\"])([^'\"]{1,24})\3", lambda m: m.group(2) + m.group(4), text)


def base_views(record: FileRecord) -> list[TextView]:
    text = read_text(record)
    if text is None:
        return []
    views = [
        TextView(record, "raw", text, "decoded text"),
        TextView(record, "unicode_normalized", unicodedata.normalize("NFKC", text), "NFKC"),
        TextView(record, "hidden_revealed", reveal_hidden(text), "zero-width markers"),
        TextView(record, "html_unescaped", html.unescape(text), "html.unescape"),
        TextView(record, "percent_decoded", urllib.parse.unquote(text), "urllib.parse.unquote"),
        TextView(record, "comments", extract_comments(text), "simple comment extraction"),
        TextView(record, "split_strings", split_string_view(text), "joined adjacent string literals"),
    ]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            escaped = codecs.decode(text, "unicode_escape", errors="ignore")
        views.append(TextView(record, "unicode_escape", escaped, "unicode_escape"))
    except Exception:
        pass
    return views


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    printable = sum(byte in b"\n\r\t" or 32 <= byte <= 126 for byte in data)
    return printable / len(data)


def decode_blobs(view: TextView) -> list[TextView]:
    if view.depth >= MAX_DECODE_DEPTH:
        return []
    decoded: list[TextView] = []
    candidates = set(re.findall(r"(?<![A-Za-z0-9+/=])(?:[A-Za-z0-9+/]{24,}={0,2})(?![A-Za-z0-9+/=])", view.text))
    for candidate in sorted(candidates, key=len, reverse=True)[:25]:
        try:
            raw = base64.b64decode(candidate, validate=True)
        except Exception:
            continue
        decoded.extend(decoded_bytes_to_views(view, raw, "decoded_base64"))
    hex_candidates = set(re.findall(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{32,})(?![0-9a-fA-F])", view.text))
    for candidate in sorted(hex_candidates, key=len, reverse=True)[:15]:
        if len(candidate) % 2:
            continue
        try:
            raw = bytes.fromhex(candidate)
        except ValueError:
            continue
        decoded.extend(decoded_bytes_to_views(view, raw, "decoded_hex"))
    return decoded


def decoded_bytes_to_views(parent: TextView, raw: bytes, name: str) -> list[TextView]:
    if not raw or len(raw) > MAX_DECODED_BYTES:
        return []
    views = []
    if raw.startswith(b"\x1f\x8b"):
        try:
            raw = gzip.decompress(raw)
            name = f"{name}_gzip"
        except Exception:
            return []
    if printable_ratio(raw) < 0.65:
        return []
    text = raw[:MAX_DECODED_BYTES].decode("utf-8", errors="replace")
    views.append(TextView(parent.file, name, text, f"{name} from {parent.name}", parent.depth + 1))
    return views


def line_number(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def excerpt(text: str, start: int, end: int, limit: int = 240) -> str:
    snippet = text[max(0, start - 90) : min(len(text), end + 130)].replace("\n", "\\n")
    return snippet if len(snippet) <= limit else snippet[: limit - 3] + "..."


def scan_patterns(view: TextView, finding_start: int) -> list[dict]:
    findings = []
    next_id = finding_start
    for rule in RULES:
        regex = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE)
        for match in regex.finditer(view.text):
            findings.append(
                {
                    "id": f"F{next_id:03d}",
                    "title": rule.title,
                    "severity": rule.severity,
                    "category": rule.category,
                    "intent_risk": rule.intent_risk,
                    "capability_risk": rule.capability_risk,
                    "file": view.file.relpath,
                    "line": line_number(view.text, match.start()),
                    "view": view.name,
                    "evidence": excerpt(view.text, match.start(), match.end()),
                    "why_it_matters": rule.why_it_matters,
                    "recommended_action": rule.recommended_action,
                }
            )
            next_id += 1
    return findings


def special_findings(record: FileRecord, finding_start: int) -> list[dict]:
    findings = []
    next_id = finding_start
    if record.skipped_reason:
        findings.append(
            {
                "id": f"F{next_id:03d}",
                "title": "Large file sampled",
                "severity": "medium",
                "category": "dos",
                "intent_risk": 1,
                "capability_risk": 1,
                "file": record.relpath,
                "line": None,
                "view": "inventory",
                "evidence": f"{record.size} bytes",
                "why_it_matters": "Large files can hide payloads or create review cost.",
                "recommended_action": "Inspect the full file manually if it is relevant.",
            }
        )
        next_id += 1
    if record.path.name in ENTRYPOINT_NAMES or ".github/workflows/" in record.relpath or ".git/hooks/" in record.relpath:
        findings.append(
            {
                "id": f"F{next_id:03d}",
                "title": "High-risk review target",
                "severity": "low",
                "category": "supply_chain",
                "intent_risk": 0,
                "capability_risk": 1,
                "file": record.relpath,
                "line": None,
                "view": "inventory",
                "evidence": record.path.name,
                "why_it_matters": "This file type can affect installation, execution, CI, or skill behavior.",
                "recommended_action": "Review this file manually even if no pattern matched.",
            }
        )
    return findings


def derive_capabilities(findings: list[dict]) -> dict[str, bool]:
    categories = {finding["category"] for finding in findings}
    text = "\n".join(finding.get("evidence") or "" for finding in findings).lower()
    return {
        "network": "exfiltration" in categories or "http" in text or "curl" in text or "wget" in text,
        "shell": "code_execution" in categories or "shell" in text or "subprocess" in text,
        "file_read": "secret_access" in categories or "cat " in text or "read " in text,
        "file_write": any(token in text for token in (">", "write", "chmod", "tee ", "open(")),
        "secret_access": "secret_access" in categories,
        "persistence": "persistence" in categories,
        "ci_modification": "ci_compromise" in categories,
    }


def correlate_findings(findings: list[dict]) -> list[dict]:
    by_file: dict[str, set[str]] = {}
    for finding in findings:
        by_file.setdefault(finding["file"], set()).add(finding["category"])
    correlated = list(findings)
    next_id = len(correlated) + 1
    combos = [
        ({"secret_access", "exfiltration"}, "Secret access plus network path", "critical"),
        ({"code_execution", "exfiltration"}, "Code execution plus network path", "high"),
        ({"code_execution", "persistence"}, "Code execution plus persistence", "critical"),
        ({"ci_compromise", "secret_access"}, "CI access plus secrets", "critical"),
        ({"prompt_control", "obfuscation"}, "Hidden or obfuscated prompt control", "high"),
    ]
    for file, categories in by_file.items():
        for required, title, severity in combos:
            if required.issubset(categories):
                correlated.append(
                    {
                        "id": f"F{next_id:03d}",
                        "title": title,
                        "severity": severity,
                        "category": "exfiltration" if "exfiltration" in required else next(iter(required)),
                        "intent_risk": 3 if severity == "critical" else 2,
                        "capability_risk": 3,
                        "file": file,
                        "line": None,
                        "view": "correlation",
                        "evidence": f"Combined categories: {', '.join(sorted(required))}",
                        "why_it_matters": "Combined signals form a stronger capability-abuse chain than isolated matches.",
                        "recommended_action": "Treat as unsafe until the chain is removed or conclusively disproven.",
                    }
                )
                next_id += 1
    return correlated


def derive_verdict(findings: list[dict], records: list[FileRecord]) -> str:
    severities = [finding["severity"] for finding in findings]
    if "critical" in severities:
        return "unsafe"
    high_count = severities.count("high")
    if high_count >= 2:
        return "unsafe"
    if high_count or "medium" in severities or any(record.skipped_reason for record in records):
        return "caution"
    return "safe"


def scan(target: Path) -> dict:
    root = target.resolve()
    records = collect_files(root)
    findings: list[dict] = []
    decoded_artifacts: list[dict] = []

    for record in records:
        findings.extend(special_findings(record, len(findings) + 1))
        views = base_views(record)
        all_views = list(views)
        for view in views:
            decoded = decode_blobs(view)
            all_views.extend(decoded)
            for decoded_view in decoded:
                decoded_artifacts.append(
                    {
                        "file": decoded_view.file.relpath,
                        "encoding": decoded_view.name,
                        "sha256": hashlib.sha256(decoded_view.text.encode("utf-8", errors="replace")).hexdigest(),
                        "preview": decoded_view.text[:220].replace("\n", "\\n"),
                    }
                )
        for view in all_views:
            findings.extend(scan_patterns(view, len(findings) + 1))

    findings = correlate_findings(findings)
    capabilities = derive_capabilities(findings)
    verdict = derive_verdict(findings, records)
    scanned = [record for record in records if record.text_like]
    skipped = [record for record in records if not record.text_like or record.skipped_reason]
    unknowns = ["Static scan cannot determine runtime behavior of dependencies."]
    if skipped:
        unknowns.append("Some binary, non-text, or large files were not fully scanned.")

    inventory_files = [
        {
            "path": record.relpath,
            "size": record.size,
            "extension": record.extension,
            "sha256": record.sha256,
            "text_like": record.text_like,
            "skipped_reason": record.skipped_reason,
        }
        for record in records
    ]

    return {
        "schema_version": "1.0",
        "target": str(root),
        "scan_started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "verdict": verdict,
        "summary": f"Static triage found {len(findings)} findings across {len(records)} files.",
        "inventory": {
            "files_total": len(records),
            "files_scanned": len(scanned),
            "files_skipped": len(skipped),
            "large_files": [record.relpath for record in records if record.skipped_reason],
            "entrypoints": [record.relpath for record in records if record.path.name in ENTRYPOINT_NAMES],
            "files": inventory_files,
        },
        "capabilities_observed": capabilities,
        "findings": findings,
        "decoded_artifacts": decoded_artifacts,
        "unknowns": unknowns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Static signal scanner for untrusted agent skills.")
    parser.add_argument("target", help="Skill directory, repository, or single file to scan")
    parser.add_argument("--json", dest="json_path", help="Write JSON report to a new file under the system temp directory")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Target not found: {target}", file=sys.stderr)
        return 2

    report = scan(target)
    output = json.dumps(report, indent=2, sort_keys=True)
    if args.json_path:
        json_path = Path(args.json_path).expanduser().resolve()
        temp_root = Path(gettempdir()).resolve()
        if not json_path.is_relative_to(temp_root):
            print(f"--json path must be under {temp_root}", file=sys.stderr)
            return 2
        if json_path.exists():
            print(f"Refusing to overwrite existing report: {json_path}", file=sys.stderr)
            return 2
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(output + "\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
