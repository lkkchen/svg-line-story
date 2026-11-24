---
name: svg-line-story
display_name: SVG Line Story
description: SVG Line Story. Turn one theme into a hand-drawn scroll whose body is pure SVG (an SMIL timeline plus a page that grows), add small transparent GIF accents when they help, and export a browser page that opens offline. Covers the story idea, the storyboard, original vector art, a continuous Bézier path, connection anchors, and browser QA. Use when someone asks for an SVG long-form story, an SVG scroll, an interactive scroll, an SVG SMIL picture book, or a page that extends itself, or gives a theme to turn into an SVG animation.
compatibility: Any agent that can read and write workspace files and run Python 3.10+. The core compiler uses only the standard library. Pillow and Playwright are optional. It does not depend on a particular editor, IDE, or agent product.
metadata:
  version: "1.1.0"
  lineage: svg-line-story V1.1
---

# SVG Line Story

Your role is **story director + vector artist + animation editor + SVG engineer**. If the user gives only a theme, you still have to move the work forward and finish the story, the storyboard, the drawings, the path, and the page yourself. Do not stop at advice or hand the user a long form.

This skill is not tied to one client. If you can read this file, write files in the workspace, and run Python, follow the steps below through to the end.

**The visual baseline is the pure-vector demo in `examples/spring/`**: clear outlines, a little flat color, open paper, and lines that connect naturally. That grammar does not change. `examples/spring/` opens with a pencil because that story starts when a mark is made. **It is not the opening template for a new story.** For how finely to draw an object, and how many concrete things belong in one chapter, use `examples/1024/story.json`. That piece is a 13-chapter, 146-second Programmer's Day scroll. Learn its drawing and its density. Do not copy its chapter count, duration, or plot into another theme. A new theme must not copy `pencil` without a reason, and must not make the first chapter "the brush comes down." Each palette is one picture: a paper color, 6 role colors, a motion amount (`calm` / `punchy`), and a way of finishing. They are defined in `scripts/palettes.py`. Narrative skeletons are in `scripts/arcs.py`. Do not turn this into a full watercolor, a soft-edged bitmap, a torn-paper collage, or a large scene paste-up. This skill **keeps a pure SVG body by default**, and it also has an **optional transparent GIF accent**. A GIF is only for a petal, a glint, a butterfly wing, or a ripple. It cannot replace the main line, a person, the structure of a scene, or the important timeline. The story must still hold together with every GIF turned off. Sample GIFs are not shipped with the skill. When you need one, generate it into the work directory with `scripts/make_decor_gif.py`.

## Working rules (read these first)

- **Skill root**: the directory that contains this `SKILL.md`. Call it `$SKILL` below. Resolve it to an absolute path before you start. Do not assume it lives in some client's config directory, and do not hard-code a relative path.
- **Where commands run**: run the commands below from the **workspace root**. Scripts find their templates and assets from their own file location, so `$SKILL` only has to point at this skill. The current directory of the call does not matter.
- **Where the work goes**: put each theme in `stories/<short-english-name>/` in the workspace (for example `stories/forest-letter/story.json` and `stories/forest-letter/dist/`). **Do not write the work into the skill directory.** `examples/` is only a reference. Do not overwrite it.
- **Local dependencies**: the core compile needs only the Python 3.10+ standard library. Check quickly before you start:

  ```bash
  python3 -c "import PIL" 2>/dev/null && echo pillow-ok || echo pillow-missing
  python3 -c "import playwright" 2>/dev/null && echo playwright-ok || echo playwright-missing
  ```

  Pillow is needed only by `make_decor_gif.py`. Playwright is needed only by `tests/browser_*smoke.py`. If one is missing, **do not install it globally on your own**. A pure SVG piece still goes ahead. If you truly need a GIF or Playwright, tell the user and suggest a workspace `.venv` (`python3 -m venv .venv && .venv/bin/pip install pillow playwright && .venv/bin/python -m playwright install chromium`), then run the matching script with `.venv/bin/python`.
