#!/usr/bin/env bash
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
  printf 'Usage: persist-visible-candidate.sh [--workspace] ABSOLUTE_WORKSPACE [--] [RELATIVE_PATH...]\n' >&2
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
[[ "$workspace" == /* && "$workspace" != / ]] || die 'workspace must be a non-root absolute path'
workspace=$(CDPATH= cd -- "$workspace" && pwd -P) || die 'workspace cannot be resolved'
repo_root=$(git -C "$workspace" rev-parse --show-toplevel 2>/dev/null) || die 'workspace is not a Git worktree'
repo_root=$(CDPATH= cd -- "$repo_root" && pwd -P) || die 'Git root cannot be resolved'
[[ "$repo_root" == "$workspace" ]] || die 'workspace must be the Git worktree root'

paths=()
identities=()
if [[ $# -eq 0 ]]; then
  while IFS= read -r -d '' path; do
    paths+=("$path")
  done < <(git -C "$workspace" diff --name-only --no-renames -z HEAD --)
  while IFS= read -r -d '' path; do
    duplicate=0
    # Bash 3.2 (the macOS system Bash) treats an empty-array expansion as an
    # unbound variable under `set -u`. The `-` form keeps discovery portable;
    # the empty sentinel is ignored.
    for existing in "${paths[@]-}"; do
      [[ -n "$existing" ]] || continue
      if [[ "$existing" == "$path" ]]; then
        duplicate=1
        break
      fi
    done
    (( duplicate == 1 )) || paths+=("$path")
  done < <(git -C "$workspace" ls-files --others --exclude-standard -z --)
  [[ ${#paths[@]} -ge 1 ]] || die 'Git found no visible candidate changes'
else
  paths=("$@")
fi
validated_paths=()
for path in "${paths[@]}"; do
  [[ -n "$path" && "$path" != /* && "$path" != -* ]] || die "invalid relative path: $path"
  [[ "$path" != *$'\n'* && "$path" != *$'\r'* && "$path" != *$'\t'* ]] || die 'control characters are not allowed in paths'
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
  if [[ "${candidate_reversed:-0}" == 1 ]]; then
    git -C "$workspace" apply --binary "$patch_file" >/dev/null 2>&1 ||
      printf 'persist-visible-candidate: automatic final-state recovery failed\n' >&2
  fi
  rm -f -- "$patch_file"
}
trap cleanup EXIT HUP INT TERM

for path in "${paths[@]}"; do
  if git ls-files --error-unmatch -- "$path" >/dev/null 2>&1; then
    git diff --binary --full-index --no-ext-diff --no-renames HEAD -- "$path" >>"$patch_file"
  elif [[ -e "$path" || -L "$path" ]]; then
    diff_status=0
    git diff --no-index --binary --full-index -- /dev/null "$path" >>"$patch_file" || diff_status=$?
    [[ "$diff_status" == 1 ]] || die "cannot snapshot untracked path: $path"
  else
    die "path is absent and untracked, so no candidate change can be persisted: $path"
  fi
done

[[ -s "$patch_file" ]] || die 'changed paths produced an empty candidate patch'
git apply --reverse --check --binary "$patch_file" || die 'candidate patch cannot reverse from the visible final state'
git apply --reverse --binary "$patch_file" || die 'candidate reverse replay failed'
candidate_reversed=1
git apply --check --binary "$patch_file" || die 'candidate patch cannot reapply from the reconstructed baseline'
git apply --binary "$patch_file" || die 'candidate forward replay failed'
candidate_reversed=0

for index in "${!paths[@]}"; do
  actual=$(path_identity "${paths[index]}")
  [[ "$actual" == "${identities[index]}" ]] || die "final identity mismatch after replay: ${paths[index]}"
  printf 'PERSISTED\t%s\t%s\n' "${paths[index]}" "$actual"
done
printf 'PERSISTENCE_PASS\tpaths=%s\n' "${#paths[@]}"
