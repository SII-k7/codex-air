#!/usr/bin/env bash
# Read-only validation for explicitly named paths in the active worktree.
# The generated patch is checked but never applied or transferred.
set -euo pipefail
IFS=$'\n\t'

die() {
  printf 'persist-visible-candidate: %s\n' "$1" >&2
  exit 1
}

hash_stream() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk '{print $1}'
  else
    die 'SHA-256 utility unavailable'
  fi
}

path_identity() {
  local path="$1"
  if [[ -L "$path" ]]; then
    printf 'symlink:%s' "$(readlink "$path" | hash_stream)"
  elif [[ -f "$path" ]]; then
    printf 'file:%s' "$(hash_stream <"$path")"
  elif [[ ! -e "$path" ]]; then
    printf 'absent'
  else
    die "unsupported changed path type: $path"
  fi
}

[[ $# -ge 1 ]] || {
  printf 'Usage: persist-visible-candidate.sh [--workspace] ABSOLUTE_WORKSPACE [--] RELATIVE_PATH...\n' >&2
  exit 2
}
if [[ "$1" == --workspace ]]; then
  [[ $# -ge 2 ]] || die '--workspace requires an absolute path'
  workspace="$2"
  shift 2
else
  workspace="$1"
  shift
fi
if [[ "${1:-}" == -- ]]; then
  shift
fi
[[ $# -ge 1 ]] || die 'at least one exact relative path is required; automatic discovery is disabled'
[[ "$workspace" == /* && "$workspace" != / ]] || die 'workspace must be a non-root absolute path'
workspace=$(CDPATH= cd -- "$workspace" && pwd -P) || die 'workspace cannot be resolved'
repo_root=$(git -C "$workspace" rev-parse --show-toplevel 2>/dev/null) || die 'workspace is not a Git worktree'
repo_root=$(CDPATH= cd -- "$repo_root" && pwd -P) || die 'Git root cannot be resolved'
[[ "$repo_root" == "$workspace" ]] || die 'workspace must be the Git worktree root'

paths=("$@")
identities=()
validated_paths=()
for path in "${paths[@]}"; do
  [[ -n "$path" && "$path" != /* && "$path" != -* ]] || die "invalid relative path: $path"
  [[ "$path" != *$'\n'* && "$path" != *$'\r'* && "$path" != *$'\t'* ]] || die 'control characters are not allowed in paths'
  [[ "$path" != */ && "$path" != *//* ]] || die "non-canonical relative path: $path"
  case "/$path/" in
    */../*|*/./*) die "non-canonical relative path: $path" ;;
  esac
  for existing in "${validated_paths[@]-}"; do
    [[ -n "$existing" ]] || continue
    [[ "$existing" != "$path" ]] || die "duplicate path: $path"
  done
  validated_paths+=("$path")
done
paths=("${validated_paths[@]}")

cd -- "$workspace"
for path in "${paths[@]}"; do
  identities+=("$(path_identity "$path")")
done

patch_file=$(mktemp "${TMPDIR:-/tmp}/codex-air-visible-candidate.XXXXXX") || die 'cannot create temporary patch'
cleanup() {
  rm -f -- "$patch_file"
}
trap cleanup EXIT HUP INT TERM

for path in "${paths[@]}"; do
  patch_size_before=$(wc -c <"$patch_file")
  if GIT_LITERAL_PATHSPECS=1 git ls-files --error-unmatch -- "$path" >/dev/null 2>&1; then
    GIT_LITERAL_PATHSPECS=1 git diff --binary --full-index --no-ext-diff --no-renames HEAD -- "$path" >>"$patch_file"
  elif [[ -e "$path" || -L "$path" ]]; then
    diff_status=0
    git diff --no-index --binary --full-index -- /dev/null "$path" >>"$patch_file" || diff_status=$?
    [[ "$diff_status" == 1 ]] || die "cannot snapshot untracked path: $path"
  else
    die "path is absent and untracked, so no candidate change can be persisted: $path"
  fi
  patch_size_after=$(wc -c <"$patch_file")
  [[ "$patch_size_after" -gt "$patch_size_before" ]] || die "path has no candidate change relative to HEAD: $path"
done

[[ -s "$patch_file" ]] || die 'changed paths produced an empty candidate patch'
git apply --reverse --check --binary "$patch_file" || die 'candidate patch cannot reverse from the visible final state'

for index in "${!paths[@]}"; do
  actual=$(path_identity "${paths[index]}")
  [[ "$actual" == "${identities[index]}" ]] || die "final identity changed during validation: ${paths[index]}"
  printf 'PERSISTED\t%s\t%s\n' "${paths[index]}" "$actual"
done
printf 'PERSISTENCE_PASS\tpaths=%s\n' "${#paths[@]}"
