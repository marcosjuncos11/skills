#!/usr/bin/env python3
"""Validate every SKILL.md and manifest in this repo.

Catches the mistakes that are invisible until someone tries to install:
malformed frontmatter (Claude Code loads the body with empty metadata, so the
skill works by name but never auto-triggers), reference links pointing at files
that moved, and manifests that disagree with the directory layout.
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def check_skill(skill_md: Path) -> None:
    text = skill_md.read_text()
    if not text.startswith("---"):
        errors.append(f"{rel(skill_md)}: no YAML frontmatter")
        return

    _, raw, body = text.split("---", 2)
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"{rel(skill_md)}: frontmatter is not valid YAML — {exc}")
        return

    if not isinstance(fm, dict):
        errors.append(f"{rel(skill_md)}: frontmatter is not a mapping")
        return

    if not fm.get("description"):
        errors.append(f"{rel(skill_md)}: missing description — the skill will never auto-trigger")
    elif len(fm["description"]) > 1024:
        warnings.append(
            f"{rel(skill_md)}: description is {len(fm['description'])} chars; "
            "the listing truncates at 1536 including when_to_use"
        )

    extensions = set(fm) - SPEC_FIELDS
    if extensions:
        warnings.append(
            f"{rel(skill_md)}: uses Claude Code-only fields {sorted(extensions)} — "
            "strip these before packaging for claude.ai"
        )

    # Every referenced sibling file must exist, or a pass silently loads nothing.
    for target in re.findall(r"`(references/[\w./-]+\.md)`", body):
        if not (skill_md.parent / target).exists():
            errors.append(f"{rel(skill_md)}: references missing file {target}")

    for orphan in skill_md.parent.glob("references/*.md"):
        if orphan.name not in body:
            warnings.append(f"{rel(orphan)}: never referenced from SKILL.md, so it will never load")


def check_manifests() -> None:
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    if not marketplace.exists():
        errors.append("missing .claude-plugin/marketplace.json")
        return

    data = json.loads(marketplace.read_text())
    plugin_root = ROOT / data.get("metadata", {}).get("pluginRoot", ".").lstrip("./")

    for entry in data.get("plugins", []):
        src = plugin_root / str(entry["source"]).lstrip("./")
        if not src.is_dir():
            errors.append(f"marketplace.json: plugin '{entry['name']}' source {src} does not exist")
            continue

        manifest = src / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            warnings.append(f"{rel(src)}: no plugin.json (fine only with strict: false)")
            continue

        pm = json.loads(manifest.read_text())
        if pm.get("name") != entry["name"]:
            errors.append(
                f"{rel(manifest)}: name '{pm.get('name')}' does not match "
                f"marketplace entry '{entry['name']}' — the slug is immutable once published"
            )
        if pm.get("version") != entry.get("version"):
            warnings.append(
                f"{rel(manifest)}: version {pm.get('version')} differs from "
                f"marketplace entry {entry.get('version')}"
            )


def main() -> int:
    skills = sorted(ROOT.glob("plugins/*/skills/*/SKILL.md"))
    if not skills:
        errors.append("no SKILL.md found under plugins/*/skills/*/")
    for skill in skills:
        check_skill(skill)
    check_manifests()

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error:   {e}")

    print(f"\n{len(skills)} skill(s) checked — {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
