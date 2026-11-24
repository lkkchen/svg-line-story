# Vector art rules · a pure SVG body, a transparent GIF only as a detail

## The style anchor

What V1 looks like: the paper feeling comes from the ground color and the open space, not from a noise texture. Outlines use one line color. Flat fills use only a few role colors. Local curves are slightly irregular, and line caps are round. Drawings take a small part of the canvas. Type has room to breathe.

The palette is not locked to Spring. Each set in `scripts/palettes.py` provides a paper color and 6 role colors. The original Spring colors are `ink #375763`, `sage #98B99F`, `orange #D68E5C`, `rose #F0C5B6`, `sky #E5EDEA`, `light #E5ECE2`, and `paper #FCFAF4`. Use them only when the user chooses `spring`. Wood, petals, sails, and other material colors on built-in objects follow the current palette. The role names stay. `sage` is still the second fill. `orange` is still the accent.

## Making an object

By default use the 24 vector drawings in `scripts/motifs.py`. Each is drawn in a local 200 × 200. The default anchor is `[100,180]`: the visible body must actually touch that coordinate. Do not leave an invisible empty anchor.

When you need a new object (a fox, a violin, a train, a coffee machine), add it to `story.json`:

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

The chapter object:

```json
{"id":"letter","motif":"paper-letter","x":310,"y":990,"scale":1,"reveal":"touch","leadSeconds":0.15}
```

The main-line waypoint:

```json
{"hit":"letter"}
```

The canvas coordinate of the contact becomes `(410,1170)` automatically. You do not measure an approximate point on the path by hand.

A custom SVG may use `<g>`, `<path>`, `<circle>`, `<ellipse>`, `<rect>`, `<line>`, `<polyline>`, `<polygon>`, `<text>`, `<tspan>`, and a little SMIL. The outer `<g>` of an object defaults to a `palette.ink` stroke. `<text>` must set `stroke="none"` and an explicit `font-family`, or the letters get a thick stroke. The text must not contain `&`. Forbidden: `<image>`, `<script>`, `<foreignObject>`, external links, and CSS `url(...)`. The compiler replaces `{{ink}}`, `{{sage}}`, `{{orange}}`, `{{rose}}`, `{{sky}}`, `{{light}}`, and `{{paper}}` with the chosen palette. `{{cue}}` becomes the moment the path touches this drawing. `{{cue+0.25}}` and `{{cue-0.3}}` are offsets, used to stagger motion. Staggering is in "Offset the parts of one object" below.

## Small annotations and ornaments