- **Tracking the task**: this is a multi-step task. Move through the 8 steps below. If the environment has a task list, update it item by item. Otherwise report by step as you go.
- **Visual QA**: prefer the Playwright scripts that ship with the skill. If Playwright is missing and the agent can open a browser, do the same page checks that way. See step 6. If neither is available, report only the static checks. Do not invent a screenshot.
- **The skill directory stays text**: this directory is what gets distributed, so it cannot contain binary files. Allowed: `.md`, `.py`, `.json`, `.js`, `.css`, `.html`, `.svg`. Do not put or generate `.zip`, `.png`, `.gif`, `.jpg`, or `.webp`, and do not leave `__pycache__`. Do not leave `preview.png`, `gif-preview.png`, or sample `.gif` files in `examples/`. GIFs and screenshots for a work go only to `stories/<slug>/` in the workspace, not back into the skill. If a screenshot belongs in the reply, name its path in words. Do not add the image file to the skill package.

If the user gives only a theme, use the defaults for chapter count, duration, and size. **Do not ask**: 3 chapters, about 32 seconds, 750 × 4050 SVG coordinates, a vertical scroll, mobile first. Before any work you must hand over a story plan (palette, narrative arc, what the line means, and a three-chapter storyboard). Write files and compile only after the user confirms. See "Before you start: the story plan" below. If the user has already named a palette, a color, or an arc, fill the missing item in the plan with the recommendation. Do not ask about that item on its own.

## Art and motion rules that must not break

1. **One line that means something**: it is the journey, not a decorative frame. In different passages it can stand for a vine, a river, a kite string, a road, or a star track. The objects in every chapter are strung on one continuous path.
2. **Pure SVG, one stroke weight**: the main scene uses only editable SVG `<path>`, `<g>`, `<circle>`, `<ellipse>`, `<rect>`, and the like. Body outlines are about 2.5–4.5 design units. The main line is 4.5. The pale stroke under it is 11. Do not generate a full-page picture and paste it into the SVG to pretend it is pure SVG. Do not draw a scene with an image tool and embed it.
3. **Few colors and few motions, enough things in the picture**: "few" applies only to how many colors you use and how many things move at once. It does not limit the object count. Each chapter has **at least** 1 hero + 3 supporting objects + 4 small ornaments (tufts of grass, star dots, a ground shadow, a small label, steam, scraps of paper — two or three written as one motif still counts, but you need at least 2 groups) plus at least 1 small annotation (a year, a place, a number, or a quoted line, in small type or monospace). These are floors, not targets. See "Small annotations and ornaments" in `references/vector-art.md`. Any 1000 design units of height in the scroll needs at least 5 objects (type does not count). Open space comes from contrast between dense and sparse, not from leaving a whole screen empty. The background uses only a few light blocks. The paper color never changes. The whole scroll uses only the 6 role colors of the chosen palette: `ink` for lines and type, `sage` for the second fill, `orange` for the accent, `rose` for the third fill, `sky` / `light` for pale blocks. Each chapter uses `emphasis` so the hero takes one role color. Neighboring chapters do not repeat it. Do not invent a second spring-palette, and do not flood every chapter with a ground color.
4. **Place the anchors, then draw the path**: every `route` item that matters to the plot is `{"hit":"object-id"}`. The compiler derives the absolute coordinate from the object's local anchor. The path must pass through that point exactly. The default local anchor is `[100,180]`. The real visible stroke or root of every custom SVG must touch it too.
5. **The line does not break or jump**: the last waypoint of one chapter and the first waypoint of the next share the same coordinate. The generator joins every waypoint into cubic Béziers that share tangents. Transitions are not hard cuts. The line does not suddenly appear at the other end.
6. **SMIL plays the piece itself**: `stroke-dasharray` / `stroke-dashoffset` draw the path. `animateTransform` grows, blooms, and sways. `animateMotion` moves the traveling dot along the path (an orange dot, the tip of the timeline, not a pencil you are required to draw). `animate width` grows the layout. JavaScript only does playback, follow, the timeline, and anchor debugging. About 2.4 seconds after the pointer leaves, the bottom control bar slides off and leaves a thin strip. Moving onto the strip opens it again. It stays open while the pointer rests on it or while the timeline is being dragged. `story.json` may include a `sound` table that plays with the timeline: muted by default, audible after the first click on the controls. Pause stops the sound with the picture. Dragging the timeline does not play the cues that were skipped.
7. **The page grows. It does not show everything at once**: the story SVG uses its full `viewBox` from the start. A second empty SVG grows its `width` over time so the page height grows with the story. The two SVGs keep the same jobs they had in V1.
8. **A local GIF is optional and must not take over**: add `gifDecorations` for a butterfly wing, petals, dew, or ripples beside a paper boat. Zero to 2 per chapter is right. 3 is the maximum. Transparent, with lines and colors that match the scene. Bind `trigger:{"hit":"object-id"}` to the real arrival time of the path. Prefer `attachTo + offset` on an SVG anchor. The GIF itself is not part of the main-line math. Read `references/gif-decoration.md` first.
9. **The line lands, and the motion settles**: the main line stops on the object's real stroke (a root, a waterline, a corner) and leaves from there. It does not cut through a shape or through type. A stem, river, or rail that grows is one `stroke-dashoffset` path, not several stacked pieces. In one chapter only the orange traveling dot means "this is happening now." The hero fill uses `emphasis`. Supporting objects fall back to `light` / `sky`. Later parts of the same object are offset by 0.15–0.4 seconds. `pop` / `sway` ease in on a spline, overshoot once, and stop. Distance is `z:"back"`. An object that should cover the line stays the default `front`. Details are in `references/vector-art.md`. When `prefers-reduced-motion: reduce` matches, the page holds the finished state at the end and does not follow automatically.

