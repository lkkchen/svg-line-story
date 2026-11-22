# GIF 局部装饰动画 · v1.1

## 设计定位

**V1 依然是纯 SVG 手绘故事为主，GIF 仅是可选的小面积、短时装饰层。** 最好的 GIF 会让插画轻轻活起来，但关闭 GIF 后，故事仍完整可读。

- **必须由 SVG + SMIL 完成**：故事主线/曲线运动、主角轮廓、转场、画布伸长、重要情节触发、文章文字。
- **可由 GIF 增强**：蝴蝶轻扇翅膀、零星花瓣落下、露珠闪光、纸船边的水纹、小灯忽明忽暗、树叶细微摆动。
- **不要用 GIF**：整张插画/整幕背景、带大面积白底或水彩底的贴图、任何必须在特定帧精确同步的转场、包含关键文字与 CTA 的画面。
- 建议每幕 0–2 张，不超过 3 张；160 × 110 像素左右，透明背景，2–4 秒，轻量文件（典型 20–100 KB）；必要时 1 张循环，但必须有明确结束时间。
- 线条主色取本篇 `palette.ink`；装饰只使用对应的 `sage`、`rose`、`orange` 等。远离大面积渐变、水彩、照片与硬边矩形框。

## 如何创作新 GIF

先完成 storyboard、SVG 主要物件和连续路径，再决定哪些场景的局部细节值得用 GIF。素材应来自与场景一致的手绘造型，可用手绘关键帧、Pillow 逐帧描绘或独立素材生成后逐帧修正。**不要为了凑数量而生成 GIF。**

仓库有一个可选 Pillow 工具，用于制作透明、手绘线条风格的小动画：

```bash
# $SKILL = 本技能 SKILL.md 所在目录的绝对路径
# 如果没有 Pillow：征得用户同意后 python3 -m venv .venv && .venv/bin/pip install pillow，再用 .venv/bin/python 运行
OUT=stories/<slug>
python3 "$SKILL/scripts/make_decor_gif.py" --kind sparkles --palette sea --output "$OUT/assets/sparkles.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind petals   --palette sea --output "$OUT/assets/petals.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind ripples  --palette sea --output "$OUT/assets/ripples.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind flutter  --palette sea --output "$OUT/assets/butterfly.gif"
```

支持 `--frames`、`--frame-ms`、`--width`、`--height`、`--playback once|loop`，以及 `--palette`（色板 id 或中文名，需与 `story.json` 的 `paletteName` 一致；省略时为春笺）。这是基础形状生成器，不会自动理解主题；遇到独特角色/物件，需要 Agent 自己设计帧。GIF 使用所选色板和透明通道；不要将整张场景截图切成 GIF。

## story.json 示例

在对应 chapter 的 `gifDecorations` 列表中声明：

```json
{
  "id": "flower-petals",
  "src": "assets/petals.gif",
  "attachTo": "blossom",
  "offset": [-55, -140],
  "width": 180,
  "height": 125,
  "trigger": {"hit": "blossom"},
  "offsetSeconds": 0,
  "playback": "once",
  "z": "front",
  "fadeInSeconds": 0.12,
  "fadeOutSeconds": 0.24
}
```

- `attachTo`：绑定已经绘制的 SVG 物件锚点，放置坐标 = `anchor` + `offset`，物件移动时装饰自动跟着移。
- `x,y`：也支持直接给绝对设计坐标，不能与 `attachTo` 同时使用；生成器不会从 GIF 内容推断锚点。
- `trigger`：绝对秒数（如 `12.6`），或 `{ "hit": "blossom" }`，后者取主线**真正到达该物件锚点**的时间，而不是提前淡入的 `leadSeconds`。
- `offsetSeconds`：与路径命中时间之间的微调，可为负数；编译器拒绝越出整个故事时长的装饰。
- `playback:once`：GIF 必须**未配置循环扩展**。编译器读取帧时长，默认播放一个自然周期后退出。可通过 `activeSeconds` 定义可见窗口。
- `playback:loop`：GIF 必须具有**无限循环扩展**，并显式配置 `activeSeconds`，避免无限占屏。
- `z:front|back`：装饰与主线的前后层级。
- `fadeInSeconds`、`fadeOutSeconds`：SVG `<g>` 透明度的 SMIL 渐变，与 GIF 内部帧动画是两层独立时间线。
- `src`：必须是 `story.json` 所在目录下的本地相对 `.gif` 文件，不能是外链、绝对路径或 `../` 逃逸路径。完整项目导出会拷贝 GIF 作为可编辑资产；HTML/SVG 中会内嵌素材。

## 生成器的同步策略

编译器以路径弧长计算 `lineArrival`，再得到每个 GIF 的 `begin`。**不是用 CSS opacity 模拟 GIF 触发。**

### 普通浏览器 `index.html`

- HTML 内联了 GIF 字节；没有远程请求，双击即可离线运行。
- GIF 的 `<image>` 初始不带 `href`。动画到达 cue 时，浏览器 JS 使用该 GIF 字节创建新的 Blob URL 并挂入 SVG `<image>`，使其以新的解码实例开始播放，而不是让早已播放结束的 GIF 才显形。
- 播放区间结束时，从元素上移除 `href` 并回收 Blob URL。
- 重播、时间轴跳转、暂停后恢复，会创建新的实例、**从第一帧重新播放**。因为原生 GIF 不支持以统一的 SVG `setCurrentTime` 帧精确 seek，不能保证暂停时保持原 GIF 内部帧，也不能声称跨所有浏览器毫秒级同步。
- 线条、画布撑高和场景的 SMIL 时间轴不受 GIF 的反复加载影响；GIF 只是装饰层，提前/延后小量帧不会破坏故事。

### `story.svg`

- `story.svg` 的 `<image href="data:image/gif;base64,...">` 会预先加载 GIF；SMIL 只控制其显示时刻与消失时刻，**不保证 GIF 是从可见瞬间的第一帧开始解码**。
- 浏览器页 `index.html` 才按 cue 新建 Blob 解码。要看精确入场，打开 `index.html`，不要只看 `story.svg`。

## 视觉与技术 QA

1. 先暂时隐藏 GIF，检查故事是否依旧完整。看不懂则说明关键内容被错误地交给了 GIF。
2. 检查 GIF 透明背景、色板、边界；不得产生明显矩形贴片。
3. 运行 `validate_story.py --input stories/<slug>/story.json`：会检查 GIF 真实格式、帧数、透明标记、循环方式、尺寸、路径安全性、锚点、触发是否越界。
4. 运行 `compile_story.py` 后查看 `cues.json` 里的 `gifDecorations`，确认 GIF 命中时间与路径点相符。
5. 可选浏览器实测：`python3 "$SKILL/tests/browser_gif_smoke.py" stories/<slug>/dist/index.html stories/<slug>/dist/gif-preview.png`（需 Playwright；否则按 `SKILL.md` 第 6 步，用当前 Agent 的浏览器拖时间轴截图），检查触发前未挂载 / 触发后 Blob / 结束卸载 / seek 新解码器。
6. 暂时去掉 `gifDecorations` 再编译一次，确认没有 GIF 时故事仍然完整。
