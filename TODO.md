# TODO

## v1.2 low-credit iteration gate

Status: **first screen stopped at budget guard; diagnostic only**.

The 2026-08-27 SQLFmt + Termenv screen stopped at 66.85 of the 70-credit
screen budget. Both model runs were interrupted before a terminal Luna record
and Sol final review, so the cells are `INVALID` / `BUDGET_ABORTED`; the
confirmation stage was not launched. The offline verifier output is promising
but is not performance evidence. See `docs/evidence/README.md` and
`tests/fixtures/microbench-screen-20260827.json` for the exact boundary.

Use `tests/deepswe-v11-microbench.md` and
`tests/fixtures/microbench-v1.json` for routine architecture iterations:

1. run the SQLFmt + Termenv screen only, with a 70-credit hard cap;
2. stop on any quality, latency, cost, Luna-share, polling, tool-call, routing,
   tier, provenance, or Terra gate failure;
3. run Kea + Effect only after screen PASS, with a 220-credit cumulative cap;
4. publish the zero-model scorer output as historical-replay development
   evidence, never as a fresh matched A/B result;
5. require Host-side stage admission, one hard wall timer, one interrupt, and
   no automatic model retry.

Run at least one preregistered fresh Direct anchor before a release-level
performance claim after a Codex CLI, model, price, or runtime change. Reserve
the full hardest-10 matched A/B below for major architecture releases or when
quota is deliberately allocated; do not spend it on every prompt iteration.

## v1.2 Sol-control / Luna-execution matched rerun

Status: **deferred until quota is available**.

Rerun the same frozen hardest-10 tasks and containers, comparing Direct
Sol/xhigh/Standard with v1.2 AIR:

- the current proved Sol/xhigh Host, or one fallback Sol/xhigh controller,
  performs understanding, repository exploration, decomposition, solution
  selection, exact task packets, and final artifact review;
- Luna/max with Fast requested performs bounded implementation, verification,
  and at most one focused correction;
- Terra calls and tokens must remain zero;
- record Sol versus Luna input/cached/output tokens, requested and actual tier,
  wall time, correction count, strict resolved, and partial score;
- compare raw token ratio as well as tier-priced credits/API-equivalent cost.

Use the same 1,800-credit absolute cap unless a new estimate based on current
rates is approved. The v1.2 success targets are quality non-inferior on both
strict resolved and mean partial, median paired wall ratio `0.85–1.15`, priced
cost at most `55%` of Direct, at least 70% of model tokens on Luna, and total
raw model tokens no more than `1.10×` Direct for the first rerun.

## Broader distribution

Status: **v1.2 ships as a standalone Skill plus five custom agent profiles**.

Investigate an optional Codex Plugin package for a later release. Adopt it only
when installation can deliver and validate the complete Skill/agent bundle,
retain explicit-only invocation, preserve transactional rollback, and keep
Terra at zero. Until then, the versioned POSIX and Windows installers remain
the supported distribution path; do not publish a Skill-only package that
silently loses the configured Sol/Luna roles.

## Completed v1.0 DeepSWE v1.1 hardest-10 A/B

Status: **completed on 2026-08-23**. The paired 20-cell run finished normally.
See `tests/deepswe-v11-hardest10-results.md` for the frozen, repository-safe
result. Raw local trajectories and runtime files are intentionally not tracked.

### Goal

Compare direct GPT-5.6 Sol against Codex AIR on difficult, coding-focused tasks:

- quality: official resolved rate plus mean verifier pass fraction;
- latency: end-to-end wall time and paired per-task time;
- usage: input, cached-input, output, and total tokens by model and role;
- quota efficiency: measured Pro credits, repriced per model and service tier.

This is a small, qualitative stress test. With 10 tasks, one task changes the
resolved score by 10 percentage points, so the result must not be presented as
a statistically robust non-inferiority claim.

### Frozen task selection

Select the 10 hardest tasks using only the historical results of the
highest-reasoning configuration of 20 non-OpenAI models. Do not use any Sol or
Luna result to select tasks. This avoids choosing tasks based on either A/B
arm's known successes or failures.

