# Contributing to Codex AIR

Thank you for helping improve Codex AIR. Contributions should keep the project focused on one job: Sol controls planning, delegation, and review while bounded Luna workers execute independently verifiable work.

## Ways to help

- Improve setup instructions for a supported operating system.
- Add a minimal reproduction for a runtime or installer defect.
- Strengthen a contract test around routing, permissions, ownership, or evidence.
- Propose a representative, reproducible benchmark rather than an isolated model-quality anecdote.
- Make the Chinese and English public documentation easier to understand without overstating measured results.

Look for an unclaimed [`good first issue`](https://github.com/SII-k7/codex-air/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22) if this is your first contribution. Documentation, diagnostics, and focused contract tests are the best entry points. Comment on the issue before starting so work is not duplicated.

## Before you start

- Search existing issues and pull requests before opening a new one.
- Use the bug or feature issue form for reproducible defects and proposals.
- Use [GitHub Discussions](https://github.com/SII-k7/codex-air/discussions) for usage questions and early ideas that are not yet a focused proposal.
- Open an issue before a material routing, security, installer, or compatibility change.
- Use GitHub's [private vulnerability reporting](https://github.com/SII-k7/codex-air/security/advisories/new) for security-sensitive reports. Do not disclose them in a public issue.

## Development setup

The repository requires Python 3.11 or newer. On macOS or Linux, run:

```sh
bash scripts/validate.sh
bash scripts/test.sh
bash scripts/install.sh --check
```

On Windows, validate from PowerShell 5.1 or PowerShell 7:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/windows-lifecycle.ps1
```

Use `pwsh` in place of `powershell` to exercise PowerShell 7.

These validation and test commands are ordinary local programs: they do not launch a model and consume no Codex credits.

## Architecture contract

Changes must preserve these public invariants unless a maintainer-approved proposal deliberately revises the architecture:

- exactly one Sol controller owns task understanding, exploration, solution selection, decomposition, and final overall review;
- Sol uses xhigh reasoning, while bounded write-capable executors use Luna Max with Fast requested; Terra is not a routing option;
- one Luna executor is the default, and parallel executors are used only for independent, explicitly owned work;
- authorization, permission, write-ownership, candidate-identity, and fail-closed boundaries remain explicit;
- worker evidence is leaf evidence; only the Sol controller can issue the overall completion verdict.

Runtime routing changes should start with an issue and include a rollback boundary. Avoid adding another role when a tighter packet, test, or existing role is sufficient.

## Benchmark policy

The checked-in microbenchmark scorer is safe for routine development:

```sh
python3 scripts/microbench.py validate tests/fixtures/microbench-v1.json
python3 scripts/microbench.py evaluate tests/fixtures/microbench-v1.json path/to/candidate-results.json
```

Both commands only validate or score existing files. They do not call a model and consume zero Codex credits. The second command requires previously collected candidate results; it does not collect them.

A live benchmark is any run that invokes Codex models to produce new candidate results. It may consume paid credits and must not be started for a contribution without explicit maintainer approval, a stated credit cap, and a stop condition. A live run is not required for an ordinary documentation, installer, or contract-test pull request.

## Pull requests

Keep each pull request focused and explain both the user-visible change and its evidence. A pull request should:

- preserve user changes, permission boundaries, exact model routing, and fail-closed behavior;
- add or update the smallest relevant contract or forward test;
- keep canonical `README.md` and `README.zh-CN.md` aligned when shared facts
  change; keep `README.en.md` as a compatibility pointer rather than a third
  documentation copy;
- distinguish local tests, hosted CI, installed state, and runtime evidence;
- contain no credentials, private paths, private repository data, or generated test residue;
- avoid unrelated refactors, new roles, or duplicated implementations.

Configure a verified GitHub email or GitHub-provided noreply email before committing so GitHub can attribute future work correctly.

By submitting a contribution, you agree that it may be licensed under the repository's [Apache License 2.0](LICENSE).
