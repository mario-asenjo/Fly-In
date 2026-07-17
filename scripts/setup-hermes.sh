#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
INSTALL_SOUL=false

if [[ "${1:-}" == "--install-soul" ]]; then
  INSTALL_SOUL=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--install-soul]" >&2
  exit 2
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "Hermes is not installed or is not on PATH." >&2
  echo "Install/configure Hermes first, then rerun this script." >&2
  exit 1
fi

mkdir -p "$HERMES_HOME_DIR/skills" "$HERMES_HOME_DIR/skill-bundles" \
  "$HERMES_HOME_DIR/memories"

SKILL_TARGET="$HERMES_HOME_DIR/skills/flyin"
if [[ -L "$SKILL_TARGET" ]]; then
  ln -sfn "$ROOT/.agents/skills" "$SKILL_TARGET"
elif [[ -e "$SKILL_TARGET" ]]; then
  echo "Keeping existing non-symlink skill directory: $SKILL_TARGET" >&2
  echo "Remove or move it manually if you want this repository-linked catalog." >&2
else
  ln -s "$ROOT/.agents/skills" "$SKILL_TARGET"
fi

for source in "$ROOT"/.agents/skill-bundles/*.yaml; do
  target="$HERMES_HOME_DIR/skill-bundles/$(basename "$source")"
  if [[ -L "$target" || ! -e "$target" ]]; then
    ln -sfn "$source" "$target"
  else
    echo "Keeping existing bundle file: $target" >&2
  fi
done

if [[ ! -e "$HERMES_HOME_DIR/memories/MEMORY.md" ]]; then
  cp "$ROOT/hermes/MEMORY.seed.md" "$HERMES_HOME_DIR/memories/MEMORY.md"
  echo "Seeded MEMORY.md"
else
  echo "Existing MEMORY.md preserved; review hermes/MEMORY.seed.md and merge useful entries."
fi

if [[ ! -e "$HERMES_HOME_DIR/memories/USER.md" ]]; then
  cp "$ROOT/hermes/USER.seed.md" "$HERMES_HOME_DIR/memories/USER.md"
  echo "Seeded USER.md"
else
  echo "Existing USER.md preserved; review hermes/USER.seed.md and merge useful entries."
fi

if [[ "$INSTALL_SOUL" == true ]]; then
  if [[ -e "$HERMES_HOME_DIR/SOUL.md" ]]; then
    backup="$HERMES_HOME_DIR/SOUL.md.backup.$(date +%Y%m%d%H%M%S)"
    cp "$HERMES_HOME_DIR/SOUL.md" "$backup"
    echo "Backed up existing SOUL.md to: $backup"
  fi
  cp "$ROOT/hermes/SOUL.flyin.md" "$HERMES_HOME_DIR/SOUL.md"
  echo "Installed Fly-In SOUL.md globally for this Hermes home."
elif [[ -e "$HERMES_HOME_DIR/SOUL.md" ]]; then
  echo "Existing SOUL.md preserved. Optional Fly-In template: hermes/SOUL.flyin.md"
else
  echo "SOUL.md not changed. Rerun with --install-soul after reviewing the template."
fi

echo "Installing/enabling official Ponytail plugin..."
hermes plugins install DietrichGebert/ponytail --enable

python3 "$ROOT/scripts/validate-context.py"

echo
echo "Hermes project setup complete."
echo "Restart Hermes so the Ponytail plugin hooks load, then start Hermes from:"
echo "  $ROOT"
echo "First prompt: docs/prompts/FIRST_SESSION.md"
