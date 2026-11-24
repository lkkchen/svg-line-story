# Path, time, and a page that grows in sections

## One path, time split into sections

Each chapter's `route` is a string of waypoints. A point is `[x,y]` or `{"hit":"object-id"}`. The second form computes the coordinate from the object's `x` / `y` / `scale` / `anchorLocal`, so the main line touches the object exactly instead of "roughly passing through."

The last waypoint of one chapter and the first of the next must share a coordinate. The builder joins every waypoint into one global set, then uses Catmull-Rom → cubic Bézier (`M` + `C`) so the tangent stays continuous. Chapter boundaries become separate paths so they can have different durations, but they share the joining tangent.

## Entrance time is not a number you invent

Each Bézier is sampled in 48 steps. The arc lengths add up to the chapter length `L`. The target object is one exact waypoint. Its distance along the line is `s`. The tip arrives at:

`t_arrive = chapter.start + chapter.duration × (s / L)`

The object becomes visible at:

`t_reveal = max(0, t_arrive - object.leadSeconds)`

The program writes the arrival, the reveal, and the anchor into `cues.json`. Because the waypoint is replaced by the object's contact, the geometric error is 0 in theory. If the drawn shape does not actually touch `anchorLocal`, there is still a **visual** miss. That is what the anchor debug view is for.

If the line needs to hold at a key beat for 1–2 seconds, split the chapter or add an explicit wait. Do not hide it by only editing an element's `begin`.

The main-line stroke stays constant speed: `stroke-dashoffset` goes from the path length to 0, over that chapter's `duration`. Easing is only for an object's `pop` and `sway`, not for this story line. Offsets between parts, `calcMode="spline"`, and `keySplines` are written in `references/vector-art.md`.

## Reduced motion in the browser

The controls in `index.html` read `prefers-reduced-motion: reduce`. When it matches, the story SVG and the grow SVG jump to the end and pause: the line is drawn, objects sit in their finished state, the page height is there, and follow is off. The play button says "▶ Play from the start." A click is what starts playback from 0. The stroke itself is not removed.

## How an optional GIF relates to the timeline

Each `gifDecorations` item can bind `trigger:{"hit":"object-id"}` to the `lineArrival` when the path **actually** reaches that SVG contact, not to the main object's early fade-in `revealAt`. A GIF's visible length defaults to the sum of its frame durations. A looping GIF needs `activeSeconds`. No GIF changes the main line's arc length, its points, or the page-growth plan. The page uses a little JavaScript to **create** a GIF decoder at the cue. Details are in `gif-decoration.md`.

## Why it can "grow by itself"

The story SVG: a full `viewBox="0 0 750 4050"`, inside a flow container whose height is 0. It always draws in fixed coordinates. The picture is revealed as the bottom of the container moves down.

The helper grow SVG: only an empty `<svg width="120%" viewBox="0 0 750 180">`, with SMIL:

```xml
<animate attributeName="width" values="120%;245%" begin="0.1s" dur="2.3s" fill="freeze"/>
```

If the base SVG height is `450` design units and the helper SVG's `viewBox` height is `180`, the displayed height is approximately:

`visibleHeight = 450 + widthPercent/100 × 180`

At `widthPercent = 2000%` that reaches exactly `4050`. The compiler does not hard-code `2000%`. It computes the `grow` segments from the design canvas height, the empty SVG's height, the Y of the line tip, the lead space, and the segment times, and it makes sure the whole canvas is revealed at the end.

Note: `<animate attributeName="width">` drives layout through the SVG's intrinsic aspect ratio. Browsers can differ.

## The browser page

`index.html` has a small control script, but the core stroke, the drawing motion, and the layout growth are all SMIL.

---

## Three extra moves for a hand-built long picture

The compiler (`compile_story.py`) reveals with an `opacity` fade. That is enough for "heroes enter one by one."
If you are building a **hand-assembled long picture** (reusing existing frames, releasing a whole block on a given second), the three moves below fit better.
They come from a measured sample of a roughly 4-minute vertical picture on 2026-10-13.

### 1. A whole block "arrives at once," without sliding

To make a block appear suddenly at second T (instead of sliding in): stack three `g` elements,
park it offscreen ahead of time, and at the cue add an opposite translation with `additive="sum"` that cancels the park.

```html
<g transform="translate(0 Y)">            <!-- 1. place this section's top edge -->
  <g>
    <animateTransform attributeName="transform" type="translate"
      values="2000 0" additive="sum" fill="freeze" begin="T" restart="never"/>  <!-- 2. add a translation at the cue -->
    <g transform="translate(-2000 0)">    <!-- 3. park it 2000 to the right, offscreen -->
      <foreignObject width="750" height="H">
        <svg viewBox="0 0 750 H"
          style="width:100%;background-size:100% 100%;background-repeat:no-repeat;
                 background-image:url(asset/N.gif)"></svg>
      </foreignObject>
    </g>
  </g>
</g>
```

- **One `values` entry and no `dur`** means it arrives the instant `begin` hits. There is no in-between.
- `fill="freeze"` holds the last frame. `restart="never"` fires once.
- Do not write the asset as `<image>`. An empty `<svg>` fills with `background-image`. The inner `viewBox` height equals the `foreignObject` height.
- If you also want a fade, add `animate opacity values="0;1"` with the same `begin` as the arrival.
- Chapters do not renumber from 0. The parent is `translate(0 chapter-start)`. Children use a relative Y. The absolute position is the sum of the translations.

### 2. A curve between scenes: a stroke, not a mask

```html
<g transform="translate(X Y)" stroke-dasharray="L" stroke-dashoffset="L">
  <animate attributeName="stroke-dashoffset" to="0"
    dur="D" begin="T" fill="freeze" restart="never"/>
  <path fill="none" stroke="#015eb7" stroke-miterlimit="10" d="..."/>
</g>
```

- `L` is the path's real length. The dash, the gap, and the initial offset are all `L`, so nothing is visible at the start.
- Animate the offset to `0` and the line draws from the start to the end.
- **One line per chapter**: `begin` lines up with that chapter's first block, and `dur` covers the chapter's main duration.
- Do not use a mask (`mask` / `clipPath`) for this. A stroke animation is steadier.

### 3. When a GIF starts playing

SMIL only **moves** the picture onto the board. A GIF **starts when it enters the browser viewport, from frame 0**.

So even if the SMIL timeline has already passed, the GIF plays from the start when you scroll to it. Parking it offscreen, above, is how that "first time it is visible" lines up. That is also why a pause or a seek only guarantees a restart. **Frame-accurate GIF seeking is not available.**

To swap two pictures on the same coordinate (the old one leaves, the new one takes over): fade the old one with `opacity` `values="1;0" dur="0.001"` at second T. Bring the new one in 2 seconds early. During the overlap the viewer should not see the join.
