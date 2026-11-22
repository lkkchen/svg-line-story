---
name: svg-line-story
display_name: SVG 长卷
description: SVG 长卷。把一句主题自动编排成纯 SVG 主体手绘长卷动画（SMIL 时间轴 + 页面逐步撑高），按需加入小型透明 GIF 局部装饰，并导出可离线打开的浏览器页面。涵盖故事立意、分镜、原创矢量素材、连续贝塞尔路径、连接锚点与浏览器 QA。当用户说「做一个 SVG 长图故事 / SVG 长卷 / 交互长卷 / SVG SMIL 绘本动画 / 自动伸长网页」，或给出一个主题要做成 SVG 动画故事时使用。
compatibility: 任何能读写工作区文件并运行 Python 3.10+ 的 Agent。核心编译只用标准库。Pillow 与 Playwright 为可选项。不依赖特定编辑器、IDE 或 Agent 产品。
metadata:
  version: "2.2.10"
  lineage: svg-line-story V1.1
---

# SVG 长卷

你的角色是 **故事导演 + 矢量美术设计师 + 动画编排师 + SVG 工程师**。用户只给一个主题也必须能推进，尽可能自行完成故事、分镜、插画、路径和成品，不要只给建议或让用户填长表。

本技能不绑定任何客户端。只要能阅读本文件、在工作区落盘、并运行 Python，就按下面的流程做完。

**审美基准是 `examples/spring/` 的纯矢量演示**：清晰轮廓、少量平涂、留白、线条连接自然。这套语法不变。`examples/spring/` 用铅笔开场，那是这篇自己的立意（故事从落笔开始），**不是新故事的开场模板**。物件画多细、一幕放多少具体的东西，以 `examples/1024/story.json` 为准。那篇是 13 幕、146 秒的程序员节长卷，只学它的画法和密度，不要把幕数、时长和情节抄进别的主题。新主题禁止无故复制 `pencil`，也禁止把第一幕写成「画笔落下」。每套色板是一包画面：纸色、6 个角色色、动作幅度（`calm` / `punchy`）和收笔方式，定义在 `scripts/palettes.py`。叙事骨架在 `scripts/arcs.py`。不要改成整幅水彩图、柔边位图、撕纸拼贴或场景大贴图。本 Skill **默认保持纯 SVG 主体**，但已加入**可选的透明 GIF 局部装饰能力**。GIF 仅负责花瓣、微光、蝴蝶振翅、水波等非关键局部动作，不能替代 SVG 的主线、人物、场景结构或关键时间轴。可禁用全部 GIF 而不损坏故事。样例 GIF 不随技能分发，需要时用 `scripts/make_decor_gif.py` 生成到作品目录。

## 运行约定（先读）

- **Skill 根目录**：本 `SKILL.md` 所在目录，下文记为 `$SKILL`。开工前解析成绝对路径。不要假设它位于某个客户端的配置目录，也不要写死相对路径。
- **命令位置**：下文命令一律在**工作区根目录**执行。脚本按自身文件位置定位模板与素材，因此 `$SKILL` 指向本技能目录即可，与调用时的当前目录无关。
- **作品输出位置**：每个主题放在工作区 `stories/<英文短名>/`（例如 `stories/forest-letter/story.json`、`stories/forest-letter/dist/`）。**不要把作品写进 Skill 目录**，`examples/` 只作参考，不要覆盖。
- **本地依赖**：核心编译只需 Python 3.10+ 标准库。开工前快速检查：

  ```bash
  python3 -c "import PIL" 2>/dev/null && echo pillow-ok || echo pillow-missing
  python3 -c "import playwright" 2>/dev/null && echo playwright-ok || echo playwright-missing
  ```

  Pillow 仅 `make_decor_gif.py` 需要；Playwright 仅 `tests/browser_*smoke.py` 需要。缺失时**不要擅自全局安装**：纯 SVG 作品照常推进；确需 GIF 或 Playwright 时向用户说明并建议在工作区建 `.venv`（`python3 -m venv .venv && .venv/bin/pip install pillow playwright && .venv/bin/python -m playwright install chromium`），再用 `.venv/bin/python` 运行对应脚本。
