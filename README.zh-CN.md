[English](README.md) · [简体中文](README.zh-CN.md)

![Codex AIR 通过 Sol 控制面与 Luna 执行面路由复杂编码任务](docs/assets/readme/hero-zh.svg)

<p align="center">
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/posix-validation.yml"><img alt="POSIX CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/posix-validation.yml?branch=main&amp;label=POSIX&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/windows-validation.yml"><img alt="Windows CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/windows-validation.yml?branch=main&amp;label=Windows&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/releases/tag/v1.2.0"><img alt="稳定版 v1.2.0" src="https://img.shields.io/badge/stable-v1.2.0-65D6C4?style=flat-square"></a>
  <a href="LICENSE"><img alt="Apache-2.0 License" src="https://img.shields.io/github/license/SII-k7/codex-air?style=flat-square"></a>
</p>

# Codex AIR

**Sol 负责想清楚，Luna 负责做到底，证据决定能宣称什么。**

Codex AIR（Adaptive Intelligence Routing）是一个只在显式调用时进入的 Codex
编排 Skill，面向复杂编码任务：

- **Sol `xhigh` 控制语义：**理解意图、探索仓库、形成要求、选择方案、拆解、分配
  ownership，并审核最终候选；
- **Luna `max` 固定请求 Fast 并执行：**有界实现、聚焦验证和修正；
- **Terra 不参与 AIR：**调用、路由和 token 必须为零。

AIR 适合多文件修改、迁移、困难缺陷，以及必须先探索再实现的任务。问答和已经完全
定位的小修改可以保留 Direct，避免派发开销超过任务本身。

只有输入 `$codex-air` 才会进入 AIR。它不是全局默认，也不会扩大授权。
`$codex-prove` 仅保留为已弃用的显式兼容别名。

