# 路径、时间与网页逐段增高

## 一条路径，分段时间

各章节 `route` 都是一串 waypoint，点可以是 `[x,y]` 或 `{"hit":"object-id"}`。后者会从目标物件的 `x/y/scale/anchorLocal` 精确计算坐标，因此主线精确触碰物件，而不是「差不多穿过」。

相邻章节首尾 waypoint 必须坐标相等；构建程序把所有 waypoint 合成一组全局点，再使用 Catmull-Rom → cubic Bézier (`M`+`C`) 产生天然连续切线。章节边界会分成独立路径以便设置不同时长，但共享相同的连接切线。

## 入场时间不是凭经验写死

每段贝塞尔曲线分 48 步近似弧长并累计得到章节总长度 `L`。目标物件对应一个确切 waypoint，其沿线距离为 `s`，则线头抵达时间：

`t_arrive = chapter.start + chapter.duration × (s / L)`

物件开始可见的时刻：

`t_reveal = max(0, t_arrive - object.leadSeconds)`

程序在 `cues.json` 里输出抵达时刻、揭示时刻和锚点坐标。因为 waypoint 被直接替换成对象接点，几何误差理论上 0；但是如果对象的绘制图形未真正碰到 `anchorLocal`，仍有**视觉**连接错误，这需要打开锚点调试。

如果 line 需要在关键节点停下来 1–2 秒，则拆分章节或增加明确的等待段，不要仅调节元素的 `begin` 来掩饰。

主线描边保持匀速：`stroke-dashoffset` 从路径长度收到 0，时长等于该幕 `duration`。缓入只给物件的 `pop` 和 `sway`，不给这根故事线。物件零件的错峰、`calcMode="spline"` 和 `keySplines` 写在 `references/vector-art.md`。

## 浏览器版的减少动态

`index.html` 的控件会读 `prefers-reduced-motion: reduce`。命中时，故事 SVG 和撑高 SVG 都跳到结尾并暂停：线已经画完，物件停在终态，页面高度到位，自动跟随关掉。播放钮显示「▶ 从头播放」，点下去才从 0 秒开始播。描线本身不删。

## 可选 GIF 的触发与时间线关系

每个 `gifDecorations` 元素可以通过 `trigger:{"hit":"object-id"}` 绑定路径**实际**抵达该 SVG 物件接点的 `lineArrival`，而不是主物件提前淡入的 `revealAt`。GIF 的可见长度默认取其文件内各帧时长之和，循环 GIF 需写 `activeSeconds`。所有 GIF 自身都不会改变主线弧长、主线点位或页面伸长计划。页面以少量 JS 按 cue **新建** GIF 解码实例。详细见 `gif-decoration.md`。

## 为什么能「自动长高」

故事内容 SVG：完整 `viewBox="0 0 750 4050"`，放在高度为 0 的流布局容器。它始终在固定坐标中绘制，随容器底部逐渐露出画面。

辅助撑高 SVG：只有空白 `<svg width="120%" viewBox="0 0 750 180">`，采用 SMIL：

```xml
<animate attributeName="width" values="120%;245%" begin="0.1s" dur="2.3s" fill="freeze"/>
```

假设基底 SVG 高度为设计单位 `450`，辅助 SVG 的 `viewBox` 高 `180`，其显示高度随 width 百分比近似为：

`visibleHeight = 450 + widthPercent/100 × 180`

当 `widthPercent = 2000%` 时，恰好撑到 `4050`。编译器并不硬编码 `2000%`，而是根据设计画布高度、空 SVG 高度、主线线头的 Y 坐标、提前留白距离和片段时间自动计算 `grow` 分段，并保证最后露出整个画布。

注意：`<animate attributeName="width">` 触发布局依赖 SVG 的内在宽高比，不同浏览器可能表现不同。

## 浏览器页面

`index.html` 有小型控制 JS，但核心描线、插画动作、布局增长全由 SMIL 实现。

---

## 手工长图的三个补充手法

编译器（`compile_story.py`）用 `opacity` 淡入做揭示，这对「主角逐个出场」够用。
如果要做**手工拼装的长图**（比如复用已有素材帧、按秒放出整块画面），下面三个手法更合适，
它们来自 2026-10-13 那份约 4 分钟竖向长图的实测样本。

### 一、整块画面「瞬时到位」，不滑动

让一块画面在第 T 秒突然出现（而不是滑进来）：三层 `g` 叠加，
预先把它甩到画面外，到点用 `additive="sum"` 加一份反向位移抵消。

```html
<g transform="translate(0 Y)">            <!-- ① 定位到这段的顶边 -->
  <g>
    <animateTransform attributeName="transform" type="translate"
      values="2000 0" additive="sum" fill="freeze" begin="T" restart="never"/>  <!-- ② 到点补一份位移 -->
    <g transform="translate(-2000 0)">    <!-- ③ 预先甩到画面右侧 2000 外 -->
      <foreignObject width="750" height="H">
        <svg viewBox="0 0 750 H"
          style="width:100%;background-size:100% 100%;background-repeat:no-repeat;
                 background-image:url(素材/N.gif)"></svg>
      </foreignObject>
    </g>
  </g>
</g>
```

- **`values` 只有一个值、且没有 `dur`** = 到了 `begin` 就瞬间到位，中间没有过渡
- `fill="freeze"` 停在最后一帧；`restart="never"` 只触发一次
- 素材不写 `<image>`：空 `<svg>` 用 `background-image` 铺满，内层 `viewBox` 高 = `foreignObject` 高
- 需要淡入再补一条 `animate opacity values="0;1"`，`begin` 与到位同秒
- 分章不从 0 重算：父级 `translate(0 章节起点)`，子级写相对 Y，绝对位置 = 各级 translate 相加

### 二、曲线串场：描边，不是蒙版

```html
<g transform="translate(X Y)" stroke-dasharray="L" stroke-dashoffset="L">
  <animate attributeName="stroke-dashoffset" to="0"
    dur="D" begin="T" fill="freeze" restart="never"/>
  <path fill="none" stroke="#015eb7" stroke-miterlimit="10" d="..."/>
</g>
```

- `L` = 路径实际长度；虚线段长、间隙、初偏移全写成 `L` → 一开始什么都看不见
- 偏移量动画到 `0`，线就从起点画到终点
- **一章一条线**：`begin` 对准该章第一块画面，`dur` 覆盖这一章主要时长
- 别用蒙版（`mask` / `clipPath`）做这个效果，描边动画更稳

### 三、GIF 什么时候开始播

SMIL 只负责把图**移进**画板；GIF 是**进入浏览器视口后才开始播，且从第 0 帧起**。

所以即使 SMIL 时间轴已经走过，滑到时 GIF 仍从头播 —— 上面「预先甩到画面外」的写法
正是为了对齐这次「首次可见」。这也是为什么暂停/跳转后只保证重新开始，
**做不到 GIF 帧级 seek**。

同一坐标叠两张换画（比如旧图收掉、新图接上）：旧图用
`opacity` 的 `values="1;0" dur="0.001"` 在第 T 秒收掉，新图提前 2 秒进，
重叠期让观众看不见接缝。
