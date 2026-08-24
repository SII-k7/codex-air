#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)

require_codex=0
for argument in "$@"; do
  case "$argument" in
    --require-codex) require_codex=1 ;;
    *) printf 'Usage: doctor.sh [--require-codex]\n' >&2; exit 1 ;;
  esac
done

die() {
  printf 'doctor.sh: %s\n' "$1" >&2
  exit 1
}

raw_home=${ORCHESTRATE_HOME:-${HOME:-}}
[[ -n "$raw_home" && "$raw_home" == /* && "$raw_home" != / ]] || die 'ORCHESTRATE_HOME must be a non-root absolute path'
[[ -d "$raw_home" && ! -L "$raw_home" ]] || die 'ORCHESTRATE_HOME is missing or unsafe'
base_dir=$(CDPATH= cd -- "${raw_home%/}" && pwd -P) || die 'cannot resolve ORCHESTRATE_HOME'

python_bin=
for candidate in python3.14 python3.13 python3.12 python3.11 python3 python; do
  candidate_path=$(command -v "$candidate" 2>/dev/null || true)
  if [[ -n "$candidate_path" ]] && "$candidate_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    python_bin="$candidate_path"
    break
  fi
done
[[ -n "$python_bin" ]] || die 'Python 3.11 or newer is required'

"$python_bin" - "$base_dir" <<'PY'
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

home = Path(sys.argv[1])
skill = home / ".agents/skills/codex-air/SKILL.md"
alias = home / ".agents/skills/codex-prove/SKILL.md"
expected = {
    "air-controller.toml": ("air-controller", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
    "air-critical-controller.toml": ("air-critical-controller", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
    "air-complex-worker.toml": ("air-complex-worker", "gpt-5.6-luna", "max", 272000, 244800, "fast", "workspace-write"),
    "air-efficient-worker.toml": ("air-efficient-worker", "gpt-5.6-luna", "max", 272000, 244800, "fast", "workspace-write"),
    "air-challenger.toml": ("air-challenger", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
}

for path in (skill, alias):
    if not path.is_file():
        raise SystemExit(f"missing installed Skill: {path}")

for filename, values in expected.items():
    path = home / ".codex/agents" / filename
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"missing installed agent: {path}")
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"invalid agent TOML {path}: {exc}") from exc
    actual = tuple(
        data.get(key)
        for key in (
            "name",
            "model",
            "model_reasoning_effort",
            "model_context_window",
            "model_auto_compact_token_limit",
            "service_tier",
            "sandbox_mode",
        )
    )
    if actual != values:
        raise SystemExit(f"agent profile mismatch in {path}: expected {values!r}, got {actual!r}")

config_path = home / ".codex/config.toml"
if config_path.exists():
    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"invalid Codex config {config_path}: {exc}") from exc
    if config.get("features", {}).get("multi_agent") is False:
        raise SystemExit("~/.codex/config.toml explicitly disables features.multi_agent")
    if config.get("agents", {}).get("enabled") is False:
        raise SystemExit("~/.codex/config.toml explicitly disables agents.enabled")
    limit = config.get("agents", {}).get("max_concurrent_threads_per_session")
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
        raise SystemExit("agents.max_concurrent_threads_per_session must be a positive integer")

agents_path = home / ".codex/AGENTS.md"
if agents_path.is_symlink():
    raise SystemExit("~/.codex/AGENTS.md must not be a symbolic link")
if agents_path.exists():
    instructions = agents_path.read_text(encoding="utf-8")
    legacy_markers = (
        "<!-- codex-air-default:start -->",
        "<!-- codex-air-default:end -->",
        "<!-- codex-prove-default:start -->",
        "<!-- codex-prove-default:end -->",
        "<!-- sol-control-default:start -->",
        "<!-- sol-control-default:end -->",
    )
    if any(marker in instructions for marker in legacy_markers):
        raise SystemExit(
            "legacy Codex AIR global default routing is enabled; "
            "run bash scripts/default.sh disable"
        )

print("Installed Skill and five agent profiles: PASS")
print("Codex multi-agent configuration is not disabled: PASS")
print("Codex AIR subagent context isolation: PASS")
print("Codex AIR explicit-only routing: PASS")
PY

if (( require_codex )); then
  command -v codex >/dev/null 2>&1 || die 'codex is not available on PATH'
  codex --version
fi

printf 'Doctor: PASS\n'
printf 'Restart Codex, verify $codex-air in /skills, then inspect agents with /agent.\n'
printf 'Exact model entitlement, actual service tier, and runtime selection require authoritative live launch telemetry.\n'