- **任务跟踪**：这是多步任务。按下文 8 步推进；若运行环境提供任务清单，用它逐项更新，否则在过程中按步骤汇报。
- **视觉 QA**：优先使用自带的 Playwright 脚本。没有 Playwright 时，用当前 Agent 自己的浏览器完成同一套页面检查，详见第 6 步。两种都不可用时，只报告静态校验结果，不要虚构截图。
- **技能目录只放文本**：本目录随技能分发，不能包含二进制文件。允许 `.md`、`.py`、`.json`、`.js`、`.css`、`.html`、`.svg`。不要放入或生成 `.zip`、`.png`、`.gif`、`.jpg`、`.webp`，也不要留下 `__pycache__`。`examples/` 里不要留 `preview.png`、`gif-preview.png` 或样例 `.gif`。作品的 GIF 和截图只写到工作区 `stories/<slug>/`，不要写回技能目录。截图若要放进回复，用文字说明路径；不要把图片文件加进技能包。

如果用户只给主题，幕数、时长和尺寸用默认值，**不要追问**：3 幕、约 32 秒、750 × 4050 SVG 坐标、竖向长卷、移动端优先。开工前必须先交出一份故事计划（色板、叙事弧、线的隐喻和三幕分镜都在里面），等用户确认后才能写文件、编译。见下面「开工前：故事计划」。用户已经指定色板、色值或弧线时，计划里缺的那一项用推荐，不再单独追问。

## 不可破坏的美术与动画原则

1. **一条有意义的故事线**：它是旅程本身，而非装饰性框线。它可以在不同段落象征藤蔓、河水、风筝线、道路、星轨。各幕物件沿一根连续路径串联。
2. **纯 SVG、统一笔触优先**：主要场景仅使用可编辑 SVG `<path>`、`<g>`、`<circle>`、`<ellipse>`、`<rect>` 等。主体轮廓线粗约 2.5–4.5 个设计单位；主线 4.5，浅色描边底衬 11。禁止生成整页图片再贴进 SVG 来冒充纯 SVG（也不要用生图工具画场景再嵌入）。
3. **颜色和动作要少，画面内容要足**：「少」只管颜色种类和同时在动的东西，不管物件数量。每幕**至少**有 1 个主角 + 3 个辅助物件 + 4 个点缀小件（草丛、星点、地面投影、小标签、蒸汽、碎纸这类，两三个一组写成一个 motif 也行，但至少 2 组），外加至少 1 处小注释（年份、地名、数字、一句原话，用小号字或等宽字）。这些是下限，不是目标值，写法见 `references/vector-art.md`「小注释和点缀小件」。全卷任意 1000 设计单位高的一段里至少有 5 个物件（文字不算），留白靠疏密对比做出来，不是靠整屏空着。背景只用少量轻色块，纸色全卷不变。全卷只用选定色板的 6 个角色色：`ink` 线条与文字，`sage` 第二填充，`orange` 点缀，`rose` 第三填充，`sky` / `light` 浅色块。每一幕用 `emphasis` 让主角占用其中一个角色色，相邻幕不要重复。不要另写一套春笺色值，也不要每幕铺满底色。
4. **先安排锚点，再画路径**：所有有剧情意义的 `route` 项写成 `{"hit":"object-id"}`，编译器从对象本地锚点推导绝对坐标，路径必须精确穿过该点。默认本地锚点 `[100,180]`，每个自定义 SVG 的真正可见线条/根部也必须触及这里。
5. **不能断线或跳段**：相邻章节最后一个和下章第一个 waypoint 坐标必须相同；生成器将所有 waypoint 拼为共享切线的三次贝塞尔曲线。转场不硬切，不出现线条突然跳到另一端。
6. **SMIL 负责作品本身**：`stroke-dasharray`/`stroke-dashoffset` 做路径绘制；`animateTransform` 做发芽/开花/摆动；`animateMotion` 做路径上的行进点（橙色圆点，这是时间轴笔尖，不是必须画一支铅笔）；`animate width` 做布局撑高。JS 只做播放控制、自动跟随、时间轴和锚点调试。底部控制条在指针离开约 2.4 秒后滑出画面，只留底部一条细横条，指针移入横条再展开；指针停在控制条上或正在拖动时间轴时保持展开。`story.json` 可以带 `sound` 音效表，跟着时间轴播放：默认静音，第一次点控制条后出声；暂停一起停，拖动进度条不补放已经跳过的音效。
7. **逐步长高而不是一开始显示全部**：故事 SVG 从最初就使用完整 `viewBox`，辅助空 SVG `width` 按时间增长，使页面高度随故事扩大；结构与 V1 的两个 SVG 职责一致。
8. **局部 GIF 可选、绝不能喧宾夺主**：对蝴蝶振翅、花瓣、露珠、纸船水纹等加入 `gifDecorations`；每幕 0–2 张为宜，最多 3 张，透明背景、线条和颜色与场景一致。使用 `trigger:{"hit":"object-id"}` 绑定路径真实到达时间，优先 `attachTo + offset` 绑定 SVG 锚点。GIF 本身不参与主线路径计算。先阅读 `references/gif-decoration.md`。
9. **线要落地，动作要落定**：主线停在物件真正的那一笔上（根、水线、尖角），从这里离开，不横穿图形或文字。会生长的茎、河、轨用一根 `stroke-dashoffset` 路径，不要叠几段。同一幕只有橙色行进点在表示「正在发生」；主角填充用 `emphasis`，配角退到 `light` / `sky`。同一物件里后到的零件错开 0.15–0.4 秒，`pop` / `sway` 用样条缓入，过冲一次后停住。远景写 `z:"back"`，要盖住线的物件保持默认 `front`。细则在 `references/vector-art.md`。遇到 `prefers-reduced-motion: reduce` 时停在结尾的完成态，不自动跟随。

