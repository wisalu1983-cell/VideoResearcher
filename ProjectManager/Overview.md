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
| 下一版本 | V2-lite | 基本追问可用 | 待启动 |

## 当前阶段（V1）

**阶段目标**：实现本地视频到带时间戳转录、Markdown 笔记、YAML 主索引、JSON 派生索引和日志的自动建索引链路。

**当前状态**：v0.1 已完成收口验收；V1 Phase 1-4 已完成。Phase 4 已补齐 `process_video.py --phase4` 产物结构 QA、`logs/qa_report.md`、失败记录和处理日志收口；当前真实样本已通过 V1 产物结构验收。

**下一步**：进入 V2-lite 规划，围绕基本追问、片段检索、答案依据和不足提示建立闭环。

## 权威入口

- 需求调研：`video_agent_requirements_research.md`
- 当前版本：`ProjectManager/Plan/V1/README.md`
- v0.1 收口：`ProjectManager/Reports/2026-04-29-v0.1-closure-report.md`
- 规格索引：`ProjectManager/Specs/_index.md`
- 开放问题：`ProjectManager/ISSUE_LIST.md`
- 候选需求：`ProjectManager/Backlog.md`
- QA 体系：`QA/README.md`
