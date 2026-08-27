# Codex AIR 故障排查

简体中文 · [English](troubleshooting.md)

从已 checkout 的 Codex AIR 仓库开始排查。在下面的只读检查定位问题前，不要删除
安装文件或手改 agent 配置。

## 快速诊断

macOS 或 Linux：

```bash
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/doctor.sh --require-codex
bash scripts/default.sh check
```

Windows PowerShell：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/default.ps1 check
```

只有旧版全局 AIR 默认路由块仍然存在时，`default.sh check` 才应非零退出。使用
`bash scripts/default.sh disable` 事务式移除该块。

## `/skills` 中看不到 `$codex-air`

1. 确认安装进程和 Codex 进程使用同一个操作系统账号与主目录。
2. 确认该主目录下存在 `.agents/skills/codex-air/SKILL.md`。
3. 运行 install check、重新安装，然后彻底重启 Codex；旧会话不一定重新加载新
   Skill。
4. AIR 只支持显式触发。它应显示为 `$codex-air`，不会只因任务复杂而自动进入。

如果安装时设置了 `ORCHESTRATE_HOME`，请确保它就是 Codex 使用的绝对主目录，
否则取消该变量后重装。不要指向 `/`、符号链接或 ownership 不清楚的共享目录。

## `/agent` 中看不到 AIR agent

安装后 `.codex/agents/` 下应有五个配置：

- `air-controller.toml` 与 `air-critical-controller.toml`；
- `air-efficient-worker.toml` 与 `air-complex-worker.toml`；
- `air-challenger.toml`。

POSIX 环境运行 `doctor.sh`，Windows 运行 `doctor.ps1`。它们会检查名称、模型、
reasoning、上下文限制、tier 和 sandbox mode。还要确认用户 Codex 配置没有显式
设置 `features.multi_agent = false` 或 `agents.enabled = false`。修正后重启
Codex。

## 模型不可用或没有权限

静态配置不能赋予模型权限。AIR 需要 Sol 完成语义控制与终审，需要 Luna 执行。
请确认 Codex 登录账号、工作区、区域和当前产品方案都能使用这两个配置模型。

无法证明所需模型身份时，AIR 必须失败关闭，不能偷偷换成 Terra、降低 reasoning
契约，或把不同路由包装成 AIR 结果。你可以解决权限问题，也可以明确在 AIR 之外
另做一次 Direct 尝试。

寻求支持时提供 Codex CLI 版本和实时错误原文，但不要附带凭据或私有仓库全文。

## 已请求 Fast，但 actual tier 是 `unobserved`

Luna 配置固定请求 `service_tier = "fast"`，但部分运行时遥测不会暴露响应的实际
tier。此时 `unobserved` 只表示“没有证明”，既不等于确认 Standard，也不等于
确认 Fast。

不要只凭配置推断实际速度。计费时分开保存 requested 与 actual tier；能取得时以
权威账单或响应 metadata 为准。benchmark 可以报告 `unobserved` 警告，但不能声称
已经观测到 Fast-tier 交付。

## 两个 worker 都需要修改同一个文件

这是 ownership collision。AIR 要求每个可写文件只有一个 owner，不能用“最后再
merge”代替 ownership。

把冲突交回 Sol controller。常见处理方式是：

- 由一个 worker 独占共享文件和集成步骤；
- 串行执行有依赖的任务；
- 收窄分支，使写入 scope 真正互斥。

不要让两个 worker 继续同时写同一路径。另一个会话拥有的脏工作树，在 owner 与
scope 查明前也属于冲突。

## Luna 返回 `REPLAN_NEEDED`

这是受控交接，不是整体失败。它说明关键事实不成立、选定方案无法满足要求、
scope 必须扩大、verifier 无效，或出现新的授权/风险问题。

同一个 Sol controller 应检查紧凑证据并修改计划或任务包，同时保持授权边界。
不要要求 Luna “随便想办法”，也不要原样反复发送同一个任务包。

## AIR 返回 `BLOCKED`

先读 failure class 和明确 blocker。常见类别包括 runtime、model identity、
permission、dependency、scope、conflict、verification 和 evidence quality。

只解决已经报告的条件，再开始一次新的有界恢复。不能把缺少权限理解为隐含授权，
不能跳过 verifier，也不能接受路径/哈希无法持久化的候选。重复出现的相同失败说明
应该停止，而不是无限重试。

## 安装器拒绝覆盖目标

安装器使用 checksum 跟踪受管文件，并拒绝未知或已经修改的目标，这是为了保护用户
改动和其他工具安装的文件。

检查 `git status`、报错中的安装路径和 `.codex/codex-air/install-state`，先保存
所有本地编辑。如果当前安装完整，使用项目卸载器或 `--restore-latest`；不要手动
删除整个 `.agents` 或 `.codex` 目录。

## Windows 专项

- 使用 PowerShell 5.1 及以上版本。文档命令中的 `-ExecutionPolicy Bypass` 只影响
  当次进程。
- 使用 `scripts/validate.ps1`、`scripts/install.ps1 -Check` 和
  `scripts/install.ps1`，然后运行 `scripts/doctor.ps1 -RequireCodex` 诊断。
- 如果 Codex 运行在 WSL 中，请在 WSL 主目录内使用 POSIX 脚本安装；Windows 主
  目录中的安装不会自动出现在 WSL 内。
- `ORCHESTRATE_HOME` 必须是 Codex 所在环境中的绝对、非根路径。
- 使用 `scripts/default.ps1 check` 检查旧全局默认路由，或用
  `scripts/default.ps1 disable` 移除它。
- 使用 `scripts/uninstall.ps1 -RestoreLatest` 恢复上一份受管状态。

Windows 安装或回滚后，关闭并重新打开 Codex，再检查 `/skills` 和 `/agent`。

## 报告问题时提供什么

请提供：

- release tag；若安装自 `main`，提供精确的 `git rev-parse HEAD`；
- `codex --version`；
- 操作系统，以及 Codex 是原生运行还是运行在 WSL；
- validate、install check 和可用时的 doctor 输出；
- AIR 终态与 failure class；
- 分开的 requested tier 与 observed tier。

请移除 secret、私有源码、私有绝对路径和模型凭据。支持渠道见
[SUPPORT.md](../SUPPORT.md)。