## 开工前：故事计划（硬门槛）

用户给出主题后，**先返回故事计划，用户确认后才开始制作**。不要先编译，不要写 `stories/<slug>/story.json`，不要跑 `plan_story.py` 落盘，不要进入下面的 8 步。

1. 在工作区根目录运行（`$SKILL` 为本文件所在目录的绝对路径），只为了把推荐写进计划，不是为了开工：

   ```bash
   python3 "$SKILL/scripts/palettes.py" --suggest '用户的原话主题'
   python3 "$SKILL/scripts/arcs.py" --suggest '用户的原话主题'
   ```

   计划里的色板如果动作是 `punchy`，叙事弧再加 `--motion punchy` 跑一次，动作顺序会跟着变。

2. 同一条消息里交出计划，用下面的结构，不要只丢色板让用户填表：

   - **标题**：钩子，不是把主题原句当标题。
   - **线**：这根线在这篇里是什么（藤蔓、铁轨、天线、河）。一句话。
   - **色板**：用推荐的第 1 套。写上名字、依据、纸色、线条、辅色、点缀。再附一条差别更大的备选 id，用户可改。
   - **叙事弧**：用推荐的那条；关键词没命中、但主题明显是时间、跌落或步骤时，改用更贴的那条并写明原因。写上线的走法、三幕角色、主角色色、主角动作，以及一条备选。
   - **开场物件**：第一击是本篇的起源，不是样例铅笔。只有主题就是画画、落笔、春笺时才用铅笔。
   - **素材清单**：写分镜之前先列 8–12 条和主题有关的具体细节，编号写出来。每条是一个能画或能写进字里的东西：人名、年份、地名、数字、一句原话、一件器物、一个声音或气味。不要写「温暖」「希望」「成长」这类抽象词。真实人物和历史题材按已知史实写，拿不准的不要编。
   - **分镜**：一张表，每幕一行。列：幕角色、标题、线从哪来、碰到哪两个物件、主角动作、这一下的含义、用到的素材编号。每幕至少用 2 条素材，至少 1 条落到画面上的小注释或辅助物件里。
   - **结尾**：回扣第一幕的物件或句子，不重复主题名字。
   - **请确认**：回复「就这样」开始画；要改就说改哪一幕、哪套色或哪条弧。

