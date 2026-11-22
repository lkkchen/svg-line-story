# 平台适配和质量门槛

## 浏览器端

推荐 Chrome / Edge / Safari 的当前版本，优先验证最新 Chromium。`index.html` 是单 HTML，内联 SVG/SMIL/样式/脚本（有 GIF 时将其字节内嵌），可离线双击打开。浏览器 JS 用于暂停、重播、时间轴、调试锚点和自动滚动；作品的核心路径、物体和伸长全部是 SVG+SMIL。底部控制条在指针离开约 2.4 秒后收成一条细横条，移入再展开，避免挡住画布。若 `story.json` 有 `sound`，页面按时间轴播放音效，默认静音，点控制条后出声。截图前仍要隐藏 `.dock-slot`、`.dock`、`.dock-peek` 和 `.topbar`。

最低 QA 流程：

```bash
# $SKILL = 本技能 SKILL.md 所在目录的绝对路径
OUT=stories/<slug>
python3 "$SKILL/scripts/validate_story.py" --input "$OUT/story.json"
python3 "$SKILL/scripts/compile_story.py" --input "$OUT/story.json" --output "$OUT/dist"
python3 -m unittest discover -s "$SKILL/tests" -p 'test_*.py'
# 可选，需 playwright + Chromium；没有时用当前 Agent 的浏览器（见 SKILL.md 第 6 步 B）
python3 "$SKILL/tests/browser_smoke.py" "$OUT/dist/index.html" "$OUT/dist/preview.png"
# 如果添加了透明 GIF：
python3 "$SKILL/tests/browser_gif_smoke.py" "$OUT/dist/index.html" "$OUT/dist/gif-preview.png"
```

对比 440px 手机宽和 1280px 桌面宽；在 0s、每一幕的入口、触碰时刻和结尾检查可见高度、线的描边状态、交互图形位置、文字遮挡。审美缺陷无法由 unit test 代替。

## 验收 checklist

- 路径和对象视觉锚点在同一个真实描边接触处；手绘主线停在该笔画上并从此离开，不横穿物件或文字。
- 会生长的茎、河、轨是一根 `stroke-dashoffset` 路径。`pop` / `sway` 缓入后停住，同一物件的后到零件错开 0.15–0.4 秒。
- 远景在 `z:"back"`，主线在其上，要盖住线的物件在默认 `front`。
- 时间轴 cue 与路线弧长相符，动作只播放设计时长，暂停和重播可用。
- 场景之间不出现路径断点；过场不是简单地插入一张整屏静态图。
- 每幕至少 1 个主角、3 个辅助物件、4 个点缀小件、1 处小注释；任意 1000 设计单位高的一段里至少 5 个物件。主角达到 `references/vector-art.md` 的图形数和填充下限。
- 物件 `id` 和画出来的东西一致，没有拿 `cloud` / `star` / `bird` 顶替素材清单里的东西。
- 所有主角与关键构图属于真正的 SVG 原语且样式统一。可选 GIF 仅小面积、透明、短时，关闭后故事仍完整；不允许整页图片或网络依赖。
- 使用 GIF 时检查本地文件格式、循环属性、开始/结束 cue 和浏览器 Blob 重载。去掉 GIF 后故事仍要完整。
- 动画会长高到最终画布高度，手机/桌面均无横向滚动。
- 首尾空白和文案正确；如果用了特殊中文字体，仅依赖系统字体回退。
- 用户要求仅一个主题时，Agent应自己完成故事结构和风格选择，不以缺参数为由停止。