Codex AIR 由 [SII-k7](https://github.com/SII-k7) 独立设计与维护，不是 OpenAI
官方产品或背书。

## 安装稳定版 v1.2.0

请锁定 release tag。`main` 是开发通道，不同 commit 之间可能变化。

### macOS 或 Linux

这些 POSIX 校验、安装和诊断脚本需要 Python 3.11 及以上版本。

```bash
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
cd codex-air
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

### Windows PowerShell

```powershell
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
Set-Location codex-air
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
```

重启 Codex，在 `/skills` 中确认 `$codex-air`，并用 `/agent` 检查安装的配置。你
需要支持 Skills 与自定义 agent 的 Codex 运行时，并且有权使用配置中的 Sol 与
Luna 模型。

前置条件、升级、事务回滚，以及与稳定版严格分离的 `main` 流程见
[入门指南](docs/getting-started.zh-CN.md)。运行时表面缺失时，先阅读
[故障排查](docs/troubleshooting.zh-CN.md)。

## 第一个任务

给 AIR 一个可观察的目标和明确边界：

```text
$codex-air

目标：修复本地配置加载器，使其忽略空行和只有注释的行，同时不改变公共 API。

完成条件：新增回归测试，且聚焦的既有测试套件通过。
边界：不新增依赖、不访问网络、不 commit、不 push、不修改无关文件。
```

这是 prompt 模板，不是已经成功执行的记录。参见带注释的
[第一个 AIR 任务](docs/examples/first-air-task.zh-CN.md)。

## 运行契约

```text
请求
  └─ Sol xhigh：理解 → 探索 → 选解 → 拆解 → 分配
       ├─ 很小且已定位：Direct
       └─ 复杂任务：紧凑任务包，fork_turns="none"
            └─ Luna max，固定请求 Fast：实现 → 验证 → 修正
                 └─ 可见候选 + 文件身份
                      └─ 同一个 Sol xhigh：最终 diff + verifier 终审
                           └─ PASS | focused FIX | BLOCKED
```

默认只使用一个 Luna executor。只有通过量化并行门槛，并且每个可写文件都有唯一
owner 时，才允许启动两到三个。Luna 不能扩大 scope、创建子 agent 或批准整体
任务。关键事实不成立或必须扩大 scope 时返回 `REPLAN_NEEDED`；只有 Sol 能给出
整体 `PASS`。

| Profile | 模型 / reasoning / 请求 tier | 职责 |
| --- | --- | --- |
| `air-controller` | Sol / xhigh / Standard | 普通语义控制与终审 |
| `air-critical-controller` | Sol / xhigh / Standard | 高后果任务控制、回滚与终审 |
| `air-efficient-worker` | Luna / max / Fast requested（固定请求） | 默认有界执行 |
| `air-complex-worker` | Luna / max / Fast requested（固定请求） | 有界公共接口、迁移、并发或大局部上下文执行 |
| `air-challenger` | Sol / xhigh / Standard | 例外的只读反证检查；不能批准 |

Fast 是请求，不是运行时证明。权威遥测没有暴露实际交付 tier 时，AIR 把 actual tier
记录为 `unobserved`。

## 不使用营销缩写的证据台账

| 证据集 | 状态 | 它实际上说明什么 |
| --- | --- | --- |
| 历史 v1.0 DeepSWE hardest-10 配对 A/B | 已完成，每个 arm-task 一次尝试 | Direct 与历史 AIR：严格 resolved `2/10` 对 `1/10`，平均 partial `0.8943` 对 `0.8932`，credits `919.34` 对 `358.83`，配对耗时比中位数 `1.267`；AIR 使用 `3.17×` 原始 input-plus-output tokens |
| v1.2 两题低额度诊断 | **`BUDGET_ABORTED / INVALID`** | 在终端 Luna record 和 Sol 终审前于 `66.85` credits 中止；候选成本为复用的历史 Direct 单元的 `39.7%`，配对耗时比中位数 `1.198`，Luna tool calls 为 `170` |
| v1.2 Sol 控制 / Luna 执行 hardest-10 | **未运行** | 不存在广泛的 v1.2 质量、耗时、token 或成本结论 |

v1.2 诊断还记录到 short polls 与 Terra 用量为零，actual Fast tier 为
`unobserved`。其中止后的 verifier 分数只是诊断观察，不是被接受的 AIR 结果，也
不是新的匹配 A/B。

这些样本不能建立统计非劣性。Codex AIR 不承诺“质量等价、成本减半”，也不承诺
原始 token 更少或完成更快。v1.0 属于不同的历史架构；v1.2 hardest-10 尚未复测。

请阅读完整的[证据与结论边界](docs/evidence/README.zh-CN.md)、
[历史 v1.0 结果](tests/deepswe-v11-hardest10-results.md)和
[v1.2 低额度协议](tests/deepswe-v11-microbench.md)。

## 文档

- [入门指南](docs/getting-started.zh-CN.md)
- [故障排查](docs/troubleshooting.zh-CN.md)
- [第一个 AIR 任务](docs/examples/first-air-task.zh-CN.md)
- [证据与结论边界](docs/evidence/README.zh-CN.md)
- [Public Skill](.agents/skills/codex-air/SKILL.md)
- [编排契约](.agents/skills/codex-air/references/orchestration.md)
- [运行时说明](.agents/skills/codex-air/references/runtime-notes.md)
- [运行表面矩阵](docs/release/runtime-surface-matrix.md)

## 贡献与支持

贡献前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。使用
[GitHub Discussions](https://github.com/SII-k7/codex-air/discussions)交流使用问题，
用 [GitHub Issues](https://github.com/SII-k7/codex-air/issues)报告可复现缺陷。
安全敏感问题按 [SECURITY.md](SECURITY.md) 报告；一般支持边界见
[SUPPORT.md](SUPPORT.md)。

除非维护者已经明确批准任务集和硬额度上限，否则不要为了贡献运行会消耗模型额度的
benchmark。

## 许可证

[Apache License 2.0](LICENSE)。参考项目归属见 [NOTICE](NOTICE)，发布记录见
[CHANGELOG.md](CHANGELOG.md)。
