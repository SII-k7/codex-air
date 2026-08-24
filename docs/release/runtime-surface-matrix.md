# Runtime surface matrix

Release-time evidence for Codex AIR. Configuration, an agent label, or a child
self-report is not runtime proof. Statuses are `VERIFIED`, `FAILED`,
`UNVERIFIED`, or `RETAINED HISTORICAL`.

Candidate date: 2026-08-24

## Optimized fork profile

| Surface | Signal | Status | Evidence location | Date |
| --- | --- | --- | --- | --- |
| Local repository | five agent TOMLs, canonical and compatibility Skills, validators | VERIFIED | `bash scripts/test.sh` passed 94 tests; Skill Creator `quick_validate.py` passed both Skill entries | 2026-08-24 |
| POSIX-compatible shell simulation | install, doctor, rollback, uninstall, managed v5/v6-to-v7 upgrade and restore | VERIFIED | Isolated HOME lifecycle tests passed for fresh installs and both legacy migration families | 2026-08-22 |
| Native Ubuntu/macOS CI | validation and complete unittest lifecycle | VERIFIED | Single-contributor `main` run [32564633665](https://github.com/SII-k7/codex-air/actions/runs/32564633665), Ubuntu and macOS with Python 3.11 and 3.13 | 2026-08-22 |
| Windows PowerShell | install, rollback, uninstall | VERIFIED | Local Windows PowerShell 5.1 lifecycle contract passed | 2026-08-21 |
| Native Windows CI | validation and complete install lifecycle | VERIFIED | Single-contributor `main` run [32564633619](https://github.com/SII-k7/codex-air/actions/runs/32564633619), Windows Server 2022 and `windows-latest`, Windows PowerShell and PowerShell 7 | 2026-08-22 |
| Ubuntu Codex CLI | installed Skill discovery and `air-efficient-worker` selection | VERIFIED | Fresh root session `01a0247f-7a8a-7250-b6ac-0d0810edafc6` launched child `01a0247f-c7db-7c80-8630-4752ff1433ed`; remaining four custom selections were not exercised | 2026-08-21 |
| Sol control profiles | `air-controller`, `air-critical-controller`, and exceptional `air-challenger` pin Sol/xhigh/Standard | UNVERIFIED | Static configuration and validators prove requested profiles, not authoritative live model selection | 2026-08-24 |
| Luna execution profiles | efficient and complex executors both pin Luna/max/Fast with low-output and no-nesting guards | UNVERIFIED | Static configuration proves requested tier; actual Fast response tier and matched runtime remain unobserved | 2026-08-24 |
| Controlled AIR route | current Sol/xhigh Host or one fallback Sol controller explores and plans; one Luna executor implements; the same Sol reviews | UNVERIFIED | v1.1 static contract is complete; no matched end-to-end v1.1 runtime record yet | 2026-08-24 |
| Parallel AIR route | Sol admits only ≥65% parallelizable work with ≤60% largest branch and ≤15% coordination; 2–3 Luna executors run one batch | UNVERIFIED | Static contract exists; no authoritative v1.1 Sol-to-parallel-Luna run has been captured | 2026-08-24 |
| Hard quality benchmark | DeepSWE v1.1 hardest-10 paired A/B | RETAINED HISTORICAL | v1.0 AIR achieved mean partial 0.8932 vs 0.8943, 39.0% credits, 1.267 median paired time ratio, and 1/10 vs 2/10 strict resolved; v1.1 has not been rerun | 2026-08-23 |

The rows below are retained upstream v1.0 evidence. They do not prove the v1.1
Sol-control/Luna-execution route, changed efforts, or actual Fast tier.

## Retained upstream v1.0 model-neutral roles

| Surface | Signal | Status | Evidence location | Date |
| --- | --- | --- | --- | --- |
| Desktop | `air-controller` selection | VERIFIED | Fresh session `01a01e7c-477a-7a03-9b74-8a7144d6f958`; Host launch plus two-turn handshake and final review | 2026-08-20 |
| Desktop | `air-complex-worker` selection | VERIFIED | Same fresh session; Host launch plus two-turn handshake | 2026-08-20 |
| Desktop | `air-efficient-worker` selection | VERIFIED | Same fresh session; Host launch plus two-turn handshake | 2026-08-20 |
| Desktop | exact models and reasoning | VERIFIED | Host/tool mapping and parent launch records: Sol/high, Terra/high, Luna/max | 2026-08-20 |
| Desktop | Native Nested | UNVERIFIED | Requires a real controller-to-worker launch with the new role names | 2026-08-20 |
| Desktop | Compatibility | VERIFIED | Fresh session `01a01e7c-477a-7a03-9b74-8a7144d6f958`; Controller plan, Host worker dispatch, same-Controller final verdict `PASS` | 2026-08-20 |
| Desktop | fresh-session Skill discovery | RETAINED HISTORICAL | Pre-AIR session `01a01e81-92bc-7462-bb95-450bc929e971` exercised the former `$codex-prove` entry; the current compatibility entry redirects `$codex-prove` to `$codex-air` and is covered structurally | 2026-08-22 |
| Desktop | transactional global install | VERIFIED | Persistent backup `/Users/kin3/.codex/codex-air/backups/20260820T092316Z-61245`; installed canonical Skill, alias, and three roles | 2026-08-20 |
| POSIX CI | validation and lifecycle | VERIFIED | `main` run [32353507136](https://github.com/SII-k7/codex-air/actions/runs/32353507136) | 2026-08-20 |
| Windows CI | install/upgrade/rollback/uninstall | VERIFIED | `main` run [32353507150](https://github.com/SII-k7/codex-air/actions/runs/32353507150), Windows Server 2022 and `windows-latest`, PowerShell 5.1 and 7 | 2026-08-20 |
| Physical Windows 11 | Native Nested | UNVERIFIED | No v1.0 physical-device runtime payload captured | 2026-08-20 |

Update this table only from actual launch, result, lifecycle, or CI evidence.

## Retained v0.5 historical evidence

The previous model-branded release verified the following on 2026-08-17:

- Desktop Host/tool mapping selected `sol-controller`, `terra-high-worker`, and
  `luna-max-worker` with `fork_turns="none"` and the configured model/effort.
- `sol-controller` launched two independent Terra audits, one bounded Luna
  smoke, and one qualifying read-only challenge.
- Host-owned baseline/final snapshots bound changed paths and artifacts before
  the final review.
- A separate `codex exec` Native Nested path proved Sol-to-Luna dispatch and a
  structured worker result.

This evidence supports continuity of the protocol, but it does not prove the new
`air-*` agent names. The v1.0 release must capture a fresh runtime record.

The matched protocol and retained smoke are documented in
[`tests/v100-ab-benchmark.md`](../../tests/v100-ab-benchmark.md) and
[`tests/v100-live-smoke.md`](../../tests/v100-live-smoke.md). The smoke remains a
single historical pair and does not replace the unfinished full benchmark.
