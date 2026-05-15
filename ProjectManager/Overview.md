# VideoResearcher 项目概览

> 最后更新：2026-05-15
> 角色：活跃控制面。只保留项目背景、版本轴、当前阶段目标、当前状态、下一步和权威入口。

## 项目背景

VideoResearcher 是一个视频理解 Agent 工具项目，目标是帮助用户高效率消化本地或可合法访问的视频内容。核心价值不是一次性摘要，而是建立可追溯、可复盘、可继续追问的视频理解工作流。

## 版本轴

| 阶段 | 版本 | 状态 | 入口 |
|---|---|---|---|
| 已收口 | v0.1 / R0 | 规格、模板、数据契约、QA 口径已完成 | `ProjectManager/Plan/v0.1/README.md` |
| 已收口 | V1 | 自动建索引，Phase 4 已完成 | `ProjectManager/Plan/V1/README.md` |
| 当前版本 | V2-lite | 基本追问闭环，Phase 1-2 已完成 | `ProjectManager/Plan/V2-lite/README.md` |

## 当前阶段（V2-lite）

**阶段目标**：在 V1 索引产物基础上建立基本追问闭环，支持关键词检索片段、时间段转录回查、索引回写和不足提示。

**当前状态**：V2-lite Phase 1-2 已完成。`scripts/query_video.py` 已实现检索核心（关键词搜索、转录提取）和索引回写（主题追加、价值等级修改、变更日志）。38/38 测试通过，真实样本 QA 验证通过。

**下一步**：围绕真实追问场景迭代改进（繁简体归一化、同义词扩展、更高质量转录模型）。

## 权威入口

- 需求调研：`video_agent_requirements_research.md`
- 当前版本：`ProjectManager/Plan/V2-lite/README.md`
- v0.1 收口：`ProjectManager/Reports/2026-04-29-v0.1-closure-report.md`
- 规格索引：`ProjectManager/Specs/_index.md`
- 开放问题：`ProjectManager/ISSUE_LIST.md`
- 候选需求：`ProjectManager/Backlog.md`
- QA 体系：`QA/README.md`
