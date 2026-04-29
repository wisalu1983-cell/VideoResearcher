# Project Management Starter Template

这是一套从 Mathquest 项目管理实践中抽象出来的通用项目起始模板。它只保留跨项目稳定成立的目的层和方法层：活跃控制面、版本化计划、长期规格 current spec、Issue / Backlog 分流、QA 编排、项目一致性检查和正式开发文档流。

## 使用方式

1. 复制本目录到新项目根目录，或把其中的 `ProjectManager/`、`QA/`、`scripts/`、`agent-guides/` 合并到新项目。
2. 先填写 `ProjectManager/Overview.md`，明确项目背景、当前版本、当前阶段和下一步。
3. 按 `ProjectManager/Plan/version-lifecycle.md` 创建首个版本包。
4. 按项目类型填写 `ProjectManager/Specs/_index.md`、`QA/capability-registry.md` 和 `agent-guides/project-doc-flow.md` 的项目配置位。
5. 在多源项目管理文档变更、版本启动/收口、里程碑关闭前运行 `python scripts/pm_sync_check.py`。

## 抽象边界

- 进入模板：目的、流程、接口、文档关系、质量门、产物结构。
- 留给项目：具体版本主线、Phase、Specs 维度、QA 模块、工具命令、领域校验规则。
- 不进模板：历史版本正文、项目私有规格、真实 Issue/Backlog、具体 QA run、大体积证据。
