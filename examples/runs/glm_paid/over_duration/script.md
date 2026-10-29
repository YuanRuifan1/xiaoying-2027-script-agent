# 短视频脚本

> 产品资料为虚构；时长为规则估算。

状态：completed

说明：脚本通过时长检查（26秒≤30秒）和品牌检查，两条产品事实正确引用，所有文案符合白名单规则

运行模式：real / glm-4.7

## 字幕编辑小指南

| 分镜 | 画面 | 旁白/字幕 | 来源 | 预计秒数 |
|---|---|---|---|---|
| 1 | 标题卡 | 想给画面加点表达？ | 非产品主张 | 3 |
| 2 | 字幕编辑界面示意 | 支持手动编辑字幕。 | P01/F01 | 6 |
| 3 | 字体颜色设置界面示意 | 可以调整字幕的字体和颜色。 选择你喜欢的表达方式。 | P01/F02 | 7 |
| 4 | MP4 导出界面示意 | 让创意留在画面里。 来看看字幕编辑。 | 非产品主张 | 7 |
| 5 | 结束卡 | 试试字幕编辑吧。 | 非产品主张 | 3 |

## 时长检查

```json
{
  "ok": true,
  "script_hash": "c3e435733385fac8b44d61823e1f362c632fa288d94a665f4392b27b8c7e1eda",
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
      "seconds": 6
    },
    {
      "shot": 3,
      "speech_units": 22,
      "speech_seconds": 5.5,
      "seconds": 7
    },
    {
      "shot": 4,
      "speech_units": 15,
      "speech_seconds": 3.75,
      "seconds": 7
    },
    {
      "shot": 5,
      "speech_units": 7,
      "speech_seconds": 1.75,
      "seconds": 3
    }
  ],
  "is_initial_draft_estimate": false,
  "total_seconds": 26,
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
  "script_hash": "c3e435733385fac8b44d61823e1f362c632fa288d94a665f4392b27b8c7e1eda",
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
    },
    {
      "shot": 3,
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
