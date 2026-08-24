# AIR runtime notes

Use this reference only for runtime identity, tier, nesting, capacity,
persistence, and recovery. The orchestration contract remains authoritative for
Planning, Routing, Ownership, Verification, and Evidence.

## Fixed role matrix

| Runtime role | Purpose | Model / effort | Tier | Sandbox |
| --- | --- | --- | --- | --- |
| Current Host | Preferred sole semantic controller when identity is proved | Sol / xhigh or stronger | Standard | Host boundary |
| `air-controller` | Fallback semantic controller | Sol / xhigh | Standard | read-only |
| `air-critical-controller` | High-consequence semantic controller | Sol / xhigh | Standard | read-only |
| `air-efficient-worker` | Ordinary bounded execution | Luna / max | Fast | workspace-write |
| `air-complex-worker` | Broader/high-consequence bounded execution | Luna / max | Fast | workspace-write |
| `air-challenger` | Exceptional independent falsification | Sol / xhigh | Standard | read-only |

Terra has no AIR role. A runtime that maps either worker to Terra or maps a
controller to Luna is incompatible and must Fail Closed.

## Prefer the current Sol Host

The current conversation contains the user's language, decisions, and
authorization. Reuse it as controller when authoritative metadata proves Sol
xhigh. This avoids paying for a second Sol context and preserves conversational
continuity. Do not make it thin after it has accepted semantic ownership.

If identity or effort cannot be proved, use exactly one fallback controller with
`fork_turns="none"`. The Host becomes thin for that run. Natural-language model
self-identification is not proof.

## Luna Max Fast invariant

Both execution profiles permanently pin:

```toml
model = "gpt-5.6-luna"
model_reasoning_effort = "max"
service_tier = "fast"

[features]
fast_mode = true
```

Fast is a latency tier, not token compression. Record `requested=fast` and the
actual response tier (`priority`, `default`, or `unobserved`) separately. Never
silently downgrade Luna to save credits. Both profiles also disable nesting,
use low verbosity, omit reasoning summaries, and cap tool output so cheap
execution tokens are not wasted on orchestration prose.

Sol controllers and the challenger pin `model_reasoning_effort="xhigh"` and
`service_tier="default"`. Do not enable Fast for Sol in AIR; the architecture
spends Sol only on high-leverage semantic work.

## Launch proof

Before each child launch, prove from authoritative Host/tool metadata:

- exact agent type and configured model;
- reasoning effort and requested service tier;
- sandbox boundary;
- `fork_turns="none"`;
- requested write scope and authorization;
- live thread capacity.

Do not launch on an alias guess, inherited-history assumption, or agent
self-report. Fail Closed with `Failure class: model_identity` or `runtime` when
proof is unavailable.

## Native Nested and Compatibility

Use Native Nested when the verified Sol controller can launch worker profiles
directly. It keeps ownership and review inside one semantic controller.

Compatibility mode exists for runtimes where the fallback controller is
read-only and cannot spawn. The thin Host may mechanically launch the exact
worker requested by the controller, relay the complete packet unchanged, wait,
perform deterministic candidate persistence, and relay the compact result to
the same controller. The Host must not reinterpret the task, choose another
profile, widen scope, or approve the candidate.

Workers and challenger have `[agents] enabled=false`; they never create
subagents. A controller must not create another controller.

## Capacity and waiting

Reserve one thread for the active Sol controller. Single Executor needs one
additional worker slot. Parallel AIR requires capacity for the full ready batch;
otherwise retain one executor or queue stages.

After launch, use one long agent wait (`timeout_ms=3600000` where supported).
The wait returns early on completion. Do not short-poll, reread repository state,
or emit unchanged updates. User input interrupts the wait; process it, preserve
ownership, then resume the same live task.

## Candidate persistence

Write-capable child sessions may use isolated worktrees. A Luna `PASS` therefore
requires exact changed paths, `Delivery: VISIBLE_CANDIDATE`, and one final hash
per path. When active files match, run:

```text
scripts/persist-visible-candidate.sh --workspace <absolute-workspace>
```

Git snapshots the visible dirty state, reverses it, reapplies it, and verifies
byte-identical final identities. The `PERSISTED` set must match the worker
manifest exactly. This operation is mechanical and does not add a semantic
reviewer. On failure, return runtime BLOCKED; never ask a model to serialize or
reconstruct the patch.

## Telemetry

For every matched evaluation record:

- controller model, effort, tier, input/cached/output tokens, and wall time;
- executor profile, requested/actual tier, tokens, wall time, and correction
  count;
- any challenger or Sol implementation tokens as separate exceptions;
- dispatch, persistence, and final-review time;
- parallel batch span and slowest branch when applicable;
- verifier result and final quality score;
- direct baseline and AIR cost computed with each model/tier's own price.

Do not infer dollar cost from raw tokens or assume ChatGPT credits equal API
dollars. Fast pricing must be applied to Luna Fast rather than Luna Standard.

## Failure and recovery

Use stable failure classes:

```text
runtime | timeout | model_identity | permission | dependency | scope |
verification | evidence_quality | conflict | critical_risk | none
```

Recovery rules:

- false decisive observation, wrong solution, or scope expansion:
  `REPLAN_NEEDED` to the same Sol controller before writes;
- bounded implementation or verifier failure: Luna corrects once while inside
  the packet;
- Sol final-review `FIX`: one delta packet to the same Luna owner;
- second material failure or solution change: return to Sol Planning;
- missing authority, unavailable dependency, model mismatch, persistence
  failure, or exhausted safe recovery: `BLOCKED`;
- malformed terminal output: one result-only follow-up to the same live agent.

Never hide a fallback, downgrade, retry, or missing tier observation. Runtime
recovery must preserve one owner, the authorization boundary, and evaluation
isolation.
