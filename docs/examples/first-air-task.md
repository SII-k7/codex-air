# Your first Codex AIR task

[简体中文](first-air-task.zh-CN.md) · English

This walkthrough uses a deliberately generic, sanitized bug-fix request. It is
not a recorded run and makes no benchmark claim.

## Before you start

Use a local repository whose changes you can recover. Inspect its current
working tree yourself and decide whether AIR may edit it. AIR preserves
unrelated changes, but it cannot infer who owns an ambiguous shared worktree.

Verify `$codex-air` in `/skills` and the AIR profiles in `/agent`. Then open the
repository in a fresh Codex session.

## Copy this task

```text
$codex-air

Goal
Fix the local configuration loader so whitespace-only lines and comment-only
lines are ignored, while preserving its current public API.

Acceptance criteria
1. Add a regression test that demonstrates the current bug.
2. The regression test and the existing focused suite pass after the fix.
3. Non-comment keys, values, ordering, and error behavior remain unchanged.
4. The final response lists exact changed paths and verification commands.

Boundaries
- Work only in this repository.
- Do not add or update dependencies.
- Do not access external services or change generated/vendor files.
- Do not commit, push, open a PR, or modify unrelated dirty files.
- If satisfying the request requires a public API change or a wider write
  scope, return REPLAN_NEEDED before making that expansion.

Output language: English.
```

Adapt the behavior and acceptance criteria to your repository. Keep boundaries
that matter; remove invented paths rather than guessing the project layout.

## Why this prompt works

The goal states user-visible behavior. The acceptance criteria are observable
and preserve non-target behavior. The boundaries make authorization explicit
and tell Luna when a discovery belongs back with Sol.

Avoid prompts such as “improve the parser however you think is best.” They do
not define completion, public-interface constraints, or permitted side
effects.

## Expected control flow

The exact narration can vary. The architectural invariants cannot:

1. Sol `xhigh` reads the applicable instructions and minimum repository surface,
   identifies requirements, chooses one solution, and assigns exact ownership.
2. If the task is substantial enough for Controlled AIR, Sol sends one compact
   packet to one Luna `max` executor with Fast requested. If the repository
   proves the task is truly tiny and localized, Direct admission is valid.
3. Luna verifies decisive facts, edits only its scope, runs focused checks,
   corrects bounded failures, and reports the visible candidate plus hashes.
4. The same Sol controller reviews the real final diff and fresh verifier
   evidence. Only Sol can issue the overall `PASS`.
5. Terra usage remains zero.

Do not expect multiple Luna workers on this example. Parallel AIR requires a
quantified speedup case and disjoint file ownership.

## Expected output shape

A successful result should identify:

- whether AIR admitted Direct or Controlled execution;
- exact changed paths;
- requirement-to-evidence coverage;
- exact verification commands and exit status;
- Sol's final `PASS`, plus material residual risks if any;
- Fast `requested` and actual tier as `priority`, `default`, or `unobserved`.

This is an expected shape, not a claim that the sample task has been run. Check
the diff and command output yourself before keeping the change.

If Luna returns `REPLAN_NEEDED`, Sol should revise the packet based on the
reported mismatch. If AIR returns `BLOCKED`, resolve the concrete failure class
instead of asking for an unbounded retry. See
[troubleshooting](../troubleshooting.md).

## A stronger follow-up task

After the first local task, try a real multi-file change with a stable public
interface and a repository-native test command. Keep it non-destructive and
explicitly forbid external deployment. This gives the Sol/Luna split enough
execution work to be meaningful without turning your first run into a
high-consequence experiment.

For measured claims, use the protocol and limitations in
[Evidence and claim boundaries](../evidence/README.md), not an anecdotal first
task.
