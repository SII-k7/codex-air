[简体中文](README.md) · [English](README.en.md)

![Codex AIR 通过规划、路由、所有权、验证与证据完成复杂任务](docs/assets/readme/hero-zh.svg)

<p align="center">
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/posix-validation.yml"><img alt="POSIX CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/posix-validation.yml?branch=main&amp;label=POSIX&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/actions/workflows/windows-validation.yml"><img alt="Windows CI" src="https://img.shields.io/github/actions/workflow/status/SII-k7/codex-air/windows-validation.yml?branch=main&amp;label=Windows&amp;style=flat-square"></a>
  <a href="https://github.com/SII-k7/codex-air/releases/tag/v1.1.1"><img alt="release v1.1.1" src="https://img.shields.io/badge/release-v1.1.1-2563eb?style=flat-square"></a>
  <a href="LICENSE"><img alt="Apache-2.0 License" src="https://img.shields.io/github/license/SII-k7/codex-air?style=flat-square"></a>
</p>

# Codex AIR

**Sol 负责想清楚，Luna 负责做到底。**

`codex-air` 是一个仅由 `$codex-air` 显式触发的 Codex 编排 Skill：

- **Sol xhigh 控制面**负责理解用户意图、探索仓库、拆解要求、选择方案、划定 scope、编排与最终产物审核；
- **Luna Max Fast 执行面**负责长程实现、测试、验证与有界修正；
- **Terra 不参与任何 AIR 路由**；
- 短任务可以直接执行，避免编排成本高于任务本身；
- 只有通过量化门槛的独立工作流才并行启动 2–3 个 Luna executor。

