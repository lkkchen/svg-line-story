# Story design: from a theme to a spatial scroll

## The input stays small

The theme is required. If length, tone, or audience are not specified, use the baseline: 3 chapters / 32 seconds / 750 × 4050 / hand-drawn line art / portrait first. After the user gives a theme, hand over the story plan: palette, narrative arc, what the line means, the opening object, the material list, and a three-chapter storyboard. Do not write `story.json` and do not compile before the user confirms. "You decide," "just do it," and "whatever" only choose the recommended palette and arc inside the plan. They do not skip showing the plan. Start only after the user has seen the plan and says "go ahead" or an equivalent confirmation. Do not add a questionnaire beyond that.

## Gather materials before the storyboard

A thin story is usually a story with nothing concrete to draw or write. Before you draw, list 8–12 materials, numbered. Later chapters pull from those numbers.

| A real material | Not a material |
|---|---|
| "the seventh year of Jianxing," Changban Slope, the child in his arms, one silver spear | brave, loyal, a legendary life |
| ENIAC in 1946, a room of vacuum tubes, a punched card | technological progress, changing the world |
| a breakfast stall at four in the morning, steam from a basket, two coins for one fried dough stick | street life, warmth, ordinary beauty |

Each chapter uses at least 2: one in the title or caption, one as a supporting object or a small annotation on screen. The whole scroll uses more than 6. Keep the unused ones. When step 6 finds an empty stretch, fill it from this list.

## Choose the arc, then write the three chapters

`scripts/arcs.py` only has skeletons that fit a scroll. Ad arcs that push a pain point or end on a call to action are not in it.

| id | When to use it | What the three chapters mean on the line |
|---|---|---|
| `three_act` | When there is no more specific skeleton | Cause → turn → echo. The line completes one change, and the ending returns to the opening feeling |
| `timeline` | History, change, growing up, a life | Start → passing through → this moment. The line only goes forward. No flashback |
| `man_in_hole` | Standing up again after failure, getting lost, or a loss | Steady → the fall → climbing out. The line sinks first, then rises higher than the start |
| `myth_buster` | Correcting a misconception | What people think → not so → therefore. The line passes through something that looks true, then turns toward the real cause |
| `how_it_works` | How one thing happens | First sight → the middle step → so this is why. The line follows the real order |
| `story_spine` | An ordinary day rewritten by one event | Every day → until one day → from then on |

Write the choice into `arc` on `story.json`. Each chapter gets `role`, `emphasis`, and `motion`. The next two sections say what those mean. `plan_story.py --arc` fills the three fields. You still rewrite the prose.

One `storyBeat` per chapter says: where the line comes from → what it hits → what that triggers → where it goes next.

## The first screen is a hook

Do not title the first chapter with a warm-up such as "a line sets out." The first screen has to tell the promise or the turn, for example "this letter will drift to the lighthouse," not "there is a letter by the sea." The line grows from **the first object in this piece that matters to the plot**: an envelope, a seed, a lamp, a ticket stub, a railroad tie. The pencil in `examples/spring/` belongs only to that "it starts with a mark" sample. A new story does not get a `pencil` by default, and it does not say "the brush comes down." Use a pencil only when the theme itself is drawing, making a mark, or spring stationery. For how many concrete objects belong in one chapter, look at any chapter of `examples/1024/story.json`, not at its total chapter count. The ending returns to an object or a sentence from the first chapter. It does not repeat the theme's name.

## A new event every 3–5 seconds

A chapter is about 10 seconds. Each chapter has at least two hits: the line meets the hero, then 3–5 seconds later it meets another object, or the hero finishes the second half of a motion. Do not let one object enter and then hold the whole chapter. The transition is still the continuous tangent of the same line. Do not hard-cut.

## Neighboring heroes change motion

There are only four motions: `draw` grows along the line, `pop` pops and overshoots once then stops, `sway` swings once then stops, `still` only fades in. The last chapter of the piece is `still`, so the stop is saved for the return. Neighboring heroes do not share a motion.

The real motion of a built-in object is `MOTIF_MOTION` in `scripts/motifs.py`. A flower is `pop`, a sprout is `draw`, a boat and a butterfly are `sway`, and most of the rest are `still`. If the chapter's `motion` does not match the built-in object, write `customMotifs` for that beat. Do not pretend the built-in drawing will change motion. The scale overshoot stops at `1.06–1.08` and returns to `1`. Do not shrink past the end size. `pop` and `sway` ease in on a spline. The markup is in `references/vector-art.md`. A later part of the same object is 0.15–0.4 seconds after the body.

The one continuous line is the moving subject that crosses the whole scroll. Do not add another character that flies across the frame in every chapter. The same rule is for GIFs: a `calm` palette usually has 0–1, a `punchy` palette may add one short spark on the beat the theme turns on. Not every chapter.

## One palette, a different hero color each chapter

The paper color never changes. Do not lay a ground block in every chapter. `emphasis` decides who owns the color in this chapter: the hero fill uses that role color, and the other objects fall back to a paler `light` / `sky`. The narrative arc gives the recommended order. A common one is second fill → accent → line color. Neighboring chapters do not emphasize the same role. The orange traveling dot is the only mark in the whole scroll that means "this is happening now." Do not add another moving highlight on a supporting object.

## The rhythm of the eye

- A vertical length of 1200–1600 design units per chapter is a good range. Inside a chapter, vary the density: a tight cluster around the hero (hero + close parts + shadow + a small annotation), and between clusters a stretch that is only the main line and ornaments. Any 1000 design units of height needs at least 5 objects (type does not count).
- Each chapter has at least 1 hero + 3 supporting objects + 4 small ornaments + 1 small annotation. That is the floor. A small ornament is a tuft of grass, a star dot, a scrap of paper, a ground shadow, steam, or a speed line, about 20–60 design units, scattered on both sides of the main line so the journey is not empty.
- Leave some journey before the main drawing, so the viewer is led downward. A key beat appears somewhere the eye can find.
- Let the curve alternate left and right, but not as a mechanical zigzag. A local loop is allowed. Transitions use a continuous tangent. A `timeline` line folds back rarely. Chapter two of `man_in_hole` sinks clearly.
- Keep type 70–100 design units away from the path. A headline is about 2–6 words per line. A caption is 2 lines. The palette's `typeStyle` decides whether the title is loose or a little heavy. Do not switch to another font family.

## Storyboard checklist

A scene must include: `role`, `storyBeat`, `headline`, `caption`, `emphasis`, `motion`, the hero drawing, a specific local anchor, at least two route hits, a concrete animation after the trigger, the direction it enters from, at least 2 material numbers, more than 3 supporting objects, more than 4 small ornaments, and at least 1 small annotation.

Before you hand the idea to the program, check: if every drawing is hidden and only the line remains, does it still look as if it is going somewhere in the next chapter? If the main line is hidden, are the drawings just a random pile? If either answer is no, rewrite the story.