## Before you start: the story plan (a hard gate)

After the user gives a theme, **return the story plan first. Start making it only after the user confirms.** Do not compile first. Do not write `stories/<slug>/story.json`. Do not run `plan_story.py` to save a file. Do not enter the 8 steps below.

1. Run this from the workspace root (`$SKILL` is the absolute path of the directory that contains this file), only so the recommendation can go into the plan. This is not the start of production:

   ```bash
   python3 "$SKILL/scripts/palettes.py" --suggest 'the theme in the user's own words'
   python3 "$SKILL/scripts/arcs.py" --suggest 'the theme in the user's own words'
   ```

   If the palette in the plan has motion `punchy`, run the arc again with `--motion punchy`. The motion order follows.

2. In the same message, hand over the plan in the structure below. Do not just drop a palette and ask the user to fill in a form:

   - **Title**: a hook. Do not use the theme sentence as the title.
   - **The line**: what this line is in this piece (a vine, a rail, an antenna, a river). One sentence.
   - **Palette**: use the first recommendation. Write its name, why it fits, the paper, the line, the second color, and the accent. Add one alternate id that differs more. The user can change it.
   - **Narrative arc**: use the recommended one. If no keyword hit, but the theme is clearly about time, a fall, or steps, switch to the closer arc and say why. Write how the line travels, the three chapter roles, the hero colors, the hero motions, and one alternate.
   - **Opening object**: the first hit is this piece's origin, not the sample pencil. Use a pencil only when the theme itself is drawing, making a mark, or spring stationery.
   - **Material list**: before the storyboard, list 8–12 concrete details tied to the theme, numbered. Each one is something you can draw or write: a name, a year, a place, a number, a quoted line, an object, a sound, or a smell. Do not write abstract words such as "warmth," "hope," or "growth." For real people and history, use known facts. Do not invent what you are not sure of.
   - **Storyboard**: one table, one row per chapter. Columns: role, title, where the line comes from, which two objects it hits, the hero's motion, what that beat means, and which material numbers it uses. Each chapter uses at least 2 materials, and at least 1 of them lands in a small annotation or a supporting object on screen.
   - **Ending**: return to an object or a sentence from the first chapter. Do not repeat the theme's name.
   - **Please confirm**: reply "go ahead" to start drawing. To change something, say which chapter, which palette, or which arc.

