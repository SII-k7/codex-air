## Summary

Describe the user-visible change.

## Why

Explain the problem and why this is the smallest sufficient change.

## Scope

- Changed:
- Intentionally unchanged:

## Validation and evidence

List exact commands, exit codes, and relevant runtime evidence. Distinguish local verification, hosted CI, installed state, and model/runtime observations.

For benchmark-related changes, say whether you ran only the zero-credit scorer or used a maintainer-approved live paid run. Link the approval and credit cap for any live run.

## Checklist

- [ ] The change is focused and does not include unrelated refactors.
- [ ] Relevant contract or forward tests were added or updated.
- [ ] Canonical `README.md` and `README.zh-CN.md` remain aligned when shared facts changed; `README.en.md` stays a compatibility pointer.
- [ ] No credentials, private paths, or private repository data are included.
- [ ] Permission, write-ownership, exact-routing, and fail-closed boundaries are preserved.
- [ ] No live paid benchmark was run, or maintainer approval and a credit cap are linked above.
- [ ] Claims are supported by fresh evidence and known limitations are explicit.
- [ ] Documentation and licensing attribution are complete.
