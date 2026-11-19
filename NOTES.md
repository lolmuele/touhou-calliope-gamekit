# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written by Claude on 2026-11-13 from a long chat with the project owner. Sections 6-7 refreshed on 2026-11-16 after
re-reading main.py blob aff1521f; the first hardware results and the engine analysis (section 2 and 7) were added the same day.
Benchmark v1 results (2026-11-17), benchmark v2 results and benchmark v3 (2026-11-19) are in section 7. Section 9 (web simulator) added 2026-11-13.
Claude has no memory between chats. To resume: open a new chat, connect the
GitHub connector, and say "read NOTES.md and main.py in lolmuele/touhou-calliope-gamekit".

Everything here is marked as one of: VERIFIED (read in source/docs or seen in the
repo), MEASURED (owner observed it), or UNSURE (my belief, check before relying on it).

---

**Standing permission (owner, 2026-11-13):** Claude may edit this file whenever it sees fit, without asking. Scope is this file only. Other files in the repo are only changed when the owner asks. (On 2026-11-19 the owner said Claude may add whatever is needed on the benchmark branches to make them work.)

## 1. Project and working style

- MakeCode Arcade, **Python** editor (preferredEditor: pyprj), target Arcade 4.1.x, runs on the
  Calliope gamekit. `main.ts` is just the generated transpile; `main.py` is the source of truth.
- Screen is 160x120. Stage area is 120x120 (x 0-120). HUD panel is 40x120 (x 120-160).
- The owner wants to understand problems, not receive vibe-coded dumps. Explain the issue, point at
  the fix, and let them write it. They ask again if stuck. When they ask for code, give it.
- The owner is colorblind (blue vs purple is hard). Name colors by hex and give previews.
- Owner said not to comment on the unfinished game-over mechanic unless asked (this was early on).
- Hardware tests are rare. Make each session count (see section 7).
- The owner gets overwhelmed by big features (bosses) and procrastinates; break work into 20-45 minute pieces,
  each testable on its own, and suggest one concrete next step.
- The owner is blunt about quality: describe the project honestly (it is an early prototype, not "playable").
- The owner prefers to write the fixes themselves, even when another AI hands over a full rewrite.

## 2. MakeCode quirks learned in this project

- VERIFIED (owner saw it): inside `sprites.on_overlap` handlers, reading `self.enemies` crashed with
  "Cannot read properties of undefined (reading 'iface')". Using the global `gameObj` instead worked.
  Some other handlers using `self` also work, so cause unknown. Keep using `gameObj` in handlers.
- Handler params need `: Sprite` annotations. Handlers receive raw sprites, not your wrapper objects.
- `range()` takes numbers: `range(len(lst))`, never `range(lst)`. Removing while iterating forward
  skips the next element; iterate backwards (`range(len(x) - 1, -1, -1)` compiles and is used in `bombActive`).
- Declare every attribute in `__init__`. Reading undefined attributes silently gives falsy/NaN.
- Compile gotchas (VERIFIED by the owner's errors, 2026-11-17/18): `List[int]` fails with "cannot find type 'int'" (use `List[number]` or no
  annotation; plain `x: int` parameters are fine); a variable named `img` clashes with MakeCode's built-in image-literal function and gives
  "types not compatible: (_: string) => Image" (use another name); assigning `ArcadePhysicsEngine(...)` to
  `game.current_scene().physics_engine` in Python gives "types not compatible: PhysicsEngine and ArcadePhysicsEngine" (so do that in a .ts file).
- `SpriteFlag.GHOST_THROUGH_SPRITES`, `Sprite.left/top/right/bottom`, `Math.floor`, `sprite.lifespan` all compiled and ran on the device (benchmark v2).
- `sprites.set_data_number` / `read_data_number` come from the **extension**
  `microsoft/arcade-sprite-data` (already added to this project).
- Tiles and images are the same format (VERIFIED by decoding the jres). Tiles are 16x16; images can be any size.
  Sprites draw 1:1 on the 160x120 screen.
