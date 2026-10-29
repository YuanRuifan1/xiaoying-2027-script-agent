# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：failed

说明：GLM HTTP 429; check account/model/quota; response body omitted

运行模式：real / glm-4.7-flash

## 字幕编辑小指南

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 标题卡 | 想给画面加点表达？ | 非产品主张 | 3 |
| 2 | 字幕编辑界面示意 | 支持手动编辑字幕。 | P01/F01 | 38 |
| 3 | 结束卡 | 试试字幕编辑吧。 | 非产品主张 | 3 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "90d5e4c773e0f71adc33ce10064d1515e7649e9c8e7121e42ea94609aa435cff",
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
      "seconds": 38
    },
    {
      "shot": 3,
      "speech_units": 7,
      "speech_seconds": 1.75,
      "seconds": 3
    }
  ],
  "is_initial_draft_estimate": true,
  "total_seconds": 44,
  "target_seconds": 30,
  "passed": false,
  "excess_seconds": 14,
  "method": "sum(max(speech_units/4, hold_seconds)); estimated only"
}
```

## 规则检查、引用及风险

```json
null
```