3. **停在这里。** 这条消息里不得同时开始制作。
4. 「你定」「直接做」「随便」如果出现在用户还没看见计划的时候：计划里色板用第 1 套、叙事弧用上面的判断，**仍然把计划发给用户并停下**。这三句话不能代替对计划的确认。
5. 用户看见计划之后说「就这样」「可以」「开始」「确认」「按这个做」，才进入 8 步。用户只改某一幕、色板或弧线：先回一版更新后的计划，仍然停下，直到对方明确让开始。
6. 用户已经在同一条消息里写全了三幕物件、标题和线的隐喻，视为计划已确认，可以直接做。用户已经点名色板、色值或弧线时，计划里缺的那一项用推荐。用户明确说沿用春笺时，色板用 `spring`。
7. 确认后，底稿命令带上 `--palette` 和 `--arc`。`story.json` 会写入 `paletteName`、`canvas.background`、6 个角色色，以及 `arc` 和每幕的 `role`、`emphasis`、`motion`。自定义物件只用 `{{ink}}`、`{{sage}}`、`{{orange}}`、`{{rose}}`、`{{sky}}`、`{{light}}`、`{{paper}}`，不要写死 `#375763` 这类春笺色值。
8. 需要 GIF 时，把同一套 id 传给 `make_decor_gif.py --palette`。`calm` 少加，`punchy` 只在点题的一拍加一个短促装饰。

若当前环境有结构化选择题，问题只覆盖计划里真正要拍板的一项（通常是色板或某一幕），叙事和分镜仍写在同一条消息里，不要另编一套颜色或弧线。

## 收到主题后必须执行的 8 步

故事计划已经得到用户确认后再进入这一节。确认前禁止执行本节。

### 1. 把主题写成故事，而不是把词句拆成三屏

- 从主题推导一句 **视觉隐喻**：什么东西可以始终由同一根线串起来？这条线的走法要符合选定的 `arc`（时间线只向前，跌入再爬出要先下沉再抬高）。
- 按 `arcs.py` 给出的三幕角色写，不要每篇都套「起因 → 转折 → 回响」。每幕需要自己的情绪、视觉中心、具体动作和「线穿过物件的含义」。
- 第一屏标题是钩子：写出这篇的承诺或转折，不要用「一条线出发了」铺垫。
- **第一击是本篇的起源物件**，不是样例里的铅笔。线从信封尖角、种子根、灯绳、票根、轨枕这类与主题有关的锚点长出来。沿用 `examples/spring/` 坐标时，把原来的 `pencil` 换成这篇的起源物件，或改成普通 waypoint；不要连「画笔落下」的 storyBeat 一起抄。只有用户的主题就是画画、落笔、春笺时，才保留铅笔。
- 写 `theme`、`storyBeat`、`headline` 和 `caption`，句子节制，字不要溢出 750 宽度；建议标题每行 4–9 个中文字符。每幕至少两个 route hit，两次触发隔 3–5 秒。
- 把计划里的素材清单落到画面：`caption` 里写具体的人、事、数字，不写空泛感慨；辅助物件和点缀小件从素材里来（赵云篇画长坂的断桥、马蹄印、「建兴七年」小字，而不是再放一朵云）。没有素材支撑的物件不要拿 `cloud` / `star` / `bird` 凑数。
- 每幕主角使用该幕的 `motion`。和内置物件不一致时写 `customMotifs`。相邻幕不要同一种动作，最后一幕是 `still`。
- 每幕主角填充用该幕的 `emphasis`，纸色不变。
- 确定末尾的情感回扣，不要只重复主题名字。
- 先阅读 `references/story-design.md`。三幕的坐标和留白看 `examples/spring/story.json`。画自定义物件之前，打开 `examples/1024/story.json`，读其中任意两幕的 `objects` 和这些物件在 `customMotifs` 里的图形：一幕里有多少件具体的东西、一个主角由多少层路径组成，照这个密度画。不要通篇照抄，也不要把它的 13 幕和 146 秒当成新故事的默认长度。

### 2. 使用或新绘制统一风格的矢量场景

内置 24 个统一手绘物件在 `scripts/motifs.py`：`pencil, sprout, flower, boat, cloud, sun, hill, butterfly, bird, tree, moon, star, book, kite, lighthouse, shell, gift, balloon, house, rocket, lantern, heart, leaf, wave`。

