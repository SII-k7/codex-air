---
name: codex-air
description: Plan, execute, verify, and evidence-gate a task with a Luna-first architecture only when the user explicitly invokes $codex-air.
---

# Codex AIR

AIR means **Adaptive Intelligence Routing**. Planning, ownership, verification,
and evidence remain its delivery contract. Its ordinary path has one
task-context owner: a Luna Max Fast primary agent performs
planning, diagnosis, implementation, verification, artifact review, and the
terminal verdict. When an eligible request has a wide independent frontier,
Parallel AIR uses a Luna Max Fast controller and two or three Luna Max Fast leaf
owners to shorten the critical path, then performs one aggregate review. The
Host is a thin dispatch-and-integration shim, not a second solver or reviewer.
Because Codex subagents may use isolated worktrees, a
write-capable child result is not delivered until Git mechanically snapshots
and replays the session-visible candidate in the user's active workspace.

Enter only when the user explicitly invokes `$codex-air` or the deprecated
explicit `$codex-prove` alias. Never infer AIR from complexity or a global
`AGENTS.md` default. Requests without an explicit invocation stay Direct. Never
invoke AIR recursively from an AIR agent.

Keep capability separate from authorization. Broader technical access does not
widen the user's scope or authorize an external or destructive side effect.

## Language

默认使用中文输出路由说明、任务结果、验证证据和最终审核。用户明确要求其他语言时，
使用用户指定的语言；代码、命令、路径、标识符和原始证据按需保留原文。

## Select the route from the request

Classify from the user request and already-visible conversation constraints.
Do not inspect the repository merely to decide whether ordinary Lean work is
eligible.

### Lean Primary — default

Use Lean Primary for reversible workspace work that can have one logical owner.
An initially unknown root cause, unfamiliar code, tests, refactors,
documentation, configuration, and ordinary multi-file work inside one component
are all Lean work. A falsifiable local check is preferred; when none exists the
primary must explicitly assess evidence quality instead of manufacturing PASS.

```text
Host dispatch shim -> air-efficient-worker (Luna Max Fast primary)
                   -> deterministic candidate persistence gate
                   -> Host terminal relay
```

Lean has no controller, no Sol reviewer, no Terra worker, and no challenge by
default. The `air-efficient-worker` is the sole task decision owner and final
reviewer in `Mode: Lean Primary`; despite its stable compatibility name, it may
approve the overall Lean task.

### Parallel AIR — latency-gated coordination

Treat multiple components as a candidate, not automatic permission to fan out.
Use the exact `air-controller` profile for an implementation run only when the
request already shows at least two independently ownable workstreams and the
controller can justify every part of this gate with relative-work estimates:

- the **parallelizable share** is **at least 65%** of estimated serial work;
- the **largest branch** is **no more than 60%** of the parallelizable share;
- **coordination and integration overhead** is **no more than 15%** of estimated
  Lean serial work;
- two or three ready owners have disjoint writes, satisfied dependencies, and
  no competing ownership of a shared interface, lockfile, generated output,
  integration file, migration state, or external resource;
- live capacity admits at least two leaves plus the controller.

If any condition is unproved or fails, return `LEAN_RECOMMENDED` before worker
launch and immediately route the request to the ordinary single Luna Max Fast
Primary. A public/shared interface or architecture decision may be assigned to
one owner before a later eligible batch; it is never a reason to parallelize
overlapping work. Planning-only or review-only requests may still use the
read-only controller with zero workers and do not claim a parallel speedup.

For an accepted Parallel AIR implementation, launch **two or three
air-efficient-worker** leaves using the **same gpt-5.6-luna / max / fast**
configuration. Ordinary Parallel AIR uses at most three concurrent leaves;
queue a larger frontier in waves. Never use Complex merely to increase speed.
Launch each ready stage as a **single concurrent batch**. The rule is **do not
wait worker-by-worker**: use **one long wait** for batch completion. After every
leaf is terminal, construct one union manifest in **deterministic Task-ID order**,
prove that its paths are disjoint and its hashes equal the complete visible
candidate, then invoke the Git persistence transaction once for that union. Send
one aggregate capsule to the controller for **one aggregate final review**.
These constraints reduce orchestration turns without relaxing evidence or
one-owner rules.

The controller is Luna Max Fast, read-only, and the sole Full-run reviewer. Read
[references/orchestration.md](references/orchestration.md) before dispatching
this route. Read [references/runtime-notes.md](references/runtime-notes.md) only
for runtime selection, nesting, capacity, identity, tier, or recovery issues.

### Critical AIR — high consequence only

Select `air-critical-controller` at entry for authentication or authorization,
secrets, payments, destructive or irreversible operations, production state,
privacy-sensitive data, data migration, concurrency correctness, or comparable
consequences. It uses Sol Max and the Full contract. Cost never overrides safety.

