# Codex AIR runtime profiles

Use this reference only for role selection, launch proof, nesting, capacity,
service tiers, model replacement, telemetry, or runtime recovery.

## 1. Stable roles and current defaults

Role names are model-neutral compatibility interfaces:

| Agent type | Capability role | Default | Requested tier | Boundary |
|---|---|---|---|---|
| `air-efficient-worker` | Lean Primary end-to-end owner; Parallel/Coordinated Leaf for bounded ordinary work | Luna / Max | Fast | workspace-write |
| `air-controller` | parallel or controller-only non-critical graph owner and final reviewer | Luna / Max | Fast | read-only |
| `air-complex-worker` | explicit architecture, irreducible-context, or high-consequence execution exception | Terra / Max | Standard | workspace-write |
| `air-critical-controller` | critical-risk graph owner and final reviewer | Sol / Max | Standard | read-only |
| `air-challenger` | one bounded independent falsification check, no approval | Sol / Max | Standard | read-only |

The ordinary route uses `air-efficient-worker` in `Mode: Lean Primary`. Its
stable name does not reduce its Lean authority: it owns requirements, execution,
verification, artifact review, and the overall verdict. Under a Full controller,
the same profile uses `Mode: Coordinated Leaf` and approves only its packet.

Never dispatch a generic or unnamed implementation child. It can inherit the
Host model and destroy the Luna-first cost boundary. Every Luna profile is
permanently `gpt-5.6-luna` / `max` / Fast: validators must require
`model_reasoning_effort = "max"`, `service_tier = "fast"`, and
`features.fast_mode = true`. This invariant does not follow the Host's `/fast`
toggle and must not be weakened to save credits. Sol and Terra pin
`service_tier = "default"`. Requested tier is configuration, not proof of the
tier served.

Every profile pins `model_context_window = 272000` and
`model_auto_compact_token_limit = 244800`. This prevents an unusually large Host
context override from silently expanding every child trajectory. Long-context
pricing still applies if an individual request crosses the provider threshold.

## 2. Single-turn launch proof

Launch with `fork_turns="none"` by default. Before launch the Host records the
authoritative Host/tool role mapping plus the launch record: model, reasoning
effort, fork mode, requested tier, and effective boundary. Agent names or TOML
contents alone are not runtime identity proof. This is the **Fail Closed** rule;
return `BLOCKED` when the required configuration cannot be proved.

Send the complete packet in the first child turn. Never spend an identity-only
model turn and do not ask the child to self-report metadata it cannot observe.

For Lean, the first packet contains only the raw request, relevant explicit
conversation constraints, workspace, authorization boundary, exclusions,
visible risk flags, and output language. Do not include copied skill text,
repository exploration, a Host-authored plan, baseline, diff, or verification
output. This preserves the single-semantic-context invariant.

Use `fork_turns="all"` only when essential prior user decisions cannot be
faithfully represented in a compact packet. Record that exception because it
duplicates the parent context.

## 3. Lean runtime

```text
Host transport turn
  -> air-efficient-worker / Mode: Lean Primary
       -> requirements + baseline + implementation + verification + review
  -> Host Git-generated candidate persistence + terminal relay
```

Codex multi-agent tasks may run in isolated worktrees. Never infer that a
write-capable child changed the user's active workspace from its `PASS`, diff,
or tests. The Host does not inspect task semantics before dispatch or perform a
semantic review afterward, but it must validate launch identity, authorization,
terminal schema, and deterministic candidate persistence. After launch, make one long agent wait
(`timeout_ms=3600000` where supported), which returns early on completion. Never
short-poll or create model turns for unchanged status. User input can interrupt
the wait; after handling it, make one new long wait for the same live primary.
A transport-truncated result allows one result-only follow-up to that primary.

For a changed Lean candidate, the primary returns exact relative paths and final
changed-file hashes, never a patch body. The Host compares active hashes first.
When the reviewed final is still session-visible, it invokes
`scripts/persist-visible-candidate.sh` once. The script makes Git snapshot the
visible binary diff, reverse it, immediately reapply it, and verify identical
final path identities in one Host transaction. A missing visible final,
non-Git workspace root, unsupported path type, replay failure, or unexpected
hash is a runtime conflict and fails closed. This mechanical gate is not a
second semantic review and does not rerun tests.

Lean ordinary work has zero controller, Terra, challenger, or other Sol child
calls. The top-level Host model is outside the skill's control; keeping it thin
is therefore part of the cost contract.

## 4. Native Nested and Compatibility

Both modes use the same requirement graph, task packets, ownership rules,
verification threshold, role profiles, and final review.

### Native Nested

Use only when the runtime proves custom role selection, effective
`max_depth >= 2`, controller-to-worker launch, model identity, and required
boundaries.

