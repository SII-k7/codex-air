# AIR orchestration contract

This is the normative source for Planning, Routing, Ownership, Verification,
and Evidence in Controlled AIR and Critical AIR. Sol xhigh owns the semantic
control plane; Luna Max executes bounded packets with Fast requested. Terra is
forbidden.

## 1. Sole controller and decision sufficiency

Reuse the Host only with proof of exact `gpt-5.6-sol` / `xhigh` / Standard
requested tier. Any other proved Sol Host may transport one exact fallback
controller if profile/launch proof exists; record its actual effort/tier as Sol
overhead. It cannot explore, plan, reread, implement, or review. Non-Sol/unknown
Hosts are `BLOCKED` / `model_identity` before child calls. Self-report is not
proof. Never switch controllers.

At **decision sufficiency**, Sol has falsifiable requirements, decisive facts,
one approach, fixed interfaces, ownership, risks, authority, and verifier.
Explore an alternative only for one unresolved material decision.

## 2. Requirement graph and routing

Record Requirement IDs/conditions, decisive observations, non-goals, solution,
baseline/dirty paths, verifier assumptions, and bounded nodes. Sol owns semantics;
Luna owns reversible mechanics inside fixed scope.

Use `air-efficient-worker` normally; reserve `air-complex-worker` for a bounded
public interface, large local context, migration/concurrency, or high consequence.
Both are Luna Max with Fast requested. Tiny localized work stays Direct before
AIR admission. Every AIR write is Luna-owned; Sol and Terra never implement.

## 3. Parallel admission

One executor is normal. `Parallel proof` estimates executable-time ratios:
share >=65%, largest branch <=60%, coordination <=15%, critical path/serial
<=0.85; and proves ready dependencies, disjoint consequences, live slots, and
branch ceilings inside the envelope. Shared interfaces/state or sequential
verification close the gate. Launch one batch and one long wait; quality remains
non-inferior and authorization unchanged.

## 4. Ownership and packet

Every task has one owner; live tasks must never own the same file/consequence.
Transfer only before writes or after a terminal capsule. Never widen `write_scope`.

With `fork_turns="none"`, send the `SKILL.md` packet, remaining envelope, worker
share, and `Parallel proof`/`NONE`; omit conversation, protocol copies, broad
listings, unrelated diffs, and duplicate evidence.

Before writes, return `REPLAN_NEEDED` to the same controller when a decisive
fact is false, the approach cannot satisfy a Requirement ID, scope must expand,
the verifier targets the wrong artifact, or authority/critical risk changes.
This is evidence for replanning, not permission to redesign.

Hidden critical risk triggers `Mode: Critical In-Place` in the same Sol
controller before approval or further writes. It adds safety, authorization,
rollback, and rollback-verification obligations and inherits the unchanged run
envelope. If they cannot be established, return `BLOCKED` / `critical_risk`.

## 5. Efficient execution state machine

The run envelope fixes deadline, priced cap/unit/status, Sol phases, aggregate
Luna calls/launches, replan <=1, correction <=1 total, and challenger=0 normally
or <=1 explicit/critical. Every stage spends it without reset; reject poor fits.

Luna follows `discover -> implement -> focused verify -> correct -> final verify
-> report`. Group reads; do not reread unchanged files, branch, or commit unless
required. Run each verifier once per candidate state and an unchanged failure
never twice. After verification/diff audit, report. Wait >=30 seconds on long
commands, never one-second poll. Incomplete evidence at a ceiling is `BLOCKED` /
`budget`.

Use `PYTHONDONTWRITEBYTECODE=1` unless bytecode is under test. Evaluation isolation
forbids sibling worktrees, candidate solutions, hidden tests, prior trajectories,
benchmark output, and harness state. Worker PASS is a leaf bound to commands,
statuses, paths, Requirement coverage, and final SHA256 identities.

## 6. Deterministic candidate persistence

Require `VISIBLE_CANDIDATE`, exact paths, and hashes already visible in the
controller's active workspace through shared semantics or official transport.
Validate them directly; an optional read-only replayability check is:

```text
scripts/persist-visible-candidate.sh --workspace <absolute-workspace> -- <exact-relative-path>...
```

The script never discovers paths, transfers an isolated candidate, or mutates
the worktree. Its complete `PERSISTED` set must match. An isolated-only candidate
without deterministic transport, missing visibility, hash mismatch, or replay
failure is runtime `BLOCKED`; never ask an LLM to reconstruct a patch.

## 7. Sol final review and bounded repair

The same Sol inspects real files as needed, complete diff, Requirement coverage,
and fresh evidence. Verify the verifier; rerun a trusted pass only for a concrete
freshness, coverage, or environment gap.

Return `Verdict: PASS | FIX | BLOCKED`. Only Sol can issue overall PASS. Permit
one focused `FIX` total to the same Luna owner and at most one replan, each using
the remaining envelope and followed by fresh persistence/review. A further miss,
scope expansion, or solution change is `BLOCKED`; budgets never reset.

Use `air-challenger` only for an explicit independent review or one unresolved
high-consequence falsification question. It returns findings, never approval.
Critical AIR additionally requires explicit safety invariants, authorization,
rollback conditions, and rollback verification; cost cannot relax them.

## 8. Continuity

Wait event-driven until completion, deadline, or authoritative cap; interrupt
once, preserve visible work, and do not retry. Without telemetry, priced/tool
caps are projected/cooperative; deadline and launches are mechanical. User
interruption may resume the owner within the unchanged envelope. One truncated
result-only follow-up is allowed. On compaction keep
controller proof, requirements, ownership, baseline, candidate/evidence,
authorization, remaining budget, and next action—not the transcript.
