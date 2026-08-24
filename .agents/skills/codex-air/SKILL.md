---
name: codex-air
description: Use Sol xhigh to understand, explore, decompose, and review substantial coding work while Luna Max Fast executes, only when the user explicitly invokes $codex-air.
---

# Codex AIR

AIR means **Adaptive Intelligence Routing**. It is a two-role workflow:

- **Sol xhigh is the semantic controller.** It owns task understanding,
  repository exploration, solution selection, decomposition, authorization
  boundaries, and final artifact review.
- **Luna Max Fast is the executor.** It owns bounded implementation, focused
  diagnosis inside the assigned scope, verification, and correction.

Terra is not part of AIR. Never route to it. The controller and executor are
roles, not interchangeable model labels: Luna must not approve the overall
task, and Sol should not perform routine implementation that can be delegated.

Enter only when the user explicitly invokes `$codex-air` or the deprecated
explicit `$codex-prove` alias. Never infer AIR from complexity or a global
`AGENTS.md` default. Never invoke AIR recursively from an AIR agent.

Keep capability separate from authorization. Broader technical access does not
widen the user's scope or authorize an external or destructive side effect.

## Language

默认使用中文输出路由说明、任务结果、验证证据和最终审核。用户明确要求其他语言时，
使用用户指定的语言；代码、命令、路径、标识符和原始证据按需保留原文。

## Admission and controller selection

First classify the visible request without repository exploration:

- **Direct:** answer-only work, tiny edits, or an already-localized change whose
  AIR dispatch overhead would dominate. Explain briefly that AIR was admitted
  but direct execution is cheaper.
- **Controlled AIR:** substantial coding, diagnosis, refactoring, migration,
  multi-file work, or any request whose solution or scope requires exploration.
- **Critical AIR:** authentication/authorization, secrets, payments,
  destructive or irreversible operations, production state, privacy-sensitive
  data, migration correctness, concurrency correctness, or comparable risk.

Use the current Host as the sole Sol controller when authoritative runtime
metadata proves it is `gpt-5.6-sol` with `xhigh` or stronger reasoning. This is
the preferred path because the main conversation already contains the user's
intent. If the Host identity or effort cannot be proved, launch exactly one
`air-controller` (`air-critical-controller` for Critical AIR) with
`fork_turns="none"`. The Host then becomes a transport and authorization shim;
it must not create a second plan or second semantic review.

Read [references/orchestration.md](references/orchestration.md) before a
Controlled or Critical AIR run. Read
[references/runtime-notes.md](references/runtime-notes.md) for identity,
nesting, capacity, tier, persistence, or recovery decisions.

## Sol control contract

Before writes, the sole Sol controller must:

1. read applicable instructions and the minimum repository context needed to
   understand the task;
2. derive stable Requirement IDs and falsifiable completion conditions;
3. identify concrete observations, constraints, non-goals, risks, and the
   changed-path baseline;
4. choose one solution and name exact files, symbols, ownership boundaries,
   verification commands, and stop conditions;
5. decide whether one Luna executor is sufficient or whether the parallel gate
   below is proved;
6. send a compact task packet, not the controller's entire transcript.

Exploration and solution selection stay with Sol. Luna may inspect assigned
files and their local dependencies to execute safely, but it must return
`REPLAN_NEEDED` before any write when a decisive observation contradicts the
packet, the requested scope must expand, or the proposed approach is materially
wrong. The same Sol controller then revises the packet.

## Compact execution packet

Use `fork_turns="none"` and send only:

```text
Mode: Single Executor | Coordinated Leaf
Task ID: <stable id>
Requirement IDs: <owned requirements and completion conditions>
Chosen solution: <specific approach, not an open-ended request to solve>
Decisive observations: <facts Luna should verify before writes>
Write scope: <exact paths or narrow glob>
Read scope: <exact paths plus local dependencies>
Do not touch: <paths, interfaces, side effects>
Baseline: <HEAD and dirty paths relevant to this task>
Verification: <exact commands and expected behavior>
Authorization boundary: <allowed workspace/external effects>
Stop conditions: <when to return REPLAN_NEEDED or BLOCKED>
Required final report language: <language>
```

Do not attach copied skill text, broad repository listings, unrelated diffs,
or repeated conversation history. This compact handoff is the main token-saving
mechanism; `fork_turns="none"` prevents the executor from inheriting the large
Sol exploration context.

## Luna execution contract

Launch `air-efficient-worker` by default. Use `air-complex-worker` only for a
bounded implementation unit with unusually large local context, a public
interface, migration/concurrency mechanics, or high-consequence code. Both are
the same `gpt-5.6-luna` / `max` / `fast` model; the profile changes execution
instructions, not price or intelligence tier.

The Luna executor must:

