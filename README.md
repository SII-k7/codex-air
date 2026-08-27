[English](README.md) · [简体中文](README.zh-CN.md)

![Codex AIR routes substantial coding work through a Sol control plane and Luna execution plane](docs/assets/readme/hero-en.svg)

<p align="center">
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/posix-validation.yml"><img alt="POSIX CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/posix-validation.yml?branch=main&amp;label=POSIX&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/windows-validation.yml"><img alt="Windows CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/windows-validation.yml?branch=main&amp;label=Windows&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/releases/tag/v1.2.0"><img alt="stable release v1.2.0" src="https://img.shields.io/badge/stable-v1.2.0-65D6C4?style=flat-square"></a>
  <a href="LICENSE"><img alt="Apache-2.0 License" src="https://img.shields.io/github/license/SII-k7/codex-air?style=flat-square"></a>
</p>

# Codex AIR

**Sol thinks it through. Luna carries it through. Evidence decides what can be
claimed.**

Codex AIR (Adaptive Intelligence Routing) is an explicit-only Codex Skill for
substantial coding work:

- **Sol `xhigh` controls semantics:** intent, repository exploration,
  requirements, solution choice, decomposition, ownership, and final review;
- **Luna `max`, Fast requested, executes:** bounded implementation, focused
  verification, and correction;
- **Terra has no AIR role:** calls, routes, and tokens must remain zero.

AIR is for multi-file changes, migrations, difficult defects, and work that
needs exploration before implementation. Answers and tiny localized edits can
stay Direct, because dispatch should not cost more than the task.

AIR activates only when you enter `$codex-air`. It is not a global default and
does not widen authorization. `$codex-prove` remains a deprecated explicit
compatibility alias.

Codex AIR is independently designed and maintained by
[SII-k7](https://github.com/SII-k7); it is not an official OpenAI product or
endorsement.

## Install stable v1.2.0

Pin the release tag. `main` is the development channel and may change between
commits.

### macOS or Linux

These POSIX validation, installation, and diagnostic scripts require Python
3.11 or newer.

```bash
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
cd codex-air
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

### Windows PowerShell

```powershell
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
Set-Location codex-air
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
```

Restart Codex, verify `$codex-air` in `/skills`, and inspect the installed
profiles with `/agent`. You need a Codex runtime that supports Skills and
custom agents, plus access to the configured Sol and Luna models.

For prerequisites, upgrades, transactional rollback, and the deliberately
separate `main` workflow, use the
[getting-started guide](docs/getting-started.md). If either runtime surface is
missing, start with [troubleshooting](docs/troubleshooting.md).

## First task

Give AIR an observable goal and hard boundaries:

```text
$codex-air

Goal: Fix the local configuration loader so blank and comment-only lines are
ignored without changing its public API.

Done when: A regression test and the focused existing suite pass.
Boundaries: No new dependencies, network access, commits, pushes, or unrelated
edits.
```

This is a prompt template, not a recorded result. See the
[annotated first-task example](docs/examples/first-air-task.md).

## Runtime contract

```text
request
  └─ Sol xhigh: understand → explore → choose → decompose → assign
       ├─ tiny/localized: Direct
       └─ substantial: compact packet, fork_turns="none"
            └─ Luna max, Fast requested: implement → verify → correct
                 └─ visible candidate + file identities
                      └─ same Sol xhigh: final diff + verifier review
                           └─ PASS | focused FIX | BLOCKED
```

One Luna executor is the default. Two or three are admitted only when the
quantitative parallel gate passes and every writable file has one owner. Luna
cannot expand scope, create subagents, or approve the overall task. A false
decisive fact or required scope expansion returns `REPLAN_NEEDED`; only Sol can
issue the overall `PASS`.

| Profile | Model / effort / requested tier | Responsibility |
| --- | --- | --- |
| `air-controller` | Sol / xhigh / Standard | Ordinary semantic control and final review |
| `air-critical-controller` | Sol / xhigh / Standard | High-consequence control, rollback, and final review |
| `air-efficient-worker` | Luna / max / Fast requested | Default bounded execution |
| `air-complex-worker` | Luna / max / Fast requested | Bounded public-interface, migration, concurrency, or large-local-context execution |
| `air-challenger` | Sol / xhigh / Standard | Exceptional read-only falsification; never approval |

Fast is a request, not runtime proof. When authoritative telemetry does not
expose the delivered tier, AIR records actual tier as `unobserved`.

## Evidence, without the marketing shorthand

| Evidence set | Status | What it actually says |
| --- | --- | --- |
| Historical v1.0 DeepSWE hardest-10 paired A/B | Complete, one attempt per arm-task | Direct vs historical AIR: strict resolved `2/10` vs `1/10`, mean partial `0.8943` vs `0.8932`, credits `919.34` vs `358.83`, paired median time ratio `1.267`; AIR used `3.17×` raw input-plus-output tokens |
| v1.2 two-task low-credit diagnostic | **`BUDGET_ABORTED / INVALID`** | Interrupted before terminal Luna records and Sol reviews at `66.85` credits; candidate cost was `39.7%` of reused historical Direct cells, paired median time ratio was `1.198`, and Luna made `170` tool calls |
| v1.2 Sol-control/Luna-execution hardest-10 | **NOT RUN** | No broad v1.2 quality, latency, token, or cost conclusion exists |

The v1.2 diagnostic also recorded zero short polls and Terra usage, with actual
Fast tier `unobserved`. Its post-abort verifier scores are diagnostic
observations, not accepted AIR outcomes or a fresh matched A/B.

These samples do **not** establish statistical non-inferiority. Codex AIR does
not promise “equivalent quality at half the cost,” lower raw token use, or
faster completion. The v1.0 result belongs to a different historical
architecture; the v1.2 hardest-10 rerun has not happened.

Read the full [evidence ledger and claim boundaries](docs/evidence/README.md),
the [historical v1.0 result](tests/deepswe-v11-hardest10-results.md), and the
[v1.2 low-credit protocol](tests/deepswe-v11-microbench.md).

## Documentation

- [Getting started](docs/getting-started.md)
- [Troubleshooting](docs/troubleshooting.md)
- [First AIR task](docs/examples/first-air-task.md)
- [Evidence and claim boundaries](docs/evidence/README.md)
- [Public Skill](.agents/skills/codex-air/SKILL.md)
- [Orchestration contract](.agents/skills/codex-air/references/orchestration.md)
- [Runtime notes](.agents/skills/codex-air/references/runtime-notes.md)
- [Runtime surface matrix](docs/release/runtime-surface-matrix.md)

## Contributing and support

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Use
[GitHub Discussions](https://github.com/SII-k7/codex-air/discussions) for usage
questions and [GitHub Issues](https://github.com/SII-k7/codex-air/issues) for
reproducible defects. Security-sensitive reports follow
[SECURITY.md](SECURITY.md); general support expectations are in
[SUPPORT.md](SUPPORT.md).

Do not spend model credits on a benchmark for a contribution unless a
maintainer has explicitly approved its task set and hard cap.

## License

[Apache License 2.0](LICENSE). Prior-art attribution is recorded in
[NOTICE](NOTICE); release history is in [CHANGELOG.md](CHANGELOG.md).