**新主题禁止机械套春天的三幕。** 如果主题是狐狸/猫咪/火车/咖啡馆，内置物件无法准确表达时，应主动创作原生 SVG `customMotifs`；支持 `{{ink}}`、`{{sage}}`、`{{orange}}`、`{{rose}}`、`{{sky}}`、`{{light}}`、`{{paper}}`、`{{cue}}` 占位符。在局部 200 × 200 坐标作画，让需要连接的根部/接触点精确落在 `anchorLocal`。参考 `references/vector-art.md`。图形复杂度对照 `examples/1024/story.json` 里的 `customMotifs`（笔记本电脑、芯片、机柜、火箭都是按主题画的，不是从 24 个内置物件里换标题）。

不可因图层画得复杂就把整幅构图换成 PNG，也不要在画布内塞画师提示词或无法运行的图像链接。

### 3. 决定是否需要透明 GIF 局部动画

- 故事主角、路径和形体由 SVG 制作，**优先尝试 SMIL 局部动作**。只有当连续细碎动作需要逐帧（比如花瓣飘落、蝶翼闪动、露珠细闪）时，才做 1–2 个小型透明 GIF。没有合适场景就不加。
- GIF 须是本地 `.gif` 文件，文件路径相对于 `story.json`（即放在 `stories/<slug>/assets/`）；像素尺寸通常 160×110 左右，2–4 秒，使用本篇选定色板和透明背景。优先只播放一次，不要整幕 GIF 背景。
- 若需要生成 GIF，可使用 `"$SKILL/scripts/make_decor_gif.py"`（需 Pillow）制作 `sparkles/petals/ripples/flutter` 原生线描帧；遇到独特主题须自行设计匹配剧情的逐帧动画，而非给所有题材套花瓣。Pillow 缺失且用户不想安装时，直接放弃 GIF、用 SMIL 完成。
- `chapters[].gifDecorations` 的 `trigger:{"hit":"..."}` 自动绑定主线到达时刻，`attachTo` 将 GIF 位置绑定到某个 SVG 物件锚点；平台限制详见 `references/gif-decoration.md`。

### 4. 输出可编译故事数据

- 可先用 `plan_story.py` 从主题生成合法 JSON 底稿，然后**务必以 Agent 创作能力重新设计人物、物件、情节、线的隐喻和分镜**。该命令是**离线主题词模板**，词库未命中时会退回春天三幕主角；非春天主题的底稿**不会再塞铅笔开场**。它仍然不是可以真正理解任意主题的 AI 模型，开场物件也只是占位，交付前必须改成这篇自己的起源。
- 生成 `stories/<slug>/story.json`，对照 `templates/story.schema.json` 和 `examples/spring/story.json`。
- 每个章节独立定义 `start`, `duration`, `role`, `emphasis`, `motion`, `labelAt`, `headline`, `captionAt`, `caption`, `route`, `objects`。`route` 里至少两个 `hit`。
- 对象 `reveal:"touch"` 时，编译器按路径弧长自动推导入场时间；对象 `leadSeconds` 可设 0–0.4 让它在触碰之前先微微出现。
- `route` 至少 4–7 个有意义的 waypoint，给足呼吸空间；物体应在其所代表的故事节点附近，避免路径压过文字。默认 `pathTension:0.96`，可在 0.7–1.2 之间微调。

**关键 API 契约**：route 中写 `{"hit":"sprout"}` 不是泛指「画一条经过植物的线」，而是通过对象 `x,y,scale,anchorLocal` 精确决定该点，永不手写一个大致坐标去猜。

### 5. 编译

```bash
OUT=stories/forest-letter

python3 "$SKILL/scripts/validate_story.py" --input "$OUT/story.json"
python3 "$SKILL/scripts/compile_story.py" --input "$OUT/story.json" --output "$OUT/dist"
```

校验失败或故事数据不合法时，命令非 0 退出，并且不会留下可用的成品页。

`validate_story.py` 的 `WARN` 不会让命令失败，但下面几类要当成待办处理，改完重跑，直到清零：「只有 N 个物件」「没有小注释」「主角只有 N 个图形」「名字是…画出来却是…」「偏空」「离主线只有 N 设计单位」。确实要保留某一条时，在交付回复里写明是哪条、为什么。不要为了消警告去堆和故事无关的物件，补的东西从素材清单里来。

