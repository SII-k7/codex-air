# Frontier coding A/B: DeepSWE v1.1

Status: **task source and selection frozen; v1.2 protocol not run**. This
document records a future evaluation; it does not claim a Codex AIR result.

## Selection

The primary benchmark is the complete **DeepSWE v1.1** corpus: 113 original,
long-horizon software-engineering tasks across 91 active repositories and five
languages. Each task runs in an isolated environment and is graded by a
purpose-written behavioral verifier. The agent must explore a real repository,
make substantial multi-file changes, and preserve unrelated behavior.

This benchmark directly satisfies the frontier-difficulty requirement. OpenAI's
published GPT-5.6 results report **72.7% for GPT-5.6 Sol at max effort** and
**69.7% for Claude Fable 5 at max effort** on DeepSWE v1.1. Neither model is
close to a perfect score, while the benchmark remains centered on code rather
than general knowledge or UI interaction.

Primary sources:

- [OpenAI GPT-5.6 coding evaluation table](https://openai.com/index/gpt-5-6/)
- [DeepSWE v1.1 official benchmark](https://deepswe.datacurve.ai/)
- [DeepSWE official task repository](https://github.com/datacurve-ai/deep-swe)
- [DeepSWE paper](https://arxiv.org/abs/2607.07946)

The exact source tree and protocol are pinned in
[`fixtures/deepswe-v11-ab.json`](fixtures/deepswe-v11-ab.json). The earlier
single FeatureBench Level-2 proposal was removed because one task can still
saturate by chance and cannot support a robust claim about frontier quality.

## Primary A/B

Run all 113 tasks once per arm. Use the same pinned task tree, Pier version,
Codex version, Sol model and `xhigh` effort, Standard controller tier, timeout,
network policy, hardware class, and task ordering. The only intended difference
is explicit AIR routing and its Luna execution work.

| Arm | Root behavior | AIR internals |
| --- | --- | --- |
| Direct | GPT-5.6 Sol / xhigh / Standard, no AIR invocation | none |
| AIR | One Sol / xhigh / Standard semantic controller with explicit `$codex-air` | one Luna / max worker with Fast requested by default; 2–3 only after the quantitative parallel gate |

The same AIR Sol controller owns understanding, repository exploration,
solution selection, decomposition, authorization, and final review. Luna owns
bounded implementation and verification, cannot approve the overall result,
and reports actual Fast tier as `unobserved` unless authoritative telemetry
proves it. Routine challenger usage is forbidden and Terra calls/tokens remain
zero.

Use one attempt per arm-task to limit cost. Counterbalance the arm order per task
from the pinned task ID hash, and never reuse a candidate, trajectory, cache
entry, or failure message across arms.

The official deterministic ten-task command (`--n-tasks 10 --sample-seed 0`)
may be used only as an infrastructure pilot. It cannot replace the 113-task
primary comparison and cannot support the claim that the benchmark is
unsaturated.

## Scoring and decision rule

Primary quality is the official resolved rate:

```text
resolved_rate = 100 * passed_tasks / 113
```

Also report the mean verifier pass fraction from `reward.json`, because it
preserves partial progress when a task is not fully resolved. Collection
failure, empty verifier output, timeout, invalid candidate, or evaluation
isolation violation scores zero for that task unless both arms are invalidated
by the same pre-inference infrastructure failure.

Interpret the results in this order:

1. AIR must match or exceed Direct resolved rate. A lower score is a quality
   regression regardless of cost or speed.
2. Report the paired task-level result, mean verifier pass fraction, and the
   bootstrap confidence interval. Do not infer a win from aggregate prose.
3. After the quality gate passes, compare end-to-end wall time using total time,
   median paired task ratio, and 95th-percentile task time.
4. Record raw tokens and reprice input, cached-input, output, and reasoning
   tokens separately for every model and actual service tier. Keep Pro credits
   and API dollars as distinct accounting units. AIR meets its cost target at
   `AIR / Direct <= 0.55` in the preregistered unit.
5. Declare the architecture successful only when quality is non-inferior, wall
   time is not worse, and the measured cost target is met.

## Isolation

DeepSWE's public repository includes held-out verifiers and reference solutions.
Neither arm may inspect `tests/`, `solution/`, prior trajectories, leaderboard
task outcomes, sibling workspaces, or the benchmark repository outside its
prepared agent-visible task environment. Use Pier's separate verifier container;
the candidate patch is collected and graded only after inference in a pristine
container.

Archive exact task IDs, source SHA, runtime versions, launch identities, actual
tiers, task-level rewards, patches, verifier artifacts, wall times, and token
telemetry. Any exception must be recorded before unblinding the other arm.
