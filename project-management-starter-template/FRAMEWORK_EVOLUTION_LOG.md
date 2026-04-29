# 框架演进日志

用于记录在具体项目实例化过程中发现的通用骨架优化点。只记录会影响模板自身的经验，项目私有决策留在项目自己的 `ProjectManager/Reports/` 或版本文档中。

| 日期 | 触发项目 / 场景 | 骨架原样 | 调整建议 | 原因 | 状态 |
|---|---|---|---|---|---|
| YYYY-MM-DD | <项目 / 场景> | <原设计> | <建议改法> | <为什么> | candidate / accepted / rejected |
| 2026-04-29 | Mathquest QA 防复发规则 | QA 规范只要求用例、Risk、Coverage 和 Exit Criteria | L1 及以上 QA 增加 Execution Matrix，要求每个用例 ID 有 Result / Evidence；缺 P0/P1 结果不得声明 QA PASS | 命令级 PASS 容易掩盖未执行或未记录的用例，执行矩阵应成为 QA 结论事实源 | accepted |
