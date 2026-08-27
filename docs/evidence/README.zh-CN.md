# 证据与结论边界

简体中文 · [English](README.md)

Codex AIR 把架构事实与实测性能结论分开。当前运行契约是 Sol `xhigh` 控制与终审、
Luna `max` 固定请求 Fast 并负责有界执行、Terra 用量为零。静态测试可以验证这份
契约，但成本、质量、耗时、token 占比和实际 tier 都需要运行证据。

## 证据台账

| 证据 | 被测架构 | 状态 | 可以得出的结论 |
| --- | --- | --- | --- |
| v1.0 DeepSWE v1.1 hardest-10 配对 A/B | 历史 Sol 薄 Host + Luna-first v1.0 AIR | 2026-08-23 完成 | 仅代表 v1.0 的历史成本、质量与耗时 |
| v1.2 两题低额度诊断 | 当前 Sol 控制 / Luna 执行候选 | 终审前因预算中止 | 可定位瓶颈；作为 screen 无效且不计分 |
| v1.2 hardest-10 匹配复测 | 当前 Sol 控制 / Luna 执行架构 | 未运行 | 不能给出广泛的 v1.2 性能结论 |

## 历史 v1.0 hardest-10 A/B

已完成测试包含 10 道困难编码题，每个 arm-task 一次尝试，共 20 个有效单元。
Direct 使用 Sol `xhigh` Standard；历史 v1.0 AIR 使用 Sol 薄 Host 和 Luna `max`
Fast-requested 主执行器。

| 指标 | Direct Sol | 历史 v1.0 AIR |
| --- | ---: | ---: |
| 严格 resolved | 2/10 | 1/10 |
| 平均 partial | 0.8943 | 0.8932 |
| 单题耗时中位数 | 20.3 分钟 | 23.2 分钟 |
| Pro credits | 919.34 | 358.83 |
| input + output model tokens | 56,005,220 | 177,272,916 |

该测试显示计价 credits 降低 61.0%，但原始 token 更多、耗时更慢，也没有建立严格
质量非劣性。它早于 v1.2 的 Sol 语义控制与最终审核契约，因此不能把该节省称为
v1.2 实测结果。

完整逐题表、计费、环境与失败披露见
[历史 hardest-10 结果](../../tests/deepswe-v11-hardest10-results.md)。

## v1.2 两题预算中止诊断

2026-08-27，冻结的低额度 screen 同时启动 SQLFmt 与 Termenv。每题使用一个 Sol
`xhigh` controller 和一个 Luna `max` worker，固定请求 Fast，无 challenger，
Terra=0。运行接近 70-credit 硬上限时停止；两个 agent 进程都以 `-2` 退出，尚未
产生终端 Luna record 和 Sol 最终审核，因此严格 scorer 会把单元判定为无效。
confirm 阶段没有启动。

候选 patch 被保留，并且只为诊断目的进行了评分。Termenv verifier 在运行中完成；
SQLFmt 被中断的 verifier 使用完全相同的 patch 离线重跑，没有再次调用模型：

| 任务 | 历史 Direct partial | 诊断候选 partial | Direct 耗时 | 候选耗时 | Direct credits | 候选 credits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLFmt | 0.9939 | 0.9946 | 25.8 分钟 | 26.7 分钟 | 110.23 | 39.50 |
| Termenv | 0.9672 | 0.9754 | 19.7 分钟 | 26.7 分钟 | 58.24 | 27.34 |

两道历史 Direct 和两个诊断候选的严格 resolved 都是 `0`。聚合诊断信号为：

- 候选共 66.85 credits，是两道历史 Direct 的 39.7%；
- Luna 承担 95.4% 的 input-plus-output model tokens；
- 配对耗时比中位数约 1.198，超过 screen 的 1.10 门槛；
- Luna tool calls 共 170，超过 160 门槛；short polls 为零；
- actual Fast tier 为 `unobserved`，配置只能证明已请求 Fast；
- 每题一个 Sol session、一个 Luna session，无 challenger，Terra=0。

这些 partial 是中止后的 verifier 观察，不是被接受的 AIR 结果。本次运行不能得到
`CONTINUE` 或 `PASS`，不能证明质量相当，也不能与历史 Direct 拼成新的匹配 A/B。
它提供的改进方向是：成本路由与 polling 已改善，但 Termenv 耗时、总工具调用量和
在预算内完整收敛仍未解决。

冻结开发协议和门槛见
[低额度 microbenchmark](../../tests/deepswe-v11-microbench.md)。经过脱敏的精确遥测和
可复算聚合值见[预算中止 screen 工件](../../tests/fixtures/microbench-screen-20260827.json)。

## v1.2 hardest-10 状态

当前 Sol 控制 / Luna 执行架构尚未运行冻结 hardest-10 匹配 A/B。仓库中已经完成的
hardest-10 文件是历史 v1.0 结果，不是 v1.2 复测。延后的复测仍记录在
[TODO.md](../../TODO.md)。

在新的匹配复测完成前，不能声称 v1.2 比 Direct 更快、质量保持不变、普遍成本减半
或使用更少的原始 token。

## 统计限制

v1.0 benchmark 只有 10 道题，每个 arm-task 一次尝试。v1.2 诊断只有两道事后选定
的题，复用了历史 Direct 单元，而且在有效完成前中止。两者都不能证明统计非劣性。
单次样本容易受到模型方差、运行时负载、缓存、选题和 verifier 噪声影响。

广泛的公开性能结论需要：预注册匹配任务集、相同环境、成功的终端审核、完整披露
失败，以及足够的独立重复或任务数量来量化不确定性。

## 可以安全公开的表述

可以准确表述：

- v1.2 的设计和静态验证契约是 Sol `xhigh` 控制、Luna `max` Fast-requested
  执行、Terra=0；
- 历史 v1.0 hardest-10 使用 Direct 的 39.0% credits，平均 partial 几乎持平，
  但更慢且少解出一题；
- 中止的 v1.2 两题诊断在成本和 partial 上出现积极观察，但没有通过有效性、耗时
  和工具调用条件。

不要把这些表述缩写成“同等质量、成本减半”或“v1.2 更快”；现有证据没有建立这些
结论。
