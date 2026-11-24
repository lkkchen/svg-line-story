# Platform fit and the quality bar

## In the browser

Current Chrome, Edge, and Safari are the ones to use. Prefer the latest Chromium. `index.html` is a single HTML file with inline SVG, SMIL, style, and script (and the GIF bytes, when there are GIFs). Double-click it offline. Browser JavaScript pauses, replays, seeks, debugs anchors, and follows. The core path, the objects, and the growth are all SVG + SMIL. About 2.4 seconds after the pointer leaves, the bottom control bar collapses to a thin strip and opens again when the pointer enters, so it does not cover the canvas. If `story.json` has `sound`, the page plays cues on the timeline, muted by default, audible after a click on the controls. Before a screenshot, still hide `.dock-slot`, `.dock`, `.dock-peek`, and `.topbar`.

Minimum QA:

```bash
# $SKILL = the absolute path of the directory that contains this skill's SKILL.md
OUT=stories/<slug>
python3 "$SKILL/scripts/validate_story.py" --input "$OUT/story.json"
python3 "$SKILL/scripts/compile_story.py" --input "$OUT/story.json" --output "$OUT/dist"
python3 -m unittest discover -s "$SKILL/tests" -p 'test_*.py'
# Optional. Needs Playwright and Chromium. Without them, use the agent's browser (SKILL.md step 6 B).
python3 "$SKILL/tests/browser_smoke.py" "$OUT/dist/index.html" "$OUT/dist/preview.png"
# If you added a transparent GIF:
python3 "$SKILL/tests/browser_gif_smoke.py" "$OUT/dist/index.html" "$OUT/dist/gif-preview.png"
```

Compare a 440px phone width and a 1280px desktop width. At 0s, at each chapter entrance, at each touch, and at the end, check the visible height, the stroke state of the line, where the interactive drawings are, and whether type is covered. A unit test cannot stand in for an art defect.

## Acceptance checklist

- The path and the object's visual anchor meet on one real stroke. The hand-drawn main line stops on that stroke and leaves from there. It does not cut through an object or through type.
- A stem, river, or rail that grows is one `stroke-dashoffset` path. `pop` / `sway` ease in and then stop. Later parts of the same object are offset by 0.15–0.4 seconds.
- Distance is `z:"back"`. The main line is above it. An object that should cover the line stays the default `front`.
- Timeline cues match the route's arc length. Motion plays only for its designed duration. Pause and replay work.
- There is no path break between scenes. A transition is not a full-screen still dropped in.
- Each chapter has at least 1 hero, 3 supporting objects, 4 small ornaments, and 1 small annotation. Any 1000 design units of height has at least 5 objects. The hero meets the shape-count and fill floors in `references/vector-art.md`.
- An object's `id` matches what is drawn. Do not use `cloud` / `star` / `bird` to stand in for something on the material list.
- Every hero and every important composition is a real SVG primitive in one style. An optional GIF is small, transparent, and short. The story is still complete with it off. No full-page image and no network dependency.
- When you use a GIF, check the local file format, the loop flag, the start and end cues, and the browser Blob reload. Remove the GIF and the story must still be complete.
- The animation grows to the final canvas height. There is no horizontal scroll on a phone or on a desktop.
- The opening and ending space and the type are correct. If you use a special font, depend only on the system font fallback.
- When the user asks for only one theme, the agent finishes the story structure and the style choices. Do not stop because a parameter is missing.