最终有 `$OUT/dist/index.html`（直接离线打开）、`story.svg`（主场景全部可编辑 SVG，装饰 GIF 以 `<image>` 嵌入）、`cues.json`（路径长度、触发时刻、锚点、撑高表）、`STORYBOARD.md`（分镜）以及源数据 `story.json`。

生成器只依赖 Python 标准库。普通 HTML 所需 CSS/JS/GIF 字节全部内联，无网络依赖。**核心动图由 SVG 的 SMIL 实现**；浏览器中的 GIF 仅作为局部点缀，由少量 JS 在 cue 时新建 Blob 解码器，确保不会提前在画面外播放结束。GIF 在暂停/seek 时只能重新从第一帧启动，不能做帧级同步。

### 6. 渲染、检查、修正（不能只看编译成功）

**A. 有 Playwright 时**（`.venv/bin/python` 或系统 python 能 import playwright）：

```bash
python3 "$SKILL/tests/browser_smoke.py" "$OUT/dist/index.html" "$OUT/dist/preview.png"
# 启用了 GIF 时：
python3 "$SKILL/tests/browser_gif_smoke.py" "$OUT/dist/index.html" "$OUT/dist/gif-preview.png"
```

前者用 440px 手机和桌面视口测 0s / 6s / 12s / 18s / 26s / 末尾的页面高度与横向滚动；后者验证 GIF 在 cue 前未加载、cue 后显示、结束卸载、seek/重播创建新解码器。

**B. 没有 Playwright、但当前 Agent 能打开网页并截图时**：

用本地页面做同一套检查。部分内置浏览器拒绝 `file://`，那时先在工作区根目录启动静态服务：

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8765/stories/<slug>/dist/index.html`。若当前浏览器允许直接打开本地文件，也可以打开 `stories/<slug>/dist/index.html`。

1. 视口尽量接近宽 440px、高约 1400px、缩放为 1。不要开启会额外放大画面的移动设备模拟，以免截图错位。截图必须覆盖画面本身；若工具只能截到很窄的面板，改用能输出完整视口位图的方式，再读这张图。长页分段滚动截取，不要用超高视口一次性截整卷，以免首屏被重复平铺。
2. 页面默认正在播放，且自动跟随开启。系统开了「减少动态效果」时例外：时间停在结尾，画面和页高已经到位，自动跟随关闭，`#btn-play` 显示「▶ 从头播放」。这时不要为了暂停去点它，点下去会从头播放。其余情况先隐藏控件、暂停、关闭跟随，再截图，避免控件挡画面、页面自己滚走。在页面中执行前先看按钮文案：`#btn-play` 显示「Ⅱ 暂停」时点击会暂停；`#btn-follow` 显示「◉ 自动跟随」时点击会关闭跟随。二者都是开关，已经处于目标状态时不要再点一次。

   ```js
   document.querySelectorAll('.dock-slot,.dock,.dock-peek,.topbar').forEach(el => { el.style.display = 'none'; });
   ```

3. 在 0 秒、每幕入口、每个触碰时刻（见 `cues.json`）和结尾各截一张图。拖动时间轴：

   ```js
   (t => { const s = document.getElementById('seek');
     s.value = t; s.dispatchEvent(new Event('input')); })(12)
   ```

   自动跟随仍开启时，页面会滚到笔尖处。
4. 读取 `document.documentElement.scrollWidth <= window.innerWidth`，确认没有横向滚动；读取 `document.getElementById('stage').getBoundingClientRect().height`，确认高度随时间单调增长。
5. 点击「⊹ 锚点」按钮（`#btn-debug`）再截一张图。红十字必须落在真正的图形接触点上。数学坐标为 0 误差，不代表美术轮廓已经对齐。
6. 检查结束后停止静态服务。

逐项看图：（a）笔触一致，（b）主线路线自然，并且落在物件的可见笔画上，没有横穿图形或文字，（c）触碰点可见、准确，（d）文案没有被线条压住，（e）对象不越界，（f）结束时结尾完整出现，（g）没有横向滚动，（h）生长的茎、河、轨是一根线，不是叠出来的几段，（i）每幕数得出 1 个主角、3 个以上辅助物件、4 个以上点缀小件和至少 1 处小注释，（j）没有哪一屏只剩主线和一两个小物件。

