# SVG 长卷

一套可安装到支持 Agent Skills 的创作指令与编译器。**给 Agent 一个主题**，它规划情节、原创矢量物件与连续路径，然后生成 SVG + SMIL 长卷网页。**V1 的画风、故事主线与场景仍以原生 SVG 为主体**；需要时才加入透明 GIF 的微小局部动画（蝴蝶振翅、花瓣、微光、波纹），不会回到 V2 的整页水彩图片。

## 包含什么

- `SKILL.md`：可被 Agent 阅读和执行的故事导演 / 插画 / 路径 / 动画完整工作流。
- `references/`：分镜与视觉语言、GIF 创作和同步策略、路径时间轴、浏览器 QA。
- `scripts/plan_story.py` / `run_theme.py`：无需模型、基于主题词的**底稿生成器**。真正的自定义故事、人物与插画仍依赖阅读 Skill 的 Agent，不能把这两个模板程序误称为自动理解所有主题的 AI。
- `scripts/motifs.py`：24 个统一风格的原生 SVG 手绘物件，支持 Agent 自己绘制 `customMotifs`。
- `scripts/compile_story.py`：把场景对象、精确锚点、连续路径与 SMIL 时间轴编译成离线长卷网页；有 GIF 时附加受控的透明装饰层。
- `scripts/gif_decor.py`：Python 标准库检查 GIF 帧数、时长、透明标记、循环扩展、尺寸与本地路径安全；根据主线命中时间自动生成装饰入场 cue。
- `scripts/make_decor_gif.py`：**可选 Pillow**，自动绘制 4 类小型透明手绘 GIF（sparkles / petals / ripples / flutter）。特殊主题需由 Agent 创作对应逐帧素材。
- `scripts/validate_story.py`：检查路径、锚点、时序、素材格式、页面伸长。
- `scripts/theme_map.py`：按 `story.palette` 重映射 motif 里残留的硬编码色（保留明度差）。**仅老作品需要**——带 `paletteName` 时自动跳过，否则暗色纸底会被误翻成金色。
- `scripts/smoke.py`：Playwright 体检 —— 撑高曲线单调、无横向溢出、无 JS 报错。
- `scripts/palettes.py`：**12 套命名色板**，每套含纸色 + 6 个角色色 + 动作幅度（calm/punchy）+ 收笔风格；`--suggest <主题>` 按主题词推荐。
- `scripts/arcs.py`：**6 条叙事弧**（三幕 / 时间线 / 跌入再爬出 / 破除迷思 / 原理拆解 / 故事脊），决定每幕的 role、emphasis、motion。
- `examples/spring/`：可直接运行的 3 幕春天演示，12 个主要矢量物件。GIF 需用 `make_decor_gif.py` 现场生成（分发包只含文本）。这篇用铅笔开场，是「从落笔开始」的样例立意，**不是新故事的必选开场**。
- `examples/1024/`：程序员节长卷，109 个自定义物件。这是画法和密度的对照，不是新故事的默认长度。不要把春笺那篇的铅笔抄进无关主题。

## 安装

本技能不绑定任何客户端。把整个目录放到你的 Agent 能读到的 skills 目录即可，例如：

```bash
cp -r svg-line-story ~/.openclaw/workspace/skills/
```

只要能读 `SKILL.md`、能落盘、能跑 Python 3.10+，就能工作。核心编译只用标准库；Pillow（生成 GIF）与 Playwright（浏览器体检）为可选项。

在对话里说：

> 用 SVG 长卷，以《森林里的一封信》为主题做一个 SVG 长卷。

Agent 会先交回一份故事计划（线的隐喻和三幕分镜）。用户确认后才把作品写到工作区 `stories/<slug>/`，不写入 Skill 目录。

## 一键跑预设底稿（无需安装额外依赖，在工作区根目录执行）

```bash
SKILL="$PWD"   # 本 README 所在目录
python3 "$SKILL/scripts/run_theme.py" '海边的一封信' --output stories/sea-letter
```

这个命令使用模板词库，默认**不复制春天的 GIF** 到无关主题。Agent 执行 Skill 后可自主绘制新图形、生成符合该主题的 GIF，再编辑 `story.json`、编译和检查。

## 手动编译 GIF 示例

```bash
python3 scripts/validate_story.py --input examples/spring/story.json
python3 scripts/compile_story.py --input examples/spring/story.json --output examples/spring/dist
```

`story.json` 中每章可写 `gifDecorations`，示例：

```json
{
  "id": "bloom-petals",
  "src": "assets/petal-drift.gif",
  "attachTo": "blossom",
  "offset": [-55, -140],
  "width": 180,
  "height": 125,
  "trigger": {"hit": "blossom"},
  "playback": "once"
}
```

`attachTo + offset` 让局部 GIF 跟着 SVG 物件的几何锚点移动；`trigger.hit` 的 GIF 入场时间由主线弧长自动推导。也可用 `x, y` 固定放置、使用数字 `trigger` 表示绝对秒数。详细字段及限制见 `references/gif-decoration.md`。

`stories/<slug>/dist/` 或 `examples/spring/dist/` 的输出：

| 文件 | 作用 |
|---|---|
| `index.html` | 单文件、离线可用的浏览器长卷。小型 GIF 在 cue 时由 JS 新建 Blob 解码实例，时间轴重播会重新加载 |
| `story.svg` | 主线和插画为 SVG/SMIL，可选 GIF 内嵌为 SVG `<image>`（GIF 帧播放与 SMIL 时间并非完全同步） |
| `story.json` | 故事结构、路径、对象、GIF 及时间数据源 |
| `assets/...` | 同步复制的 GIF 原素材，方便后续二次编辑 |
| `cues.json` | 路径长度、SVG 触发时间、GIF 入场与退出时间、长高计划 |
| `STORYBOARD.md` | 分镜和动态装饰清单 |

## GIF 的播放边界

初始不挂载 GIF，在指定入场秒数才为该 GIF 创建新的 Blob URL 以开始解码，结束后卸载，重新播放 / 拖动进入播放区间时重建。这比「事先加载 GIF、到点把 opacity 设为 1」可靠，但**无法对原生 GIF 精确暂停在某帧或在 seek 后跳到中间的指定帧**；seek/暂停后恢复会重新从第一帧启动。请不要把 GIF 用作关键的精确节拍动作。

## 验证

核心编译器使用 Python 3.10+ 标准库；仅制作样例 GIF 时需要 Pillow，浏览器 QA 可选 Playwright + Chromium。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_story.py --input examples/spring/story.json
python3 tests/browser_smoke.py examples/spring/dist/index.html examples/spring/dist/preview.png
python3 tests/browser_gif_smoke.py examples/spring/dist/index.html examples/spring/dist/gif-preview.png
```

**美术规范不变：** 统一墨蓝线条、奶油白留白、少量鼠尾草绿/暖橙/珊瑚色块；路径必须经过真实几何锚点。GIF 不得覆盖整张画布、不能携带必读文字，更不能替代主线与主体轮廓。
