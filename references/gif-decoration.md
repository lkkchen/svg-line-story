# Local GIF accents · v1.1

## What they are for

**V1 is still a hand-drawn SVG story. A GIF is only an optional, small, short decoration.** The best GIF makes a drawing stir. With the GIF turned off, the story is still complete and readable.

- **SVG + SMIL must do these**: the story line and curve motion, the hero outline, transitions, canvas growth, important plot triggers, and the words of the piece.
- **A GIF may add**: a butterfly wing, a few falling petals, a glint of dew, ripples beside a paper boat, a small lamp flickering, a leaf shifting.
- **Do not use a GIF for**: a whole drawing or a whole-chapter background, a paste-up with a large white or watercolor ground, any transition that must sync to an exact frame, or a frame that carries essential type or a call to action.
- Aim for 0–2 per chapter, never more than 3. About 160 × 110 pixels, a transparent ground, 2–4 seconds, a light file (typically 20–100 KB). One may loop if it must, but it needs a clear end time.
- The line color comes from this piece's `palette.ink`. Decoration uses only the matching `sage`, `rose`, `orange`, and so on. Stay away from large gradients, watercolor, photographs, and hard rectangular frames.

## How to make a new GIF

Finish the storyboard, the main SVG objects, and the continuous path first. Then decide which local detail deserves a GIF. The art should be a hand-drawn shape that matches the scene. Draw keyframes by hand, paint frames with Pillow, or generate frames and correct them one by one. **Do not generate a GIF just to raise the count.**

The repo has an optional Pillow tool for small transparent line-drawn animations:

```bash
# $SKILL = the absolute path of the directory that contains this skill's SKILL.md
# If Pillow is missing: after the user agrees, python3 -m venv .venv && .venv/bin/pip install pillow, then run with .venv/bin/python
OUT=stories/<slug>
python3 "$SKILL/scripts/make_decor_gif.py" --kind sparkles --palette sea --output "$OUT/assets/sparkles.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind petals   --palette sea --output "$OUT/assets/petals.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind ripples  --palette sea --output "$OUT/assets/ripples.gif"
python3 "$SKILL/scripts/make_decor_gif.py" --kind flutter  --palette sea --output "$OUT/assets/butterfly.gif"
```

It accepts `--frames`, `--frame-ms`, `--width`, `--height`, `--playback once|loop`, and `--palette` (a palette id or English name, matching `paletteName` in `story.json`. Omit it for Spring). This is a basic shape generator. It does not understand a theme. A character or object of its own needs frames the agent designs. The GIF uses the chosen palette and a transparent channel. Do not slice a screenshot of the whole scene into a GIF.

## A story.json example

Declare it in that chapter's `gifDecorations` list:

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

- `attachTo`: bind an SVG object's anchor that is already drawn. Position = `anchor` + `offset`. If the object moves, the accent follows.
- `x, y`: an absolute design coordinate is also allowed. Do not use it together with `attachTo`. The generator does not infer an anchor from the GIF's pixels.
- `trigger`: an absolute second such as `12.6`, or `{ "hit": "blossom" }`. The hit form uses the time the main line **actually reaches that object's anchor**, not the early fade-in `leadSeconds`.
- `offsetSeconds`: a nudge from the path-hit time. It may be negative. The compiler rejects an accent that falls outside the story's duration.
- `playback:once`: the GIF must **not** have a loop extension. The compiler reads the frame durations and, by default, plays one natural cycle and then leaves. `activeSeconds` can set the visible window.
- `playback:loop`: the GIF must have an **infinite loop extension**, and you must set `activeSeconds`, so it does not stay on screen forever.
- `z:front|back`: whether the accent sits in front of or behind the main line.
- `fadeInSeconds`, `fadeOutSeconds`: an SMIL opacity ramp on the SVG `<g>`. It is a separate timeline from the GIF's own frames.
- `src`: a local relative `.gif` under the directory that contains `story.json`. Not a remote URL, not an absolute path, not a `../` escape. A full export copies the GIF as an editable asset. HTML and SVG embed the bytes.

## How the generator stays in sync

The compiler computes `lineArrival` from the path's arc length, then each GIF's `begin`. **It does not fake a GIF trigger with CSS opacity.**

### The ordinary browser `index.html`

- The HTML inlines the GIF bytes. There is no remote request. Double-click it and it runs offline.
- The GIF `<image>` starts without `href`. When the animation reaches the cue, browser JavaScript builds a new Blob URL from those bytes and attaches it to the SVG `<image>`, so a new decoder starts. It does not reveal a GIF that already finished playing.
- When the play window ends, it removes `href` and revokes the Blob URL.
- Replay, a timeline seek, and resume after pause create a new instance and **play again from the first frame**. A native GIF cannot seek to an exact frame through SVG `setCurrentTime`. Do not claim it holds the internal frame while paused, and do not claim millisecond sync in every browser.
- The line, the canvas growth, and the scene's SMIL timeline are not affected by reloading the GIF. The GIF is a decoration. Being a few frames early or late does not break the story.

### `story.svg`

- `story.svg` preloads the GIF in `<image href="data:image/gif;base64,...">`. SMIL only controls when it is shown and when it disappears. **It does not guarantee that the GIF starts decoding on its first frame at the moment it becomes visible.**
- The browser page `index.html` is what creates a new Blob decoder at the cue. To see the entrance precisely, open `index.html`. Do not judge it from `story.svg` alone.

## Visual and technical QA

1. Hide the GIFs for a moment and check that the story is still complete. If it is not readable, something essential was wrongly given to a GIF.
2. Check the transparent ground, the palette, and the edges. There should be no obvious rectangular patch.
3. Run `validate_story.py --input stories/<slug>/story.json`. It checks the real GIF format, frame count, transparency, loop mode, size, path safety, anchors, and whether a trigger falls outside the story.
4. After `compile_story.py`, read `gifDecorations` in `cues.json` and confirm the hit times match the path points.
5. Optional browser check: `python3 "$SKILL/tests/browser_gif_smoke.py" stories/<slug>/dist/index.html stories/<slug>/dist/gif-preview.png` (needs Playwright. Otherwise follow SKILL.md step 6 and drag the timeline in the agent's browser). Check: not mounted before the trigger, a Blob after it, unloaded at the end, a new decoder on seek.
6. Remove `gifDecorations` and compile once more. The story must still be complete with no GIF.
