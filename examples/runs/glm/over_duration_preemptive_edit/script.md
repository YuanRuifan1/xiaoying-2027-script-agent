# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：completed

说明：脚本时长达标（30秒）、产品事实正确引用且品牌规则合规，任务完成

运行模式：real / glm-4.7-flash

## 字幕编辑小指南

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 标题卡 | 想给画面加点表达？ | 非产品主张 | 3 |
| 2 | 字幕编辑界面示意 | 支持手动编辑字幕。 | P01/F01 | 23 |
| 3 | 结束卡 | 试试字幕编辑吧。 | 非产品主张 | 4 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "49533e8b690812799a978f141ab98797771f7dfe538e1e27fb7db9ccf3a900c2",
  "shots": [
    {
      "shot": 1,
      "speech_units": 8,
      "speech_seconds": 2.0,
      "seconds": 3
    },
    {
      "shot": 2,
      "speech_units": 8,
      "speech_seconds": 2.0,
      "seconds": 23
    },
    {
      "shot": 3,
      "speech_units": 7,
      "speech_seconds": 1.75,
      "seconds": 4
    }
  ],
  "total_seconds": 30,
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
  "script_hash": "49533e8b690812799a978f141ab98797771f7dfe538e1e27fb7db9ccf3a900c2",
  "passed": true,
  "issues": [],
  "citations": [
    {
      "shot": 2,
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
