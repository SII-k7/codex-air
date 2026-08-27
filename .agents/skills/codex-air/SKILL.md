---
name: codex-air
description: Use Sol xhigh to understand, explore, decompose, and review substantial coding work while Luna Max executes with Fast requested, only when the user explicitly invokes $codex-air.
---

# Codex AIR

AIR means **Adaptive Intelligence Routing**:

- **Sol xhigh controls semantics:** intent, repository exploration, solution
  selection, decomposition, authorization, and final review.
- **Luna Max executes with Fast requested:** bounded implementation, diagnosis,
  verification, and correction.

Terra is forbidden; Luna never approves and Sol never writes. Enter only for
explicit `$codex-air` or deprecated `$codex-prove`. Never infer AIR, make it a
default, or recurse. Capability is not authorization and never widens scope.

Use the language of the user's visible request or preference;
无法判断时默认使用中文。Preserve code, commands, paths, identifiers, and raw evidence.

## Admission and controller

Classify from the visible request before repository exploration:

- **Direct:** answers, tiny edits, or localized work where dispatch overhead
  dominates;
- **Controlled AIR:** substantial coding, diagnosis, refactoring, migration,
  multi-file work, or work needing exploration;
- **Critical AIR:** authentication/authorization, secrets, payments, production
  or irreversible effects, privacy, migration/concurrency correctness, or
  comparable risk.

Reuse the Host only with authoritative proof of exact `gpt-5.6-sol`, `xhigh`, and
Standard requested tier. Any other proved Sol Host may transport exactly one
read-only fallback `air-controller` (`air-critical-controller` for visible risk)
with `fork_turns="none"` only when the exact profile/launch is proved; record its
actual effort/tier as Sol overhead. Luna, Terra, other, or unknown Hosts return
`BLOCKED` / `model_identity` before AIR child calls. Never switch controllers.

For Controlled/Critical AIR read
[references/orchestration.md](references/orchestration.md). Read
[references/runtime-notes.md](references/runtime-notes.md) only for identity,
nesting, capacity, tier, persistence, or recovery.

## Sol decision contract

Before writes, the same Sol reads applicable instructions and minimum relevant
code; records stable Requirement IDs/conditions, decisive repository observations,
non-goals, risks, baseline, authority, verifier, one solution, and ownership; then
stops at decision sufficiency. Explore alternatives only for an unresolved
material decision. Leave reversible local mechanics to one Luna by default.

Create one whole-run envelope: deadline; priced cap/unit and hard/projected state;
Sol phases; aggregate Luna calls/launches; replan <=1; correction <=1 total;
challenger=0 normally or <=1 explicit/high-consequence; remaining budget. Branches,
`FIX`, and replan share it without reset. Launch only work that fits.

Before any write Luna returns `REPLAN_NEEDED` only when a decisive observation is
false, the approach cannot satisfy a requirement, scope must expand, the verifier
is invalid, or authority/critical risk changes. Hidden Critical risk makes the
same Sol set `Mode: Critical In-Place` before approval or further writes, add
safety, authorization, rollback, and rollback-verification conditions, and keep
the envelope. If they cannot be established, return `BLOCKED` / `critical_risk`.

## Compact execution packet

Launch with `fork_turns="none"` and send only:

```text
Mode: Single Executor | Coordinated Leaf | Critical In-Place
Task ID: <stable id>
Requirement IDs: <owned requirements and completion conditions>
Chosen solution: <semantic approach and fixed interfaces>
Decisive observations: <facts to verify before writes>
Write scope: <exact paths or narrow glob>
Read scope: <exact paths plus named local dependencies>
Do not touch: <paths, interfaces, side effects>
Baseline: <HEAD and relevant dirty paths>
Verification: <exact commands and passing behavior>
Run envelope: <absolute deadline; priced cap+unit and hard/projected; Sol phases; aggregate Luna calls/launches; replans; corrections; challengers; remaining>
Efficiency budget: <worker share of calls/time/verifier repeats and Host enforcement>
Parallel proof: <share/largest/coordination/critical-path ratios, dependencies, ownership, capacity, branch ceilings; or NONE>
Authorization boundary: <allowed workspace/external effects>
Stop conditions: <REPLAN_NEEDED or BLOCKED conditions>
Required final report language: <language>
```

Do not copy skill text, history, broad listings, unrelated diffs, or generic
process prose. Sol pays once for semantic exploration; Luna gets its result.

## Luna execution

Use `air-efficient-worker` normally; reserve `air-complex-worker` for a bounded
public interface, large context, migration/concurrency, or high consequence.
Both use the same Luna Max profile and request Fast.

