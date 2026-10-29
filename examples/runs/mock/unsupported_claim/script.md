# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：incomplete

说明：离线固定策略，仅验证工程流程。

运行模式：mock / offline-fixed-policy-v1

## 字幕编辑小指南

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 字幕编辑界面示意 | 支持手动编辑字幕。 效率提升80%。 | P01/F01, P01/F01 | 5 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "b94ef4a4fab03aac70d35d7df4c3f2cc0abb45ac5ff7d697f7d0cfdcd4345043",
  "shots": [
    {
      "shot": 1,
      "speech_units": 13,
      "speech_seconds": 3.25,
      "seconds": 5
    }
  ],
  "total_seconds": 5,
  "target_seconds": 30,
  "passed": true,
  "excess_seconds": 0,
  "method": "sum(max(speech_units/4, hold_seconds)); estimated only"
}
```

## 规则检查、引用及风险

```json
{
  "ok": true,
  "script_hash": "b94ef4a4fab03aac70d35d7df4c3f2cc0abb45ac5ff7d697f7d0cfdcd4345043",
  "passed": false,
  "issues": [
    {
      "code": "unsupported_claim",
      "shot": 1,
      "line": 2,
      "text": "效率提升80%。",
      "source_id": "P01",
      "fact_id": "F01",
      "exact_text_matches": [],
      "repair_hint": "使用匹配到的来源和事实ID；没有匹配时删除该句或改用已批准中性句。"
    },
    {
      "code": "banned_term",
      "term": "80%"
    }
  ],
  "citations": [
    {
      "shot": 1,
      "line": 1,
      "source_id": "P01",
      "fact_id": "F01",
      "quote": "支持手动编辑字幕。",
      "version": "2026-10-29"
    }
  ],
  "scope": "exact approved facts and controlled copy; not a general semantic verifier"
}
```