项目仓库：[SII-k7/codex-air](https://github.com/SII-k7/codex-air)。Codex AIR 由 SII-k7 独立设计和维护，不代表 OpenAI 官方产品或背书；`$codex-prove` 仅作为旧命令的显式兼容入口。

## 为什么是这个架构

v1.0 的困难代码 A/B 已经证明 Luna 能把成本显著压低，但也暴露了两个问题：Luna 独自做开放式探索会产生很长的工具轨迹，而且缺少独立终审时，少量高价值错误不容易在交付前被发现。

v1.1 将职责按优势重新分配：

```text
用户请求
   │
   ▼
Sol xhigh：理解 → 探索 → REQ-ID → 选解 → 精确任务包
   │                         │
   │                         ├─ 小任务：Direct
   │                         └─ 长程任务：fork_turns="none"
   ▼
Luna Max Fast：验证关键事实 → 实现 → 测试 → 有界修正
   │
   ▼
Git：确定性持久化候选
   │
   ▼
同一个 Sol xhigh：真实文件 + 完整 diff + verifier 终审
   │
   └─ PASS / 一次 focused FIX / BLOCKED
```

关键点不是“多开几个 agent”，而是**让昂贵的 Sol token 只出现在高杠杆语义环节，并让廉价的 Luna token 承担主要执行量**。任务包使用 `fork_turns="none"`，不会把 Sol 的长探索上下文复制给 Luna。

## v1.0.0 定量评测结论（历史架构）

2026-08-23 完成了 DeepSWE v1.1 hardest-10 配对 A/B：10 道困难代码任务分别运行一次 Direct Sol/xhigh/Standard 与 v1.0 AIR（Sol 薄 Host + Luna Max Fast Primary），共 20 个有效单元，使用冻结任务顺序、同一 OCI 镜像与隐藏 verifier。

| 指标 | Direct Sol/xhigh | v1.0 AIR | 结论 |
| --- | ---: | ---: | --- |
| 严格 resolved | 2/10 | 1/10 | 严格质量非劣性未建立 |
| 平均 partial | 0.8943 | 0.8932 | 差 0.0011，几乎持平 |
| 单题耗时中位数 | 20.3 分钟 | 23.2 分钟 | AIR 慢 14.4% |
| 配对耗时比中位数 | 1.000× | 1.267× | AIR 在 9/10 题更慢 |
| Pro credits | 919.34 | 358.83 | AIR 为 Direct 的 **39.0%**，节省 **61.0%** |
| input + output tokens | 56,005,220 | 177,272,916 | AIR 使用约 **3.17×** token |

因此，v1.0 证明的是“**可以用更多廉价 Luna token 换取明显更低成本**”，没有证明“更少 token”或“更快”。完整逐题表与运行边界见 [DeepSWE v1.1 hardest-10 结果](tests/deepswe-v11-hardest10-results.md)。这是 10 题、每个 arm 单次尝试的定性压力测试，不是统计意义上的非劣性证明。

v1.1 的 Sol 控制 / Luna 执行架构正是针对上述失败模式设计的，**尚未完成新的匹配 A/B**，因此不能把 v1.0 的 61% 节省当作 v1.1 的已验证结果。

## 核心路由与预计节省

下表以同一任务全部使用 Sol 为 `1.00×` credits 基线，并把 Luna **Fast** 按 `0.125×` 计入（Luna Standard `0.05×` × Fast 的 `2.5×` credits）。`编排开销`是相对于全 Sol 基线新增的控制、交接和返工成本。

| 场景 | 示例 token 路由 | 编排开销 | 预计节省 |
| --- | --- | ---: | ---: |
| **明确的长程任务** | Sol 20% · Luna Fast 80% | 3%–8% | **62.0%–67.0%** |
| **典型复杂编码任务** | Sol 30% · Luna Fast 70% | 5%–12% | **49.3%–56.3%** |
| **高风险或高歧义任务** | Sol 40% · Luna Fast 60% | 8%–15% | **37.5%–44.5%** |
| **Direct 小任务** | 当前 Codex 直接完成 | 0% | **0% 路由节省** |

这些是 `scenario_model_projection`，用于规划预算。**这些投影不是保证**，也不是质量、速度或单题成本的实测结果。API 美元与 ChatGPT/Codex credits 是不同计费单位，必须按真实模型、tier、input、cached input 和 output 分别复算。

### 官方费率与计算口径

按 2026-08-24 查得的官方短上下文 API 价格，每 1M tokens：

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | $4.00 | $0.40 | $20.00 |
| GPT-5.6 Luna Standard | $0.20 | $0.02 | $1.20 |
| GPT-5.6 Luna Fast / Priority | $0.40 | $0.04 | $2.40 |

Codex token-based credits 每 1M tokens：

| Model / tier | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol Standard | 100 | 10 | 500 |
| GPT-5.6 Luna Standard | 5 | 0.5 | 30 |
| GPT-5.6 Luna Fast | 12.5 | 1.25 | 75 |

场景投影公式：

```text
route_cost = sol_share × 1.00
           + luna_fast_share × 0.125
           + orchestration_overhead

saving = 1 - route_cost
```

OpenAI 当前说明 Codex Fast 约提供 **1.5×** 生成速度，并在 ChatGPT 订阅中消耗 **2.5× credits**；API Fast/Priority 价格按官方费率单独计算。响应中的实际 tier 才是权威值，AIR 同时记录 requested 与 actual tier。

官方来源：[模型概览](https://developers.openai.com/api/docs/models)、[GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)、[API pricing](https://developers.openai.com/api/docs/pricing)、[Codex Fast mode](https://learn.chatgpt.com/docs/agent-configuration/speed)、[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

## 60 秒开始

### Ubuntu / macOS / Linux

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
git clone https://github.com/SII-k7/codex-air.git
cd codex-air
bash scripts/validate.sh
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

### Windows

```powershell
git clone https://github.com/SII-k7/codex-air.git
Set-Location codex-air
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
```

安装后启动新的 Codex 会话：

```text
$codex-air

目标：重构认证模块并保持现有 API 兼容。
完成条件：测试和构建通过；不修改支付模块。
```

Codex AIR 仅显式触发；未出现 `$codex-air` 的请求保持 Direct。旧版本写入的全局默认路由可用 `bash scripts/default.sh disable` 清理。

## 工作方式

### Controller 选择

优先复用当前主会话作为唯一 Controller，但必须由权威 runtime metadata 证明它是 `gpt-5.6-sol` 且 reasoning effort 至少为 `xhigh`。若无法证明，AIR 启动一个 `air-controller`；高后果任务从入口选择 `air-critical-controller`。Host 随后只负责运输、授权与候选持久化，不创建第二套方案或第二次语义审核。

### 角色层级

| 角色 | 配置 | 负责什么 | 明确边界 |
| --- | --- | --- | --- |
| **Controller** | `air-controller` → Sol / xhigh / Standard / read-only | 理解、探索、REQ-ID、选解、拆解、路由与终审 | 不做常规实现；不创建第二 Controller |
| **Critical controller** | `air-critical-controller` → Sol / xhigh / Standard / read-only | 高后果任务的授权、安全、回滚与终审 | 成本不能覆盖安全边界 |
| **Efficient executor** | `air-efficient-worker` → Luna / max / Fast / workspace-write | 普通有界实现、验证与修正 | 不重做全局方案、不扩大 scope、不批准整体任务 |
| **Complex executor** | `air-complex-worker` → Luna / max / Fast / workspace-write | 公共接口、大局部上下文、迁移/并发或高后果执行 | 与 Efficient 同价同模型，只增加执行约束 |
| **Challenger** | `air-challenger` → Sol / xhigh / Standard / read-only | 极少数独立反证检查 | 非常规路径、无写权、无批准权 |

五个 agent 都固定 `model_context_window = 272000` 和 `model_auto_compact_token_limit = 244800`。两个 Luna executor 还固定低 verbosity、无 reasoning summary、`tool_output_token_limit = 4000`、无 personality，并关闭子代理，减少非交付 token 与递归扩张。

### 路由选择

| 路径 | 什么时候使用 | 执行方式 |
| --- | --- | --- |
| **Direct** | 回答、微小修改、已经完全定位的短任务 | 当前 Sol 直接完成，避免派发成本 |
| **Controlled AIR** | 需要探索、拆解、长程实现或多文件验证 | 一个 Sol Controller + 默认一个 Luna executor |
| **Parallel AIR** | 可并行 ≥65%、最大分支 ≤60%、协调 ≤15%、写范围互斥 | 同一个 Sol Controller + 2–3 个 Luna executor |
| **Critical AIR** | 认证、密钥、支付、生产、隐私、不可逆、迁移或并发正确性 | Critical Sol Controller + 有界 Luna executor |

### 一条完整的证据闭环

1. **Sol 理解与探索。** 读取适用指令和必要代码，形成稳定 `REQ-ID`、关键事实、选定方案、精确 scope、baseline 与 verifier。
2. **紧凑交接。** 用 `fork_turns="none"` 向 Luna 发送可执行任务包，不复制 Sol 的完整探索记录。
3. **Luna 执行。** 先核对关键事实；冲突时在写入前返回 `REPLAN_NEEDED`，否则连续实现、测试与有界修正。
4. **确定性持久化。** Luna 返回精确 changed paths 与 SHA-256，Host 调用 `scripts/persist-visible-candidate.sh` 让 Git 快照并重放可见候选。
5. **Sol 终审。** 同一个 Controller 审核真实文件、完整 diff、REQ 覆盖与 verifier；只允许一次 focused `FIX`。
6. **结论。** 只有 Sol 能返回整体 `PASS`；硬阻塞或有界恢复耗尽返回 `BLOCKED`。

### 不可妥协的边界

1. 一个文件只有一个 owner；共享接口和生成产物不能并行写。
2. Luna executor 不能创建子代理、扩大授权、重做全局方案或批准整体任务。
3. 验证必须绑定最终候选；候选变化后，旧行为证据失效。
4. 子工作树的 `PASS` 不代表主工作区已交付；路径、哈希或 Git 重放不匹配就失败关闭。
5. Challenger 不是常驻第二 Controller；没有明确高后果反证问题就不启动。
6. Terra token、调用与路由必须保持为零。
7. 不能为了成本或速度降低授权、验证与证据门槛。

## 当前状态

当前稳定版本是 [`v1.1.1`](https://github.com/SII-k7/codex-air/releases/tag/v1.1.1)。`v1.1.1` 只修正 POSIX 专用安装测试在 Windows CI 上的错误执行，运行架构与 `v1.1.0` 相同。

| 验证面 | 状态 |
| --- | --- |
| v1.0 hardest-10 A/B | 已完成：partial 近似持平、credits 节省 61%、耗时较慢、严格 resolved 少 1 题 |
| v1.1 静态契约 | Sol xhigh 控制、Luna Max Fast 执行、Terra=0、紧凑 task packet、终审与校验脚本已覆盖 |
| v1.1 匹配 A/B | **尚未运行**；需要用相同题目与容器重新比较 Direct Sol/xhigh 和新 AIR |
| Fast tier | 配置请求固定 Fast；实际 response tier 必须由运行遥测证明 |
| CI | POSIX 与 Windows 工作流覆盖安装、校验和生命周期表面 |

## 安装、检查与卸载

```sh
bash scripts/validate.sh
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
bash scripts/uninstall.sh
```

Windows 使用对应的 `.ps1`。安装器只管理本项目拥有的 Skill 与五个 agent 文件，保留无关 agent 和用户的 `~/.codex/config.toml`。支持从旧 Codex PROVE/`sol-control` 受管版本事务迁移和 `--restore-latest` 恢复。安装或升级后请重启 Codex 会话。

## 仓库结构

```text
.agents/skills/codex-air/       Skill、编排契约与运行时说明
.agents/skills/codex-prove/     旧命令兼容入口
.codex/agents/                  Sol controller 与 Luna executor 配置
scripts/                        validate / install / doctor / uninstall
tests/                          契约、生命周期、持久化与 benchmark 证据
docs/                           发布证据、设计记录与 README 资源
```

## 文档入口

- [Public Skill](.agents/skills/codex-air/SKILL.md)
- [编排契约](.agents/skills/codex-air/references/orchestration.md)
- [运行时说明](.agents/skills/codex-air/references/runtime-notes.md)
- [DeepSWE v1.1 hardest-10 定量结果](tests/deepswe-v11-hardest10-results.md)
- [运行表面矩阵](docs/release/runtime-surface-matrix.md)
- [贡献指南](CONTRIBUTING.md)
- [安全策略](SECURITY.md)

## 限制

- v1.1 还没有新的匹配 A/B，预计节省不等于实测结果。
- 子 Agent、Fast tier、隔离 worktree 和线程容量依赖 Codex runtime；缺少权威身份或 tier 证据时 AIR 会失败关闭或标记 `unobserved`。
- 10 题单次样本不能证明统计非劣性。
- 旧版 benchmark 与设计文档保留历史架构描述，不代表 v1.1 当前路由。

## 许可证

[Apache License 2.0](LICENSE)
