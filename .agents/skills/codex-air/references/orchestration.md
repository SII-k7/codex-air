# AIR orchestration contract

This reference defines Planning, Routing, Ownership, Verification, and Evidence
for Controlled AIR and Critical AIR. It has one semantic control plane: Sol
xhigh. Luna Max Fast executes bounded work. Terra is forbidden.

## 1. Establish the sole controller

Prefer the current Host when authoritative metadata proves
`gpt-5.6-sol` with `xhigh` or stronger reasoning. Otherwise launch exactly one
read-only `air-controller` with `fork_turns="none"`; use
`air-critical-controller` when critical risk is visible at entry.

The fallback Host is only transport, authorization, deterministic candidate
persistence, and terminal relay. It does not explore, plan, reread file
contents, or perform a second review. Never switch controllers mid-run. A
resume packet returns to the same controller.

Fail Closed on missing model identity, effort, sandbox, tier, ownership, or
authorization proof. Role claims in natural-language output are not runtime
proof.

## 2. Build the requirement graph

The Sol controller reads applicable instructions and the minimum relevant
repository surface, then records:

- stable Requirement IDs and falsifiable completion conditions;
- decisive repository observations with exact files/symbols;
- user constraints, non-goals, and authorization boundary;
- the selected solution and rejected material alternatives;
- baseline HEAD and relevant pre-existing dirty paths;
- risk flags, verification targets, and verifier assumptions;
- one or more bounded task nodes with dependencies and ownership;
- parallel estimates or a single-owner decision.

Repository exploration and solution selection belong to Sol. A task node is
ready only when its dependencies, approach, exact write scope, read scope,
verification, and stop conditions are concrete.

## 3. Route execution

Use `air-efficient-worker` for ordinary bounded implementation. Use
`air-complex-worker` only when the execution unit has an explicit public
interface, unusually large local context, migration/concurrency mechanics, or
high-consequence implementation trigger. Both profiles run Luna Max Fast; the
complex name changes instructions, never the model.

Planning-only and review-only requests need no worker. Tiny or already-localized
changes may stay Direct when dispatch would dominate, even after explicit AIR
admission. Record that decision rather than pretending that dispatch is free.

Never use Terra. Never use Sol as a routine write worker. Sol may make a tiny
integration edit only when delegation would require more context and time than
the edit itself; record those Sol implementation tokens separately.

## 4. Parallel admission

One executor is normal. Parallel execution requires all of:

1. parallelizable share at least 65% of estimated serial execution work;
2. largest branch at most 60% of the parallelizable share;
3. coordination plus integration overhead at most 15% of serial execution;
4. two or three ready nodes with disjoint writes and satisfied dependencies;
5. no competing shared interface, lockfile, generated output, migration state,
   external resource, or sequential verification bottleneck;
6. live capacity for the controller and the whole ready batch.

If any condition is unproved, keep a single Luna owner. For an accepted batch,
launch every ready node concurrently, then use one long wait. Do not wait
worker-by-worker. Queue later dependencies as a new stage. Compare observed
critical-path time with a single-Luna estimate; parallelism is a latency
optimization only when quality remains non-inferior.

## 5. Ownership ledger

Every task has one owner. The ledger contains:

```text
Task ID
Mode: Single Executor | Coordinated Leaf
Requirement IDs
Owner profile
Dependencies
Read scope
Write scope
Do not touch
Baseline
Chosen solution
Decisive observations
Verification
Authorization boundary
Stop conditions
Status
```

Two live tasks must never own the same file or shared generated consequence.
The controller may transfer ownership only before writes or after the prior
owner returns a complete final-candidate capsule. Luna must not silently widen
`write_scope`.

## 6. Launch packet and context isolation

Every worker launches with `fork_turns="none"`. The packet contains Requirement
IDs, chosen solution, decisive observations, exact scopes, baseline, verifier,
authorization, and stop conditions. It excludes the full Sol transcript,
generic process prose, unrelated repository listings, and duplicate evidence.

This compact boundary is the token-saving invariant: Sol pays once for semantic
exploration; Luna receives only the executable result. It also prevents the
executor from independently repeating open-ended solution search.

