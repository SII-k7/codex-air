# Ubuntu 上安装 Codex AIR

这份流程把优化配置安装到当前 Linux 用户的 Codex CLI：Skill 位于
`~/.agents/skills`，五个自定义代理位于 `~/.codex/agents`。安装器不会改写
现有 `~/.codex/config.toml`，也不会覆盖没有 ownership state 的同名文件。

## 1. 准备环境

推荐 Ubuntu 24.04 或更新版本，并确认以下命令可用：

```bash
git --version
python3 --version
```

POSIX 校验、安装和诊断脚本要求 Python 3.11 或更新版本。若系统默认版本较旧，请先使用
Ubuntu 的受信任软件源或你现有的 Python 版本管理工具安装 Python 3.11+，
并确保 `python3.11`、`python3.12`、`python3.13` 或 `python3.14` 在 `PATH`。

按 [Codex CLI 官方文档](https://developers.openai.com/codex/cli)安装或更新：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
exec "$SHELL" -l
codex --version
```

首次运行 `codex`，按界面提示使用 ChatGPT 或服务器可用的认证方式登录。

## 2. 安装优化配置

```bash
git clone --branch v1.2.0 --depth 1 https://github.com/SII-k7/codex-air.git
cd codex-air
git describe --tags --exact-match

bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
bash scripts/default.sh status
```

`git describe` 应输出 `v1.2.0`。锁定 tag 可以避免 `main` 的未发布变化
悄悄进入安装；需要试用开发版时，请明确使用主
[入门指南](getting-started.zh-CN.md)中的 `main` 流程。

`--check` 是只读预检。正式安装会先创建带校验和的备份，再以事务方式安装：

- `air-controller`：Sol `xhigh` + Standard，任务理解、探索、拆解、方案与同一主控终审；
- `air-critical-controller`：Sol `xhigh` + Standard，关键风险任务的授权、规划与终审；
- `air-efficient-worker`：Luna `max` + 固定请求 Fast，默认承担有界诊断、代码修改、测试、重构、文档与普通单组件多文件推进；Fast 请求固定在该 agent 自己的配置层，不跟随主会话的 `/fast` 状态；
- `air-complex-worker`：Luna `max` + 固定请求 Fast，只处理带明确触发器的公共接口、大局部上下文、迁移/并发或高后果实现；它与 efficient 使用同一模型，只增加执行约束；
- `air-challenger`：Sol `xhigh` + Standard，极少数只读对抗式检查，无批准权。

安装器使用 state v7，并支持从本项目旧的 state v5/v6 配置升级和恢复升级前状态。

Codex AIR 只允许显式触发。若旧版本曾启用“所有请求自动进入 AIR”，执行：

```bash
bash scripts/default.sh disable
bash scripts/default.sh status
bash scripts/doctor.sh --require-codex
```

清理脚本只删除旧版本写入 `~/.codex/AGENTS.md` 的受管区块，保留其他全局
指令并先备份。`default.sh enable` 已被拒绝，避免再次把框架设为隐式默认。

两个 Luna executor 文件固定请求 `service_tier = "fast"`、`features.fast_mode = true`
和 `model_reasoning_effort = "max"`。三个 Sol 角色固定 `xhigh` 与
`service_tier = "default"`。配置中的 Fast 只表示请求；实际交付 tier 仍需权威
运行时遥测证明。AIR 当前没有 Terra 角色。

五个子代理还会显式使用：

```toml
model_context_window = 272000
model_auto_compact_token_limit = 244800
```

这是 v1.2 agent profile 固定的窗口值，不是对 Codex 当前默认值的声明。它们不会
继承主 `~/.codex/config.toml` 中的 `512000/400000`；安装器也不会修改用户的
主配置。AIR 子代理按上述固定值运行，并在界面中显示约 258.4K 的有效窗口。

`doctor.sh` 和 `default.sh status` 是不调用模型的本地检查。不要为了验证安装
额外启动付费模型任务；重启 Codex 后直接检查 `/skills` 与 `/agent`。

## 3. 让新会话加载配置

结束安装前已打开的 Codex 会话，在项目目录重新运行：

```bash
codex
```

在交互界面中：

1. 输入 `/skills`，确认能看到 `$codex-air`；
2. 输入 `/agent`，确认五个 `air-*` 自定义代理可见；
3. 只有需要 AIR 时显式输入 `$codex-air`；普通请求直接输入任务。

示例：

```text
$codex-air

目标：修复订单状态并补齐回归测试。
完成条件：现有 API 兼容；指定测试与构建通过。
限制：不修改支付接口，不执行生产操作。
```

Skill 优先复用已由权威 metadata 证明为 Sol `xhigh` 的主会话作为唯一
Controller；无法证明时才启动 `air-controller`。Sol 负责要求、仓库探索、方案、
精确 scope 与终审，Luna `max` 固定请求 Fast，只接收 `fork_turns="none"` 的紧凑 task packet，
负责实现、验证和有界修正。Host 会在启动前证明 agent、模型、推理档位与边界；
TOML 文件存在本身不等于运行时模型已经生效。

## 4. 配置诊断

在已锁定 `v1.2.0` 的 checkout 中随时运行：

```bash
git status --short
git describe --tags --exact-match
bash scripts/default.sh disable
bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
bash scripts/default.sh status
```

如果 `git describe` 不再输出 `v1.2.0`，先确认自己是否有意使用 `main`；不要把
开发版安装报告成稳定版。升级到新 tag 时遵循
[入门指南的升级步骤](getting-started.zh-CN.md#升级)，不要在稳定 checkout 中
直接 `git pull` 混入未发布文件。

如果 doctor 报告 `features.multi_agent` 或 `agents.enabled` 被显式关闭，请编辑
现有 `~/.codex/config.toml` 中对应的已有表，将值改为 `true`。不要重复添加
`[features]` 或 `[agents]` 表。可选的并发上限应为正整数，例如：

```toml
[features]
multi_agent = true

[agents]
enabled = true
max_concurrent_threads_per_session = 4
```

Codex 当前默认开启多代理，所以配置文件没有这些键也是正常的。并发只是容量
上限；AIR 仍会按依赖和不重叠的 write scope 使用最少数量的 worker。

如果 agent 可见但启动证明失败，先重新运行官方安装命令更新 Codex CLI，确认
账号或工作区有对应模型权限，再开始新的 Codex 会话。框架会失败关闭，不会把
其他模型冒充成目标配置。

## 5. 卸载与恢复

只删除本项目当前拥有的文件：

```bash
bash scripts/default.sh disable
bash scripts/uninstall.sh
```

卸载并恢复最近一次安装前的受管状态：

```bash
bash scripts/default.sh disable
bash scripts/uninstall.sh --restore-latest
```

如果安装后的受管文件被手工修改，卸载器会拒绝删除，避免误删用户内容。先保存
你的改动并恢复对应安装校验和，再执行卸载或恢复。