3. **Stop here.** This message must not also start production.
4. If "you decide," "just do it," or "whatever" arrives before the user has seen a plan: use the first palette and the arc judgment above, **still send the plan, and still stop.** Those three phrases do not count as confirmation of the plan.
5. Enter the 8 steps only after the user has seen the plan and says "go ahead," "yes," "start," "confirmed," or "do it this way." If the user changes only one chapter, the palette, or the arc, send an updated plan and stop again until they clearly say to start.
6. If the same message already spells out the objects, titles, and what the line means for all three chapters, treat the plan as confirmed and start. If the user already named a palette, a color, or an arc, fill the missing item with the recommendation. If the user explicitly says to keep the spring palette, use `spring`.
7. After confirmation, pass `--palette` and `--arc` to the draft command. `story.json` then stores `paletteName`, `canvas.background`, the 6 role colors, `arc`, and each chapter's `role`, `emphasis`, and `motion`. Custom objects use only `{{ink}}`, `{{sage}}`, `{{orange}}`, `{{rose}}`, `{{sky}}`, `{{light}}`, and `{{paper}}`. Do not hard-code a spring hex such as `#375763`.
8. When you need a GIF, pass the same id to `make_decor_gif.py --palette`. `calm` adds few. `punchy` adds one short accent on the beat that the theme turns on.

If the environment has a structured choice, the question covers only the one item in the plan that truly needs a decision (usually the palette or one chapter). The narrative and the storyboard stay in the same message. Do not invent a second set of colors or arcs.

## The 8 steps you must run after a theme is confirmed

Enter this section only after the user has confirmed the story plan. Before that, this section is forbidden.

### 1. Turn the theme into a story, not three screens of split phrases

- Derive one **visual metaphor** from the theme: what can stay strung on the same line the whole way? How the line travels has to match the chosen `arc` (a timeline only goes forward; a fall and climb sinks first, then rises).
- Write the three chapter roles that `arcs.py` gives you. Do not dress every piece as "cause → turn → echo." Each chapter needs its own feeling, visual center, concrete action, and "what it means when the line passes through this object."
- The first-screen title is a hook: the promise or the turn of this piece. Do not warm up with "a line sets out."
- **The first hit is this piece's origin object**, not the pencil in the sample. The line grows from an anchor that belongs to the theme: the corner of an envelope, a seed's root, a lamp cord, a ticket stub, a railroad tie. When you reuse coordinates from `examples/spring/`, replace the old `pencil` with this piece's origin, or turn it into an ordinary waypoint. Do not also copy the "the brush comes down" story beat. Keep the pencil only when the user's theme is drawing, making a mark, or spring stationery.
- Write `theme`, `storyBeat`, `headline`, and `caption`. Keep the sentences tight so the type does not overflow a width of 750. Aim for 2–6 words per headline line. Each chapter has at least two route hits, 3–5 seconds apart.
- Land the material list on the picture: `caption` names a specific person, event, or number, not a vague sigh. Supporting objects and small ornaments come from the materials (a broken bridge, hoofprints, and the small type "the seventh year of Jianxing" in a Zhao Yun piece, not another cloud). Do not pad with `cloud` / `star` / `bird` when a material does not support the object.
- Each chapter's hero uses that chapter's `motion`. When that does not match a built-in object, write `customMotifs`. Neighboring chapters do not share a motion. The last chapter is `still`.
- Each chapter's hero fill uses that chapter's `emphasis`. The paper color stays.
- Decide the emotional return at the end. Do not merely repeat the theme's name.
- Read `references/story-design.md` first. For three-chapter coordinates and breathing room, look at `examples/spring/story.json`. Before you draw a custom object, open `examples/1024/story.json` and read the `objects` of any two chapters and those objects' drawings in `customMotifs`: how many concrete things are in one chapter, and how many path layers make one hero. Draw at that density. Do not copy the whole piece, and do not treat its 13 chapters and 146 seconds as the default length of a new story.

### 2. Use or draw vector scenes in one style

The 24 built-in drawings, one style, are in `scripts/motifs.py`: `pencil, sprout, flower, boat, cloud, sun, hill, butterfly, bird, tree, moon, star, book, kite, lighthouse, shell, gift, balloon, house, rocket, lantern, heart, leaf, wave`.

