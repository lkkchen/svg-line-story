# 矢量美术规范 · V1 主体纯 SVG，透明 GIF 仅作细节

## 风格锚定

V1 参考特点：纸张感来自底色与留白，而不是噪声纹理；轮廓用同一支线色；平涂只用少量角色色；局部有手绘不规则曲率与圆头线帽。图形占画布小面积，文本排版呼吸感强。

色板不固定成春笺。`scripts/palettes.py` 里每套都提供纸色和 6 个角色色。春笺原色是 `ink #375763`、`sage #98B99F`、`orange #D68E5C`、`rose #F0C5B6`、`sky #E5EDEA`、`light #E5ECE2`、`paper #FCFAF4`，只在用户选定 `spring` 时使用。内置物件的木材、花瓣、船帆等材料色会跟着当前色板走；角色名不变，`sage` 仍是第二填充，`orange` 仍是点缀。

## 制作物件

默认使用 `scripts/motifs.py` 中 24 个矢量图形。每个在 200 × 200 局部坐标里创作，锚点默认 `[100,180]`：视觉形体必须真的触及该坐标，不能留一个看不见的空锚点。

如果需要新物件（狐狸、小提琴、火车、咖啡机等），给 `story.json` 新增：

```json
{
  "customMotifs": {
    "paper-letter": {
      "anchorLocal": [100, 180],
      "svg": "<path d=\"M35 85L100 180 165 85 165 155Q100 190 35 155Z\" fill=\"{{light}}\" stroke=\"{{ink}}\" stroke-width=\"3\"/>"
    }
  }
}
```

对应章节对象：

```json
{"id":"letter","motif":"paper-letter","x":310,"y":990,"scale":1,"reveal":"touch","leadSeconds":0.15}
```

对应主线 waypoint：

```json
{"hit":"letter"}
```

对象接触点的画布绝对坐标自动变为 `(410,1170)`，不会再手动测算路径的近似位置。

支持自定义 SVG 的 `<g>`, `<path>`, `<circle>`, `<ellipse>`, `<rect>`, `<line>`, `<polyline>`, `<polygon>`, `<text>`, `<tspan>`，以及少量 SMIL 元素。物件外层 `<g>` 默认带 `palette.ink` 描边，`<text>` 必须写 `stroke="none"` 并显式给 `font-family`，否则字会被描粗；文字内容不能含 `&`。禁止 `<image>`, `<script>`, `<foreignObject>`, 外部链接、CSS `url(...)`。占位符 `{{ink}}`, `{{sage}}`, `{{orange}}`, `{{rose}}`, `{{sky}}`, `{{light}}`, `{{paper}}` 由编译器替换为选定配色，`{{cue}}` 替换为该图形被路径触碰的触发时刻（`{{cue+0.25}}`、`{{cue-0.3}}` 表示相对偏移，用于错峰动作）。错峰见下面「同一物件里的零件错开」。

## 小注释和点缀小件

编译器没有单独的注释类型，用 `customMotifs` 写，对象不进 `route`，`reveal` 写一个秒数（通常是附近主角的触碰时刻加 0.3–0.8 秒）。

小注释：一行 16–20 号的小字，配一个短箭头或一条引线指向它说明的物件。`<text>` 写 `stroke="none"` 和 `font-family`。

```json
"note-1946": {
  "svg": "<text x=\"10\" y=\"40\" font-size=\"18\" font-family=\"Menlo, Consolas, monospace\" fill=\"{{sage}}\" stroke=\"none\" letter-spacing=\"2\">1946 · ENIAC</text><path d=\"M14 52q40 14 76 4\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"1.4\" stroke-dasharray=\"3 5\"/><path d=\"M84 50l8 5-9 4\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"1.4\"/>"
}
```

点缀小件：一组草丛、星点、碎纸或投影，写在同一个 motif 里，`scale` 0.4–0.8，放在主线两侧 40–120 设计单位外，`z:"back"`。

```json
"grass-tufts": {
  "svg": "<path d=\"M20 180q4-18 10-24M30 180q2-14-4-22M40 180q6-12 14-16\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"2\"/><path d=\"M120 180q4-14 10-20M130 180q3-12-3-18\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"2\"/><circle cx=\"80\" cy=\"176\" r=\"3\" fill=\"{{orange}}\" stroke=\"none\"/>"
}
```

地面投影直接写进主角的 motif 最底层：`<ellipse cx="100" cy="182" rx="46" ry="7" fill="{{light}}" stroke="none"/>`。

## 四种命名动作

全卷只使用这四种，相邻两幕的主角各用一种，最后一幕是 `still`。色板 `motion: punchy` 时弹出用 0.7 秒，`calm` 时用 1.2 秒。过冲停在 1.08 再回到 1。