- `assets.image(...)` may return a shared image (UNSURE). HUD code clones it before drawing.
- On-screen console output is slow on the Calliope (MEASURED, frame time crept to 65+ ms with it on).
  Don't print in hot paths. Show diagnostics with `sprite.say_text(...)` instead (the bubbles themselves cost nothing measurable, see section 7).
- Simulator frame time is ~20-23 ms because the loop sleeps to a ~20 ms floor (forum sources disagree
  between 30 and 50 Hz, both say capped). It does NOT measure your code's cost. `control.micros()` works.
- Image literals in the jres store palette **indices**, not colors. Changing a palette hex recolors all art.
- Sprite `z` is draw order; the 2nd arg of `sprites.create` is the *kind*, not a layer. Changing `z` sets a flag so the scene
  re-sorts all sprites (full sort with a callback) before the next draw (VERIFIED in basesprite.ts / scene.ts, pxt-common-packages v14.1.7).
  MEASURED on the device: this is cheap here.
- `sprites.destroy` the sprite AND remove the wrapper from any Python list, or it leaks.

**Arcade physics engine facts (VERIFIED by reading `libs/game/physics.ts` and `spritemap.ts` of pxt-common-packages v14.1.7 on 2026-11-16;
UNSURE whether the owner's editor ships exactly that version):**
- `ArcadePhysicsEngine(maxVelocity = 500, minSingleStep = 2, maxSingleStep = 4)`; frame dt is capped: `MAX_TIME_STEP = 100` ms.
  Above 100 ms per frame the world runs in slow motion.
- Each sprite's movement for the frame is halved until a step is <= `maxSingleStep` px, and the frame runs as many sub-steps as the
  fastest sprite needs. A 250 px/s shot moves 5-7 px at 20-27 ms frames (2 sub-steps) and 25 px at the 100 ms cap (8 sub-steps).
- After EVERY sub-step `spriteCollisions` runs. It ignores which sprites moved: it walks every filled grid cell and compares every
  pair of sprites in it. For each pair it creates/pushes into a per-sprite `_alreadyChecked` list and searches it with `indexOf`
  BEFORE it checks whether the two kinds have an overlap handler. Cost grows roughly with (sprites per cell)^2 x sub-steps.
- It returns immediately when no overlap handlers are registered, and a sprite is only inserted into the grid when its kind appears in
  some registered overlap handler AND it does not have the ghost-through-sprites flag (`SPRITE_NO_SPRITE_OVERLAPS = GhostThroughSprites |
  Destroyed | RelativeToCamera`; VERIFIED in current physics.ts via code search; CONFIRMED on the device by benchmark mode sp+ghost). `Sprite.overlapsWith` also returns false for such sprites.
- Grid: cell size = clamp(8, areaSize/4, 2 x largest sprite) = 40x30 px on this 160x120 screen (16 cells). The grid is cleared once per
  frame, but moving sprites are re-inserted every sub-step and are never removed from the cells they pass through.
- Every overlap event is run with `control.runInParallel` (its own thread), and fires again each frame the sprites still overlap.
- `scene.createRenderable(z, handler(target, camera))` and `camera.drawOffsetX/Y` exist (used by the tilemap code), so things can be drawn
  without being sprites. `sprites.Flag.HitboxOverlaps` exists in current sprite.ts (skips the pixel test).
- A bigger max step must be set from TypeScript: `game.currentScene().physicsEngine = new ArcadePhysicsEngine(500, 2, 16)` before any sprite
  exists (benchmark v3 does this in `engine_step.ts`, listed first in pxt.json). UNSURE whether a hand-written .ts file next to main.py compiles
  in the Python editor, and whether `settings` is reachable from it.

## 3. Palette

Stored in `pxt.json` as `palette` (16 entries, index 0 is transparent in Arcade). Currently "option B"
(derived by weighted Lab k-means/swap search from EoSD screenshots, white/black/yellow/skin/dark-red locked):

| slot | hex | role |
|---|---|---|
| 0 | #000000 | transparent (unused) |
| 1 | #FFFFFF | white |
| 2 | #F4423F | red |
| 3 | #F350CA | magenta pink |
| 4 | #A81818 | dark red |
| 5 | #E8DC14 | yellow |
| 6 | #AF9E88 | tan (also the stage background color; dimmed UI text) |
| 7 | #4FB719 | green |
| 8 | #4745CB | blue |
| 9 | #B0C9F0 | ice blue |
| 10 | #3F36E9 | vivid blue |
| 11 | #7776CE | periwinkle |
| 12 | #2B2B3A | navy (HUD) |
| 13 | #EDC1B9 | skin |
| 14 | #DB6B62 | salmon |
| 15 | #000000 | black |

There is no true grey. Option A (not used) had a grey and cyan instead of skin and dark red.

## 4. Real EoSD data (from the community decompilation github.com/GensokyoClub/th06, v1.02h)

Read: `src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`. Not verified against the original
game by me. Units are EoSD internal units at 60 fps. Playfield is 384x448 (from memory, UNSURE).

**Player**
- No HP: one hit kills. Deathbomb window about 6 frames. After respawn 240 frames of invulnerability.
- Speed 5 px/frame unfocused, 2.5 focused (Marisa A and B). Shot speed 12 px/frame.
- Hitbox half-size 1.25 px (2.5 px box). Item grab half-size 12. Graze adds 20 px per side.
- Scaled by playfield width (x0.3125) into this game: move ~94/47 px/s, shot ~225 px/s, hitbox ~0.8 px,
  grab box ~7.5 px, graze margin ~6 px, orb offsets +-24 -> +-7.5 px unfocused.

**Fire rate (my reading of the code)**
- A 30-frame cycle restarts while Shoot is held. Each stream fires when `frame % 5 == 0`, i.e. every
  5 frames = 83 ms = 12 shots/s per stream, at every power level.
- Lasers have NO tick limiter: laser damage is applied every frame (60 Hz) while it overlaps an enemy,
  and lasers are not consumed on hit. The laser's re-fire timer is 120-330 frames. The on/off split lives
  in animation data I could not see (assume always on; trim 20-30% if too strong).

**Marisa B damage by power**

| Tier | Power | Main shot damage per volley | Laser dmg per frame (each of 2) | approx dps if all hit |
|---|---|---|---|---|
| 0 | 0-7 | 48 (1 stream) | none | 576 |
| 1 | 8-31 | 32 | 3 | 744 |
| 2 | 32-63 | 44 (2x22) | 3 | 888 |
| 3 | 64-95 | 50 (15/20/15) | 4 | ~1080 |
| 4 | 96-126 | 50 (15/20/15) | 5 | 1200 |
| 5 | 127+ | 74 (12/15/20/15/12) | 6 | 1608 |

Exact ranks: 0-7, 8-15, 16-31, 32-47, 48-63, 64-79, 80-95, 96-126, 127+. Laser cycle frames by rank
(rank2..9): 120, 170, 200, 210, 230, 250, 270, 330. Laser width 10/15/20 px (scaled ~3.1/4.7/6.25 px here).

**Damage rules**
- Per frame, an enemy takes at most 70 damage.
- During boss spell cards, non-bomb damage is divided by 7 (minimum 1).
- While a bomb is active, shot damage is 1/3. Marisa B cannot shoot during her bomb.
- Touching an enemy's body kills the player and deals 10 damage to the enemy.
- Marisa A orbs are missiles that stay after hit and deal 1/4 damage.

**HP**
- Boss HP (from a 2013 forum post, shrinemaiden.org topic 15824, "obtained from the game program"; notation
  for some stages is unclear): Sakuya 750/1000/1100 by shot type; Remilia 1200/1600/1600/1300/4700-5300;
  stage 2 boss 1500/1400-1800/1400. Spell phases take damage / 7.
- Normal enemy HP is NOT in the decomp source (stage data). Suggested values are MY heuristics, not EoSD:
  small fairy ~80, mid fairy ~380, large fairy ~950.

**Items** (from EnemyManager): random drops 16 small power / 15 point / 1 large in a 32-entry table;
only every 3rd killed random-drop enemy drops. Small power +1, large +10.

## 5. Conversion plan (agreed with owner)

Use EoSD damage and HP numbers as-is (they are in the same units). Convert only timing and geometry.
1. `Enemy.takeDamage(amount)` and per-projectile `damage` (DONE: damage lives in sprite data).
2. Fire on timestamps, not frames: every 80-83 ms (DONE roughly; `lastShot = now`). Better: add to
   the timestamp so the average rate stays exact at 40 ms frames.
   Hardware-friendly option: fire every ~167 ms at double damage (same dps, half the sprites; MEASURED: half the shots cut a 215 ms frame to 46 ms).
3. Tier table keyed off `self.power` (tiers 0-5 DONE as `self.tier`; still set manually; should come from power).
4. Laser tick: damage = laser_dps x elapsed seconds, where laser_dps = (dmg per frame) x 60
   (180 / 240 / 300 / 360 per laser). Clamp elapsed to ~100 ms. Keep a timer per (enemy, laser).
   Current code uses `damage * 40 // 16` per overlap frame, tuned for 40 ms frames; it deals half the dps at 20 ms frames.
5. Boss phases: list of HP values, `isSpell` flag applying the /7 rule. See the boss plan below.
6. Items: only `starItem` is handled; the rest of the item table is TODO.
Sanity check: a 1600 HP spell phase should take ~7 s at tier 5 and ~19 s at tier 0 (if everything hits).

**Boss plan (agreed idea, small steps; none done yet).** Milestone "smallest boss" = one phase, one ring pattern, HP bar, stage clear.
- B1. Reuse `Enemy`: add a `phases` list of HP values and `phaseIndex`; when health hits 0 and another phase exists,
  advance instead of setting `dead`.
- B2. One hard-coded pattern: a function that fires a ring of N bullets with `setAngle` (parameters: count, speed, angle offset).
  Keep a constant cap on bullets alive until hardware numbers are in. Dense enemy patterns will hit the same collision wall as the
  player shots did (see section 7), so enemy bullets should be ghost-through-sprites with a manual hit test against the player.
- B3. Boss HP bar: a thin image sprite at the top, redrawn only when HP changes.
- B4. Phase change: clear bullets into stars (reuse `bombActive` logic), short invulnerability, `isSpell` flag applying
  the /7 damage rule, optional timer and spell name text.
- B5. Movement: reuse the existing `route` system, looping.
- B6. Intro, death, item drops, stage clear.
Suggested order of work: fix the collision cost first (section 7), then link `tier` to `power` and add power/point item drops from kills
(makes the HUD power bar meaningful), then the smallest boss.

## 6. State of the code (last read: main.py blob aff1521f on master, 2026-11-16) and known issues

Done: HUD with live power bar and a dirty flag that now resets (`redrawHud` clears `hudChanged`); game over screen with
continue; player i-frames; time-based shooting; tiered shot with lasers (laser damage fixed, no longer 0); one test enemy
(950 HP) that spawns every 1.2 s and flies the same hard-coded route firing aimed shots; bombs that turn enemy bullets into
stars (trigger requires bombs > 0 and a 6000 ms gap); star collection; palette; sprites cropped to small images; stage
background is `scene.set_background_color(6)`; debug prints, `info.show_score` and `game.stats` removed; bullet lists
iterated backwards; frame interval and own-code time are measured in `frametimes` (average now divides by 60).

Known issues (priority order):
0. **Performance: the engine's collision scan with ~25 player shots in one grid cell costs ~185 ms per frame on the device; ghost-through-sprites shots fix that part (section 7). With enemies, lasers and enemy bullets a further ~90 ms is still unexplained.**
1. Bomb constants disagree: the trigger checks `>= 6000` but `bomb()` requires `> 6100`. In the 6000-6100 ms window
   `bombActive(first=True)` runs without spending a bomb (free clear). `playerDamaged` uses 6200 for invulnerability.
   Define one constant.
2. `enemyHitByLaser` damage is tuned for 40 ms frames (see section 5, step 4). It also loops over all enemies without a `break`.
3. Enemy removal loop in `projectileDestructor`: `i += 1` runs after a removal, so the index drifts; dead enemies waiting for
   bullets get `sprites.destroy` every frame; offscreen-alive enemies keep running `goRoute`. The test-projectile list loop
   is still forward (list is unused).
4. `playerDamaged` calls `takeDamage()` even if no bullet was found; mixes `self` and `gameObj`.
5. Game over: continues can go negative; sprites keep moving and overlaps still fire while the game over screen is up.
6. Undeclared attributes: `Enemy` (`xVel`, `yVel`, `maxSpeed`), `Game` (`lastUpdateStart`, `frameAverage`, `average`, `yes`).
   The first `say_text` shows `frameAverage` before it is assigned.
7. `self.tier = 5` and `Player.power = 0` are test values; the HUD power bar does not follow the tier.
8. Only `starItem` drops/collects; enemies drop nothing when killed.
9. (Dropped) Narrowing the lasers: the benchmark shows 8 px and 4 px lasers cost the same (nothing) when no shots share their cells.
10. Focus (hold B) only slows movement when lasers exist (`B and self.Lasers`), so at tier 0 it does nothing.
11. Real-time timers (`game.runtime()`) are used for spawning, firing and route waits, but physics time is capped at 100 ms per frame.
    At 200-300 ms frames the world moves in slow motion while enemies still spawn at full rate, so enemies pile up (14 alive in M3),
    which slows the game further. Fix: one game clock advancing at most 100 ms per frame.
12. Enemy steering costs ~4-5 ms of own code for 14 enemies on the device (benchmark `enemy14`); fine for now.

## 7. Performance: results, conclusions and plan

Image sizes (decoded): player shot 8x8, enemy orb (miniHakkero) 8x8, laser 8x120, star 5x5, masterSpark 47x120,
HUD 40x120, gameOver 120x120.

**Hardware test harness: branch `hardware-test`** (created 2026-11-16; master untouched; one commit b3d40e3 that only appends a block at the
end of `main.py` between `HWTEST-BEGIN` and `HWTEST-END`; 138 additions, 0 deletions). A cycles modes 0-4; bombs disabled; player
can't be hit. Display: upper bubble `M<mode> <avg ms>/<worst ms> c<own us>`, lower bubble `s<shot sprites>/<list> b<bullets> e<enemies> t<seconds>`.
It compiled and ran on the device.

**MEASURED results, game on hardware (owner's photos, 2026-11-16; files mode1-5.jpg = modes 0-4):**

| Mode | What | avg / worst frame ms | own code | shots | bullets | enemies |
|---|---|---|---|---|---|---|
| 0 | tier 0 | 27 / 38 | 1.3 ms | 6 | 0 | 0 |
| 1 | tier 5, no lasers | 206 / 255 | ~12.7 ms | 25 | 0 | 0 |
| 2 | + lasers | 246 / 268 | ~13 ms | 25 | 0 | 0 |
| 3 | + enemies (the real game) | 328 / 580 | 12.6-22.6 ms | 29 | 9 | 14 |
| 4 | same, HUD hidden | 324 / 541 | 21.5-26.8 ms | 28 | 9 | 14 |

**MEASURED results, synthetic benchmark v1 then v2 (branch `hardware-bench`, owner's photos of the summary screen, 2026-11-17 and 2026-11-19; step 4 = engine default).**
Modes 0-14 repeated within 1-3 ms between the two runs, so the measurements are repeatable. Combined table (v2 run; the photo had glare on sp+ovl and the
right-hand columns were read by row order, so code/n values are UNSURE by a digit):

| Mode | avg / worst ms | code ms | n alive |
|---|---|---|---|
| nothing | 26 / 36 | 0.0 | 0 |
| hud+plyr | 26 / 36 | 0.0 | 0 |
| bubbles | 26 / 37 | 0.0 | 0 |
| static30 | 26 / 35 | 0.0 | 30 |
| move30 | 26 / 37 | 1.0 | 30 |
| spawn | 28 / 43 | ~2.3 | ~27 |
| sp+data | 28 / 44 | 2.4 | ~30 |
| sp+z | 28 / 43 | ~2.4 | ~27 |
| sp+wrap | 29 / 43 | ~5.1 | ~27 |
| sp+all | 30 / 46 | 5.7 | 25 |
| **sp+ovl** | **~215-220 / 239** | 11.9 | 25 |
| lasers8 | 26 / 35 | 0.0 | 2 |
| lasers4 | 26 / 35 | 0.0 | 2 |
| enemy14 | 30 / 41 | 4.7 | 14 |
| full | 468 / 512 | 18.2 | 50 |
| **sp+ghost** | **30 / 46** | 5.7 | 25 |
| **fullghst** | **121 / 139** | 21.1 | 50 |
| **sp+half** | **46 / 68** | 3.3 | 15 |

**Conclusions so far:**
- The bare device floor is ~26 ms (about 38 fps). Sprites existing, moving, being created/destroyed at ~60/s, having data, `z` or Python wrapper
  objects add only ~0-4 ms in total. Draw cost, garbage collection, data objects, `z`, Python loops, bubbles and the HUD are all small.
- Registering the overlap handlers with the SAME 25 shots takes the frame from 30 ms to ~215 ms (mode sp+ovl). That is the engine's collision scan over
  crowded grid cells, repeated per sub-step. Estimate (UNSURE): ~23 ms per scan of ~25 sprites in one cell.
- **CONFIRMED: ghost-through-sprites shots remove that cost completely** (sp+ghost 30 ms vs sp+ovl ~215 ms). Halving the shots also helps a lot (sp+half 46 ms).
- With everything else on screen, ghost shots plus a manual hit test bring the game-like case from 468 ms (`full`) to 121 ms (`fullghst`): 3.9x better but still slow.
  The Python part is 21 ms (the manual hit test is roughly 10 ms of it: 25 shots x 14 enemies with boxed floats; it can be made cheaper). That leaves ~75-90 ms of engine
  cost that is NOT explained by enemy14 (30 ms), lasers8 (26 ms) or sp+ghost (30 ms) alone. Hypotheses (UNSURE): laser-vs-enemy overlap events (each starts a thread
  every frame while overlapping), enemies crossing the laser columns and crowding cells, enemy bullets, or the combination. Benchmark v3 splits these.
- Lasers on their own and 14 spread-out enemies cost almost nothing; a crowd of sprites in ONE cell, or overlap events, is what hurts.
- Python-side per-bullet code is NOT the main problem, so the wrapper/list refactor is not worth doing for speed.

**Fix order (revised 2026-11-19):**
1. Player shots as ghost-through-sprites plus a manual swept box test against enemy boxes (replaces the `enemyDamaged` overlap). PROVEN for the shot part (sp+ghost).
   Make the hit test cheaper (read boxes once; skip enemies by x range; avoid `Math.floor` on every shot).
2. Find what the remaining ~90 ms in `fullghst` is (benchmark v3 modes en+lasr, en+bull, en+ghst). If it is the laser overlap events, make lasers ghost too and test
   enemy x/y against the laser rectangles manually.
3. Bigger physics step (16) through `engine_step.ts`. Predicted gain for the old crowded case was 215 -> ~50 ms; with ghost shots it matters less. Check tunnelling (pixel-perfect overlaps, tiny player hitbox).
4. Enemy bullets: ghost-through-sprites plus a manual test against the single player hitbox, before building boss patterns.
5. One game clock advancing at most 100 ms per frame for spawning, firing, route waits, bomb and invulnerability timers.
6. Halve the shot count if still needed (fire every ~167 ms at double damage); small items: `break` in `enemyHitByLaser`.

**Benchmark branches (all replace `main.py` with a standalone benchmark; master untouched; delete them when done):**
- `hardware-bench` v2 (commit 854203c): 18 modes, ran on the device. Its commented-out engine line does not compile in Python (see section 2).
- `hardware-bench-v3` (commits 65dd3b5 `engine_step.ts`, 7133294 `pxt.json` lists it first, 0eba952 `main.py`; 2026-11-19; UNSURE it compiles, not run yet).
  15 modes from a flag table: nothing, base, spawn, sp+all, sp+ovl, sp+ghost, sp+half, lasers8, enemy14, then NEW en+lasr (14 enemies + lasers, no shots), en+bull (14 enemies +
  9 enemy bullets), en+ghst (14 enemies + ghost shots + manual hit test), then full, fullghst, fg+half (fullghst with a volley every 160 ms). Dropped as already measured and cheap:
  bubbles, static30, move30, sp+data, sp+z, sp+wrap, lasers4. TWO RUNS FROM ONE FLASH: on the summary screen A saves the setting `bstep` (4 or 16), restarts, and
  `engine_step.ts` builds the physics engine with that max step before any sprite exists; the footer shows the current step. New APIs it relies on (all UNSURE until it compiles):
  a hand-written .ts file in the Python project, `settings.exists/readNumber` in TS, `settings.exists/read_number/write_number` in Python, `game.reset()`.
  If `settings` fails, remove the settings use and hard-code the step in `engine_step.ts`.

## 8. Useful links

- Decompilation: https://github.com/GensokyoClub/th06 (`src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`)
- Boss HP / shot analysis thread: http://www.shrinemaiden.org/forum/index.php?topic=15824.0
- Sprite data extension: https://github.com/microsoft/arcade-sprite-data
- Arcade engine source: https://github.com/microsoft/pxt-common-packages (`libs/game/physics.ts`, `spritemap.ts`, `sprite.ts`, `scene.ts`, `basesprite.ts`)
- Rotation extensions (not used): `Marupio/arcade-cleanEdge` (best for pre-rendering rotated bullets at startup),
  `robo-technical-group/pxt-arcade-image-transform` (keeps per-sprite state that is never freed; avoid for bullets).
- MakeCode forum: Richard's Arcade Tips #6 (hitboxes and overlaps).

## 9. Web simulator (GitHub Pages) and releases

- The page https://lolmuele.github.io/touhou-calliope-gamekit/ (linked from README.md) runs a **prebuilt** file,
  `assets/js/binary.js`, loaded by `index.html` via `makeCodeRun`. Committing code does NOT rebuild it.
- That file (and `assets/version.txt`) is regenerated only when a **release** is created from MakeCode's GitHub window
  ("Commit & create release to update Pages"). Pages then takes up to ~10 minutes, and browsers may need a hard refresh.
  (VERIFIED from MakeCode docs and forum threads; the same forum threads say commits alone don't update the site.)
- VERIFIED state on 2026-11-13: the repo has no tags and no releases; `assets/js/binary.js` was last changed by the initial
  commit (2026-11-09); `assets/version.txt` is `0.0.0`. So the page shows the project as it was in the first commit.
- `.github/workflows/makecode-release.yml` only runs when a release is created and attaches UF2 builds (d51, f4, rpi) to
  the release. It does not deploy the Pages site. Which UF2 matches the Calliope gamekit is UNSURE.
- Claude's GitHub tools have no way to create releases or tags, and `binary.js` is a compiled file that should not be
  edited by hand. The owner has to create the release in the MakeCode editor.
- README.md was rewritten by Claude on 2026-11-14 as an honest "early prototype" description.
