#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
  printf 'Usage: default.sh status|check|disable|--help\n'
  printf 'Inspect or remove legacy global routing; Codex AIR remains explicit-only.\n'
}

if (( $# != 1 )); then
  usage >&2
  exit 1
fi
action=$1
case "$action" in
  status|check|disable) ;;
  -h|--help) usage; exit 0 ;;
  enable)
    printf 'default.sh: global default routing has been removed; invoke $codex-air explicitly\n' >&2
    exit 1
    ;;
  *) usage >&2; exit 1 ;;
esac

die() {
  printf 'default.sh: %s\n' "$1" >&2
  exit 1
}

raw_home=${ORCHESTRATE_HOME:-${HOME:-}}
[[ -n "$raw_home" && "$raw_home" == /* && "$raw_home" != / ]] || die 'ORCHESTRATE_HOME must be a non-root absolute path'
[[ ! -L "$raw_home" ]] || die 'ORCHESTRATE_HOME must not be a symbolic link'
raw_home=${raw_home%/}

python_bin=
for candidate in python3.14 python3.13 python3.12 python3.11 python3 python; do
  candidate_path=$(command -v "$candidate" 2>/dev/null || true)
  if [[ -n "$candidate_path" ]] && "$candidate_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    python_bin="$candidate_path"
    break
  fi
done
[[ -n "$python_bin" ]] || die 'Python 3.11 or newer is required'

"$python_bin" - "$raw_home" "$action" <<'PY'
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

home = Path(sys.argv[1])
action = sys.argv[2]
marker_pairs = (
    ("<!-- codex-air-default:start -->", "<!-- codex-air-default:end -->"),
    ("<!-- codex-prove-default:start -->", "<!-- codex-prove-default:end -->"),
    ("<!-- sol-control-default:start -->", "<!-- sol-control-default:end -->"),
)

if not home.exists():
    if action == "disable":
        print(f"Legacy default routing already disabled ({home / '.codex/AGENTS.md'})")
    else:
        print("Codex AIR explicit-only routing: PASS")
    raise SystemExit(0)
if home.is_symlink() or not home.is_dir():
    raise SystemExit("ORCHESTRATE_HOME is missing or unsafe")

codex_dir = home / ".codex"
agents_path = codex_dir / "AGENTS.md"
state_root = codex_dir / "codex-air" / "default-routing-backups"

if codex_dir.exists() and (codex_dir.is_symlink() or not codex_dir.is_dir()):
    raise SystemExit("~/.codex is unsafe")
if agents_path.is_symlink():
    raise SystemExit("~/.codex/AGENTS.md must not be a symbolic link")

current = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
active_pairs = [pair for pair in marker_pairs if pair[0] in current or pair[1] in current]
if not active_pairs:
    if action == "disable":
        print(f"Legacy default routing already disabled ({agents_path})")
    else:
        print("Codex AIR explicit-only routing: PASS")
    raise SystemExit(0)
if len(active_pairs) != 1:
    raise SystemExit("legacy default-routing markers are malformed or duplicated")
start, end = active_pairs[0]
if current.count(start) != 1 or current.count(end) != 1:
    raise SystemExit("legacy default-routing markers are malformed or duplicated")

if action in {"status", "check"}:
    raise SystemExit(
        "legacy Codex AIR global default routing is enabled; "
        "run bash scripts/default.sh disable"
    )

begin = current.index(start)
finish = current.index(end, begin) + len(end)
prefix, suffix = current[:begin], current[finish:]
updated = (prefix.rstrip("\n") + "\n\n" + suffix.lstrip("\n")).strip("\n")
if updated:
    updated += "\n"

codex_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{os.getpid()}"
backup_dir = state_root / backup_id
counter = 0
while backup_dir.exists():
    counter += 1
    backup_dir = state_root / f"{backup_id}-{counter}"
backup_dir.mkdir(mode=0o700)
if agents_path.exists():
    shutil.copy2(agents_path, backup_dir / "AGENTS.md")
else:
    (backup_dir / "AGENTS.absent").write_text("", encoding="utf-8")

if not updated:
    agents_path.unlink(missing_ok=True)
else:
    descriptor, temporary = tempfile.mkstemp(prefix=".AGENTS.md.", dir=codex_dir)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        if agents_path.exists():
            os.chmod(temporary, agents_path.stat().st_mode & 0o777)
        else:
            os.chmod(temporary, 0o600)
        os.replace(temporary, agents_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

print("Legacy default routing: disabled")
print("Codex AIR explicit-only routing: PASS")
print(f"Global instructions: {agents_path}")
print(f"Backup path: {backup_dir}")
PY
