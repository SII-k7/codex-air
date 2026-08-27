# Runtime evidence matrix

This page records what the Codex AIR v1.2 candidate has actually demonstrated.
Configuration, an agent label, a child self-report, or an unfinished candidate
is not runtime or benchmark proof.

Statuses used here are `VERIFIED`, `UNVERIFIED`, `NOT RUN`,
`BUDGET_ABORTED / INVALID`, and `RETAINED HISTORICAL`.

Candidate date: 2026-08-27

## Current v1.2 static contract

| Surface | Status | Proven evidence | Boundary |
| --- | --- | --- | --- |
| Canonical and compatibility Skills | VERIFIED | Source validation covers valid frontmatter, explicit-only invocation, maintained references, and the compatibility redirect | Static evidence does not prove a model launch |
| Sol control profiles | VERIFIED | Controller, critical-controller, and optional challenger profiles request Sol with `xhigh` reasoning and the standard service tier | The active Host must still prove the model and tier selected at runtime |
| Luna execution profiles | VERIFIED | Efficient and complex worker profiles request Luna with `max` reasoning, Fast mode, low-output settings, and worker nesting disabled | The actual Fast response tier remains unobserved |
| Current model boundary | VERIFIED | Static validation rejects Terra and requires the two Luna worker profiles; Terra is not a current AIR route | This is a source contract, not evidence that a live run honored it |
| Routing and ownership contract | VERIFIED | One Sol semantic controller owns planning and final review; bounded Luna workers receive explicit write scopes, evidence requirements, and one-file ownership | No static check establishes task quality, latency, or cost |
| Installation lifecycle | VERIFIED | Isolated lifecycle checks cover managed install, upgrade, rollback, restore, and uninstall behavior | A fresh v1.2 hosted cross-platform release run is recorded separately when available |

These rows verify the repository contract. They do not establish runtime model
identity, actual service tier, benchmark quality, or a cost/latency advantage.

## Current v1.2 runtime and evaluation

| Surface | Status | Evidence | Conclusion boundary |
| --- | --- | --- | --- |
| Exact current-role model selection | UNVERIFIED | No privacy-safe authoritative v1.2 launch record has been retained | TOML values and child statements are insufficient |
| Native Nested with current roles | UNVERIFIED | No complete current-role controller-to-worker-to-controller record has been retained | Compatibility or static routing tests do not prove nesting |
| Two-task low-credit screen | BUDGET_ABORTED / INVALID | The budget guard stopped the run before both cells produced terminal Luna records and Sol final reviews | Candidate files and partial telemetry are diagnostic only; the published comparisons are not accepted score evidence or proof of parity |
| Low-credit confirmation stage | NOT RUN | The invalid screen could not open the confirmation gate | No confirm-stage conclusion exists |
| v1.2 DeepSWE hardest-10 matched A/B | NOT RUN | No v1.2 hardest-10 cells have been executed | There is no v1.2 hardest-10 quality, cost, or latency result |

The low-credit protocol and its fail-closed scoring rules are documented in the
[staged microbenchmark protocol](../../tests/deepswe-v11-microbench.md). The
two-task attempt is classified `BUDGET_ABORTED / INVALID`: its diagnostic
ratios cannot support a claim that v1.2 preserves quality, matches elapsed
time, or reduces cost in completed work.

## Historical evidence, not v1.2 proof

| Evidence | Status | Historical observation | Current boundary |
| --- | --- | --- | --- |
| v1.0 DeepSWE hardest-10 matched A/B | RETAINED HISTORICAL | Direct resolved 2/10 and AIR resolved 1/10; mean partial scores were 0.8943 and 0.8932; AIR used 358.83 credits versus 919.34; median paired time ratio was 1.267 | This predecessor result does not establish quality equivalence and has not been reproduced by v1.2 |
| v1.0 routing/runtime evidence | RETAINED HISTORICAL | Earlier role selection and compatibility evidence informed later contract tests | Earlier model assignments and routing are not current v1.2 evidence |
| Earlier install and CI evidence | RETAINED HISTORICAL | Previous releases exercised POSIX and Windows lifecycle paths | Historical CI does not replace a release-specific v1.2 run |

The complete historical benchmark is preserved in
[DeepSWE hardest-10 results](../../tests/deepswe-v11-hardest10-results.md).
Its ten one-attempt tasks are useful engineering evidence, but they are not a
statistical non-inferiority result or proof of quality equivalence.

Older protocol and smoke records remain available in
[the v1.0 A/B protocol](../../tests/v100-ab-benchmark.md) and
[the v1.0 live smoke](../../tests/v100-live-smoke.md). They are historical only;
old model-branded routing is deliberately excluded from the current matrix.

## Evidence update rules

- Do not publish local usernames, machine paths, session identifiers, prompts,
  credentials, or private task details.
- Mark a budget-aborted or incomplete cell `INVALID`, even when it produced a
  plausible worktree candidate or partial telemetry.
- Mark exact runtime model and service-tier claims `VERIFIED` only from
  authoritative Host evidence retained in a privacy-safe form.
- Bind benchmark claims to complete runner output, hidden grading, candidate
  identity, and the frozen scoring protocol.
- Do not claim quality equivalence from a close mean, a partial run, or a small
  historical sample.
- Do not publish a fixed test count as enduring release evidence; cite the
  reproducible validation command instead.

Update this matrix only when the evidence class and its limitations remain
explicit.