- `draw`：一根路径用 `stroke-dashoffset` 从满长收到 0。根部先在，末端后到。主线保持匀速，不要给主线加样条。
- `pop`：`animateTransform`，`type="scale"`，`values="0.2;1.08;1"`，`keyTimes="0;0.72;1"`，`calcMode="spline"`，`keySplines="0.45 0 0.2 1; 0.25 0 0.35 1"`，`fill="freeze"`。前一段缓入到 1.08，后一段落回 1。
- `sway`：绕锚点 `rotate`，`values="-4;3;-1;0"`，`keyTimes="0;0.34;0.67;1"`，`calcMode="spline"`，`keySplines="0.4 0 0.2 1; 0.3 0 0.3 1; 0.2 0 0.25 1"`，只播一次然后停住。不要无限循环。
- `still`：只有透明度淡入，没有位移、缩放和旋转。线的到达就是这一拍的运动。

`pop` 和 `sway` 都要带 `restart="never"`。一帧从 0 跳到 1 不算弹出。缓入落在第一段里，大约 80 毫秒量级的起步，不是另加一段静止。

内置物件已经带好自己的那一种，见 `MOTIF_MOTION`。要换种，另写 `customMotifs`，并在对象上写 `"motion"`。芽的第二片叶比茎晚 0.4 秒。花和船的缩放、摇摆用上面的样条。

## 线要落地

这些规则管自定义物件和主线怎么接、怎么长、怎么叠。不要改成等距仪器，也不要加四面明暗。

- **线停在真正的那一笔上。** 锚点必须落在可见轮廓、根或尖角上。缝、刻度、叶脉、指针停在另一条描边、一个圆点或外轮廓上。装饰线不要在色块中间突然停住。
- **接触是贴住或相切。** 藤停在船的水线，线从信封尖角长出。下一段从同一个锚点离开。路径不要横穿船身、屋顶或文字。编译器保证坐标误差为 0；锚点调试用来确认笔画也接上了。
- **生长用一根路径。** 茎、河、轨、轨枕连线写成一条 path，`stroke-dasharray` 和初始 `stroke-dashoffset` 都等于这条路径的长度，再动画到 0。不要用几段重叠的线冒充变长，接缝会在运动里露出来。
- **同一幕只有一个「正在发生」。** 橙色行进点是时间轴笔尖，全卷只有它表示线头走到了哪里。主角填充用该幕 `emphasis`。配角退到 `light` / `sky`，不要再给配角加会动的高亮。物件上可以留一个静止的小橙点，不要再做第二个沿路径跑的点。
- **远的在下，近的在上。** 编译顺序是 `z:"back"`、主线、默认的 `front`。山、云、河面写 `"z":"back"`，让线从它们前面走过。船、人、信保持默认 `front`，盖住线的末端。同一层里，`objects` 数组后面的盖住前面的。播放过程中不要改层级。

## 同一物件里的零件错开

根、船体、灯座用 `begin="{{cue}}"`。叶、帆、光束再晚 0.15–0.4 秒（`{{cue+0.25}}` 这一类）。每一段都 `fill="freeze"`，停在终态。间隔不要超过 0.6 秒，否则这一拍会散。顺序是先承重的部分，后长出来的部分。

```xml
<animateTransform attributeName="transform" type="scale"
  values="0.2;1.08;1" keyTimes="0;0.72;1"
  calcMode="spline" keySplines="0.45 0 0.2 1; 0.25 0 0.35 1"
  begin="{{cue+0.25}}" dur="1.2s" fill="freeze" restart="never"/>
```

`calcMode` 和 `keySplines` 写在 `<animate>` / `<animateTransform>` 上，不依赖 `<style>`。

## 局部动作优先于整体换图

花朵：花瓣围绕花芯组 `<g>` 进行一次 `scale`，根部静止。种子：茎干描边使用 `stroke-dashoffset`，叶片分组展出。纸船：船身小角度 `rotate`，河面波纹用 `path`。关键动作均使用 SMIL；如局部花瓣、微光、翅膀细节确需逐帧效果，可添加**小型透明 GIF 装饰**，但不能替换这朵花、纸船或人物本身的矢量几何。详见 `gif-decoration.md`。

自定义图形要有层次，但不靠杂乱的线堆出「精美」。下面是下限：

- **主角**：至少 8 个图形、3 种以上填充（主色、浅一档的辅色、一点点缀色），外加一层细节线（衣褶、木纹、按键、刻度）和一个地面投影或底座。人物要画出脸（眼睛、嘴或腮红）和手里的东西。
- **辅助物件**：至少 4 个图形、2 种填充。
- **点缀小件**：1–3 个图形即可，但要成组出现（三簇草、一串星点、两三片碎纸）。

线宽分三档并全卷统一：外轮廓 3–3.5，内部结构线 2–2.5，细节线 1.2–1.6。不要所有线都一样粗，也不要出现 5 以上的粗线（主线除外）。参考 `examples/spring/dist/story.svg` 的笔触重量。
