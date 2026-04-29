# 索引变更记录

只记录非增量修改，例如修正、删除、重写和高价值标记调整。普通补充可以直接写回 `index/video_index.yaml`。

```yaml
change_record:
  time:
  changed_section:
  change_type: incremental_addition | correction | deletion | rewrite | value_reclassification
  reason:
  source:
  related_question:
  before:
  after:
```