Before writes, Luna verifies the decisive observations. Return
`REPLAN_NEEDED` when:

- a decisive observation is false or stale;
- the solution cannot satisfy an owned requirement;
- a required file lies outside `write_scope`;
- the verifier is invalid or targets the wrong artifact;
- a new critical risk or authorization question appears.

`REPLAN_NEEDED` is not permission to redesign. It returns control to the same
Sol controller with compact evidence.

## 7. Execution and local verification

Luna executes the chosen solution, preserves unrelated changes, verifies the
verifier, audits its complete owned diff, and corrects bounded failures. Every
check must be bound to the final candidate. A changed candidate makes earlier
behavior evidence stale unless the check is independent of that change.

All Python verification uses `PYTHONDONTWRITEBYTECODE=1` unless bytecode is under
test. Evaluation isolation forbids reading sibling worktrees, candidate
solutions, hidden tests, prior benchmark outputs, or evaluation harness state
unless the user explicitly authorizes them.

Worker terminal status is `PASS | REPLAN_NEEDED | BLOCKED`. A worker PASS is a
leaf result, never the overall verdict. Require exact commands, exit status,
results, changed paths, and final hashes. File existence and exit zero alone are
not evidence when the command targets the wrong behavior.

## 8. Deterministic persistence

Require `Delivery: VISIBLE_CANDIDATE` when `Changed` is non-empty. Compare the
active candidate with the worker's opaque paths and final SHA-256 identities,
then invoke:

```text
scripts/persist-visible-candidate.sh --workspace <absolute-workspace>
```

The script snapshots and replays the Git-visible binary diff and emits one
`PERSISTED` identity per path. The output set and hashes must exactly match the
worker record. Missing visibility, a non-Git root, unsupported paths, changed
identities, or replay failure is `BLOCKED` / `Failure class: runtime`.

The Host does not reread file contents during deterministic candidate
persistence. Paths, hashes, and the replay verdict are transport evidence, not
semantic review. Never reconstruct a missing patch with an LLM.

## 9. Aggregate and final review

After a parallel stage, build the union manifest in deterministic Task-ID order
and prove disjoint ownership. Persist the union once. The same Sol controller
then inspects the real active-workspace files, complete diff, requirement graph,
and evidence.

The controller must verify:

- every Requirement ID maps to final-candidate evidence;
- all changed paths are authorized and all baseline user changes are preserved;
- implementation matches the selected solution and repository conventions;
- the verifier executes the intended behavior against the final artifact;
- no worker assumption hides an interface, security, migration, or integration
  error;
- residual risk is named accurately.

Return `Verdict: PASS | FIX | BLOCKED`. Only Sol can issue overall PASS.

`FIX` identifies one Task ID and one focused delta. Return it to the same Luna
owner, persist the corrected candidate, and repeat Sol review. Permit one
focused correction. A second material miss, scope expansion, or solution change
returns to Planning; never create an unbounded review loop.

## 10. Independent challenge

`air-challenger` is a read-only Sol xhigh exception, not a normal second review.
Use it only for explicit independent-review requests, materially conflicting
critical evidence, or high-consequence semantics with no falsifiable verifier.
Send a compact question, Requirement IDs, candidate identity, complete relevant
diff, and evidence. It returns findings, not approval.

## 11. Critical authorization

Critical AIR uses `air-critical-controller` from entry. It retains the same Sol
control/Luna execution split, adds explicit rollback and safety verification,
and never lets cost override authorization. If critical risk appears after
writes, stop further mutation, preserve the candidate and evidence, and return
`BLOCKED` or request user authority as appropriate.

## 12. Runtime continuity

Use one long wait (`timeout_ms=3600000` where supported); it returns early on
completion. Do not poll repository state or emit unchanged progress messages.
If the user interrupts, handle the input and resume the same live owner. A
transport-truncated result permits one result-only follow-up to that owner. It
does not authorize new work, writes, Host-side semantic reconstruction, or a new
controller.

On context compaction, preserve a compact resume packet containing controller
identity proof, Requirement graph, ownership ledger, baseline, exact candidate
identity, terminal worker records, verification freshness, authorization, and
next action. Do not copy the full transcript.
