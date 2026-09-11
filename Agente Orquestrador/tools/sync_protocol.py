#!/usr/bin/env python3
"""
sync_protocol.py: Synchronizes messaging_protocol.md to all skills' memory/ folders.

Usage:
    python "Agente Orquestrador/tools/sync_protocol.py"

This script copies the canonical `messaging_protocol.md` from `Agente Orquestrador/Resumo do projeto/`
into the `memory/` directory of every skill under `.agents/skills/`.

Run this script every time the messaging_protocol.md is updated to propagate
the changes across the entire ecosystem.
"""

import shutil
from pathlib import Path

# Resolve paths relative to workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_FILE = WORKSPACE_ROOT / "Agente Orquestrador" / "Resumo do projeto" / "messaging_protocol.md"
SKILLS_DIR = WORKSPACE_ROOT / ".agents" / "skills"

# Skills to exclude from sync (deprecated or non-agent skills)
EXCLUDED_SKILLS = {"fullstack-dev"}


def sync():
    if not SOURCE_FILE.exists():
        print(f"ERROR: Source file not found: {SOURCE_FILE}")
        return

    if not SKILLS_DIR.exists():
        print(f"ERROR: Skills directory not found: {SKILLS_DIR}")
        return

    skill_dirs = sorted(
        [d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name not in EXCLUDED_SKILLS]
    )

    synced = 0
    skipped = 0

    for skill_dir in skill_dirs:
        memory_dir = skill_dir / "memory"

        # Create memory/ if it doesn't exist
        if not memory_dir.exists():
            memory_dir.mkdir(parents=True, exist_ok=True)
            print(f"  CREATED: {memory_dir}")

        dest_file = memory_dir / "messaging_protocol.md"
        shutil.copy2(SOURCE_FILE, dest_file)
        synced += 1
        print(f"  SYNCED:  {skill_dir.name}/memory/messaging_protocol.md")

    print(f"\n--- Sync Complete ---")
    print(f"  Synced:  {synced} skills")
    print(f"  Source:  {SOURCE_FILE}")


if __name__ == "__main__":
    sync()
