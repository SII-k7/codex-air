# Codex AIR orchestration contract

This reference is the normative **Full AIR** execution contract. Load it only
after the entry Skill selects Parallel, controller-only, or Critical AIR. Lean AIR is fully
defined in `SKILL.md` and deliberately skips this controller layer.

In Full AIR the selected controller owns planning, routing, scheduling,
ownership, correction, and review. Workers own only their bounded task packets.

## Contents

1. Entry and invariants
2. Requirement graph
3. Routing and stages
4. Ownership
5. Task and result contracts
6. Verification and evidence
7. Review and correction
8. Failure handling
9. Continuity

## 1. Entry and invariants

- Enter only after an explicit `$codex-air` invocation (or the deprecated
  explicit `$codex-prove` alias) and a concrete Full-route trigger from
  `SKILL.md`. Ordinary one-owner work stays Lean after explicit invocation.
- Start Full AIR with exactly one controller. Select
  `air-critical-controller` when an entry request has a critical-risk flag;
  otherwise select `air-controller`. Do not switch controllers or create a
  standing team.
- Allow zero workers for planning-only or review-only work.
- Keep work Direct when the Skill was not explicitly invoked.
- Use capability roles, not permanent model brands, in plans and task packets.
- Launch with `fork_turns="none"`. Prove the selected agent, model, reasoning
  effort, fork mode, requested service tier, and effective boundary from the
  authoritative Host/tool role mapping plus the launch record before sending work.
  When those fields are authoritative, send the complete packet in the first
  child turn. Never spend a separate model turn on an identity-only handshake or
  ask a child to guess metadata it cannot observe.
- Preserve the Host as authorization boundary, runtime dispatcher, and final
  user-communication relay. Treat write-capable child worktrees as isolated
  unless the runtime proves otherwise. The Host may mechanically compare final
  file hashes and ask Git to snapshot plus replay a session-visible candidate,
  but never interpret the diff. The controller is the sole graph decision owner,
  integration reviewer, and Full-run evidence reviewer. The Host validates only
  transport/schema state and never repeats the controller's semantic review.
- Keep the Host and controller out of implementation. Dispatch every repository
  write, routine debugging pass, implementation-oriented exploration, test
  authoring, and correction to an exact custom worker profile; never use a
  generic or built-in child that can inherit the parent controller model.

AIR is an evidence gate. It reduces unsupported completion claims; it cannot
guarantee perfect correctness.

## 2. Requirement graph

The controller returns this top-level shape. A Parallel candidate includes the
gate inputs even when the decision is `LEAN_RECOMMENDED`:

```yaml
goal: "Concrete outcome"
route: PARALLEL | CONTROLLER_ONLY | CRITICAL
parallel_assessment:
  parallelizable_share: "relative-work estimate and basis"
  largest_branch: "relative-work estimate and basis"
  coordination_and_integration_overhead: "relative-work estimate and basis"
  concurrent_workers: 0 | 2 | 3
  decision: PARALLEL_APPROVED | LEAN_RECOMMENDED | NOT_APPLICABLE
done_when:
  - id: REQ-1
    criterion: "Observable criterion"
    evidence: "Required evidence"
tasks:
  - id: task-a
    task: "One bounded action"
    requirements: [REQ-1]
    agent_profile: efficient | complex
    routing_reason: "Luna-first default or exact complex escalation trigger"
    dependencies: []
    read_scope: ["exact/read/path"]
    write_scope: ["exact/write/path"]
    do_not_touch: ["excluded/path or side effect"]
    expected_result: "Observable result"
    verification: "Exact procedure and passing condition"
    required_evidence: "Evidence bound to the final candidate"
    can_launch: true
    held_reason: null
stages:
  - [task-a, task-b]
  - [task-c]
integration_owner: controller
```

Every `done_when` item has a stable `REQ-*` ID. Every task maps to at least one
Requirement ID, and every Requirement ID has at least one owning task or an
explicit controller-owned integration check. Reject vague criteria, unowned
requirements, tasks with no acceptance evidence, and stages that violate a
dependency or ownership edge.

The controller states the smallest complete graph. It does not split work by
file merely to increase agent count.

## 3. Routing and stages

### Parallel AIR admission and batching

Parallel AIR is admitted only when all of the following are supported by
explicit relative-work estimates: the **parallelizable share** is **at least
65%**, the **largest branch** is **no more than 60%** of that parallelizable
share, and **coordination and integration overhead** is **no more than 15%** of
estimated Lean serial work. There must also be two or three
dependency-ready owners with disjoint writes and at least two live worker slots.
If any condition is missing or false, return `LEAN_RECOMMENDED` before dispatch
and let the Host use one Lean Luna Max Fast Primary.