- verify the packet's decisive observations before writing;
- preserve unrelated user changes and remain inside `write_scope`;
- implement continuously rather than stopping after a new plan;
- run the assigned verifier, verify that the verifier targets the final
  candidate, and correct bounded failures while authorized;
- inspect its complete owned diff and report exact final file hashes;
- never create a subagent, broaden scope, redesign the overall solution, or
  approve overall completion;
- keep the final candidate visible for deterministic persistence.

All Python verification commands must use `PYTHONDONTWRITEBYTECODE=1` unless
bytecode generation is itself under test. Never inspect sibling worktrees,
previous benchmark outputs, hidden tests, evaluation harnesses, or candidate
solutions outside the active workspace unless the user explicitly authorizes
them. This evaluation isolation boundary is absolute.

Return one compact terminal record:

```text
Task ID: <task id>
Status: PASS | REPLAN_NEEDED | BLOCKED
Summary: <what was executed>
Inspected: <decisive observations verified>
Changed: <exact paths or None>
Requirement coverage: <REQ-ID -> final-candidate evidence>
Verification: <exact command, exit status, and result>
Evidence: <artifact-bound evidence>
Delivery: NONE | VISIBLE_CANDIDATE
Final file SHA256: <path=sha256-or-ABSENT for every changed file or None>
Assumptions: <remaining assumptions or None>
Risks: <material residual risks or None>
Failure class: runtime | timeout | model_identity | permission | dependency | scope | verification | evidence_quality | conflict | critical_risk | none
Blocker: <concrete blocker or None>
Runtime tier: requested=fast; actual=<priority | default | unobserved>
```

## Parallel AIR gate

One Luna executor is the default. Use two or three executors only when Sol can
justify every condition with relative-work estimates:

- at least **65%** of serial work is parallelizable;
- the largest branch is at most **60%** of the parallelizable work;
- coordination/integration overhead is at most **15%** of estimated serial
  execution time;
- owners have disjoint writes and satisfied dependencies, with no shared
  interface, lockfile, generated output, migration state, or external resource;
- live capacity admits the Sol controller plus every ready executor.

Launch a ready stage as one concurrent batch and use one long wait, not
worker-by-worker polling. Queue larger frontiers in waves. Never use extra
workers merely to increase token throughput. The same Sol controller integrates
and reviews the union candidate once.

## Deterministic candidate persistence

A child `PASS` is not proof that an isolated worktree changed the user's active
workspace. For every write-capable result, require `VISIBLE_CANDIDATE`, exact
changed paths, and final SHA-256 identities. If active files match, invoke
`scripts/persist-visible-candidate.sh --workspace <absolute-workspace>` once.
Require its complete `PERSISTED` path/hash set to equal the Luna report. If the
candidate is absent, paths differ, hashes differ, or replay fails, return
`BLOCKED` with `Failure class: runtime`; never ask an LLM to reconstruct a patch.

This is deterministic candidate persistence, not a semantic review. The Host
may compare opaque paths and hashes without duplicating the Sol controller.

## Sol final review

After persistence, the same Sol controller must inspect the real final files,
complete in-scope diff, Requirement coverage, and verification evidence. It
must verify the verifier and return exactly:

```text
Verdict: PASS | FIX | BLOCKED
Requirement coverage: <REQ-ID -> artifact and evidence>
Artifact review: <complete diff assessment>
Verification assessment: <why the checks prove the requested behavior>
Risks: <material residual risks or None>
Fix owner: <Task ID or None>
Failure class: <class or none>
Blocker: <concrete blocker or None>
```

`FIX` permits one focused correction by the same Luna owner using a delta
packet. After any change, persistence and Sol review repeat. A second material
failure, a solution change, or a scope expansion returns to Sol replanning; do
not start an unbounded repair loop. Only Sol can issue overall `PASS`.

`air-challenger` is exceptional: use it only when the user requests independent
review, critical evidence materially conflicts, or no falsifiable verifier can
establish a high-consequence semantic claim. It cannot approve completion.

## Cost, token, and latency targets

Fast is a latency tier, not token compression. Every Luna profile is permanently
Max + Fast: `model_reasoning_effort="max"`, `service_tier="fast"`, and
`features.fast_mode=true`. Do not silently downgrade it. Every Sol controller
uses `xhigh` on the Standard tier. Terra usage must remain zero.

For matched substantial-task evaluations, establish quality parity first, then
target:

- API- or credit-equivalent cost no more than **55%** of Direct Sol xhigh;
- wall time between **0.85x and 1.15x** of Direct;
- at least **70%** of model tokens on Luna;
- raw total model tokens no more than **1.10x** initially and **1.00x** after
  handoff optimization;
- one Sol semantic controller and one Luna executor by default;
- no routine challenger and no Terra tokens.

Record token and cost by model and tier, requested versus observed service tier,
wall time, quality score, correction count, and parallel critical path. Do not
trade away authorization, verification, or evidence quality to hit a budget.
