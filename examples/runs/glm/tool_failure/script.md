# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：failed

说明：GLM HTTP 429; check account/model/quota; response body omitted

运行模式：real / glm-4.7-flash

## 字幕编辑小指南

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 标题卡 | 字幕编辑小指南 | 非产品主张 | 2 |
| 2 | 字幕编辑界面示意 | 想给画面加点表达？ 来看看字幕编辑。 | 非产品主张 | 4 |
| 3 | 字体颜色设置界面示意 | 支持手动编辑字幕。 可以调整字幕的字体和颜色。 | P01/F01, P01/F02 | 5.0 |
| 4 | MP4 导出界面示意 | 选择你喜欢的表达方式。 | 非产品主张 | 4 |
| 5 | 结束卡 | 让创意留在画面里。 | 非产品主张 | 4 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "61422bac7c977fec38736c8bf68ebbf4a00585154d46a89712c30011d8114ab1",
  "shots": [
    {
      "shot": 1,
      "speech_units": 7,
      "speech_seconds": 1.75,
      "seconds": 2
    },
    {
      "shot": 2,
      "speech_units": 15,
      "speech_seconds": 3.75,
      "seconds": 4
    },
    {
      "shot": 3,
      "speech_units": 20,
      "speech_seconds": 5.0,
      "seconds": 5.0
    },
    {
      "shot": 4,
      "speech_units": 10,
      "speech_seconds": 2.5,
      "seconds": 4
    },
    {
      "shot": 5,
      "speech_units": 8,
      "speech_seconds": 2.0,
      "seconds": 4
    }
  ],
  "total_seconds": 19.0,
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
  "script_hash": "61422bac7c977fec38736c8bf68ebbf4a00585154d46a89712c30011d8114ab1",
  "passed": true,
  "issues": [],
  "citations": [
    {
      "shot": 3,
      "line": 1,
      "source_id": "P01",
      "fact_id": "F01",
      "quote": "支持手动编辑字幕。",
      "version": "2026-10-29"
    },
    {
      "shot": 3,
      "line": 2,
      "source_id": "P01",
      "fact_id": "F02",
      "quote": "可以调整字幕的字体和颜色。",
      "version": "2026-10-29"
    }
  ],
  "scope": "exact approved facts and controlled copy; not a general semantic verifier"
}
```
