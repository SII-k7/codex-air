# Codex AIR prompt recipes / 任务模板

Codex AIR works best when the request states a goal, observable completion
conditions, and hard boundaries. It does not require you to design the agent
plan or choose how many executors to launch.

Codex AIR 最适合包含目标、可观察完成条件和明确边界的任务。你不需要自己设计
agent 计划，也不需要指定 executor 数量。

## Refactor / 重构

```text
$codex-air

目标：把认证模块拆成 token 验证、会话管理和权限判断三个内部组件，保持公开 API 兼容。
完成条件：现有测试通过；新增覆盖过期 token 和权限拒绝的回归测试；构建通过。
边界：不修改数据库 schema，不修改支付模块，不执行部署。
```

```text
$codex-air

Goal: Split authentication into internal token validation, session management,
and authorization components while preserving the public API.
Done when: Existing tests pass; regression tests cover expired tokens and
permission denial; the build passes.
Boundaries: Do not change the database schema, payments, or deployment state.
Output language: English.
```

## Difficult bug / 复杂缺陷

```text
$codex-air

目标：定位并修复订单取消后库存偶尔没有释放的问题。
已知现象：压力测试约每 500 次出现一次；单线程测试没有复现。
完成条件：说明根因；加入能在修复前失败的回归测试；修复后相关测试连续通过。
边界：只修改订单与库存模块；如果需要更改消息协议，先返回 REPLAN_NEEDED。
```

```text
$codex-air

Goal: Diagnose and fix inventory that is occasionally not released after order
cancellation.
Known symptom: Roughly one failure per 500 stress-test iterations; the
single-threaded test does not reproduce it.
Done when: Explain the root cause, add a regression test that fails before the
fix, and show the relevant tests passing after the fix.
Boundaries: Modify only order and inventory modules. Return REPLAN_NEEDED before
changing the message protocol.
Output language: English.
```

## Migration or high-consequence work / 迁移或高后果任务

```text
$codex-air

目标：为用户表增加可空的 last_login_at 字段，并让新旧应用版本可以滚动升级。
完成条件：迁移可前滚和回滚；旧版本读取不受影响；迁移测试与应用测试通过。
边界：不要连接生产数据库，不执行真实迁移，不删除字段或数据。
```

AIR classifies authentication, authorization, payments, secrets, production
state, privacy, irreversible operations, migrations, and concurrency
correctness as Critical AIR. Cost goals never weaken its safety or evidence
requirements.

AIR 会把认证、授权、支付、密钥、生产状态、隐私、不可逆操作、迁移和并发正确性
视为 Critical AIR；成本目标不会降低安全或证据门槛。

## Parallel-friendly work / 适合并行的任务

```text
$codex-air

目标：为 Python SDK 和 TypeScript SDK 同时增加同一个只读查询接口。
完成条件：两个 SDK 各自的类型检查、单元测试和示例通过；公开命名保持一致。
边界：Python 与 TypeScript 文件的写入范围互不重叠；不要修改服务端协议。
并行提示：两个 SDK 没有写入依赖，但是否并行由 AIR 根据量化门槛决定。
```

Mentioning parallelism is only a useful observation. AIR still launches two or
three executors only when the work is mostly parallel, write scopes are
disjoint, integration cost is low, and runtime capacity is available.

“可以并行”只是输入事实。AIR 仍会检查并行占比、互斥写范围、集成成本和运行时
容量，只有全部通过才启动 2–3 个 executor。

## When not to invoke AIR / 什么时候不要使用

Use ordinary Codex directly for questions, explanations, brainstorming, or a
tiny edit that is already localized. AIR is explicit-only and will not change
the default behavior of requests that omit `$codex-air`.

问答、解释、方案发散或已经完全定位的微小修改，直接使用普通 Codex 即可。AIR
只允许显式触发；没有 `$codex-air` 的请求不会改变默认行为。
