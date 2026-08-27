# Codex AIR troubleshooting

[简体中文](troubleshooting.zh-CN.md) · English

Start from a checked-out Codex AIR repository. Do not delete installed files or
edit agent profiles until the read-only checks below identify the problem.

## Quick diagnostics

On macOS or Linux:

```bash
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/doctor.sh --require-codex
bash scripts/default.sh check
```

On Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/default.ps1 check
```

`default.sh check` is expected to exit nonzero only when a legacy global AIR
default block is still active. Remove that block transactionally with
`bash scripts/default.sh disable`.

## `$codex-air` is not visible in `/skills`

1. Confirm that the install and Codex process use the same operating-system
   account and home directory.
2. Check that `.agents/skills/codex-air/SKILL.md` exists under that home.
3. Run the install check, reinstall, and restart Codex completely. An existing
   session does not necessarily reload newly installed Skills.
4. Remember that AIR is explicit-only. It appears as `$codex-air`, but it does
   not activate merely because a task is complex.

If `ORCHESTRATE_HOME` was set during installation, set it to the same absolute
home used by Codex or reinstall without it. Do not point it at `/`, a symlink,
or a shared home whose ownership is unclear.

## AIR agents are not visible in `/agent`

The install should provide five profiles under `.codex/agents/`:

- `air-controller.toml` and `air-critical-controller.toml`;
- `air-efficient-worker.toml` and `air-complex-worker.toml`;
- `air-challenger.toml`.

Run `doctor.sh` on POSIX or `doctor.ps1` on Windows. It verifies names, models,
reasoning levels, context limits, tiers, and sandbox modes. Also check that the
user's Codex config does not explicitly set `features.multi_agent = false` or
`agents.enabled = false`. Restart Codex after correcting the installation.

## The configured model is unavailable or permission is denied

Static files cannot grant model access. AIR requires Sol for semantic control
and final review and Luna for execution. Confirm that the Codex login, account,
workspace, region, and current product plan expose both configured models.

AIR must fail closed when the required identity cannot be proved. It must not
silently substitute Terra, downgrade the reasoning contract, or present a
different route as an AIR result. You can resolve the entitlement issue or run
the task outside AIR as an explicitly separate Direct attempt.

Include the Codex CLI version and the exact live error when requesting support;
do not include credentials or raw private repository contents.

## Fast was requested, but the actual tier is `unobserved`

The Luna profiles request `service_tier = "fast"`. Some runtime telemetry does
not expose the actual response tier. In that case `unobserved` means “not
proven,” not “confirmed Standard” and not “confirmed Fast.”

Do not infer delivery speed from the profile alone. For accounting, retain
requested and actual tier separately and use authoritative billing or response
metadata when available. A benchmark with `unobserved` actual tier may report
that warning, but must not claim observed Fast-tier delivery.

## Two workers need to edit the same file

That is an ownership collision. AIR permits one owner per writable file and
does not use “merge it later” as a substitute for ownership.

Return the conflict to the Sol controller. Usual resolutions are:

- assign the shared file and integration step to one worker;
- serialize the dependent tasks;
- narrow the branches so their write scopes are actually disjoint.

Do not allow both workers to continue writing the same path. A dirty worktree
owned by another session is also a collision until its owner and scope are
known.

## Luna returns `REPLAN_NEEDED`

This is a controlled handoff, not an overall failure. It means a decisive fact
was false, the chosen approach cannot satisfy a requirement, scope must expand,
the verifier is invalid, or a new authorization/risk decision is needed.

The same Sol controller should inspect the compact evidence, revise the plan or
packet, and preserve the authorization boundary. Do not tell Luna to “try
anything,” and do not loop the unchanged packet back to it.

## AIR returns `BLOCKED`

Read the reported failure class and concrete blocker. Common classes include
runtime, model identity, permission, dependency, scope, conflict,
verification, and evidence quality.

Resolve only the named condition, then start a fresh bounded recovery. Do not
turn a missing permission into implied authorization, skip the verifier, or
accept a candidate whose paths/hashes cannot be persisted. Repeated unchanged
failures are evidence to stop, not a reason for an unbounded retry loop.

## Installation refuses to overwrite a target

The installer tracks managed files by checksum and refuses unknown or modified
targets. This protects user edits and files installed by another tool.

Inspect `git status`, the reported installed path, and
`.codex/codex-air/install-state`. Preserve any local edits. If the current
install is intact, use the supplied uninstaller or its `--restore-latest`
option; do not manually remove a broad `.agents` or `.codex` directory.

## Windows-specific issues

- Run PowerShell 5.1 or newer. `-ExecutionPolicy Bypass` applies only to the
  invoked process in the documented command.
- Use `scripts/validate.ps1`, `scripts/install.ps1 -Check`, and
  `scripts/install.ps1`, then diagnose with
  `scripts/doctor.ps1 -RequireCodex`.
- If Codex runs inside WSL, install AIR inside that WSL home with the POSIX
  scripts. A Windows-home install is not automatically visible inside WSL.
- `ORCHESTRATE_HOME` must be an absolute, non-root path for the environment in
  which Codex runs.
- Inspect or remove legacy global routing with `scripts/default.ps1 check` or
  `scripts/default.ps1 disable`.
- Restore the previous managed state with
  `scripts/uninstall.ps1 -RestoreLatest`.

After any Windows install or rollback, close and reopen Codex before checking
`/skills` and `/agent`.

## When reporting a problem

Include:

- release tag, or exact `git rev-parse HEAD` for a `main` install;
- `codex --version`;
- operating system and whether Codex runs natively or in WSL;
- output of validation, install check, and doctor when available;
- terminal AIR status and failure class;
- requested and observed tier as separate fields.

Remove secrets, proprietary source, absolute private paths, and raw model
credentials. See [SUPPORT.md](../SUPPORT.md) for support channels.
