# 一笔画出春天 · Storyboard

**主题**：一颗种子遇见春天　 **总时长**：32 秒　 **配色**：custom　 **叙事弧**：three_act

| 幕次 | 起止时间 | 场景 | 主线要经过的物件 |
|---|---|---|---|
| 01 | 1.6–10.7s |  初醒 · 有些故事， / 从一颗种子开始。 | pencil、seedlet |
| 02 | 10.7–20.1s |  盛放 · 等一朵花， / 慢慢盛开。 | seedlet、blossom |
| 03 | 20.1–32s |  远行 · 把春天， / 送到远方。 | paperboat |

## 路径触发点

| 元素 | 到达时间 | 入场时间 | 坐标 |
|---|---:|---:|---|
| pencil | 1.60s | 1.42s | (190.0, 575.0) |
| seedlet | 10.70s | 10.50s | (490.0, 1260.0) |
| seedlet | 10.70s | 10.50s | (490.0, 1260.0) |
| blossom | 17.39s | 17.15s | (356.0, 2063.0) |
| paperboat | 25.12s | 24.80s | (452.0, 2990.0) |

## 局部 GIF 点缀（不替代 SVG 主体）

| GIF | 作用区域 | 触发秒数 | 消失秒数 | 播放 |
|---|---|---:|---:|---|
| sprout-sparkles | assets/sprout-sparkles.gif | 10.70s | 12.86s | once |
| bloom-petals | assets/petal-drift.gif | 17.39s | 19.55s | once |
| boat-water-ripples | assets/boat-ripples.gif | 25.12s | 27.28s | once |

## 审核须知

- 所有构图位置属于 750px 设计坐标，不是 CSS 像素。
- 路径、主角和关键动作仍然属于内联 SVG；小尺寸透明 GIF 只做局部装饰。
- 浏览器版本按 cue 动态挂载 GIF；暂停/跳转后只保证重新开始，不支持 GIF 帧级 seek。
- story.svg 会提前内嵌 GIF：SMIL 控制可见性，不保证 GIF 入场时从第一帧开始。
