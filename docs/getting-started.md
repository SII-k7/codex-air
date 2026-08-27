# Getting started with Codex AIR

[简体中文](getting-started.zh-CN.md) · English

Codex AIR is an explicit Codex Skill for substantial coding work. Its fixed
runtime split is:

- Sol at `xhigh` understands the request, explores the repository, chooses the
  solution, decomposes the work, and reviews the final candidate;
- Luna at `max` with Fast requested performs bounded implementation, tests,
  and correction;
- Terra is not an AIR fallback and must receive zero calls and tokens.

AIR may keep a tiny or already-localized task Direct when dispatch would cost
more than the work. Invoke AIR explicitly with `$codex-air`; installation does
not make it a global default.

## Prerequisites

You need:

- Git and a current Codex CLI that supports Skills and custom subagents;
- an account or workspace entitled to use the configured Sol and Luna models;
- network access for GitHub during setup and for the Codex model service while
  working;
- macOS/Linux with Bash, or Windows with PowerShell 5.1 or newer;
- Python 3.11 or newer for POSIX validation, installation, and diagnostics.

The static doctor can verify installed profiles, but only a live launch can
prove model entitlement, selected model identity, and actual service tier.

By default, installation targets the home directory of the user running
Codex. Set `ORCHESTRATE_HOME` only when Codex itself uses a different absolute,
non-root home directory.

## Install the stable v1.2.0 release

Pin the tag so a later change to `main` cannot silently change the installed
runtime.

### macOS or Linux

```bash
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
cd codex-air
git describe --tags --exact-match
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

`git describe` should print `v1.2.0`. A successful setup ends with
`Validation: PASS`, `Install check: OK`, installed Skill/agent paths, a backup
path, and `Doctor: PASS`.

### Windows PowerShell

```powershell
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
Set-Location codex-air
git describe --tags --exact-match
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
```

`git describe` should print `v1.2.0`. Windows validation should end with
`Validation: PASS`; the installer then prints the installed paths and backup
path, and the diagnostic should end with `Doctor: PASS`.

## Verify the installation

Close every Codex session that predates the install and start a new one. Then:

1. open `/skills` and verify that `$codex-air` is visible;
2. open `/agent` and verify that the AIR controller and worker profiles are
   discoverable;
3. invoke `$codex-air` explicitly in a local repository.

If either surface is missing, use the
[troubleshooting guide](troubleshooting.md) before running a real task.

## Run a first task

Use a disposable branch or otherwise recoverable local repository while
learning the workflow. Give AIR a goal, observable completion conditions, and
hard boundaries:

```text
$codex-air

Goal: Fix the local configuration loader so blank and comment-only lines are
ignored without changing its public API.

Done when:
- add a regression test that fails before the fix and passes afterward;
- the focused test suite passes;
- existing behavior for non-comment values is preserved.

Boundaries:
- do not add dependencies;
- do not access the network;
- do not commit or push;
- preserve unrelated working-tree changes.
```

This is a task template, not a benchmark result. Adapt it to a real repository.
See the [annotated first-task example](examples/first-air-task.md) for expected
control flow and output.

## What to expect

For admitted Controlled AIR work, the normal trace is one semantic Sol
controller, one Luna executor, candidate persistence, and the same Sol
controller's final review. Parallel Luna workers are exceptional and require
disjoint ownership plus the Skill's quantitative gate.

Possible terminal outcomes are:

- `PASS`: Sol accepted the final candidate and verifier evidence;
- `REPLAN_NEEDED`: Luna found that the packet's decisive facts, scope, or
  verifier must change before safe implementation can continue;
- `BLOCKED`: a concrete runtime, permission, dependency, scope, or evidence
  blocker prevented completion.

Requested Fast service does not by itself prove that the runtime delivered the
priority tier. If authoritative telemetry is absent, AIR reports the actual
tier as `unobserved`.

## Stable release versus development main

Use `v1.2.0` for a reproducible installation. Use `main` only when you
deliberately want unreleased changes:

```bash
git clone https://github.com/SII-k7/codex-air.git codex-air-main
cd codex-air-main
git switch main
bash scripts/validate.sh
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

Do not describe a `main` install as v1.2.0. Record the exact commit with
`git rev-parse HEAD` when reporting a problem or result.

## Upgrade

To upgrade an older checkout to the stable v1.2.0 tag:

```bash
git status --short
git fetch --tags origin
git switch --detach v1.2.0
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

Stop if `git status --short` shows changes you do not own. On Windows, run the
corresponding `.ps1` validation, `-Check`, install, and doctor commands instead.
Restart Codex after every upgrade.

For an intentional development update, stay on `main`, use
`git pull --ff-only`, validate, and reinstall. Never mix files from a tag and
`main` in one installed bundle.

## Roll back or uninstall

Each successful install snapshots the immediately preceding managed AIR
paths. Restore that state transactionally with:

```bash
bash scripts/uninstall.sh --restore-latest
```

On Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1 -RestoreLatest
```

To remove AIR without restoring the saved state, omit the restore option. The
scripts refuse to overwrite or remove managed files whose checksums no longer
match; investigate and preserve those edits instead of deleting them by hand.

For a deliberate tag downgrade, check out that tag, validate it, and run its
installer. Restart Codex afterward.

## Next steps

- [Troubleshooting](troubleshooting.md)
- [First AIR task](examples/first-air-task.md)
- [Evidence and claim boundaries](evidence/README.md)
- [More prompt recipes](prompt-recipes.md)
