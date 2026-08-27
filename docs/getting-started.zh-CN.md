# Codex AIR 入门

简体中文 · [English](getting-started.md)

Codex AIR 是一个只在显式调用时进入的 Codex 编排 Skill，固定分工如下：

- Sol `xhigh` 负责理解请求、探索仓库、选择方案、拆解任务和审核最终候选；
- Luna `max` 固定请求 Fast，负责有界实现、测试和修正；
- Terra 不是 AIR 的后备模型，调用和 token 必须保持为零。

如果任务很小或已经完全定位，AIR 可以保留 Direct 路径，避免派发开销超过
任务本身。安装不会把 AIR 设为全局默认；请显式输入 `$codex-air`。

## 前置条件

你需要：

- Git，以及支持 Skills 和自定义子 Agent 的当前 Codex CLI；
- 对配置中 Sol 和 Luna 模型有使用权限的账号或工作区；
- 安装时能访问 GitHub，工作时能访问 Codex 模型服务；
- macOS/Linux 与 Bash，或 Windows PowerShell 5.1 及以上版本；
- POSIX 环境的校验、安装和诊断需要 Python 3.11 及以上版本。

静态 doctor 能验证已安装的配置，但模型权限、实际选中的模型身份和实际服务
tier 只有通过实时启动的权威遥测才能证明。

安装默认写入运行 Codex 的当前用户主目录。只有当 Codex 实际使用另一个主目录
时，才设置 `ORCHESTRATE_HOME`；它必须是绝对、非根路径。

## 安装稳定版 v1.2.0

锁定 tag 可以避免 `main` 后续变化悄悄改变已安装的运行时。

### macOS 或 Linux

```bash
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
cd codex-air
git describe --tags --exact-match
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

`git describe` 应输出 `v1.2.0`。成功安装会依次看到
`Validation: PASS`、`Install check: OK`、Skill/agent 安装路径、备份路径和
`Doctor: PASS`。

### Windows PowerShell

```powershell
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
Set-Location codex-air
git describe --tags --exact-match
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Check
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/doctor.ps1 -RequireCodex
```

`git describe` 应输出 `v1.2.0`。Windows 校验应以 `Validation: PASS`
结束，安装器随后会打印安装路径和备份路径，诊断应以 `Doctor: PASS` 结束。

## 验证安装

关闭所有早于本次安装启动的 Codex 会话，再开启一个新会话：

1. 打开 `/skills`，确认能看到 `$codex-air`；
2. 打开 `/agent`，确认 AIR controller 和 worker 配置可见；
3. 在本地仓库中显式输入 `$codex-air`。

任何一项不可见时，先阅读[故障排查](troubleshooting.zh-CN.md)，不要直接开始
真实任务。

## 运行第一个任务

学习阶段建议使用临时分支或其他可恢复的本地仓库。向 AIR 提供目标、可观察的
完成条件和硬边界：

```text
$codex-air

目标：修复本地配置加载器，使其忽略空行和只有注释的行，同时不改变公共 API。

完成条件：
- 新增一个修复前失败、修复后通过的回归测试；
- 聚焦测试套件通过；
- 非注释配置值的既有行为保持不变。

边界：
- 不新增依赖；
- 不访问网络；
- 不 commit、不 push；
- 保留工作树中的无关改动。
```

这是任务模板，不是 benchmark 成功记录；请按真实仓库调整。完整注释和预期流程
见[第一个 AIR 任务](examples/first-air-task.zh-CN.md)。

## 预期会发生什么

普通 Controlled AIR 的正常轨迹是：一个 Sol 语义控制器、一个 Luna 执行器、
候选持久化，再由同一个 Sol 完成终审。并行 Luna 是例外，必须同时满足写入
ownership 互斥和 Skill 的量化门槛。

终态可能是：

- `PASS`：Sol 接受最终候选和 verifier 证据；
- `REPLAN_NEEDED`：Luna 发现任务包中的关键事实、scope 或 verifier 需要先由
  Sol 调整；
- `BLOCKED`：明确的运行时、权限、依赖、scope 或证据阻塞使任务无法完成。

配置请求 Fast 不等于已经证明运行时交付了 priority tier。缺少权威遥测时，AIR
会把 actual tier 记录为 `unobserved`。

## 稳定版与开发版 main

需要可复现安装时使用 `v1.2.0`。只有明确希望试用未发布变化时才使用 `main`：

```bash
git clone https://github.com/SII-k7/codex-air.git codex-air-main
cd codex-air-main
git switch main
bash scripts/validate.sh
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

不要把 `main` 安装称为 v1.2.0。报告问题或结果时，用 `git rev-parse HEAD`
记录精确 commit。

## 升级

从旧版本升级到稳定版 v1.2.0：

```bash
git status --short
git fetch --tags origin
git switch --detach v1.2.0
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
```

如果 `git status --short` 显示不属于你的改动，请停止，不要覆盖。Windows 使用
对应的 `.ps1` 校验、`-Check`、安装和 doctor 命令。每次升级后都要重启 Codex。

如果明确要更新开发版，保持在 `main`，使用 `git pull --ff-only`，再校验和重装。
不要把 tag 与 `main` 的文件混装为一个 bundle。

## 回滚或卸载

每次成功安装都会保存安装前的受管 AIR 路径。事务式恢复上一份状态：

```bash
bash scripts/uninstall.sh --restore-latest
```

Windows：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1 -RestoreLatest
```

只卸载、不恢复时省略 restore 参数。若受管文件的 checksum 已经变化，脚本会
拒绝覆盖或删除；此时应先确认并保存改动，不要手工强删。

如需主动降级到某个 tag，请 checkout 该 tag、校验并运行该版本的安装器，完成后
重启 Codex。

## 下一步

- [故障排查](troubleshooting.zh-CN.md)
- [第一个 AIR 任务](examples/first-air-task.zh-CN.md)
- [证据与结论边界](evidence/README.zh-CN.md)
- [更多任务模板](prompt-recipes.md)