The compiler has no separate annotation type. Write one as `customMotifs`. The object does not go into `route`. Set `reveal` to a number of seconds (usually the nearby hero's touch plus 0.3–0.8 seconds).

A small annotation: one line of type around size 16–20, with a short arrow or a leader pointing at the object it explains. `<text>` sets `stroke="none"` and `font-family`.

```json
"note-1946": {
  "svg": "<text x=\"10\" y=\"40\" font-size=\"18\" font-family=\"Menlo, Consolas, monospace\" fill=\"{{sage}}\" stroke=\"none\" letter-spacing=\"2\">1946 · ENIAC</text><path d=\"M14 52q40 14 76 4\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"1.4\" stroke-dasharray=\"3 5\"/><path d=\"M84 50l8 5-9 4\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"1.4\"/>"
}
```

A small ornament: a group of grass, star dots, scraps, or a shadow, written as one motif, `scale` 0.4–0.8, placed 40–120 design units to the side of the main line, `z:"back"`.

```json
"grass-tufts": {
  "svg": "<path d=\"M20 180q4-18 10-24M30 180q2-14-4-22M40 180q6-12 14-16\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"2\"/><path d=\"M120 180q4-14 10-20M130 180q3-12-3-18\" fill=\"none\" stroke=\"{{sage}}\" stroke-width=\"2\"/><circle cx=\"80\" cy=\"176\" r=\"3\" fill=\"{{orange}}\" stroke=\"none\"/>"
}
```

A ground shadow goes in the bottom layer of the hero's motif: `<ellipse cx="100" cy="182" rx="46" ry="7" fill="{{light}}" stroke="none"/>`.

## Four named motions

The whole scroll uses only these four. Neighboring heroes each take one. The last chapter is `still`. When the palette is `motion: punchy`, a pop is 0.7 seconds. When it is `calm`, a pop is 1.2 seconds. The overshoot stops at 1.08 and returns to 1.

- `draw`: one path uses `stroke-dashoffset` from the full length down to 0. The root is there first. The tip arrives later. The main line stays constant speed. Do not put a spline on the main line.
- `pop`: `animateTransform`, `type="scale"`, `values="0.2;1.08;1"`, `keyTimes="0;0.72;1"`, `calcMode="spline"`, `keySplines="0.45 0 0.2 1; 0.25 0 0.35 1"`, `fill="freeze"`. The first stretch eases in to 1.08. The second settles back to 1.
- `sway`: `rotate` around the anchor, `values="-4;3;-1;0"`, `keyTimes="0;0.34;0.67;1"`, `calcMode="spline"`, `keySplines="0.4 0 0.2 1; 0.3 0 0.3 1; 0.2 0 0.25 1"`. Play once and stop. Do not loop forever.
- `still`: only an opacity fade. No move, no scale, no rotation. The line's arrival is the motion of this beat.

Both `pop` and `sway` need `restart="never"`. A jump from 0 to 1 in one frame is not a pop. The ease-in lives in the first stretch, a start on the order of 80 milliseconds, not an extra held still.

Built-in objects already carry their own motion. See `MOTIF_MOTION`. To change it, write `customMotifs` and set `"motion"` on the object. A sprout's second leaf is 0.4 seconds after the stem. Flowers and boats use the splines above for scale and sway.

## The line has to land

These rules govern how a custom object and the main line meet, grow, and stack. Do not turn this into an even instrument diagram, and do not add shading on all four sides.

- **The line stops on the real stroke.** The anchor lands on a visible outline, a root, or a corner. A seam, a tick, a vein, or a hand stops on another stroke, a dot, or the outer contour. A decorative line does not stop suddenly in the middle of a color block.
- **Contact is a touch or a tangent.** A vine stops on the boat's waterline. The line grows out of the corner of an envelope. The next stretch leaves from the same anchor. The path does not cut through a hull, a roof, or type. The compiler guarantees a coordinate error of 0. Anchor debug is how you confirm the strokes meet too.
- **Growth is one path.** A stem, a river, a rail, or the line that ties the ties is one path. `stroke-dasharray` and the initial `stroke-dashoffset` both equal that path's length, then animate to 0. Do not fake growth with several overlapping lines. The seam shows while it moves.
- **One chapter has one "this is happening now."** The orange traveling dot is the tip of the timeline. It is the only thing in the scroll that says where the head of the line is. The hero fill uses that chapter's `emphasis`. Supporting objects fall back to `light` / `sky`. Do not add another moving highlight to a supporting object. An object may keep one still orange dot. Do not add a second dot that runs along the path.
- **Far is underneath, near is on top.** The compile order is `z:"back"`, the main line, then the default `front`. Hills, clouds, and the river surface use `"z":"back"` so the line passes in front of them. A boat, a person, and a letter stay the default `front` and cover the end of the line. Inside one layer, later items in the `objects` array cover earlier ones. Do not change stacking while the piece is playing.

## Offset the parts of one object

A root, a hull, or a lamp base uses `begin="{{cue}}"`. A leaf, a sail, or a beam is another 0.15–0.4 seconds later (`{{cue+0.25}}` and the like). Every stretch is `fill="freeze"` and stops in its finished state. Do not space them more than 0.6 seconds apart, or the beat falls apart. The load-bearing part comes first. The part that grows comes after.

```xml
<animateTransform attributeName="transform" type="scale"
  values="0.2;1.08;1" keyTimes="0;0.72;1"
  calcMode="spline" keySplines="0.45 0 0.2 1; 0.25 0 0.35 1"
  begin="{{cue+0.25}}" dur="1.2s" fill="freeze" restart="never"/>
```

`calcMode` and `keySplines` go on `<animate>` / `<animateTransform>`. They do not depend on `<style>`.

## A local motion beats swapping the whole picture

A flower: the petals are one `<g>` around the center and scale once. The root stays still. A seed: the stem stroke uses `stroke-dashoffset`, and the leaves open as a group. A paper boat: the hull rotates a few degrees, and the river ripples are a `path`. Important motion is SMIL. If a local petal, glint, or wing truly needs frames, you may add a **small transparent GIF accent**. It cannot replace the vector geometry of the flower, the boat, or the person. See `gif-decoration.md`.

A custom drawing has layers. It does not get "beautiful" by piling messy lines. These are the floors:

- **Hero**: at least 8 shapes and more than 3 fills (the main color, a lighter second color, a little accent), plus one detail line (a fold, wood grain, a key, a tick) and a ground shadow or a base. A person needs a face (eyes, a mouth, or a blush) and something in the hands.
- **Supporting object**: at least 4 shapes and 2 fills.
- **Small ornament**: 1–3 shapes is enough, but they appear as a group (three tufts of grass, a string of star dots, two or three scraps of paper).

Stroke width has three steps and stays consistent through the scroll: outer contour 3–3.5, inner structure 2–2.5, detail 1.2–1.6. Do not make every line the same weight, and do not use a stroke of 5 or more (except the main line). For stroke weight, look at `examples/spring/dist/story.svg`.