If a critical flag appears after Lean writes, stop further writes, preserve the
candidate and evidence, and return `REVIEW_REQUIRED`; do not silently switch
controllers or transfer an already-owned file.

## Thin Host contract for Lean

The Host performs transport, authorization, and deterministic candidate persistence
only:

1. Prove the exact `air-efficient-worker` mapping, Luna model, Max effort,
   `fork_turns="none"`, requested Fast tier, and workspace-write boundary from
   authoritative Host/tool metadata. If this cannot be proved, fail closed.
2. Before launch, record only an opaque active-workspace baseline fingerprint
   (HEAD plus hashes of status/diff), without reading file contents or deriving
   task semantics. Launch immediately with one complete first-turn packet. Forward the raw
   user request and relevant explicit conversation constraints; do not rewrite
   the task into a second Host-authored plan.
3. Wait without repository polling. After launch, call one long agent wait
   (`timeout_ms=3600000` where supported); it returns early on completion. Do
   not short-poll and do not emit unchanged "still working" updates. If the
   wait returns because the user sent new input, handle it and then make one
   new long wait for the same live primary.
4. Treat a child `PASS` as a semantic verdict, not proof that its isolated
   worktree changed the user's workspace. When `Changed` is non-empty, require
   exact relative paths and the final SHA-256 for every changed file, but never
   ask the model to serialize a patch. Compare the active files with those
   opaque hashes. If every path equals the reviewed final identity, invoke
   `scripts/persist-visible-candidate.sh --workspace <absolute-workspace>` once,
   with no model-composed path arguments. The `--workspace` flag is preferred;
   the script also accepts the absolute workspace as its first argument. Git
   enumerates the entire visible dirty-path set, and the script emits one
   `PERSISTED` identity per path. Mechanically require that output set and every
   identity to equal the child's `Changed` and `Final file SHA256` fields. The script makes Git snapshot the currently visible binary
   diff, reverses it, immediately reapplies it, and verifies byte-identical final
   identities in one Host transaction. This Git-generated parent-owned replay
   is required for persistence after the child/session exits. If the final state
   is no longer visible, the workspace is not a Git root, a path is unsupported,
   or any path/hash/replay check differs, fail closed; do not ask an LLM to
   reconstruct transport. When `Changed` is `None`, require `Delivery: NONE`.
5. Deliver `PASS` only after this persistence gate succeeds. A transport-
   truncated terminal record permits one result-only follow-up to the same
   primary, with no new work or writes. Persistence failure returns `BLOCKED`
   with `Failure class: runtime`; never claim that files changed merely because
   they changed in the child's isolated worktree.

The Host does not reread file contents, semantically inspect the diff, rerun
verification, or perform a second semantic review. Path/hash comparison and the
Git-generated replay script are transport checks, not artifact judgment. The
script emits only path identities and a compact persistence verdict to the Host;
the model never receives or rewrites the patch body.

Before Lean dispatch the Host must not search the repository, assign Requirement
IDs, record a changed-path baseline, design tests, or solve any part of the task.
After dispatch it must not duplicate the primary's artifact review. A malformed
or transport-truncated result permits one result-only follow-up to the same live
agent; it does not permit Host-side semantic reconstruction.

This is the **single-semantic-context invariant**: ordinary task semantics and
artifact judgment enter one model context, the Luna primary's, exactly once.
The Host may handle opaque paths, hashes, and the Git-generated replay verdict
without becoming a second solver.

## Lean first-turn packet

Use a compact transport envelope:

```text
Mode: Lean Primary
Task ID: <stable id>
Raw user request: <verbatim request>
Explicit conversation constraints: <only relevant user decisions or None>
Workspace: <cwd and workspace roots>
Authorization boundary: <allowed workspace/external effects>
Do not touch: <known excluded paths or side effects>
Known risk flags: <flags visible before repository inspection or None>
Required final report language: <language>
```

Do not attach copied skill text, generic process instructions, a Host-generated
requirement matrix, repository listings, diffs, or test output. The custom
profile already contains the execution and evidence contract.

## Luna primary contract

In `Mode: Lean Primary`, the Luna agent must:

- derive stable Requirement IDs and falsifiable completion conditions;
- inspect the minimum repository context and preserve unrelated user changes;
- record its own baseline before writes and enforce one logical owner;
- plan privately, implement, and run verification without a plan-only stop;
- inspect the final changed paths, complete diff, and verifier target;
- bind evidence to the final candidate and mark stale checks after any change;
- correct bounded failures before returning whenever safe and authorized;
- assume its writable worktree may be isolated and keep the reviewed final
  candidate visible through return; report exact changed paths and final hashes
  only, never a model-authored patch body;
