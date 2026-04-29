# QA Leader 编排器

本文件是项目 QA 体系的规范源。核心原则是：风险驱动、规格追踪、自动化分层、探索式体验 QA 可审计、正式结论入库、过程大产物不入库。

## 0. 最小 Preflight

1. 判断任务类型：自动化 / 视觉 / 拟真人工 / 安全 / 无障碍 / 混合。
2. 判断阶段情境：hotfix、feature、核心逻辑、UI/UX、数据迁移、release、制度迭代。
3. 读取 `QA/capability-registry.md`，优先复用现成工具、模板和脚本。
4. 正式 QA 文档与结论归档到 `QA/runs/<date>-<scope>/`。

## 1. QA 深度分级

| 深度 | 适用情境 | 必需产物 | 必需验证 |
|---|---|---|---|
| L0 Smoke | 文案、小样式、低风险文档改动 | 简短 QA 记录 | 相关自检 |
| L1 Standard | 普通 feature、bugfix、局部 UI 修复 | 基础用例 + result/summary | 相关自动化 / 人工检查 |
| L2 Professional | 核心业务逻辑、复杂状态、数据迁移、跨模块重构 | 专业用例表 + risk model + coverage matrix | Code Review、自动化、拟真人工 / 视觉 QA |
| L3 Release Gate | 版本收口、上线前、全量回归 | release QA summary + 回归矩阵 | 全量测试、关键路径、历史缺陷回归 |

## 2. 测试用例设计规范

L1 及以上至少包含：ID、Test Condition、Test Basis、Procedure、Oracle、Expected UX / Expected Outcome、Priority、Verification。

L2 / L3 必须增加：Risk、Technique、Preconditions、Evidence、Result，并包含 Traceability Summary、Risk Model、Coverage Matrix、Execution Matrix、Exit Criteria、Residual Risk。

### Execution Matrix 硬性要求

L1 及以上 QA 在声明 PASS / FAIL / RISK 前，必须为每个 Functional Case 和 Exploratory Charter 留下用例 ID 级执行记录。

1. 记录可以写在 `test-cases-vN.md` 的 Result / Evidence 列，也可以单独写入 `execution-matrix.md`；若单独成文，`qa-summary.md` 必须链接它。
2. Execution Matrix 至少包含：`ID`、`Result`、`执行方式`、`Evidence`、`备注 / 残余风险`。
3. 命令级 PASS 不能替代用例 ID 级 PASS；必须能从每个用例 ID 追溯到具体测试名、源码行、截图、手工记录或命令输出。
4. 每个测试用例 ID 必须且只能有一个当前执行结论；未执行必须标 `BLOCKED` 或 `SKIP` 并说明原因。
5. 探索式 charter 也必须进入矩阵。若结论是 `RISK`，必须写清用户感知、后续观察条件和是否阻塞。
6. Exit Criteria 只能基于执行矩阵判断。若矩阵缺任何 P0 / P1 用例结果，不得声明本轮 QA PASS。

## 3. 模块划分原则

模块划分由项目定义，优先按项目生命周期和风险面划分，而不是机械按代码目录划分。

## 4. 执行编排

最小 preflight -> 选择 QA 深度 -> 设计 / 更新测试用例 -> Code Review -> 自动化测试 -> 拟真人工 / 视觉 / 无障碍 QA -> 缺陷分流 -> QA summary 和 PM 回写。