**A new theme must not mechanically reuse spring's three chapters.** If the theme is a fox, a cat, a train, or a cafe, and the built-in objects cannot say it accurately, draw a native SVG `customMotifs`. Placeholders: `{{ink}}`, `{{sage}}`, `{{orange}}`, `{{rose}}`, `{{sky}}`, `{{light}}`, `{{paper}}`, `{{cue}}`. Draw in a local 200 × 200. The root or contact that needs to connect lands exactly on `anchorLocal`. See `references/vector-art.md`. For how complex a drawing should be, compare `customMotifs` in `examples/1024/story.json` (the laptop, the chip, the rack, and the rocket are drawn for that theme. They are not built-in objects with a new title).

Do not swap the whole composition for a PNG because the layers got complicated. Do not stuff an image prompt or a link that cannot run into the canvas.

### 3. Decide whether a transparent GIF accent is needed

- The hero, the path, and the body are SVG. **Try a local SMIL motion first.** Make 1 or 2 small transparent GIFs only when a continuous fine motion needs frames (petals falling, a wing flickering, dew glinting). If the scene does not call for one, add none.
- A GIF is a local `.gif`, with a path relative to `story.json` (so it lives in `stories/<slug>/assets/`). Usually about 160×110 pixels, 2–4 seconds, in this piece's palette, on a transparent ground. Prefer playing once. Do not use a GIF as a whole-chapter background.
- To generate one, use `"$SKILL/scripts/make_decor_gif.py"` (needs Pillow) for `sparkles` / `petals` / `ripples` / `flutter` line-drawn frames. A theme of its own needs frames you design for that plot, not petals pasted onto every subject. If Pillow is missing and the user does not want to install it, drop the GIF and finish with SMIL.
- `trigger:{"hit":"..."}` on `chapters[].gifDecorations` binds the moment the main line arrives. `attachTo` binds the GIF to an SVG object's anchor. Platform limits are in `references/gif-decoration.md`.

### 4. Write story data that can compile

- You may use `plan_story.py` to make a legal JSON draft from the theme, then **you must redesign the people, objects, plot, what the line means, and the storyboard with the agent's own work.** That command is an **offline theme-word template**. When the word list misses, it falls back to spring's three heroes. A non-spring draft **no longer opens with a pencil.** It is still not a model that understands every theme, and the opening object is only a placeholder. Before you deliver, change it into this piece's own origin.
- Write `stories/<slug>/story.json`. Check it against `templates/story.schema.json` and `examples/spring/story.json`.
- Each chapter defines its own `start`, `duration`, `role`, `emphasis`, `motion`, `labelAt`, `headline`, `captionAt`, `caption`, `route`, and `objects`. `route` has at least two `hit`s.
- When an object's `reveal` is `"touch"`, the compiler derives the entrance from the path's arc length. `leadSeconds` of 0–0.4 lets it appear a little before the touch.
- `route` has at least 4–7 meaningful waypoints, with room to breathe. Objects sit near the story beat they stand for. The path does not run over type. The default `pathTension` is `0.96`. You may nudge it between 0.7 and 1.2.

**The API contract that matters**: `{"hit":"sprout"}` in a route does not mean "draw a line that roughly passes a plant." The object's `x`, `y`, `scale`, and `anchorLocal` decide that point exactly. Never hand-write an approximate coordinate and hope.

### 5. Compile

```bash
OUT=stories/forest-letter

python3 "$SKILL/scripts/validate_story.py" --input "$OUT/story.json"
python3 "$SKILL/scripts/compile_story.py" --input "$OUT/story.json" --output "$OUT/dist"
```

If validation fails or the story data is illegal, the command exits non-zero and does not leave a usable page.

A `WARN` from `validate_story.py` does not fail the command, but treat these as tasks. Fix them and run again until they are gone: "has only N objects," "no small annotation," "hero … has only N shapes," "is named … but drawn as …," "sparse," "is only N design units from the main line." If one of them should stay, say which one and why in the delivery reply. Do not pile on objects that have nothing to do with the story just to clear a warning. What you add comes from the material list.

You end with `$OUT/dist/index.html` (open it offline), `story.svg` (the whole main scene as editable SVG, with decorative GIFs embedded as `<image>`), `cues.json` (path lengths, trigger times, anchors, the grow table), `STORYBOARD.md`, and the source `story.json`.

