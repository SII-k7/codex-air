# Changelog

All notable user-visible changes are recorded here. Runtime claims remain tied
to the evidence linked from each release and the README.

## [1.2.0] - 2026-08-27

- Tighten the single Sol xhigh control path around decision-sufficient
  exploration, decomposition, routing, and final review, while bounded Luna
  Max workers request Fast for execution and Terra remains absent from every
  active route.
- Add a whole-run envelope shared across parallel work, repair, and replanning:
  absolute deadline, priced cap/unit, Sol phases, aggregate Luna calls, and hard
  limits of one replan and one focused correction. Unobservable price/call caps
  remain explicitly projected or cooperative.
- Fail closed before AIR child calls for unknown or non-Sol Hosts, add in-place
  Critical escalation without controller replacement, and make every AIR write
  Luna-owned.
- Replace candidate auto-discovery/replay with an exact-path, literal-pathspec,
  read-only replayability check that never mutates the user's worktree.
- Add a staged, zero-model microbenchmark validator and scorer. Record the
  first paid two-task screen as `BUDGET_ABORTED` near its 70-credit Host cap,
  with no confirm stage; this is a budget/routing diagnostic, not evidence of
  quality, latency, cost parity, or Fast-tier delivery.
- Add privacy-safe JSON doctors and symmetric lifecycle commands for POSIX and
  Windows, plus least-privilege CI and release-independent issue diagnostics.
- Publish focused English and Chinese getting-started, troubleshooting, task,
  and evidence guides while moving historical implementation material into an
  explicit archive.
- Add local Skill icons and UI metadata, cross-platform diagnostics, safer CI,
  community templates, and version-pinned installation guidance for adoption.

## [1.1.2] - 2026-08-24

- Put fit guidance, installation, and a copy-ready first task before the
  architecture and benchmark details in both public READMEs.
- Add bilingual prompt recipes for refactors, difficult bugs, migrations, and
  parallel-friendly tasks.
- Correct stale project names, issue examples, and the supported-version table
  across community files.
- Add clearer contribution, support, and GitHub Discussions entry points.
- Keep the v1.1 runtime architecture and routing contract unchanged.

## [1.1.1] - 2026-08-24

- Prevent POSIX-only installer execution from running in the Windows Python
  test matrix.
- Preserve the v1.1.0 runtime architecture unchanged.

## [1.1.0] - 2026-08-24

- Assign understanding, repository exploration, solution choice,
  decomposition, and final review to Sol xhigh.
- Assign bounded implementation, verification, and correction to Luna Max
  Fast.
- Remove Terra from every active route and add compact fresh-context task
  packets, deterministic candidate persistence, and a single-controller final
  review.

## [1.0.0] - 2026-08-23

- Publish the Codex AIR identity and the historical DeepSWE v1.1 hardest-10 A/B.
- Record near-equal mean partial quality, 61% lower measured Pro credits, higher
  raw token use, slower latency, and no strict quality non-inferiority claim.

[1.2.0]: https://github.com/SII-k7/codex-air/releases/tag/v1.2.0
[1.1.2]: https://github.com/SII-k7/codex-air/releases/tag/v1.1.2
[1.1.1]: https://github.com/SII-k7/codex-air/releases/tag/v1.1.1
[1.1.0]: https://github.com/SII-k7/codex-air/releases/tag/v1.1.0
[1.0.0]: https://github.com/SII-k7/codex-air/releases/tag/v1.0.0
