# Support

Codex AIR is maintained for the latest tagged release and the current `main` branch. The supported installation surfaces are macOS and Linux through the POSIX lifecycle scripts, plus Windows through Windows PowerShell 5.1 and PowerShell 7.

Exact custom-agent selection, models, reasoning effort, permissions, and nested delegation depend on the Codex host. The repository documents only runtime surfaces for which evidence has been recorded; GitHub-hosted Windows validation is not proof of every physical Windows or Codex Desktop configuration.

## Where to ask

- Usage question or early idea: start a [GitHub Discussion](https://github.com/SII-k7/codex-air/discussions).
- Reproducible repository defect: use the [bug report form](https://github.com/SII-k7/codex-air/issues/new?template=bug_report.yml).
- Focused improvement proposal: use the [feature request form](https://github.com/SII-k7/codex-air/issues/new?template=feature_request.yml).
- Security-sensitive behavior: follow the [security policy](SECURITY.md) and report it privately.
- Contribution workflow: read [CONTRIBUTING.md](CONTRIBUTING.md).
- OpenAI account, billing, product availability, or Codex service issue: use [official OpenAI support](https://help.openai.com/).

## Before opening a bug report

Record the Codex AIR version from `VERSION` (or the full commit SHA), your operating system, the Codex surface and version, installation method, exact failing command, and exit code. For installation or runtime-discovery problems, include redacted output from:

```sh
bash scripts/doctor.sh --json
```

On Windows, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -Json
```

Ordinary validation and the checked-in microbenchmark scorer do not call models. Do not spend credits on a live benchmark to open a support request; maintainers will explicitly approve and cap any run needed for diagnosis.

Support does not include debugging unrelated downstream business repositories. Never attach secrets, unredacted configuration, private source code, private filesystem paths, or complete Codex configuration files to a public issue. Maintainers will not ask for API keys or account credentials. Community support is best effort and has no guaranteed response time.