The generator depends only on the Python standard library. CSS, JS, and GIF bytes for the ordinary HTML are all inlined. There is no network dependency. **The core motion is SVG SMIL.** A GIF in the browser is only a local accent. A little JavaScript creates a new Blob decoder at the cue so the GIF does not finish playing offscreen early. On pause or seek, a GIF can only restart from the first frame. It cannot sync frame by frame.

### 6. Render, check, and correct (a successful compile is not enough)

**A. When Playwright is available** (`.venv/bin/python` or the system python can import playwright):

```bash
python3 "$SKILL/tests/browser_smoke.py" "$OUT/dist/index.html" "$OUT/dist/preview.png"
# When GIFs are enabled:
python3 "$SKILL/tests/browser_gif_smoke.py" "$OUT/dist/index.html" "$OUT/dist/gif-preview.png"
```

The first checks page height and horizontal scroll at 0s / 6s / 12s / 18s / 26s / the end, at a 440px phone width and a desktop width. The second checks that a GIF is not loaded before its cue, shows after the cue, unloads at the end, and that seek or replay creates a new decoder.

**B. When Playwright is missing but the agent can open a page and take a screenshot**:

Do the same checks on the local page. Some built-in browsers refuse `file://`. Then start a static server at the workspace root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/stories/<slug>/dist/index.html`. If the current browser can open a local file directly, you may open `stories/<slug>/dist/index.html`.

1. Use a viewport close to 440px wide, about 1400px tall, at a zoom of 1. Do not turn on a mobile-device emulation that enlarges the picture further, or the screenshots will be offset. The screenshot has to cover the picture itself. If a tool can only capture a very narrow panel, switch to something that can write a full-viewport bitmap, then read that image. Scroll a long page in sections. Do not capture the whole scroll in one very tall viewport, or the first screen gets tiled.
2. The page is playing by default, and follow is on. The exception is when the system has "reduce motion" on: time is held at the end, the picture and the page height are already there, follow is off, and `#btn-play` says "▶ Play from the start." Do not click it just to pause. Clicking it plays from the beginning. Otherwise hide the controls, pause, and turn follow off before you shoot, so the controls do not cover the picture and the page does not scroll itself away. Read the button label before you run anything in the page: when `#btn-play` says "Ⅱ Pause," a click pauses. When `#btn-follow` says "◉ Follow," a click turns follow off. Both are toggles. Do not click again once they are already in the state you want.

   ```js
   document.querySelectorAll('.dock-slot,.dock,.dock-peek,.topbar').forEach(el => { el.style.display = 'none'; });
   ```

3. Take a shot at 0 seconds, at each chapter entrance, at each touch (see `cues.json`), and at the end. Drag the timeline:

   ```js
   (t => { const s = document.getElementById('seek');
     s.value = t; s.dispatchEvent(new Event('input')); })(12)
   ```

   If follow is still on, the page scrolls to the tip of the line.
4. Read `document.documentElement.scrollWidth <= window.innerWidth` and confirm there is no horizontal scroll. Read `document.getElementById('stage').getBoundingClientRect().height` and confirm the height grows monotonically.
5. Click the "⊹ Anchors" button (`#btn-debug`) and take one more shot. The red cross must land on the real contact of the drawing. A mathematical error of 0 does not mean the drawn outline is aligned.
6. Stop the static server when the check is done.

Read the pictures one by one: (a) the stroke is consistent, (b) the main route is natural and lands on a visible stroke of the object, without cutting through a shape or type, (c) the touch point is visible and accurate, (d) type is not crushed by the line, (e) objects do not leave the frame, (f) the ending appears whole at the end, (g) there is no horizontal scroll, (h) a growing stem, river, or rail is one line, not several stacked pieces, (i) each chapter counts out 1 hero, more than 3 supporting objects, more than 4 small ornaments, and at least 1 small annotation, (j) no screen is only the main line and one or two small objects.

When (i) or (j) fails, add content before you deliver: put an unused detail from the material list into the empty stretch, or give the hero a ground shadow, a part, and a small annotation. Do not fill the gap by enlarging an object you already have or by stretching the main line.

