# Evidence and claim boundaries

[简体中文](README.zh-CN.md) · English

Codex AIR separates architecture facts from measured performance claims. The
current runtime contract is Sol `xhigh` control and final review, Luna `max`
with Fast requested for bounded execution, and zero Terra usage. That contract
is validated statically; cost, quality, latency, token share, and actual tier
require runtime evidence.

## Evidence ledger

| Evidence | Architecture tested | Status | Safe interpretation |
| --- | --- | --- | --- |
| v1.0 DeepSWE v1.1 hardest-10 paired A/B | Historical thin Sol host + Luna-first v1.0 AIR | Completed on 2026-08-23 | Historical cost/quality/latency result for v1.0 only |
| v1.2 two-task low-credit diagnostic | Current Sol-control/Luna-execution candidate | Budget-aborted before terminal review | Useful bottleneck signals; invalid and unscored as a screen |
| v1.2 hardest-10 matched rerun | Current Sol-control/Luna-execution architecture | Not run | No broad v1.2 performance conclusion |

## Historical v1.0 hardest-10 A/B

The completed run used ten difficult coding tasks, one attempt per arm-task,
and twenty valid cells. Direct used Sol `xhigh` Standard. Historical v1.0 AIR
used a thin Sol host and Luna `max` with Fast requested as the primary worker.

| Metric | Direct Sol | Historical v1.0 AIR |
| --- | ---: | ---: |
| Strict resolved | 2/10 | 1/10 |
| Mean partial | 0.8943 | 0.8932 |
| Median task time | 20.3 min | 23.2 min |
| Pro credits | 919.34 | 358.83 |
| Input + output model tokens | 56,005,220 | 177,272,916 |

The run showed 61.0% lower priced credits, but more raw tokens, slower latency,
and no strict quality non-inferiority. Its architecture predates the v1.2 Sol
semantic controller and final-review contract, so its savings cannot be
presented as a v1.2 measurement.

See the complete task table, accounting, environment, and failure disclosure
in [the historical hardest-10 result](../../tests/deepswe-v11-hardest10-results.md).

## v1.2 two-task budget-aborted diagnostic

On 2026-08-27, the frozen low-credit screen launched SQLFmt and Termenv with one
Sol `xhigh` controller and one Luna `max` worker per cell, Fast requested, no
challenger, and zero Terra. The run was stopped near its 70-credit hard cap.
Both agent processes exited with `-2` before a terminal Luna record and Sol
final review, so the strict scorer contract marks the cells invalid. The
confirm stage was not launched.

Candidate patches were preserved and graded for diagnostic purposes only.
Termenv's verifier completed in the run; SQLFmt's interrupted verifier was
rerun offline against the identical patch, without another model call:

| Task | Historical Direct partial | Diagnostic candidate partial | Direct time | Candidate time | Direct credits | Candidate credits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLFmt | 0.9939 | 0.9946 | 25.8 min | 26.7 min | 110.23 | 39.50 |
| Termenv | 0.9672 | 0.9754 | 19.7 min | 26.7 min | 58.24 | 27.34 |

Both historical Direct cells and both diagnostic candidates had strict
resolved `0`. The aggregate diagnostic signals were:

- 66.85 candidate credits, 39.7% of the two historical Direct cells;
- 95.4% of input-plus-output model tokens routed to Luna;
- paired median wall-time ratio about 1.198, above the 1.10 screen gate;
- 170 Luna tool calls, above the 160 screen gate, and zero short polls;
- actual Fast tier `unobserved`; the profiles prove only that Fast was
  requested;
- one Sol and one Luna session per task, no challenger, and zero Terra.

The partial scores are post-abort verifier observations, not accepted AIR
outcomes. The run cannot receive `CONTINUE` or `PASS`, cannot establish quality
parity, and cannot be combined with historical Direct cells as a fresh matched
A/B. Its actionable signal is that cost routing and polling improved while
Termenv latency, total tool calls, and completion-before-budget remained
unresolved.

The frozen development protocol and gates are documented in
[the low-credit microbenchmark](../../tests/deepswe-v11-microbench.md). Exact
sanitized telemetry and recomputable aggregates are published in the
[budget-aborted screen artifact](../../tests/fixtures/microbench-screen-20260827.json).

## v1.2 hardest-10 status

The current Sol-control/Luna-execution architecture has not run the frozen
hardest-10 matched A/B. The completed hardest-10 file is a historical v1.0
result, not a rerun of v1.2. The deferred rerun remains listed in
[TODO.md](../../TODO.md).

Until a fresh matched rerun completes, do not claim that v1.2 is faster than
Direct, preserves quality, halves cost in general, or uses fewer raw tokens.

## Statistical limitations

The v1.0 benchmark had ten tasks and one attempt per arm-task. The v1.2
diagnostic had only two selected tasks, reused historical Direct cells, and was
aborted before valid completion. Neither design can prove statistical
non-inferiority. A single attempt is sensitive to model variance, runtime
load, caching, task selection, and verifier noise.

A broad public claim needs a preregistered matched task set, identical
environments, successful terminal reviews, complete failure reporting, and
enough independent repetitions or tasks to quantify uncertainty.

## Safe public statements

You may accurately say:

- v1.2 is designed and statically validated for Sol `xhigh` control, Luna
  `max` Fast-requested execution, and Terra=0;
- the historical v1.0 hardest-10 run used 39.0% of Direct credits while nearly
  matching mean partial score, but was slower and lost one strict resolution;
- the aborted v1.2 two-task diagnostic produced promising cost and partial-score
  observations while failing validity, time, and tool-call conditions.

Do not shorten those statements into “same quality at half the cost” or “v1.2
is faster.” Those conclusions are not established by the available evidence.
