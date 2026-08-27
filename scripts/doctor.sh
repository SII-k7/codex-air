#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)

usage() {
  printf 'Usage: doctor.sh [--json] [--require-codex] [--help]\n'
  printf 'Diagnose the source, installed bundle, routing, and Codex CLI without exposing local paths.\n'
}

json_only=0
require_codex=0
for argument in "$@"; do
  case "$argument" in
    --json) json_only=1 ;;
    --require-codex) require_codex=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 1 ;;
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

codex_available=0
codex_version=unknown
if command -v codex >/dev/null 2>&1; then
  codex_available=1
  if version_output=$(codex --version 2>&1); then
    codex_version=${version_output:0:512}
  else
    codex_version='version query failed'
  fi
fi

"$python_bin" - "$base_dir" "$REPO_ROOT" "$json_only" "$require_codex" "$codex_available" "$codex_version" <<'PY'
from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

home = Path(sys.argv[1])
repo = Path(sys.argv[2])
json_only = sys.argv[3] == "1"
require_codex = sys.argv[4] == "1"
codex_available = sys.argv[5] == "1"


def safe_text(value: str, *, fallback: str = "unknown", limit: int = 160) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", value).strip()
    return cleaned[:limit] if cleaned else fallback


raw_codex_version = safe_text(sys.argv[6])
if raw_codex_version == "version query failed":
    codex_version = raw_codex_version
else:
    version_match = re.search(
        r"(?<![0-9A-Za-z])([0-9]+(?:\.[0-9]+){1,3}(?:[-+][0-9A-Za-z.-]+)?)(?![0-9A-Za-z])",
        raw_codex_version,
    )
    codex_version = version_match.group(1) if version_match else "unrecognized"
errors: list[str] = []
warnings: list[str] = []

release_pattern = re.compile(r"^[0-9A-Za-z][0-9A-Za-z.+-]{0,63}$")
commit_pattern = re.compile(r"^[0-9a-f]{40,64}$")

try:
    source_release = (repo / "VERSION").read_text(encoding="utf-8").strip()
except OSError:
    source_release = "unknown"
    errors.append("source VERSION is unavailable")
if source_release != "unknown" and not release_pattern.fullmatch(source_release):
    source_release = "unknown"
    errors.append("source VERSION is invalid")

source_commit = "unknown"
source_dirty: bool | None = None
try:
    commit_result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    candidate = commit_result.stdout.strip()
    if commit_result.returncode == 0 and commit_pattern.fullmatch(candidate):
        source_commit = candidate
        dirty_result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), "status", "--porcelain", "--untracked-files=normal"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if dirty_result.returncode == 0:
            source_dirty = bool(dirty_result.stdout)
except (OSError, subprocess.SubprocessError):
    pass


