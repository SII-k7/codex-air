# Codex AIR historical v1.0 implementation report

Date: 2026-08-20

Repository: https://github.com/SII-k7/codex-air

This report separates source configuration, local tests, hosted CI, installation,
and runtime proof. A configured agent name or TOML value is not presented as a
successful model launch.

> Historical evidence notice: this document was migrated from the earlier
> Codex PROVE repository. It preserves pre-AIR runtime evidence for provenance;
> it does not claim that those sessions exercised the renamed AIR roles or the
> current low-latency Luna profile.

## 1. Final architecture

Codex AIR is a model-neutral orchestration protocol for Codex. AIR means
Adaptive Intelligence Routing; planning, ownership, verification, and evidence
remain its delivery contract.

```text
User goal
  -> Host authorization and workspace safety
  -> one Controller: plan, route, schedule, arbitrate, review
  -> zero or more bounded efficient/complex workers
  -> real files, complete diff, tests, builds, and artifacts
  -> Controller verdict: PASS | FIX | BLOCKED
  -> Host integration and user delivery
```

The product name, invocation, task schema, evidence gates, and role names no
longer depend on a model generation. Model selection is a replaceable capability
profile.

## 2. Prior art and licenses

The pinned projects, reviewed commits, and license findings are recorded in
[NOTICE](NOTICE). Apache-2.0, MIT, and MIT-0 sources were reviewed. Projects with
no detected license were treated as ideas-only references. No third-party source
code or prose was copied into v1.0.

## 3. Adopted and rejected design

Adopted:

- one Controller and capability-based worker routing;
- stable Requirement IDs and final-candidate-bound evidence;
- one owner per writable file for the whole run;
- dependency stages and live-capacity batching;
- artifact-first review and verify-the-verifier checks;
- a bounded planning timebox, evidence-complete partial delivery, and resume
  state for long interrupted runs;
- at most one qualifying read-only challenge and one same-scope correction;
- Host-authoritative two-turn identity proof instead of child model self-report;
- transactional cross-platform install, rollback, uninstall, and backup restore.

Rejected:

- product or role names tied to Sol, Terra, Luna, or another model generation;
- a permanent multi-agent team, second controller, or worker-created subagents;
- fixed worker counts, challenge calls on every task, or parallel writes to one
  file;
- silent model, effort, permission, or agent substitution;
- accepting transport completion, a worker `PASS`, or an unrelated exit code as
  proof;
- renaming the product whenever the default model profile changes.

## 4. Routing

| Route | Boundary |
| --- | --- |
| Direct | Ordinary small work when `$codex-air` was not explicitly invoked |
| Controller-only | Planning, architecture, analysis, or review with zero workers |
| Controller -> efficient | Clear, bounded, low-ambiguity, independently falsifiable execution |
| Controller -> complex | Cross-module, long-context, ambiguous, shared-interface, or high-consequence execution |

The Controller uses the minimum sufficient worker count. An efficient task may
escalate once to the complex profile only when its first failure occurred before
any owned write and the task and scope remain unchanged.

## 5. Native Nested and Compatibility

Both modes share the same requirement graph, task packet, role profiles,
ownership rules, verification threshold, result schema, and final review.

- Native Nested: Host -> Controller -> workers -> Controller review -> Host.
- Compatibility: Host obtains the Controller graph, dispatches workers from it,
  and returns real worker results and artifacts to the same Controller for final
  review.

Native Nested is claimed only after a real nested launch with the new `air-*`
role names. Compatibility is a first-class mode, not a silent downgrade. The
v1.0 release verified Compatibility end to end; Native Nested remains
unverified for the new role names.

## 6. Models and agents

| Capability role | Agent type | v1.0 default | Reasoning | Requested sandbox |
| --- | --- | --- | --- | --- |
| Controller | `air-controller` | `gpt-5.6-sol` | `high` | `read-only` |
| Complex worker | `air-complex-worker` | `gpt-5.6-terra` | `high` | `workspace-write` |
| Efficient worker | `air-efficient-worker` | `gpt-5.6-luna` | `max` | `workspace-write` |

Every custom agent launches with `fork_turns="none"`. The Host proves the role,
model, reasoning effort, and fork from its authoritative tool mapping and launch
record; the child reports observable capability, its operational constraint,
and zero task/write/subagent activity before receiving work.

## 7. File structure

- `.agents/skills/codex-air/`: canonical Skill and two single-level references.
- `.agents/skills/codex-prove/`: small explicit compatibility entry only.
- `.codex/agents/air-*.toml`: model-neutral role configurations.
- `scripts/`: POSIX and PowerShell validation/install/uninstall plus A/B harness.
- `tests/`: contract, lifecycle, README/SVG, routing, forward, and benchmark
  fixtures.
- `docs/release/runtime-surface-matrix.md`: runtime evidence boundaries.

## 8. Installation and backups

The source preflight backed up the previous global Skill, agent TOMLs,
`config.toml`, and global `AGENTS.md` to:

`/tmp/codex-air-v100-preflight.XYuq0a`

The v1 installer manages only the canonical Skill, compatibility entry, three
generic agent files, and its version-5 ownership state. It backs up existing
managed targets plus `config.toml`, but never replaces the complete
`config.toml`. The isolated lifecycle tests prove fresh install, idempotent
reinstall, modified/unowned collision refusal, rollback, exact uninstall, v0.5
migration, latest-backup restore, and unrelated-file preservation.

After `main` passed hosted CI, the transactional installer migrated the global
v0.5 install to v1.0. The installed paths are
`~/.agents/skills/codex-air`, `~/.agents/skills/codex-prove`, and the three
`~/.codex/agents/air-*.toml` files. The persistent recovery backup is:

