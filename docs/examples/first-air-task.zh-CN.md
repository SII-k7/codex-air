# 第一个 Codex AIR 任务

简体中文 · [English](first-air-task.md)

这个示例使用通用、脱敏的缺陷修复请求。它不是已经执行过的记录，也不构成任何
benchmark 结论。

## 开始前

选择一个可以恢复改动的本地仓库，自己检查当前工作树并确认 AIR 可以修改。AIR 会
保留无关改动，但无法猜测共享脏工作树的 owner。

确认 `/skills` 中能看到 `$codex-air`，`/agent` 中能看到 AIR 配置，然后在该仓库
中启动一个新的 Codex 会话。

## 复制这个任务

```text
$codex-air

目标
修复本地配置加载器，使其忽略只有空白字符的行和只有注释的行，同时保持当前公共
API 不变。

验收条件
1. 新增一个能够复现当前缺陷的回归测试。
2. 修复后回归测试和既有聚焦测试套件通过。
3. 非注释 key、value、顺序和错误行为保持不变。
4. 最终回复列出精确 changed paths 和验证命令。

边界
- 只在当前仓库内工作。
- 不新增或更新依赖。
- 不访问外部服务，不修改 generated/vendor 文件。
- 不 commit、不 push、不创建 PR，也不修改无关脏文件。
- 如果需要修改公共 API 或扩大写入 scope，先返回 REPLAN_NEEDED，不要直接扩张。

输出语言：中文。
```

请按你的仓库调整行为和验收条件。保留真正重要的边界；未知项目结构时不要捏造
路径。

## 为什么这个 prompt 有效

目标描述了用户可见行为；验收条件可观察，并要求保护非目标行为；边界明确授权，
也告诉 Luna 哪些新发现必须交回 Sol 决策。

不要只写“按你认为最好的方式改进解析器”。这种请求没有完成定义、公共接口约束和
允许的副作用范围。

## 预期控制流程

具体叙述可能不同，但架构不变量必须保持：

1. Sol `xhigh` 读取适用指令和最小必要仓库表面，形成要求、选择唯一方案并分配
   精确 ownership。
2. 如果任务足够大而进入 Controlled AIR，Sol 会把紧凑任务包发送给唯一一个
   Luna `max` executor，并固定请求 Fast。如果仓库事实证明任务确实很小且已定位，
   进入 Direct 也是正确行为。
3. Luna 核对关键事实，只修改自己的 scope，运行聚焦检查、有界修正，并报告可见
   候选及哈希。
4. 同一个 Sol controller 审查真实最终 diff 和新鲜 verifier 证据。只有 Sol 能
   给出整体 `PASS`。
5. Terra 用量保持为零。

不要期待这个示例启动多个 Luna。并行 AIR 必须有可量化的加速空间和互斥文件
ownership。

## 预期输出形态

成功结果应明确：

- AIR 选择了 Direct 还是 Controlled 执行；
- 精确 changed paths；
- Requirement 到证据的覆盖；
- 精确验证命令与退出状态；
- Sol 的最终 `PASS`，以及存在时的实质残余风险；
- Fast 为 `requested`，actual tier 为 `priority`、`default` 或 `unobserved`。

这只是预期形态，不表示样例任务已经被成功运行。保留改动前，请自己检查 diff 和
命令输出。

如果 Luna 返回 `REPLAN_NEEDED`，Sol 应根据不一致证据修改任务包。如果 AIR 返回
`BLOCKED`，应解决明确的 failure class，而不是要求无限重试。参见
[故障排查](../troubleshooting.zh-CN.md)。

## 更进一步

第一次本地任务之后，可以尝试一个保留稳定公共接口、带仓库原生测试命令的真实
多文件改动。保持操作可恢复，并显式禁止外部部署。这样能给 Sol/Luna 分工提供足够
执行量，又不会让第一次尝试变成高后果实验。

如需做量化结论，请使用[证据与结论边界](../evidence/README.zh-CN.md)中的协议和
限制，而不是依赖一次体验任务。
