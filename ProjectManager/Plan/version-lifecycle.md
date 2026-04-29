# 版本生命周期管理指南

> 触发场景：开新版本、版本过程中重排管理结构、版本收口 / 切版本轴。

## 开新版本动作

当 Backlog / Issue / 项目决策正式激活为新版本 `vX.Y` 时，创建 `ProjectManager/Plan/vX.Y/` 并完成：

1. 创建 `README.md`：版本入口和状态导航。
2. 创建 `00-overview.md`：版本背景、目标、阶段结构。
3. 创建 `01-*.md`：来源材料、调研、反馈或证据目录。
4. 创建 `02-classification.md`：分类、依赖、边界。
5. 创建 `03-phase-plan.md`：Phase 总图、进入条件、收尾条件。
6. 创建 `04-execution-discipline.md`：本版本执行纪律和验收规则。
7. 创建 `phases/phase-N.md`：至少为已知 Phase 建入口。
8. `subplans/` 默认延迟创建，具体子项启动时再建。
9. 更新 `ProjectManager/Plan/README.md` 和 `ProjectManager/Overview.md`。
10. 运行 `python scripts/pm_sync_check.py`。

## 版本收口动作

1. 更新 `00-overview.md` 为收口快照。
2. 确认 `01-04` 与 `phases/` 能追溯需求、分类、阶段和执行纪律。
3. 归档关闭 issue；延期 issue 回流 Backlog。
4. 处理各 phase / subplan 的 `Spec impact`。
5. 处理 Backlog 已纳入条目的落地、延期或放弃归档。
6. 确认 QA 结论。
7. 更新版本 README、Plan README、Overview。
8. 运行 `python scripts/pm_sync_check.py`。