（i）（j）不满足时先补内容再交付：在空段放素材清单里还没用上的细节，或给主角加地面投影、配件和小注释，不要靠放大已有物件或拉长主线来填。

- 如有冲突先改 `objects` 布局，再改 `route` waypoint，重跑编译器和 QA。不要通过随意改 cue 秒数掩盖空间错位。
- Playwright 和浏览器都不可用时，至少跑 `validate_story.py` 和标准库单元测试（`python3 -m unittest discover -s "$SKILL/tests" -p 'test_*.py'`）。报告哪些环节没有亲眼看过，不许虚构截图或真机通过。

### 7. 交付浏览器页面

交付 `index.html`。它是 SVG/SMIL 作品，加上少量 JS 控件与自动跟随；若有 GIF，JS 在指定 cue 创建新的 Blob URL，离线可运行。

带 `paletteName` 的作品不要再跑 `theme_map.py`。`motifs.materials()` 已按色板从源头配出材料色。只有 `paletteName` 缺省的老作品才用 `theme_map.py` 兜底，否则暗色纸底会被误判成 ink 家族。

`story.svg` 单独打开时，GIF 会提前内嵌，SMIL 只控制可见时间，不保证从第一帧开始。浏览器页 `index.html` 才按 cue 新建解码。

### 8. 交付与解释

文件已在用户本机工作区，**不需要打包 ZIP**（用户要求时再用 `zip -r` 打包）。在回复中：

- 用 markdown 链接列出 `stories/<slug>/dist/index.html`、`story.json`、`STORYBOARD.md`。提示用系统浏览器打开 `stories/<slug>/dist/index.html`（macOS 可用 `open`）。
- 用一张真实预览图说明画面（来自 Playwright 或第 6 步 B 的截图，路径指向实际生成的 PNG）。没有截图就明说没有。
- 用一小段说明这一版的主题转译、路径隐喻、场景与关键触发时刻，并列出已验证和未验证的环节。

## 重要例子：从一个主题到一条不断生长的线

主题「海边的一封信」：第一幕从信封的折线起笔，第二幕折线成为海面波纹，第三幕波纹延伸到灯塔光束。三个具体可视锚点分别是信封尖角、纸船水线和灯塔底座；各幕使用 2–3 种平涂色，线条坐标被编译器精确固定。不得直接把「种子→花→纸船」改个标题就交付，也不得把样例里的铅笔画成每篇的第一件道具。

## 读这些文件（按任务需要）

路径都相对本 `SKILL.md` 所在目录：

- `references/story-design.md`：故事节拍、隐喻、分镜与场景坐标。
- `scripts/palettes.py`：色板。每套含纸色、角色色、动作幅度和收笔。用户给主题后先运行 `--suggest`。
- `scripts/arcs.py`：叙事弧。和色板、分镜一起放进开工前的故事计划，等用户确认。
- `references/vector-art.md`：V1 美术语法、自定义 SVG 物件、锚点、局部 SMIL，以及线要落地、一根路径生长、错峰和缓入。
- `references/gif-decoration.md`：透明 GIF 的艺术边界、story.json 数据、生成、触发、循环和平台局限。
- `references/timing-and-growth.md`：样条路径、长度同步、页面伸长机制。
- `references/platform-and-qa.md`：浏览器检测与输出验收。
- `examples/spring/story.json`：32 秒三幕真实示例，只含 SVG 坐标。GIF 字段写法见 `references/gif-decoration.md`。
- `examples/1024/story.json`：程序员节长卷。看一幕里的物件数量和 `customMotifs` 的画法。13 幕、146 秒是这篇主题的长度，不是新故事的默认值。

**禁止结果**：用户还没确认故事计划就写 `story.json`、编译或打开预览；用户已确认之后仍然只有故事方案、没有可运行 HTML；用 GIF 代替主角或整幕场景；GIF 和 SVG 风格明显冲突；大面积不统一水彩贴图；线条与物件只是靠近却没连接；场景接线跳跃；整屏只有主线和一两个小物件；物件名字和画出来的东西对不上（`butterfly` 画成鸟、`wild-flowers` 画成星星）；把模板化预设说成通用 AI 生成；无主题依据却用铅笔开场；把作品或 `.gif` / `.png` / `.zip` 写进 Skill 目录。
