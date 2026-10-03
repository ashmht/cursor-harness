#!/usr/bin/env python3
"""Install the portable rules, skills, and hooks into a Cursor home."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_GROUPS = (
    (REPO_ROOT / ".cursor" / "rules", Path("rules")),
    (REPO_ROOT / ".cursor" / "skills", Path("skills")),
    (REPO_ROOT / "hooks", Path("hooks")),
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for source_root, target_root in SOURCE_GROUPS:
        for source in sorted(source_root.rglob("*")):
            if source.is_symlink():
                raise ValueError(f"Refusing symlink source: {source}")
            if source.is_file() and "__pycache__" not in source.parts:
                files.append((source, target_root / source.relative_to(source_root)))
    return files


def backup_path(target: Path, timestamp: str) -> Path:
    candidate = target.with_name(f"{target.name}.bak-{timestamp}")
    counter = 2
    while candidate.exists():
        candidate = target.with_name(f"{target.name}.bak-{timestamp}-{counter}")
        counter += 1
    return candidate


def install(target_root: Path, *, apply: bool, force: bool) -> int:
    target_root = target_root.expanduser().resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    unsafe_conflicts: list[Path] = []
    existing_conflicts: list[Path] = []
    plan: list[tuple[Path, Path]] = []
    unchanged = 0

    for source, relative in source_files():
        target = target_root / relative
        if target.is_symlink():
            unsafe_conflicts.append(target)
            continue

        if target.exists() and digest(source) == digest(target):
            unchanged += 1
            continue

        if target.exists() and not force:
            existing_conflicts.append(target)
            continue

        plan.append((source, target))

    for target in unsafe_conflicts:
        print(f"CONFLICT symlink {target}")
    for target in existing_conflicts:
        print(f"CONFLICT exists {target}")
    for _, target in plan:
        action = "UPDATE" if target.exists() else "CREATE"
        print(f"{action} {target}")

    conflicts = len(unsafe_conflicts) + len(existing_conflicts)
    mode = "apply blocked" if apply else "dry-run"
    if conflicts:
        print(
            f"{mode}: {len(plan)} planned, {unchanged} unchanged, "
            f"{conflicts} conflicts"
        )
        if unsafe_conflicts:
            print("Symlink conflicts must be resolved manually.", file=sys.stderr)
        elif not force:
            print(
                "Re-run with --force to back up and replace existing files.",
                file=sys.stderr,
            )
        return 2

    if not apply:
        print(f"dry-run: {len(plan)} changes, {unchanged} unchanged, 0 conflicts")
        return 0

    for source, target in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = backup_path(target, timestamp)
            shutil.copy2(target, backup)
            print(f"BACKUP {backup}")
        shutil.copy2(source, target)

    print(f"applied: {len(plan)} changes, {unchanged} unchanged, 0 conflicts")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".cursor",
        help="Cursor home to update (default: ~/.cursor)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform the installation. Without this flag, only print the plan.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Back up and replace files that already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return install(args.target, apply=args.apply, force=args.force)
    except (OSError, ValueError) as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
