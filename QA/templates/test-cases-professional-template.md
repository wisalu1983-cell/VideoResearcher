# <scope> 测试用例 v<N>

**执行日期**：YYYY-MM-DD
**范围**：<phase / issue / feature / release>
**QA 深度**：L1 Standard / L2 Professional / L3 Release Gate
**目标用户画像**：<目标用户>
**设计方法**：<风险驱动 / 规格追踪 / 等价类 / 边界值 / 决策表 / 状态迁移 / 统计抽样 / 探索式 charter>

## Traceability Summary

| Task / Spec / Issue | Test Basis | 用例族 | 覆盖目标 |
|---|---|---|---|
| <T1 / ISSUE-001> | <Plan / Spec path> | <F-XXX> | <目标> |

## Risk Model

| Risk ID | 风险 | 影响 | 可能性 | 优先级 | 对应用例族 |
|---|---|---|---|---|---|
| R1 | <风险描述> | 高 / 中 / 低 | 高 / 中 / 低 | P0 / P1 / P2 | <用例族> |

## <用例族>：<模块名称>

| ID | Test Condition | Test Basis | Risk | Technique | Priority | Preconditions | Procedure | Oracle / Expected Result | Expected UX / Outcome | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| F-001 | <测试条件> | <依据> | R1 | <技术> | P0 | <前置> | <步骤> | <结果> | <体验/产物目标> | 自动化 / Code Review / 人工 |

## Exploratory Charters

| ID | Charter | Test Basis | Risk | Technique | Priority | Preconditions | Mission / Procedure | Oracle / Expected Result | Expected UX / Outcome | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| U-001 | <用户视角任务> | <依据> | R1 | Exploratory charter | P1 | <前置> | <探索任务> | <可接受 / 不可接受边界> | <体验/产物目标> | 模拟人工 / 视觉 QA |

## Coverage Matrix

| Risk | Covered By | Residual Risk |
|---|---|---|
| R1 | F-001, U-001 | <无 / 后续观察> |

## Execution Matrix

> 执行矩阵是 QA 结论的事实源。每个 Functional Case 和 Exploratory Charter 都必须有一行当前结果；命令级 PASS 不能替代用例 ID 级记录。

| ID | Result | 执行方式 | Evidence | 备注 / 残余风险 |
|---|---|---|---|---|
| F-001 | PASS / FAIL / RISK / BLOCKED / SKIP | <自动化 / Code Review / 人工> | <测试名、源码行、截图、命令输出摘要或报告链接> | <必要说明> |
| U-001 | PASS / FAIL / RISK / BLOCKED / SKIP | <模拟人工 / 视觉 QA / 观察> | <四栏记录、截图或报告链接> | <用户感知和后续观察条件> |

## Exit Criteria

- P0 用例全部 PASS。
- P1 可有 RISK，但必须写入 summary 的 residual risk。
- FAIL 必须进入 `ProjectManager/ISSUE_LIST.md` 或经产品裁决接受。
- 自动化失败不得写成 QA PASS。
- `Execution Matrix` 必须覆盖测试用例表中所有 ID；缺少 P0 / P1 结果不得声明 QA PASS。