An approved stage uses **two or three `air-efficient-worker`** leaves with the
**same `gpt-5.6-luna / max / fast`** configuration. Ordinary Parallel AIR has
**at most three concurrent** leaves. Never use Complex merely to increase
speed; the complex profile still requires a semantic escalation trigger below.
For a wider graph, schedule another wave only after dependencies and integration
evidence make it ready.

The Host launches the ready leaves as a **single concurrent batch**. The rule is
**do not wait worker-by-worker**: make **one long wait** that returns early for
updates and continue until every member of that batch is terminal. Then construct
one union manifest in **deterministic Task-ID order**. Require disjoint path sets,
the exact union of worker-reported paths, and matching final hashes in the active
workspace. Invoke the Git persistence transaction once for the complete union,
not once per leaf and without an intermediate semantic model turn. If the exact
union is not simultaneously visible or any identity differs, fail closed. Send
the controller one aggregate capsule containing every result, changed-path
identity, complete integrated diff, and verification artifact. The controller
performs **one aggregate final review** for the batch or issues the one permitted
focused correction to the original owner.

Choose the **efficient** profile by default for reversible workspace execution
when the packet has Requirement IDs, an observable acceptance condition, a
bounded read scope, one exact write scope, launch-ready dependencies, and a
falsifiable verification gate. Efficient work may include bounded
diagnosis-and-fix, ordinary multi-file changes inside one owned component,
local cross-file dependencies, tests, refactors, documentation, configuration,
and unfamiliar code. Do not require the root cause to be known before dispatch.

Choose the **complex** profile only when `routing_reason` names at least one
concrete escalation trigger: critical or high-consequence effects; concurrency
or migration correctness; an unresolved architecture or public/shared interface
decision that cannot fit one bounded component; non-deterministic verification;
genuinely irreducible broad context; materially conflicting evidence; or a
zero-write efficient failure that exposed a capability mismatch. Ordinary
cross-module work, local ambiguity, or cost preference alone is not a trigger.
These are not Complex triggers by themselves. Cost never overrides safety.
A complex task with no named trigger is an invalid plan.

Tasks in one stage may run concurrently only when:

- all dependencies are satisfied;
- their write scopes are disjoint;
- they do not mutate the same component, generated output, lockfile, shared
  configuration, migration state, or external resource;
- their combined launch count fits current live capacity.

Queue excess ready tasks for the next batch. If dependency order, generated
effects, or write overlap is uncertain, run sequentially. Later stages wait for
required earlier evidence.

Use the minimum sufficient parallelism. Parallel AIR uses two or three workers
and at most three concurrent leaves; this protocol cap is independent of a
possibly larger live capacity. Controller-only work may use zero workers, and
Lean uses exactly one Primary. Never create leaves just to fill capacity.

## 4. Ownership

Assign each writable file, component, shared interface, migration, generated
artifact, and external side effect to one owner for the entire run. Multiple
workers may read the same file. Alternative proposals may be gathered
read-only, but one selected owner performs the write.

Before dispatch, reject overlapping or ambiguous write scopes. Before
integration, the controller compares its recorded baseline with actual changed
paths and each packet. Preserve unrelated user changes. In Compatibility mode
the Host may transport deterministic snapshots, but it must not interpret them
as a second reviewer.

Ownership belongs to a stable logical owner slot for the run, not to the
lifetime of one child process. If a worker becomes unavailable, the Host may
restart the same exact custom profile in that logical owner slot only after a
fresh authoritative launch proof and a Host-owned snapshot of the current artifacts. This
is not an ownership transfer and does not reset any attempt, correction, or
recovery budget.

Never transfer an owned file after its logical owner writes it. The controller
may escalate an efficient-profile task once to the complex profile only when
the first failure occurred before any owned write and the unchanged task,
requirements, and scope remain with the same logical owner slot. After a write,
only the original logical owner may
modify that path through a focused correction or a same-run Recovery Re-plan.
A new owner is allowed only for a wholly disjoint blocker-removal scope.

## 5. Task and result contracts

### Worker task

```text
Mode: Coordinated Leaf
Task ID: <stable task id>
Task: <one bounded action>
Requirement IDs: <REQ-1, REQ-2>
Routing reason: <Luna-first default or exact complex escalation trigger>
Context: <optional minimal task-local input>
Read scope: <exact readable paths>
Write scope: <exact writable paths or []>
Do not touch: <excluded paths and side effects>
Dependencies: <completed prerequisite IDs or None>
Expected result: <observable acceptance condition>
Verification:
  Procedure: <exact command or procedure>
  Passing condition: <falsifiable passing condition>
Required evidence: <diff, output, artifact, or observation>
Stop conditions: <conditions requiring BLOCKED>
```