def read_state(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        if "=" not in line:
            raise ValueError("invalid state")
        key, value = line.split("=", 1)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or key in values:
            raise ValueError("invalid state")
        values[key] = value
    return values


state_path = home / ".codex/codex-air/install-state"
installed_state_visible = state_path.is_file() and not state_path.is_symlink()
state: dict[str, str] = {}
if installed_state_visible:
    try:
        state = read_state(state_path)
    except (OSError, UnicodeError, ValueError):
        errors.append("installed state is invalid")
else:
    errors.append("installed state is missing or unsafe")

state_format = state.get("version", "unknown")
if state and state_format != "7":
    errors.append("installed state format is unsupported")

installed_release = state.get("release_version", "unknown")
if installed_release != "unknown" and not release_pattern.fullmatch(installed_release):
    warnings.append("installed release metadata is invalid")
    installed_release = "unknown"
installed_commit = state.get("source_commit", "unknown")
if installed_commit != "unknown" and not commit_pattern.fullmatch(installed_commit):
    warnings.append("installed commit metadata is invalid")
    installed_commit = "unknown"
dirty_value = state.get("source_dirty", "unknown")
installed_dirty: bool | None
if dirty_value == "true":
    installed_dirty = True
elif dirty_value == "false":
    installed_dirty = False
else:
    installed_dirty = None
    if dirty_value != "unknown":
        warnings.append("installed dirty-state metadata is invalid")
if installed_release == "unknown" and state_format == "7":
    warnings.append("installed release metadata predates provenance reporting")
elif source_release != "unknown" and installed_release != source_release:
    warnings.append("installed release differs from this source checkout")
if installed_dirty is True:
    warnings.append("installed bundle came from a dirty source checkout")

skill_paths = {
    "canonical": home / ".agents/skills/codex-air/SKILL.md",
    "compatibility": home / ".agents/skills/codex-prove/SKILL.md",
}
skill_visibility = {
    name: path.is_file() and not path.is_symlink() for name, path in skill_paths.items()
}
if not all(skill_visibility.values()):
    errors.append("one or more installed Skill entrypoints are missing or unsafe")

expected = {
    "air-controller.toml": ("air-controller", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
    "air-critical-controller.toml": ("air-critical-controller", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
    "air-complex-worker.toml": ("air-complex-worker", "gpt-5.6-luna", "max", 272000, 244800, "fast", "workspace-write"),
    "air-efficient-worker.toml": ("air-efficient-worker", "gpt-5.6-luna", "max", 272000, 244800, "fast", "workspace-write"),
    "air-challenger.toml": ("air-challenger", "gpt-5.6-sol", "xhigh", 272000, 244800, "default", "read-only"),
}
agent_visibility: dict[str, dict[str, bool]] = {}
for filename, values in expected.items():
    path = home / ".codex/agents" / filename
    visible = path.is_file() and not path.is_symlink()
    matches = False
    if visible:
        try:
            with path.open("rb") as handle:
                data = tomllib.load(handle)
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
            matches = actual == values
        except (OSError, tomllib.TOMLDecodeError):
            matches = False
    agent_visibility[filename] = {"visible": visible, "profile_matches": matches}
if not all(item["visible"] and item["profile_matches"] for item in agent_visibility.values()):
    errors.append("one or more installed agent profiles are missing, unsafe, or mismatched")

configuration_ok = True
config_path = home / ".codex/config.toml"
if config_path.exists():
    if config_path.is_symlink() or not config_path.is_file():
        errors.append("Codex config is unsafe")
        configuration_ok = False
    else:
        try:
            with config_path.open("rb") as handle:
                config = tomllib.load(handle)
            if config.get("features", {}).get("multi_agent") is False:
                errors.append("Codex config explicitly disables features.multi_agent")
                configuration_ok = False
            if config.get("agents", {}).get("enabled") is False:
                errors.append("Codex config explicitly disables agents.enabled")
                configuration_ok = False
            limit = config.get("agents", {}).get("max_concurrent_threads_per_session")
            if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
                errors.append("Codex agent concurrency must be a positive integer")
                configuration_ok = False
        except (OSError, tomllib.TOMLDecodeError):
            errors.append("Codex config is invalid")
            configuration_ok = False

explicit_only = True
agents_path = home / ".codex/AGENTS.md"
if agents_path.is_symlink():
    errors.append("global Codex instructions are unsafe")
    explicit_only = False
elif agents_path.exists():
    try:
        instructions = agents_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        errors.append("global Codex instructions are unreadable")
        explicit_only = False
    else:
        legacy_markers = (
            "<!-- codex-air-default:start -->",
            "<!-- codex-air-default:end -->",
            "<!-- codex-prove-default:start -->",
            "<!-- codex-prove-default:end -->",
            "<!-- sol-control-default:start -->",
            "<!-- sol-control-default:end -->",
        )
        if any(marker in instructions for marker in legacy_markers):
            errors.append(
                "legacy Codex AIR global default routing is enabled; "
                "run bash scripts/default.sh disable"
            )
            explicit_only = False

if require_codex and not codex_available:
    errors.append("codex is not available on PATH")
if codex_available and codex_version == "version query failed":
    warnings.append("Codex CLI version query failed")
elif codex_available and codex_version == "unrecognized":
    warnings.append("Codex CLI returned an unrecognized version")

report = {
    "schema_version": 1,
    "status": "pass" if not errors else "fail",
    "source": {
        "release_version": source_release,
        "commit": source_commit,
        "dirty": source_dirty,
    },
    "installed": {
        "state_visible": installed_state_visible,
        "state_format": state_format,
        "release_version": installed_release,
        "source_commit": installed_commit,
        "source_dirty": installed_dirty,
    },
    "codex_cli": {"available": codex_available, "version": codex_version},
    "bundle": {
        "skills": skill_visibility,
        "agents": agent_visibility,
        "all_visible_and_matching": all(skill_visibility.values())
        and all(item["visible"] and item["profile_matches"] for item in agent_visibility.values()),
    },
    "configuration": {"multi_agent_not_disabled": configuration_ok},
    "routing": {"explicit_only": explicit_only},
    "warnings": warnings,
    "errors": errors,
}
encoded = json.dumps(report, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

if json_only:
    print(encoded)
else:
    print(f"Source version: {source_release} ({source_commit})")
    print(f"Installed version: {installed_release} ({installed_commit})")
    cli_label = f"AVAILABLE ({codex_version})" if codex_available else "UNAVAILABLE"
    print(f"Codex CLI: {cli_label}")
    bundle_ok = report["bundle"]["all_visible_and_matching"]
    print(f"Installed Skill and five agent profiles: {'PASS' if bundle_ok else 'FAIL'}")
    print(f"Codex multi-agent configuration is not disabled: {'PASS' if configuration_ok else 'FAIL'}")
    print(f"Codex AIR subagent context isolation: {'PASS' if bundle_ok else 'FAIL'}")
    print(f"Codex AIR explicit-only routing: {'PASS' if explicit_only else 'FAIL'}")
    for warning in warnings:
        print(f"Doctor warning: {warning}")
    for error in errors:
        print(f"Doctor error: {error}")
    print(f"Doctor JSON: {encoded}")
    print(f"Doctor: {'PASS' if not errors else 'FAIL'}")
    if not errors:
        print("Restart Codex, verify $codex-air in /skills, then inspect agents with /agent.")
        print("Exact model entitlement, actual service tier, and runtime selection require authoritative live launch telemetry.")

raise SystemExit(0 if not errors else 1)
PY
