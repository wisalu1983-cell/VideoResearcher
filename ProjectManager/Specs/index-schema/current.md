# 索引结构 current spec

> 状态：R0 基线
> 来源：`video_agent_requirements_research.md` §5、§6、§9、§10、§11

## 当前承诺

索引采用 YAML 主索引加 JSON 派生索引。

| 文件 | 角色 |
|---|---|
| `index/video_index.yaml` | 唯一人工 / Agent 维护源 |
| `index/video_index.json` | 从 YAML 自动导出的脚本消费格式 |

`video_index.yaml` 应覆盖完整视频脉络，并对高价值内容保留足够线索，支持后续追问定位和展开。

## 粒度原则

| 内容类型 | 索引粒度 |
|---|---|
| 普通章节 | 章节级或小节级 |
| 高价值内容 | 片段级 |
| 实操内容 | 操作步骤级 |
| 信息密集内容 | 观点、数据、案例、方法级 |
| 追问发现的重要内容 | 回写到索引 |

## YAML 初版结构

```yaml
video:
  id:
  title:
  source_type: local_video | local_audio | subtitle | transcript | online_extracted
  source_path:
  language:
  duration:
  processed_at:

analysis_profile:
  user_focus:
  video_type: knowledge | tutorial | information | mixed | unknown
  value_directions:
    - id:
      description:

chapters:
  - id:
    title:
    start:
    end:
    summary:
    value_level: high | medium | low
    tags: []
    segments:
      - id:
        start:
        end:
        type: concept | argument | data | example | method | operation | quote | question
        summary:
        key_points: []
        original_terms: []
        original_snippets: []
        supports_questions: []
        confidence: high | medium | low

follow_up_index:
  suggested_questions: []
  important_topics: []

quality:
  transcription_quality: A_precise | B_overview | C_unreliable
  timestamp_quality: precise | approximate | unreliable
  known_limitations: []
```

## JSON 派生规则

- `video_index.json` 由 `video_index.yaml` 自动生成。
- JSON 不作为人工维护源。
- 导出过程不得改变 YAML 的语义内容。
- JSON 用于脚本读取、检索和 QA 结构校验。

## 更新规则

- 追问后发现新增信息、标签或片段说明时，优先增量写回 `video_index.yaml`。
- 修改已有判断、删除旧信息、重写摘要或调整高价值标记时，必须写入 `logs/index_change_log.md`。
- 默认不为每次索引更新创建新版本文件。
- 只有用户明确要求冻结阶段结果、做分支分析或保留独立版本时，才创建新索引文件。
