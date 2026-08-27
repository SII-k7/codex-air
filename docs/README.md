# Codex AIR documentation

This index separates maintained guidance from historical design records. If a document in the archive conflicts with the current Skill, the current Skill wins.

## Start here

- [English project guide](../README.md) and [简体中文项目指南](../README.zh-CN.md)
- [Getting started](getting-started.md) and [入门指南](getting-started.zh-CN.md)
- [Troubleshooting](troubleshooting.md) and [故障排查](troubleshooting.zh-CN.md)
- [Evidence and claim boundaries](evidence/README.md)
- [Ubuntu CLI installation](ubuntu-cli-install.md)
- [Prompt recipes](prompt-recipes.md)
- [Contributing](../CONTRIBUTING.md), [support](../SUPPORT.md), and [security policy](../SECURITY.md)

## Current runtime contract

The authoritative routing and execution contract lives with the installed Skill:

- [Skill entry point](../.agents/skills/codex-air/SKILL.md)
- [Orchestration contract](../.agents/skills/codex-air/references/orchestration.md)
- [Runtime notes](../.agents/skills/codex-air/references/runtime-notes.md)
- [Runtime evidence matrix](release/runtime-surface-matrix.md)

Do not infer current model routing, pricing, or support status from archived implementation plans.

## Evaluation evidence

- [Evidence ledger and safe public claims](evidence/README.md)
- [Historical v1.0 DeepSWE hardest-10 matched A/B results](../tests/deepswe-v11-hardest10-results.md)
- [v1.2 budget-aborted screen artifact](../tests/fixtures/microbench-screen-20260827.json)
- [Low-credit staged microbenchmark protocol](../tests/deepswe-v11-microbench.md)

Each evaluation states its own evidence boundary. Historical samples are useful for diagnosis, not a guarantee for future tasks.

## Historical records

Superseded release reports, specifications, and one-time implementation plans are in the [archive](archive/README.md). They remain available for provenance and design archaeology, but their routing rules are not active guidance.
