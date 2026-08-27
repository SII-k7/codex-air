# DeepSWE v1.1 low-credit AIR microbenchmark

This is a staged **development regression gate** for iterating Codex AIR without
repeating the 1,278-credit hardest-10 A/B. It reuses four immutable DeepSWE v1.1
tasks and their historical Direct Sol/xhigh/Standard cells, then pays only for
new AIR candidate cells. It is not a fresh matched A/B, a general coding score,
or statistical evidence of non-inferiority.

## Why these four tasks

The tasks were selected after the historical run for diagnostic power, so the
selection is deliberately post-hoc and unsuitable for a leaderboard.

| Stage | Task | Signal from the historical A/B |
| --- | --- | --- |
| screen | `sqlfmt-create-table-ddl-formatting` | AIR was faster, cheaper, and slightly higher partial; positive efficiency control |
| screen | `termenv-preserve-ansi-resets` | largest AIR per-task partial regression; Go/ANSI state boundary |
| confirm | `kea-atomic-signal-selectors` | only strict resolved regression; public API and lifecycle semantics |
| confirm | `effect-sse-httpapi-streaming` | 350 tool calls and 100 short polls; long-horizon execution stress |

The frozen image digest, base commit, instruction hash, tests-tree hash,
historical measurements, routes, prices, stages, and gates live in
`tests/fixtures/microbench-v1.json`.

The tests-tree identity is SHA-256 over sorted regular files, appending each
UTF-8 relative path, NUL, lowercase file SHA-256 hex, and LF. This makes the
provenance check reproducible without exposing test contents to the agent.
The manifest also freezes the verifier HOME required by each cached image:
Termenv uses its preloaded `/root` Go cache; the other tasks use writable
`/tmp/home`. Changing this would invalidate comparison with the historical
Direct cell.

## Stages and credit guard

Run only the two screen cells first. Their historical AIR cost was about 41.1
Pro credits; the screen hard cap is 70. Continue to Kea and Effect only if every
screen gate passes. Historical cost for all four AIR cells was about 190.1
credits; the cumulative hard cap is 220. No automatic model retry is allowed.

Both stages require:

- resolved delta at least zero against the frozen historical Direct cells;
- mean partial delta at least `-0.005` and no task below `-0.015`;
- paired median wall-time ratio at most `1.10`;
- tier-priced candidate cost at most `55%` of Direct;
- at least `70%` of input-plus-output model tokens on Luna;
- short polls at most 6 for screen and 12 cumulatively;
- tool calls at most 160 for screen and 500 cumulatively;
- the applicable 70/220-credit cap.

The screen gate is intentionally strict enough to reject the historical AIR
trajectory. Passing it means the new candidate fixed known regressions; it does
not prove broad coding parity.

## 2026-08-27 screen outcome: budget-aborted diagnostic

The first candidate screen was interrupted at 66.85 of the 70-credit cap before
either cell produced a terminal Luna record or Sol final review. Both cells are
therefore invalid and unscored; the confirmation stage was not launched.

Offline grading of the preserved patches produced partial `0.9946` for SQLFmt
and `0.9754` for Termenv, versus historical Direct `0.9939` and `0.9672`.
Those are diagnostic verifier observations, not accepted AIR outcomes. Cost was
39.7% of the two historical Direct cells and Luna carried 95.4% of model tokens,
but paired median time ratio was 1.198 and 170 tool calls exceeded the 160 gate.
Short polls and Terra usage were zero; actual Fast tier was unobserved.

The result is `BUDGET_ABORTED`, not `CONTINUE`, `STOP`, or `PASS`. See the
[sanitized machine-readable artifact](fixtures/microbench-screen-20260827.json)
and [claim-boundary explanation](../docs/evidence/README.md).

## Comparable-run contract

Before any model call, the runner must:

1. use DeepSWE source commit
   `435ee89ec2f2e2289f33b0da4f992f0b7b7266b9` and Codex CLI `0.149.0`;
2. verify every frozen image, base, instruction, and tests-tree identity;
3. mount the candidate Skill and all five agent profiles from one repository
   snapshot, never from the user's global installation;
4. record the repository commit, Skill SHA-256, and agent-bundle SHA-256;
5. keep hidden tests, solutions, previous trajectories, benchmark outputs, and
   sibling workspaces outside the agent container;
6. prove one Sol/xhigh/Standard controller and one Luna/max/Fast worker per
   cell, with no challenger and zero Terra calls/tokens;
7. collect input, cached-input, output, sessions, and cost separately for Sol
   and Luna, plus wall time, score, tool calls, short polls, and corrections.

Fast is priced with the frozen requested-tier multiplier. If runtime telemetry
cannot observe the actual response tier, the scorer emits
`unobserved_fast_tier`; report that warning and do not claim observed Fast-tier
delivery.

The scorer never launches or interrupts a model. A compliant runner must
enforce active-run limits outside the scorer: conservative stage admission
before launch, one task-specific wall timer per cell, one interrupt at timeout,
and no automatic retry. Live credit/tool ceilings are mechanically enforceable
only with authoritative telemetry; otherwise report them as projected or
cooperative and use the wall timer as the hard boundary. A post-completion
credit check is not a hard cap.

## Commands

Validate the frozen protocol without launching a model:

```bash
python3 scripts/microbench.py validate tests/fixtures/microbench-v1.json
```

Score a candidate result file and receive `CONTINUE`, `STOP`, or `PASS`:

```bash
python3 scripts/microbench.py evaluate \
  tests/fixtures/microbench-v1.json path/to/candidate-results.json
```

The scorer fails closed on provenance, model, effort, requested tier, route,
Terra, per-model usage, or frozen-price mismatch. A new Codex CLI, model build,
price table, verifier, or task identity requires a new manifest rather than an
in-place rewrite.

## Claim ladder

- Per-iteration: this four-cell historical-replay gate.
- Before a release claim after material runtime/model drift: at least one fresh
  paired Direct anchor on a preregistered task.
- For a broad public performance claim: rerun the frozen hardest-10 matched A/B
  (or a larger independently selected set) and report all failures.
