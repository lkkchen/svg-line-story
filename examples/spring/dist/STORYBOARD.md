# A line into spring · Storyboard

**Theme**: A seed meets spring  **Duration**: 32 seconds  **Palette**: custom  **Arc**: three_act

| Chapter | Time | Scene | Objects the line must hit |
|---|---|---|---|
| 01 | 1.6–10.7s |  Waking · Some stories / begin with a seed. | pencil, seedlet |
| 02 | 10.7–20.1s |  In bloom · Wait for one flower / to open slowly. | seedlet, blossom |
| 03 | 20.1–32s |  Setting out · Carry spring / somewhere far. | paperboat |

## Path cues

| Object | Arrival | Reveal | Position |
|---|---:|---:|---|
| pencil | 1.60s | 1.42s | (190.0, 575.0) |
| seedlet | 10.70s | 10.50s | (490.0, 1260.0) |
| seedlet | 10.70s | 10.50s | (490.0, 1260.0) |
| blossom | 17.39s | 17.15s | (356.0, 2063.0) |
| paperboat | 25.12s | 24.80s | (452.0, 2990.0) |

## Small GIF accents (they do not replace the SVG)

| GIF | Area | Starts | Ends | Playback |
|---|---|---:|---:|---|
| sprout-sparkles | assets/sprout-sparkles.gif | 10.70s | 12.86s | once |
| bloom-petals | assets/petal-drift.gif | 17.39s | 19.55s | once |
| boat-water-ripples | assets/boat-ripples.gif | 25.12s | 27.28s | once |

## Review notes

- Positions are 750px design units, not CSS pixels.
- The path, the heroes, and the important motion stay inline SVG. Small transparent GIFs are local decoration only.
- The browser page mounts each GIF at its cue. After a pause or a seek it starts again from the first frame. Frame-accurate GIF seeking is not supported.
- story.svg embeds GIFs up front. SMIL only controls visibility, so a GIF may not begin on its first frame when it appears.