The selected non-OpenAI aggregate pass-rate range is 6.3%-19.7%. The set has
five TypeScript, three Python, and two Go tasks:

1. `obsidian-linter-auto-table-of-contents`
2. `bandit-structured-nosec-directives`
3. `gql-incremental-graphql-delivery`
4. `termenv-preserve-ansi-resets`
5. `updo-policy-alerting`
6. `effect-sse-httpapi-streaming`
7. `sqlfmt-create-table-ddl-formatting`
8. `meriyah-explicit-resource-declarations`
9. `kea-atomic-signal-selectors`
10. `superjson-error-stack-serialization`

Before running, pin the DeepSWE source and verifier exactly as recorded in
`tests/fixtures/deepswe-v11-ab.json`. Do not replace or reorder the frozen task
set after observing either arm.

### A/B configuration

Run one attempt per arm-task with identical task environments, timeouts,
network policy, hardware class, and counterbalanced arm order.

| Arm | Configuration |
| --- | --- |
| Direct | GPT-5.6 Sol / xhigh / Standard, without Codex AIR |
| AIR | Sol / xhigh / Standard thin host; Codex AIR primary work on Luna / max / Fast |

Use four-way task concurrency. Preserve isolation between arms: do not share
candidates, trajectories, caches, failure messages, verifier output, or sibling
workspaces.

### Expected budget and time

Historical token distributions and current Pro credit rates give this planning
estimate:

| Component | Expected Pro credits |
| --- | ---: |
| Direct Sol / xhigh / Standard | about 914 |
| AIR Luna / max / Fast workers | about 369 |
| AIR Sol host orchestration and review | about 40-100 |
| Expected total | about 1,320-1,380 |
| Expected total with operational variance | about 1,400-1,700 |

- Set an absolute hard stop at **1,800 Pro credits** for the complete A/B.
- Do not silently exceed the cap or add retries; stop and report instead.
- Estimated wall time with four-way concurrency: **1.5-2.5 hours**.
- Estimated fully sequential wall time: **4.5-6 hours**.

Luna Fast is already priced at 2.5 times Luna Standard credits and estimated at
roughly 1.5 times its speed. Recalculate from the current official pricing page
immediately before launch because model rates and quota rules can change.

### Result gate

Report all paired task results, including failures and infrastructure errors.
Judge the run in this order:

1. AIR quality must match or exceed Direct quality on the frozen set.
2. AIR end-to-end time must be approximately no worse than Direct.
3. AIR measured equivalent cost should be at most 55% of Direct.

Do not claim that AIR preserves quality from this 10-task sample alone. Treat a
promising result as justification for a larger confirmatory run when quota is
available.

### Completed result

- Quality gate: **failed narrowly under the frozen strict rule**. Direct
  resolved 2/10 versus AIR 1/10; mean partial was 0.8943 versus 0.8932. AIR
  partial was better on four tasks, tied on four, and worse on two.
- Time gate: **failed**. AIR's paired median time ratio was 1.267; it was slower
  on nine of ten tasks. Median task time was 23.2 minutes versus 20.3 minutes.
- Cost gate: **passed**. AIR used 358.83 credits versus Direct's 919.34, or
  39.0%. The paired median cost ratio was 40.0%, and eight tasks were at or
  below half of Direct cost.
- Complete valid A/B cost: 1,278.17 credits. Conservative invalid
  infrastructure usage: 25.88 credits. Accounted total: 1,304.05 credits,
  below the 1,800 cap.
- Valid four-way wall time: 2h 12m 47s.

Conclusion: the historical v1.0 AIR architecture achieved the aggregate cost
target and nearly matched mean partial quality, but this small run did not
establish strict quality non-inferiority or comparable latency. It is not a
measurement of the current v1.2 architecture.

References:

- <https://deepswe.datacurve.ai/>
- <https://learn.chatgpt.com/docs/pricing>
- <https://learn.chatgpt.com/docs/agent-configuration/speed>
- `tests/deepswe-v11-ab.md`