`Context` is optional; all other fields are required. Send the complete packet
in the first worker turn after Host-side runtime proof. A worker receiving an
incomplete, contradictory, unauthorized, dependency-incomplete, or trigger-free
complex packet returns `BLOCKED` without guessing.

### Worker result

```text
Task ID: <task id>
Status: PASS | BLOCKED
Summary: <what happened>
Inspected: <exact files>
Changed: <exact files, or None>
Requirement coverage: <each assigned REQ-ID and exact evidence>
Verification: <procedures and exact results>
Evidence: <diff, test, build, log, screenshot, or artifact>
Delivery: NONE | VISIBLE_CANDIDATE
Final file SHA256: <path=sha256-or-ABSENT for every changed file or None>
Assumptions: <explicit assumptions or None>
Risks: <remaining risks or None>
Failure class: runtime | timeout | model_identity | permission | dependency | scope | verification | evidence_quality | conflict | none
Blocker: <None or concrete blocker>
Runtime tier: requested=<fast | default>; actual=<priority | default | unobserved>
```

A worker approves only its task. Transport `completed` means delivery lifecycle
completion only; it, a prose summary, or an agent label is not a task `PASS`.
Likewise, a worker-local diff is not active-workspace persistence. Any changed
worker result without exact changed paths, final hashes, and a candidate that
remains visible for the Host's Git-generated replay is `BLOCKED`.

Treat the response's actual service tier as authoritative. If the runtime does
not expose it, record `unobserved`; TOML proves the request configuration, not
the tier that served the response.

If transport reports `completed` without the structured result, allow exactly
one result-only follow-up to that same worker. It authorizes no new write or
re-execution. A second missing or candidate-unbound result is classified as a
runtime failure; result-only recovery does not consume the correction or
Recovery Re-plan budget.

## 6. Verification and evidence

The controller defines the minimum falsifiable verification before dispatch.
The worker may add stronger checks but cannot lower the gate.

Examples:

- Code: exact test/build command, expected scope, exit code, and affected tests.
- Configuration: load with the real parser and assert required fields.
- UI: start the runnable product, complete the named path, inspect console and
  visual output, and capture evidence when needed.
- Documentation/design: render or open the final artifact and inspect required
  content and layout.
- Research: cite primary sources, separate fact from inference, and map findings
  to every Requirement ID.

Evidence must bind to the final candidate through a commit plus complete diff or
an exact changed-file snapshot. If the candidate changes, affected evidence is
stale. File existence, successful transport, a disconnected exit code,
"looks correct," or a worker's confidence is not evidence.

The controller verifies the verifier: the check must target the correct final
candidate, exercise the intended requirement, use the expected scope, retain a
falsifiable passing condition, and produce the required artifact. Wrong-module,
tautological, existence-only, skipped, unexpected test/lockfile-mutating, or
candidate-unbound checks fail under `evidence_quality`.

## 7. Review and correction

Review artifact-first:

1. Original request and `done_when`.
2. Baseline, dirty-worktree state, and actual changed paths.
3. Real files and complete diff.
4. Verification output and artifacts.
5. Requirement coverage.
6. Worker summaries and self-assessments.

Return:

```yaml
verdict: PASS | FIX | BLOCKED
requirements_coverage:
  - requirement: REQ-1
    status: satisfied | unsatisfied | blocked
    evidence: "Exact file, diff, output, or artifact"
findings: []
required_fixes: []
residual_suggestions: []
evidence_quality: sufficient | insufficient
remaining_risks: []
```

`PASS` requires every Requirement ID to be satisfied and evidenced, no
out-of-scope write, and verification bound to the final candidate. Optional
improvements remain residual and do not change a valid `PASS`. Any unsatisfied
Requirement ID is gating work, not a suggestion.

Issue at most one focused Correction Packet to the original owner. Keep the same
scope and include:

```text
Failure class: <non-none allowed class>
Finding: <specific failed requirement or evidence defect>
Delta: <changed instruction, narrowed action, or new evidence>
Verification: <unchanged or stronger falsifiable gate>
```

Do not relaunch an identical packet without new evidence. Do not use a failed
task as permission for broader refactoring.

When the focused correction is exhausted and the remaining failure is
`runtime`, `timeout`, `dependency`, `verification`, or `evidence_quality`, do
not automatically end the run. The controller may issue one Recovery Re-plan
per affected Requirement chain when it has a material Delta and all work remains
authorized, reversible, and bounded:

```text
Recovery ID: <stable recovery id>
Run ID: <existing run id>
Affected Requirement IDs: <REQ-1, REQ-2>
Prior Task IDs: <attempted task and correction ids>
Failure class: <recoverable non-none class>
Material Delta: <new diagnosis, resolved prerequisite, narrowed action, or new evidence>
Preserved completed work: <task ids and bound evidence>
Ownership: <existing logical owners plus wholly disjoint new owners>
Recovery tasks: <new task ids with complete ordinary task packets>
Resume condition: <falsifiable condition for resuming affected unfinished work>
Terminal condition: <condition that exhausts this Requirement chain>
```

Keep the same controller and `run_id`. Preserve candidate identity, completed
work, ownership, attempt history, and the exhausted correction. Reuse a live
verified worker when it remains the logical owner. If it is unavailable,
restart the same exact custom profile into the same logical owner slot after a
fresh authoritative launch proof and artifact snapshot; this is not an
ownership transfer. A new worker may own only a wholly disjoint blocker-removal scope. The recovery
task has at most one focused correction, and task renaming does not reset the
Requirement chain's recovery budget.

This recovery stays in the same run and does not require a new `$codex-air`
invocation. The controller must not return final `BLOCKED` only because the
original task used its correction. Terminal `BLOCKED` is valid only when a hard
permission, model-identity, unauthorized-scope, or irreversible blocker exists;
there is no material Recovery Re-plan Delta; or the one recovery re-plan and its
focused correction failed to make the resume condition true.

## 8. Failure handling

Classify a failure before retrying:

- `model_identity`: requested profile cannot be proved; fail closed.
- `permission`: effective boundary cannot safely support the authorized action.
- `scope`: changed path or side effect exceeded the packet.
- `verification` or `evidence_quality`: result lacks falsifiable proof.
- `dependency`: prerequisite or environment is unavailable.
- `conflict`: worker results or ownership claims disagree.
- `runtime` or `timeout`: transport/runtime failed.

First inspect whether the packet was ambiguous. Repair the packet when that is
the cause, then allow at most one narrow focused correction under the ownership
rules. If a recoverable failure remains, apply the same-run Recovery Re-plan
contract instead of converting correction exhaustion directly into terminal
`BLOCKED`. Escalate conflicting results to the controller for arbitration;
never mechanically merge summaries or let a Coordinated Leaf approve the Full
run.

Use zero challenge calls for ordinary low-risk work, ordinary cross-module
changes, or bounded debugging. For a critical-risk run, materially conflicting
final-candidate evidence, or an unresolved security or authorization
Requirement ID, dispatch only `air-challenger` for at most one bounded
read-only challenge, with
`write_scope: []` and a final-candidate identity. It may return findings or no
findings, but it never edits, creates subagents, issues the overall verdict, or
becomes a second reviewer. It cannot become a second reviewer through repeated
follow-ups.

## 9. Continuity

After authorization, a plan is not a stop point. Continue through approved
stages unless a new permission request, irreversible choice, real blocker,
explicit cancellation, replacement, or redirection appears. A status inquiry
does not pause work. User urgency does not lower the verification gate.
During authorized execution, `FIX` is an intermediate control action: dispatch
the correction or Recovery Re-plan and return its evidence to the same
controller. Do not end the user turn or request another Skill invocation while
the bounded recovery path remains available.

The Host sets a bounded planning timebox proportional to task risk and size.
When it expires, the controller returns the smallest executable graph, a
concrete decision, or the exact missing evidence; it does not continue
open-ended analysis. If a later stage becomes blocked, deliver any earlier
stage whose Requirement IDs and final-candidate evidence are complete, and
label the remaining blocker without upgrading partial evidence into overall
`PASS`.

After the controller emits its structured terminal verdict, the Host relays it
without rereading repository files, rerunning verification, or producing a
second artifact judgment. A malformed or truncated terminal result permits one
result-only follow-up to the same controller.

For long, interrupted, or context-compressed runs only, use a resume packet and persist:

```yaml
run_id: "stable id"
goal: "current goal"
completed: []
in_flight: []
ownership: {}
requirement_coverage: {}
candidate_identity: "commit+diff or snapshot"
attempts: {}
recovery_chains: {}
artifact_location: "path or record"
next_action: "one concrete action"
```

On resume, rebuild state from real artifacts, do not redispatch completed tasks,
do not reset attempts, corrections, or recovery budgets, and re-plan or return
`BLOCKED` on candidate mismatch.
