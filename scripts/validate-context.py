#!/usr/bin/env python3
"""Validate the Hermes/Fly-In context package without third-party packages."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "sources" / "MANIFEST.sha256"

REQUIRED = (
    "README.md",
    "AGENTS.md",
    "docs/project/02_SOURCE_OF_TRUTH.md",
    "docs/project/03_DOMAIN_CONTRACT.md",
    "docs/project/05_ROADMAP.md",
    "docs/project/10_EVALUATION_MATRIX.md",
    "docs/progress/CURRENT.md",
    "docs/progress/OPEN_QUESTIONS.md",
    "docs/prompts/FIRST_SESSION.md",
    "docs/sources/flyin_1.5.pdf",
    "docs/sources/fly-in_1.2.pdf",
    "docs/sources/Intra-Projects-Fly-in-Edit.pdf",
    "maps/provided-v12-snapshot/README_maps.md",
    "hermes/PONYTAIL.md",
)

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
NAME_RE = re.compile(r"^name:\s*([a-z0-9-]+)\s*$", re.MULTILINE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_required(errors: list[str]) -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"missing required path: {relative}")


def validate_readme(errors: list[str]) -> None:
    first = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[0]
    if not (first.startswith("*") and first.endswith(".*")):
        errors.append(
            "README first line is not the required italicized 42 statement"
        )


def validate_skills(errors: list[str]) -> None:
    skill_root = ROOT / ".agents" / "skills"
    skills = sorted(skill_root.glob("*/SKILL.md"))
    if len(skills) < 8:
        errors.append("expected at least eight project skills")
    for path in skills:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            errors.append(
                f"skill missing YAML frontmatter: {path.relative_to(ROOT)}"
            )
            continue
        match = NAME_RE.search(content)
        if match is None:
            errors.append(
                f"skill missing valid name: {path.relative_to(ROOT)}"
            )
        elif match.group(1) != path.parent.name:
            errors.append(
                f"skill name/folder mismatch: {path.relative_to(ROOT)}"
            )


def validate_context_size(errors: list[str]) -> None:
    for path in ROOT.rglob("AGENTS.md"):
        size = len(path.read_text(encoding="utf-8"))
        if size > 20_000:
            relative = path.relative_to(ROOT)
            errors.append(
                f"AGENTS context exceeds Hermes default 20k chars: {relative}"
            )


def validate_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(content):
            target = raw_target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(
                ("mailto:", "#", "<")
            ):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                relative = str(path.relative_to(ROOT))
                message = "link escapes repository: " + relative + " -> " + target
                errors.append(message)
                continue
            if not resolved.exists():
                errors.append(
                    f"broken link: {path.relative_to(ROOT)} -> {target}"
                )


def validate_manifest(errors: list[str]) -> None:
    if not MANIFEST.exists():
        errors.append("missing docs/sources/MANIFEST.sha256")
        return
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    numbered_lines = enumerate(lines, 1)
    for line_number, line in numbered_lines:
        if not line or line.startswith("#"):
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"invalid manifest line {line_number}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"manifest file missing: {relative}")
        elif sha256(path) != expected:
            errors.append(f"source snapshot changed: {relative}")


def main() -> int:
    errors: list[str] = []
    validate_required(errors)
    if (ROOT / "README.md").exists():
        validate_readme(errors)
    validate_skills(errors)
    validate_context_size(errors)
    validate_links(errors)
    validate_manifest(errors)

    if errors:
        print("Context validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Context validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
