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

仓库验证器要求 Python 3.11 或更新版本。若系统默认版本较旧，请先使用
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
git clone https://github.com/SII-k7/codex-air.git
cd codex-air

bash scripts/validate.sh
bash scripts/install.sh --check
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
bash scripts/default.sh status
```

`--check` 是只读预检。正式安装会先创建带校验和的备份，再以事务方式安装：

- `air-controller`：Sol `xhigh` + Standard，任务理解、探索、拆解、方案与同一主控终审；
- `air-critical-controller`：Sol `xhigh` + Standard，关键风险任务的授权、规划与终审；
- `air-efficient-worker`：Luna `max` + Fast，默认承担有界诊断、代码修改、测试、重构、文档与普通单组件多文件推进；Fast 固定在该 agent 自己的配置层，不跟随主会话的 `/fast` 状态；
- `air-complex-worker`：Luna `max` + Fast，只处理带明确触发器的公共接口、大局部上下文、迁移/并发或高后果实现；它与 efficient 使用同一模型，只增加执行约束；
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

两个 Luna executor 文件固定 `service_tier = "fast"`、`features.fast_mode = true`
和 `model_reasoning_effort = "max"`。三个 Sol 角色固定 `xhigh` 与
`service_tier = "default"`。AIR 当前没有 Terra 角色。

五个子代理还会显式使用：

```toml
model_context_window = 272000
model_auto_compact_token_limit = 244800
```

这样不会继承主 `~/.codex/config.toml` 中的 `512000/400000`。安装器不会修改
用户的主配置，因此主会话继续使用大窗口；AIR 子代理使用当前 Codex GPT-5.6
默认原始窗口，并在界面中显示约 258.4K 的有效窗口。

重启 Codex 后可用这条只读检查确认 AIR 不再是全局默认：

```bash
codex --ask-for-approval never 'State whether Codex AIR requires an explicit $codex-air invocation.'
```

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
精确 scope 与终审，Luna Max Fast 只接收 `fork_turns="none"` 的紧凑 task packet，
负责实现、验证和有界修正。Host 会在启动前证明 agent、模型、推理档位与边界；
TOML 文件存在本身不等于运行时模型已经生效。

## 4. 配置诊断

随时运行：

```bash
cd ~/codex-air
git pull --ff-only
bash scripts/default.sh disable
bash scripts/install.sh
bash scripts/doctor.sh --require-codex
bash scripts/default.sh status
```

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