- If something conflicts, change the `objects` layout first, then a `route` waypoint, and rerun the compiler and QA. Do not hide a spatial miss by casually editing cue seconds.
- When neither Playwright nor a browser is available, at least run `validate_story.py` and the standard-library unit tests (`python3 -m unittest discover -s "$SKILL/tests" -p 'test_*.py'`). Report which parts you did not see yourself. Do not invent a screenshot or a pass on a real device.

### 7. Deliver the browser page

Deliver `index.html`. It is an SVG/SMIL piece plus a little JavaScript for controls and follow. If there are GIFs, JavaScript creates a new Blob URL at the cue. It runs offline.

Do not run `theme_map.py` again on a piece that has `paletteName`. `motifs.materials()` already mixes material colors from the palette at the source. Use `theme_map.py` only as a fallback for an old piece that lacks `paletteName`. Otherwise a dark paper gets misread as the ink family.

When `story.svg` is opened on its own, GIFs are embedded up front. SMIL only controls when they are visible. It does not guarantee that they start on the first frame. The browser page `index.html` is what creates a new decoder at the cue.

### 8. Deliver and explain

The files are already in the user's workspace. **Do not pack a ZIP** unless the user asks (`zip -r` when they do). In the reply:

- List `stories/<slug>/dist/index.html`, `story.json`, and `STORYBOARD.md` as markdown links. Say to open `stories/<slug>/dist/index.html` in the system browser (`open` on macOS).
- Explain the picture with one real preview (from Playwright or from step 6 B). The path points at the PNG that was actually written. If there is no screenshot, say so.
- In a short paragraph, explain this version's translation of the theme, what the path means, the scenes, and the important trigger times, and list what was verified and what was not.

## A worked example: from a theme to a line that keeps growing

Theme "a letter by the sea": chapter one starts on the fold of an envelope, chapter two turns that fold into a ripple, chapter three extends the ripple into a lighthouse beam. The three visible anchors are the corner of the envelope, the paper boat's waterline, and the base of the lighthouse. Each chapter uses 2–3 flat colors. The compiler fixes the line coordinates exactly. Do not deliver "seed → flower → paper boat" with a new title, and do not make the sample pencil the first prop of every piece.

## Read these files (as the task needs them)

Paths are relative to the directory that contains this `SKILL.md`:

- `references/story-design.md`: story beats, metaphor, storyboard, and scene coordinates.
- `scripts/palettes.py`: palettes. Each has a paper color, role colors, a motion amount, and a finish. After the user gives a theme, run `--suggest` first.
- `scripts/arcs.py`: narrative arcs. Put one in the story plan with the palette and the storyboard, and wait for the user to confirm.
- `references/vector-art.md`: the V1 art grammar, custom SVG objects, anchors, local SMIL, landing the line, growing on one path, offsets, and easing.
- `references/gif-decoration.md`: the art boundary of a transparent GIF, the `story.json` fields, generation, triggers, looping, and platform limits.
- `references/timing-and-growth.md`: spline paths, length sync, and how the page grows.
- `references/platform-and-qa.md`: browser checks and what the output has to pass.
- `examples/spring/story.json`: a real 32-second, three-chapter example, SVG coordinates only. GIF fields are documented in `references/gif-decoration.md`.
- `examples/1024/story.json`: the Programmer's Day scroll. Look at how many objects are in one chapter and how `customMotifs` are drawn. 13 chapters and 146 seconds are the length of that theme, not the default for a new story.

**Forbidden results**: writing `story.json`, compiling, or opening a preview before the user confirms the story plan; after confirmation, still having only a story proposal and no HTML that runs; using a GIF in place of a hero or a whole chapter; a GIF whose style fights the SVG; a large watercolor paste-up that does not match; a line and an object that are merely near each other and not connected; a jump where scenes join; a whole screen that is only the main line and one or two small objects; an object whose name and drawing do not match (`butterfly` drawn as a bird, `wild-flowers` drawn as stars); calling a templated preset a general AI generation; opening with a pencil when the theme does not ask for one; writing the work, or a `.gif` / `.png` / `.zip`, into the skill directory.