```text
Host -> selected controller
        -> Coordinated Leaf / complex workers
        -> optional challenger
        -> same controller terminal review
Host -> terminal relay
```

The controller launches the minimum dependency-ready workers. Workers cannot
recurse. Isolated worker changes must remain visible with exact changed paths
and final hashes for Git-generated Host replay. Native
Nested write stages are valid only when the runtime exposes a proven patch
integration path to the controller/Host; otherwise use Compatibility. Never
claim Native Nested succeeded without both a real nested launch record and a
persisted active-workspace candidate.

### Compatibility

Use when nested launch is unavailable or unproven:

```text
Host transports controller plan -> exact workers
Host transports artifacts/results -> same controller review
Host relays controller verdict
```

The Host is a transport adapter, not a second controller or reviewer. It follows
the graph without rewriting it, preserves logical ownership, mechanically
persists session-visible worker candidates between dependent stages, and passes
deterministic artifacts without interpreting them. The controller reviews the
resulting candidate capsule. Compatibility is a declared mode, not a silent
downgrade.

## 5. Capacity and batching

Capacity is runtime state. Read the live limit before coordinated launch.

- Parallel AIR uses two or three `air-efficient-worker` leaves and at most three
  concurrent leaves, even when the runtime exposes more capacity.
- Launch only tasks whose dependencies are satisfied and write scopes are disjoint.
- Launch a ready frontier as one single concurrent batch; do not wait
  worker-by-worker. Use one long wait for the batch, assemble one union manifest
  in deterministic Task-ID order, require the exact disjoint path/hash union to
  be simultaneously visible, and invoke Git persistence once. Then send one
  aggregate capsule for one aggregate final review.
- Queue a wider ready frontier into later dependency-aware waves instead of
  overcommitting slots.
- Keep the Host/controller relationship alive when the runtime requires it.
- Never create agents to demonstrate parallelism or duplicate a fact.

## 6. Review escalation

Ordinary Lean has no independent review. A review capsule is justified only by
an explicit user request, a critical flag, materially conflicting evidence, or
high-consequence semantics without a falsifiable verifier. The capsule contains
only Requirement IDs, candidate identity, changed paths, complete relevant diff,
exact verification evidence, and one unresolved question.

Do not send the primary's full conversation. Use `air-challenger` for one
read-only falsification check and return findings to the same logical owner. Use
`air-critical-controller` only for a critical run selected at entry; do not
switch controllers after writes.

## 7. Telemetry and regression budget

When observable, record wall time, input/cached/output tokens by model, requested
and actual service tier, API-equivalent cost, number of agents, and correction
count. The response tier is authoritative. If it is absent, use `unobserved`.

For matched ordinary Lean tasks, establish quality parity first, then target:

- cost ratio `AIR / Direct Sol-xhigh <= 0.55`;
- time ratio between `0.8` and `1.2`;
- Luna token share at least `70%`;
- Sol child token count `0`;
- one primary agent and no Host semantic artifact review;
- exact child-to-active-workspace Git-generated candidate persistence.
- two normal Host model turns: dispatch/wait and persistence/terminal relay.

A target miss is evidence for another architecture iteration, not permission to
weaken verification.

For Parallel AIR, additionally record the admission estimates, concurrent leaf
count, batch span, slowest branch, persistence span, aggregate review span, and
total tokens/cost. Compare against Lean Luna Max Fast on the same task before
comparing against Direct Sol. Accept a latency claim only when final quality is
non-inferior and measured wall time is lower. Parallel token growth is expected
and must be reported explicitly.

## 8. Model replacement

Keep the brand, invocation, role names, schemas, and evidence gates stable.
Change `.codex/agents/air-*.toml` only after a matched evaluation:

1. prove exact availability and runtime selection;
2. compare quality, wall time, tokens, tier, and cost on representative work;
3. update the profile, this table, validators, and release evidence;
4. run static, lifecycle, routing, and fresh-session tests.

Do not rename Codex AIR for a model generation and do not assume a newer or
more expensive model is a better role fit.

## 9. Failure rules

- **Identity or boundary unprovable:** `BLOCKED`; never impersonate by label.
- **Lean runtime/result failure:** inspect live status, then use one result-only
  recovery; reuse the same exact custom profile and logical owner.
- **Candidate changed after verification:** evidence is stale; rerun affected checks.
- **Critical risk discovered after a write:** stop writes and return
  `REVIEW_REQUIRED` with the candidate preserved.
- **Conflicting evidence:** send a compact review capsule; do not duplicate the
  whole task context.
- **Controller writes:** fail the Full run and report exact changed paths.
- **Focused recovery exhausted:** keep completed evidence, preserve ownership,
  and return the concrete blocker without starting a fresh identical run.
