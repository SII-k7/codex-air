# DeepSWE v1.1 hardest-10 result

The paired 10-task, 20-cell A/B completed on 2026-08-23. It used DeepSWE source
commit `435ee89ec2f2e2289f33b0da4f992f0b7b7266b9`, one attempt per arm-task,
counterbalanced arm order, and four-way concurrency. Task OCI images were
exported with `crane` and executed through Bubblewrap because the benchmark host
had no Docker daemon. Raw trajectories and container files are intentionally
not committed to this repository.

## Decision

The historical v1.0 Codex AIR architecture passed the aggregate cost gate but
failed the quality and latency gates:

- Direct: 2/10 resolved, mean partial 0.8943, median 20.3 minutes, 919.34 credits.
- AIR: 1/10 resolved, mean partial 0.8932, median 23.2 minutes, 358.83 credits.
- AIR cost was 39.0% of Direct; paired median cost ratio was 40.0%.
- AIR paired median time ratio was 1.267 and it was slower on 9/10 tasks.
- AIR partial was better on four tasks, tied on four, and worse on two.

The two AIR quality losses were Termenv (partial 0.9426 versus 0.9672) and Kea
(AIR missed strict resolution while Direct resolved). The clearest AIR success
was SQLFmt: higher partial, 17.2% of Direct cost, and 32.6% less time. The next
architecture iteration therefore added Direct admission for short tasks, Sol
semantic control and final review, and a worker wall-time/tool-cycle budget.
This v1.0 result does not evaluate the later v1.2 implementation.

## Complete paired result

| Task | Direct resolved | AIR resolved | Direct partial | AIR partial | Direct min | AIR min | Direct credits | AIR credits | AIR cost ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bandit-structured-nosec-directives` | 0 | 0 | 0.9829 | 0.9972 | 21.0 | 23.1 | 80.45 | 24.68 | 30.7% |
| `effect-sse-httpapi-streaming` | 0 | 0 | 0.9829 | 0.9915 | 31.6 | 44.5 | 236.83 | 110.75 | 46.8% |
| `gql-incremental-graphql-delivery` | 0 | 0 | 0.9915 | 0.9928 | 18.1 | 23.3 | 113.85 | 33.82 | 29.7% |
| `kea-atomic-signal-selectors` | 1 | 0 | 1.0000 | 0.9868 | 24.3 | 30.3 | 91.42 | 38.22 | 41.8% |
| `meriyah-explicit-resource-declarations` | 1 | 1 | 1.0000 | 1.0000 | 11.9 | 23.9 | 57.99 | 35.99 | 62.1% |
| `obsidian-linter-auto-table-of-contents` | 0 | 0 | 0.9650 | 0.9650 | 14.3 | 19.1 | 48.96 | 20.89 | 42.7% |
| `sqlfmt-create-table-ddl-formatting` | 0 | 0 | 0.9939 | 0.9969 | 25.8 | 17.4 | 110.23 | 18.91 | 17.2% |
| `superjson-error-stack-serialization` | 0 | 0 | 0.9949 | 0.9949 | 13.8 | 28.9 | 37.76 | 25.12 | 66.5% |
| `termenv-preserve-ansi-resets` | 0 | 0 | 0.9672 | 0.9426 | 19.7 | 22.1 | 58.24 | 22.19 | 38.1% |
| `updo-policy-alerting` | 0 | 0 | 0.0643 | 0.0643 | 21.0 | 22.9 | 83.61 | 28.25 | 33.8% |

## Token and cost accounting

| Arm / model | Input tokens | Cached input | Output tokens | Pro credits |
| --- | ---: | ---: | ---: | ---: |
| Direct / Sol | 55,625,708 | 53,699,840 | 379,512 | 919.34 |
| AIR / Sol Host | 1,624,231 | 1,314,304 | 37,802 | 63.04 |
| AIR / Luna Max Fast | 174,989,799 | 172,281,344 | 621,084 | 295.79 |
| AIR total | 176,614,030 | 173,595,648 | 658,886 | 358.83 |

Luna Fast was charged with the frozen 2.5× credit multiplier. Runtime telemetry
confirmed Luna/max but reported the actual response tier as unobserved; the
frozen worker profile is the evidence for the Fast request.

The frozen ChatGPT Pro rate card was Sol `100 / 10 / 500` and Luna
`5 / 0.5 / 30` credits per 1M uncached-input / cached-input / output tokens.
For each row, credits were calculated as `(input - cached) * input_rate +
cached * cached_rate + output * output_rate`, divided by 1M, with the Luna row
then multiplied by 2.5 for Fast. These rates match the official Codex pricing
and speed pages checked again on 2026-08-24.

All 20 agents and final verifiers exited successfully without timeout. The
first Termenv verifier attempts used an incorrect temporary HOME and could not
see image-provided Go tooling/cache. Both unchanged candidate patches were
regraded after correcting verifier HOME; no model retry, token use, or candidate
change occurred.

Official accounting sources:

- <https://learn.chatgpt.com/docs/pricing>
- <https://learn.chatgpt.com/docs/agent-configuration/speed>
