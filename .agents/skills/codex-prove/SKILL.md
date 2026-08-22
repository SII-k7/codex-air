---
name: codex-prove
description: Use only when the user explicitly invokes the legacy $codex-prove command; redirect that request to the canonical $codex-air workflow during the compatibility window.
---

# Codex PROVE compatibility entry

This is a temporary explicit-only compatibility entry for Codex AIR.

Load and follow the complete canonical Skill at
`../codex-air/SKILL.md`, including its references, role profiles, runtime
proof, ownership, verification, and review gates. Treat the user's invocation as
if it were `$codex-air`. Do not run or reconstruct the old Sol-specific
workflow. If the canonical Skill or its configured agents cannot be loaded,
return `BLOCKED` instead of weakening the protocol.

Tell the user once that `$codex-prove` is deprecated and `$codex-air` is the
new command. Do not invoke this compatibility entry implicitly.
