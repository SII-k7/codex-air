# Contributing to Codex AIR

Thank you for helping improve Codex AIR. Contributions should keep the project focused on one job: Sol controls planning, delegation, and review while bounded Luna workers execute independently verifiable work.

## Ways to help

- Improve setup instructions for a supported operating system.
- Add a minimal reproduction for a runtime or installer defect.
- Strengthen a contract test around routing, permissions, ownership, or evidence.
- Propose a representative, reproducible benchmark rather than an isolated model-quality anecdote.
- Make the Chinese and English public documentation easier to understand without overstating measured results.

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

## Pull requests

Keep each pull request focused and explain both the user-visible change and its evidence. A pull request should:

- preserve user changes, permission boundaries, exact model routing, and fail-closed behavior;
- add or update the smallest relevant contract or forward test;
- keep `README.md` and `README.en.md` aligned when shared facts change;
- distinguish local tests, hosted CI, installed state, and runtime evidence;
- contain no credentials, private paths, private repository data, or generated test residue;
- avoid unrelated refactors, new roles, or duplicated implementations.

Configure a verified GitHub email or GitHub-provided noreply email before committing so GitHub can attribute future work correctly.

For a first contribution, documentation, prompt recipes, and narrowly scoped test improvements are good starting points. Runtime routing changes require fresh evidence and should begin with an issue.

By submitting a contribution, you agree that it may be licensed under the repository's [Apache License 2.0](LICENSE).