Luna verifies facts, implements, corrects bounded failures, audits its diff, and
keeps it visible. It preserves unrelated work and cannot spawn, widen, redesign,
or approve. Python checks use `PYTHONDONTWRITEBYTECODE=1` unless under test.
Evaluation isolation forbids sibling worktrees, hidden tests/solutions, prior
trajectories, and benchmark outputs.

Stop after the first passing required final verifier and complete diff audit.
These worker ceilings are shares, never renewable allowances:

| Worker | Converge by | Hard tool ceiling | Hard wall time |
| --- | ---: | ---: | ---: |
| `air-efficient-worker` | 48 calls | 80 calls | 30 minutes |
| `air-complex-worker` | 96 calls | 180 calls | 60 minutes |

At convergence continue only for a named unmet Requirement ID. At a hard ceiling,
incomplete evidence returns `BLOCKED` / `budget`. The Host uses one event-driven
wait until completion, absolute deadline, or authoritative live cap, then
interrupts active workers once and never retries. Without authoritative
credit/tool telemetry, cost/call limits are projected or cooperative; only the
deadline and launch count are mechanically enforced. Every Luna internal
correction decrements the run's correction counter.

Luna returns one terminal record; the Host appends tier and authoritative run
counters from telemetry:

```text
Task ID: <task id>
Status: PASS | REPLAN_NEEDED | BLOCKED
Changed: <exact paths or None>
Requirement coverage: <REQ-ID -> final-candidate evidence>
Verification: <exact command, exit status, decisive result>
Evidence: <artifact-bound evidence>
Delivery: NONE | VISIBLE_CANDIDATE
Final file SHA256: <path=sha256-or-ABSENT for every changed file or None>
Assumptions: <material assumptions or None>
Risks: <material residual risks or None>
Budget used/remaining: <deadline/wall; priced used/remaining+unit+status; Sol phases; Luna calls/launches; replans; corrections; challengers>
Failure class: runtime | timeout | budget | model_identity | permission | dependency | scope | verification | evidence_quality | conflict | critical_risk | none
Blocker: <concrete blocker or None>
Runtime tier: requested=fast; actual=<priority | default | unobserved>
```

## Parallelism, persistence, and review

One Luna executor is the default. Use two or three only when `Parallel proof`
records executable-time estimates: parallel share **>=65%**, largest branch
**<=60%**, coordination **<=15%**, critical path versus serial **<=0.85**, ready
dependencies, disjoint ownership, live slots, and aggregate branch ceilings
inside the envelope. Launch one batch; the same Sol reviews the union.

A child `PASS` is not delivery. Its exact paths/hashes must already be visible in
the controller workspace through sharing or official artifact transport. Check
directly; optionally run read-only `scripts/persist-visible-candidate.sh
--workspace <absolute-workspace> -- <exact-relative-path>...`. It neither
discovers/transfers paths nor mutates the tree. Matching output is `PERSISTED`.
Isolation without transport, invisibility, mismatch, or replay failure is runtime
`BLOCKED`; never ask an LLM to reconstruct a patch.

The same Sol reviews real final files as needed, the complete in-scope diff,
Requirement coverage, and final-candidate evidence. It must verify the verifier
without rerunning a trusted fresh pass absent a concrete gap, then returns:

```text
Verdict: PASS | FIX | BLOCKED
Requirement coverage: <REQ-ID -> artifact and evidence>
Artifact review: <complete diff assessment>
Verification assessment: <why checks prove the request>
Risks: <material residual risks or None>
Fix owner: <Task ID or None>
Failure class: <class or none>
Blocker: <concrete blocker or None>
```

Only Sol can issue overall `PASS`. One focused `FIX` total goes to the same Luna
owner only when correction remaining >0, then fresh persistence/review. At most
one replan is allowed. A further material miss, scope expansion, or solution
change is `BLOCKED`. Challenger count is zero normally and at most one when
explicitly requested or needed for a high-consequence falsification gap.

## Evaluation targets, not results

Every Luna executor configuration permanently requests Max with Fast; Sol
requests exact xhigh on Standard. Actual identity/tier still needs proof,
and Terra usage must remain zero. Establish quality parity first, then target:

- priced cost <=**55%** of Direct Sol xhigh;
- wall-time ratio **0.85x–1.15x**;
- >=**70%** of model tokens on Luna;
- raw model tokens <=**1.10x** Direct initially and <=**1.00x** after tuning;
- one Sol semantic controller, one Luna executor, and no routine challenger.

Record model/tier tokens and cost, requested/observed tier, time, quality,
corrections, calls/polls, and critical path. Never trade safety/evidence for cost.
