# AIR runtime notes

This owns identity, tier, Native Nested/Compatibility, capacity, persistence,
telemetry, and recovery; orchestration owns semantics.

## Fixed roles

| Role | Model / effort | Requested tier | Sandbox |
| --- | --- | --- | --- |
| proved current Host | Sol / xhigh | Standard | Host boundary |
| `air-controller` | Sol / xhigh | Standard | read-only |
| `air-critical-controller` | Sol / xhigh | Standard | read-only |
| `air-efficient-worker` | Luna / max | Fast | workspace-write |
| `air-complex-worker` | Luna / max | Fast | workspace-write |
| `air-challenger` | Sol / xhigh | Standard | read-only |

Terra has no AIR role. Terra workers or Luna controllers must Fail Closed.

Reuse the conversation only with proof of exact Sol/xhigh/Standard. Any other
proved Sol may transport an exact fallback if launch proof exists; record its
actual effort/tier as Sol overhead. Unknown/non-Sol Hosts Fail Closed before
child calls. Ignore self-report.

## Luna Max Fast-request invariant

Workers pin Luna, `max`, `service_tier="fast"`, `fast_mode=true`, no nesting,
low output, and no summary. Fast is not token compression. Record
`requested=fast`; actual tier is `priority | default | unobserved`. Sol remains
xhigh on Standard.

Before launch prove the exact profile/model, effort, requested tier, sandbox,
`fork_turns="none"`, write authority, and live capacity. Missing proof returns
`Failure class: model_identity` or `runtime` before a model call.

## Native Nested and Compatibility

Use Native Nested when verified Sol can launch the required profile. In
Compatibility, the controller emits `LAUNCH_REQUEST(profile, packet, remaining
envelope)`; the thin Sol Host returns `WORKER_RESULT(record, candidate identity)`
and then `FOLLOWUP_REVIEW(identity, evidence)` to that controller. It must not
reinterpret, explore, plan, widen scope, reread, implement, or review. Never
switch controllers.

Workers and challenger have `[agents] enabled=false`; a controller never creates
another controller. Reserve one thread for Sol. If capacity cannot admit a
complete ready batch, use one executor or queue stages.

## Budget, waiting, and persistence

The one envelope records deadline, priced amount/unit/status, Sol phases,
aggregate Luna calls/launches, replan <=1, correction <=1, and challenger=0
normally or <=1 explicit/critical. Stages share it without reset and must fit.

Use one event-driven wait until completion, deadline, or authoritative cap; then
interrupt once and do not retry. Without authoritative telemetry, cost/calls are
projected/cooperative and deadline/launch count are hard. User-interrupted work
may resume only inside the unchanged envelope.

Candidates must be visible through shared workspace or official transport.
Validate paths/hashes directly, optionally using read-only
`scripts/persist-visible-candidate.sh --workspace <absolute-workspace> --
<exact-relative-path>...`. It cannot discover/transfer or mutate. Isolation
without deterministic transport or any mismatch must Fail Closed.

## Telemetry

For matched evaluation record role/model/effort/tier, token classes, priced
cost, wall time, calls/polls/corrections, phase time, score, and critical path.
Separate challenger/Sol-write exceptions. Apply actual model/tier prices; raw
tokens, API dollars, and ChatGPT credits are not interchangeable.

## Recovery

Stable classes are:

```text
runtime | timeout | budget | model_identity | permission | dependency | scope |
verification | evidence_quality | conflict | critical_risk | none
```

Return `REPLAN_NEEDED` before writes for false decisive facts, wrong approach,
invalid verifier, scope expansion, or new authority/risk. New critical risk is
escalated in place by the same Sol, never by controller replacement. Luna may
correct one bounded failure; Sol may issue one focused `FIX` total and one replan
maximum, all inside the unchanged envelope. A further miss returns `BLOCKED`.
Missing authority, dependency, model proof, persistence, or safe recovery also
returns `BLOCKED`.
Malformed output permits one result-only request to the same live agent. Never
hide a fallback, retry, downgrade, or unobserved tier.