- return the overall Lean verdict itself.

For an explicit target-path task, read the named files, their nearest applicable
instructions, and the named verifier first. Do not search the whole repository,
branches, or Git history unless a concrete ambiguity remains. Record one
changed-path baseline and perform one final changed-path/diff audit; repeat a
check only after a candidate change or when it covers a distinct requirement.
When the request already specifies behavior and target paths, do not spend time
on a broad passing baseline suite before implementing; use a baseline test only
when it can falsify the need or localize an unknown defect. Prefer one focused
post-change behavior command plus one final hygiene/diff audit. Expand only for
a failed check, a distinct unmapped requirement, or a concrete risk.
Never inspect a sibling worktree, previous run, benchmark output, hidden test,
evaluation harness, or candidate solution outside the active workspace unless
the raw user request explicitly names and authorizes it. Evaluation isolation is
a hard boundary. All Python verification commands must use
`PYTHONDONTWRITEBYTECODE=1` unless bytecode generation is itself under test.

It must verify the verifier: exit zero, file existence, or a worker claim alone
is insufficient when the check targets the wrong module, stale candidate, or
wrong requirement. It must not create a subagent or ask the Host to redo work.

Return one compact terminal record:

```text
Task ID: <task id>
Verdict: PASS | REVIEW_REQUIRED | BLOCKED
Changed: <exact paths or None>
Requirement coverage: <REQ-ID -> final-candidate evidence>
Verification: <exact command/observation, exit status, and exact result>
Candidate identity: <commit+diff or exact changed-file snapshot>
Delivery: NONE | VISIBLE_CANDIDATE
Final file SHA256: <path=sha256-or-ABSENT for every changed file or None>
Evidence quality: strong | limited | insufficient
Risks: <material residual risks or None>
Review trigger: <concrete independent-review reason or None>
Failure class: runtime | timeout | model_identity | permission | dependency | scope | verification | evidence_quality | conflict | critical_risk | none
Blocker: <concrete blocker or None>
Runtime tier: requested=fast; actual=<priority | default | unobserved>
```

`PASS` requires all Requirement IDs, in-scope final changes, and sufficient
final-candidate evidence. If files changed, the exact reviewed candidate must
remain visible for the Host's Git-generated persistence transaction. Use
`REVIEW_REQUIRED` only for a concrete review
trigger, not generic uncertainty. Use `BLOCKED` for missing authority, identity,
dependency, or an exhausted safe recovery.

## Independent review is an exception

Ordinary Lean has zero Sol child calls. An independent review is allowed only
when the user explicitly requests it, a critical risk is present, evidence is
materially conflicting, or semantic correctness has high consequence and no
falsifiable verifier can establish it. Send only a compact review capsule:
requirements, candidate identity, changed paths, complete relevant diff, exact
verification evidence, and the unresolved question. Never send the full primary
conversation or make Sol rediscover the repository.

Use `air-challenger` for one bounded read-only falsification check and return
its findings to the same logical owner. Use `air-critical-controller` for a
critical run selected at entry. A challenger cannot become a second general
reviewer or approve completion.

## Cost and latency budget

Fast is a latency tier, not token compression. Report requested and actual tier
separately; if the response tier is unavailable, report `unobserved`.

Every Luna profile is permanently Max + Fast: `model_reasoning_effort = "max"`,
`service_tier = "fast"`, and `features.fast_mode = true`. Fast targets latency;
it intentionally consumes 2.5x ChatGPT credits, or Priority API rates when used
through the API. Do not silently downgrade Luna to save credits.

For matched ordinary-task evaluations, treat these as Lean regression targets
after quality parity is established:

- API-equivalent cost no more than 55% of Direct Sol/xhigh;
- wall time between 0.8x and 1.2x of Direct;
- at least 70% of model tokens on Luna and zero Sol child tokens;
- one primary launch, no independent controller, and no Host semantic artifact review;
- one implementation/verification trajectory, with bounded in-agent correction.
- exactly two normal Host model turns: dispatch/wait and persistence/terminal
  relay; deterministic Git replay does not add another model reviewer.

For a Parallel AIR candidate, record the three gate estimates, worker count,
single-batch wall span, slowest branch, total wall time, tokens by role, service
tier, persistence time, and aggregate review time. Compare it first with the
same task on Lean Luna Max Fast. Parallel AIR is a latency win only when quality
is non-inferior and observed wall time is lower; token and cost increases must
be reported rather than hidden. The gate is a scheduling heuristic, not a
guarantee or a substitute for matched measurement.

Do not lower verification, authorization, or evidence quality to hit a budget.
If the target is missed, report the measured miss and optimize the duplicated
context or tool trajectory instead of weakening the gate.