`/Users/kin3/.codex/codex-air/backups/20260820T092316Z-61245`

The global invocation rule was changed minimally: `$codex-air` is canonical
and explicit-only, while `$codex-prove` is an explicit-only compatibility
alias. The complete `config.toml` was not replaced.

## 9. Forward and static tests

The current fixture contains 41 routing and failure scenarios. It covers Direct,
Controller-only, both worker profiles, parallel batching, dependency stages,
one-file-one-owner, dirty worktrees, missing evidence, stale evidence, wrong-scope
verification, bounded correction, same-run recovery, timeout ownership, partial
delivery, resume, and fail-closed identity/permission behavior.

Current local candidate evidence:

- Skill Creator `quick_validate.py`: canonical Skill PASS; compatibility entry
  PASS;
- `scripts/validate.sh`: PASS;
- full Python suite: 151 tests PASS on the v1.0.0 release candidate;
- isolated POSIX lifecycle: PASS;
- Bash syntax, TOML/JSON/YAML parsing, Markdown links, SVG contracts, credential
  scan, and `git diff --check`: PASS;
- local PowerShell runtime: unavailable; deterministic structure checks PASS.

Hosted release evidence:

- feature-branch POSIX run
  [32353330454](https://github.com/SII-k7/codex-air/actions/runs/32353330454):
  PASS;
- feature-branch Windows run
  [32353330574](https://github.com/SII-k7/codex-air/actions/runs/32353330574):
  PASS;
- `main` POSIX run
  [32353507136](https://github.com/SII-k7/codex-air/actions/runs/32353507136):
  PASS;
- `main` Windows run
  [32353507150](https://github.com/SII-k7/codex-air/actions/runs/32353507150):
  PASS on Windows Server 2022 and `windows-latest`, with Windows PowerShell 5.1
  and PowerShell 7.

## 10. Real model calls

The retained v0.5 evidence proves the previous model-branded roles and protocol,
but it is not reused as proof of the new `air-*` agent names.

After global v1 installation, a fresh ephemeral `codex exec` session
(`01a01e7c-477a-7a03-9b74-8a7144d6f958`) loaded `$codex-air` and completed a
real Compatibility route. The Host launched every role with
`fork_turns="none"`, used the authoritative runtime mapping, and received the
required no-side-effect handshake before the second turn:

| Agent type | Proven runtime mapping | Result |
| --- | --- | --- |
| `air-controller` | `gpt-5.6-sol`, `high` | handshake, plan correction, and sole final review PASS |
| `air-efficient-worker` | `gpt-5.6-luna`, `max` | handshake and bounded no-write acknowledgment PASS |
| `air-complex-worker` | `gpt-5.6-terra`, `high` | handshake and bounded no-write acknowledgment PASS |

The Controller rejected one contradictory draft evidence requirement before
worker dispatch, returned a corrected graph, and issued the final Compatibility
verdict `PASS`. The test inspected and changed no repository files. Native
Nested was not exercised and is not claimed for the new role names.

## 11. Parallelism and ownership

Forward cases prove that independent, dependency-ready tasks with disjoint write
scopes may share a stage. Overlapping files, shared configuration, generated
outputs, migrations, external resources, or uncertain boundaries are serialized.
Alternative analyses may be read-only, but one selected owner writes.

## 12. Failure and downgrade tests

The suite fails closed on unprovable identity, unsafe install parents, symlinks,
modified managed targets, unowned collisions, missing task fields, stale or
wrong-scope evidence, candidate mismatch, and unsupported state versions. A
transaction failpoint restores the previous install and deliberately retains a
new recovery backup.

## 13. Fresh-session discovery

Fresh-session discovery passed after installation:

- session `01a01e7c-477a-7a03-9b74-8a7144d6f958` discovered canonical
  `$codex-air`, selected all three exact `air-*` roles, and completed the
  Compatibility path plus Controller final review;
- session `01a01e81-92bc-7462-bb95-450bc929e971` is retained as pre-AIR
  compatibility evidence; current static and lifecycle tests cover the
  `$codex-prove` to `$codex-air` redirect.

## 14. GitHub and version

This migrated report belongs to the new standalone
[`SII-k7/codex-air`](https://github.com/SII-k7/codex-air) history. The verified
release is `v1.0.0`; its annotated tag and release commit are published from
`main`.

## 15. Known limitations

- The cost ranges in the README remain scenario projections. The completed
  DeepSWE hardest-10 matched A/B is separately reported and measured AIR at
  39.0% of Direct credits, near-equal mean partial, and 1.267 median paired
  latency; ten one-attempt tasks are not a statistical non-inferiority proof.
- The retained live smoke is one historical ordered pair, not proof of v1 role
  discovery or a general quality, latency, or cost winner.
- A local PowerShell engine is unavailable; dynamic PowerShell 5.1 and 7 passed
  on GitHub-hosted Windows runners.
- Physical Windows installation was user-reported, but no v1 runtime identity
  payload was captured; hosted Windows Server evidence is not physical Windows
  11 evidence.
- Runtime custom-agent availability, exact model selection, nesting, and capacity
  remain Host-surface properties. Compatibility passed on the current Desktop
  runtime; Native Nested with the new role names remains unverified.
- AIR reduces unsupported completion claims; it does not guarantee perfect
  correctness.

## 16. Next steps

1. Capture a real Native Nested run with the new role names before marking that
   runtime surface verified.
2. Capture a physical Windows 11 v1 runtime identity payload if device-specific
   Native Nested support is needed.
3. Complete the matched A/B benchmark before presenting scenario projections as
   measured savings.
