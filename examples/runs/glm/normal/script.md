# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：completed

说明：脚本已通过时长和品牌规则检查，包含检索到的产品事实，满足30秒短视频要求

运行模式：real / glm-4.7-flash

## 把创意留在画面里

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 标题卡 | 把创意留在画面里 | 非产品主张 | 3 |
| 2 | 字幕编辑界面示意 | 想给画面加点表达？ 来看看字幕编辑。 | 非产品主张 | 5 |
| 3 | 字体颜色设置界面示意 | 选择你喜欢的表达方式。 支持手动编辑字幕。 | P01/F01 | 6 |
| 4 | MP4 导出界面示意 | 可以调整字幕的字体和颜色。 | P01/F02 | 6 |
| 5 | 结束卡 | 让创意留在画面里。 试试字幕编辑吧。 | 非产品主张 | 10 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "f8967ff05bd8e4fa2d67d5c9e49a08d4e64e351cdc930b282180d3c73920550e",
  "shots": [
    {
      "shot": 1,
      "speech_units": 8,
      "speech_seconds": 2.0,
      "seconds": 3
    },
    {
      "shot": 2,
      "speech_units": 15,
      "speech_seconds": 3.75,
      "seconds": 5
    },
    {
      "shot": 3,
      "speech_units": 18,
      "speech_seconds": 4.5,
      "seconds": 6
    },
    {
      "shot": 4,
      "speech_units": 12,
      "speech_seconds": 3.0,
      "seconds": 6
    },
    {
      "shot": 5,
      "speech_units": 15,
      "speech_seconds": 3.75,
      "seconds": 10
    }
  ],
  "total_seconds": 30,
  "target_seconds": 30,
  "passed": true,
  "method": "sum(max(speech_units/4, hold_seconds)); estimated only"
}
```

## 规则检查、引用及风险

```json
{
  "ok": true,
  "script_hash": "f8967ff05bd8e4fa2d67d5c9e49a08d4e64e351cdc930b282180d3c73920550e",
  "passed": true,
  "issues": [],
  "citations": [
    {
      "shot": 3,
      "line": 2,
      "source_id": "P01",
      "fact_id": "F01",
      "quote": "支持手动编辑字幕。",
      "version": "2026-10-29"
    },
    {
      "shot": 4,
      "line": 1,
      "source_id": "P01",
      "fact_id": "F02",
      "quote": "可以调整字幕的字体和颜色。",
      "version": "2026-10-29"
    }
  ],
  "scope": "exact approved facts and controlled copy; not a general semantic verifier"
}
```
