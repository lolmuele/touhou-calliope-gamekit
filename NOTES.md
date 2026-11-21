# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written and maintained by Claude (the owner's assistant in a long chat that started 2026-11-13). Last full handoff rewrite: 2026-11-20. Benchmark v4 and v5 results recorded the same day (sections 0.5-0.7, 2, 5, 6, 7).
Claude has no memory between chats. THIS FILE IS THE MEMORY. A new chat should read it completely before doing anything.

Everything here is marked as one of: VERIFIED (read in source/docs or seen in the repo), MEASURED (the owner observed it on hardware),
or UNSURE (my belief, check before relying on it).

**Standing permission (owner, 2026-11-13):** Claude may edit this file whenever it sees fit, without asking. Scope is this file only.
Other files on `master` are only changed when the owner asks. On 2026-11-19 the owner also said Claude may add whatever is needed on the
benchmark branches to make them work.

---

## 0. START HERE (handoff for a new chat)

### 0.1 What this is
- The owner (GitHub user `lolmuele`, a hobbyist who is colorblind and learning as they go) is building a Touhou-style bullet hell
  (*Embodiment of Scarlet Devil*, playing Marisa) for the **Calliope gamekit**, in the **MakeCode Arcade Python editor**. Repo: `lolmuele/touhou-calliope-gamekit`.
- The game is an early prototype: movement, tiered auto-fire with lasers, one test enemy that repeats the same route, lives/i-frames/continue, bombs that turn bullets into star items, a HUD, a custom palette.
- Since 2026-11-13 the chat did: debugging compile errors and logic bugs, a custom palette from EoSD screenshots, EoSD damage/fire-rate data from the decompilation,
  a README, the GitHub Pages explanation, and a long series of **hardware performance tests** that found the cause of the very low frame rate and a design that fixes most of it (section 7).
- The owner wants to understand things and write the code themselves. They bring me screenshots/photos and ask for diagnosis, plans, tests and notes.

### 0.2 First steps in a new chat
1. Read this whole file. Do not summarise it back at length; the owner knows it.
2. Use the GitHub connector: list branches, list the latest commits, read `main.py` on `master` (compare its blob sha with section 6; if it changed, refresh sections 6 and 10).
3. Look for new files on `master` (for example `engine_step.ts`) and on the branches (a game branch with the non-sprite bullet pool may exist).
4. Ask the owner (one short question) what happened since: did they start the game fixes, did anything fail to compile, do they want the drop-in bullet pool?
5. Then continue from section 0.6.

### 0.3 How to talk to the owner (voice and habits that have worked)
- Casual, friendly, direct. The owner jokes (":sob:", "xD", "big guy"); light humor is fine, no lecturing, no corporate tone.
- Lead with the answer or the verdict. Then the reasons. Use short bold lead-ins, bullet lists, and tables for numbers. Keep answers focused; the owner reads on a phone sometimes.
- Be honest and calibrated. Say "I believe", "UNSURE", "I couldn't compile this". The owner hates overselling (they objected to the word "playable"). Own mistakes in one plain sentence and fix them
  (examples: I said `set_data_number` was core Arcade, it is an extension; I wrote `List[int]` and a variable named `img` that did not compile).
- Explain WHY, not just WHAT. The owner prefers: "explain the issue, say what the fix is, let me write it", and asks again if stuck. When they ask for code, give it.
- At most one question per reply, at the end. Offer one concrete next step when they feel stuck or procrastinate (they get overwhelmed by big tasks like bosses; break work into 20-45 minute pieces).
- The owner is colorblind: name colors by hex and name, give previews, do not rely on hue words (blue vs purple).
- The owner asked not to comment on the unfinished game-over mechanic unless asked (early request; later they asked about it themselves).
- When the owner sends screenshots of MakeCode errors, diagnose by the line numbers in the Problems panel (they refer to `main.py`), and say whether I could not compile the code myself.
- When the owner sends photos of the Calliope screen, read them carefully: perspective can shift the right-hand columns by a row, glare can hide digits; state what is uncertain. The device font draws a 9 like a "g".
- After doing work in the repo, tell the owner in a few lines what changed and give the commit link.

### 0.4 How to work with the repo and tools
- Read with `get_file_contents` (a directory path lists files with blob shas; pass `ref` as `refs/heads/<branch>` to read a branch). Write with `create_or_update_file`: it replaces the WHOLE file and needs the current blob sha, so copy the file exactly,
  then verify with `get_commit` (include_diff) that only the intended lines changed.
- In some chats the GitHub tools are deferred and must be loaded first with `tool_search` (for example query "github get file contents", then "github list branches commits", "github create branch").
- Experiments go on branches (`create_branch` with `from_branch` works; a new benchmark branch can start from the previous one so `engine_step.ts` and `pxt.json` come along). `master` only gets NOTES.md updates, and the README (written on request). Never push game code to `master` unless asked.
- The tools cannot create releases or tags. MakeCode compiles only in the owner's browser; I cannot compile. Never claim code compiles unless the owner ran it.
- I can read other public repos (for example `microsoft/pxt-common-packages`, `GensokyoClub/th06`). Check engine claims against the source instead of guessing. `web_search` is for docs and forum posts.
- Keep this file accurate: update it after anything settled (results, decisions, new branches, new gotchas). Rewrite the whole file with the latest sha, keep all sections, mark confidence.

### 0.5 Where things stand (2026-11-20)
- **Cause of the slow game is known and confirmed on hardware** (section 7): every live sprite costs frame time, and the physics engine's collision scan with ~25 player shots crowded into one grid cell, repeated per physics sub-step, made it far worse.
- PROVEN on the device: (1) physics max step 16 through a TypeScript file (`engine_step.ts`) fixes the crowded-cell case, (2) player shots flagged ghost-through-sprites with a manual hit test, (3) **bullets and shots that are NOT sprites are 10-20x cheaper than sprites**
  (benchmark v5). The game-like test went from ~499 ms (game today) to ~103 ms (ghost sprites) to ~47 ms (non-sprite bullets and shots, 14 enemies, 120 bullets). The bare device floor is ~26 ms.
- **Benchmark v4 and v5 ran on 2026-11-20 (both compiled; step 16 only).** Results in section 7. Short version of v5: (a) non-sprite bullets are almost free (c60 and c120 sit on the 26 ms floor; +60 of them in a loaded frame cost ~4 ms, a ghost-sprite bullet costs ~1.3 ms);
  (b) non-sprite shots save 20-30 ms (csh+en 41 vs en+ghs2 61; fo+c60 73 vs fcust 43); (c) the best design so far, `fcust`/`fc+120`, runs at 43/47 ms (about 21-23 fps) with 14 enemies, 2 lasers, ~20 shots and 60/120 bullets, against 91 ms for the all-sprite `fopt9`;
  (d) the earlier "unexplained ~40 ms" was mostly a mistake in how I added things up: the 26 ms floor is not additive (work below ~26 ms is hidden, see section 7), and a sprite costs roughly 0.7-1.3 ms per frame once the frame is over the floor.
  Garbage collection was NOT the problem (one forced collection takes 4-8 ms whatever is alive).
- The game on `master` has none of the performance fixes yet. The owner intends to write them themselves.

### 0.6 Next steps / what we are waiting on (in order)
1. Decide with the owner how to get the non-sprite design into the game. Offered (waiting for the owner's answer): a drop-in, well-commented **bullet pool** for enemy bullets (flat integer arrays, one `scene.create_renderable`, manual player/graze test, bomb-to-stars loop) on a game branch for the owner to read and adapt; then the same for player shots.
2. The owner applies the proven fixes in the game: add `engine_step.ts` (hard-coded 16, listed first in `pxt.json`), non-sprite enemy bullets, non-sprite player shots with the lean manual hit test against enemy boxes, lasers as ghost sprites (or drawn rectangles) with a manual test.
   (Offered, not done: I can add `engine_step.ts` and the `pxt.json` line to a game branch if asked.) After that, re-run the `hardware-test` modes on the game to confirm.
3. Fix the other known issues in section 6 (bomb constants, game clock, laser damage per frame, enemy removal loop, undeclared attributes).
4. Link `tier` to `power` and add item drops, then the smallest boss (section 5). Dense patterns are now realistic if bullets are non-sprites (120 bullets cost ~4-8 ms).
5. Housekeeping: delete the `hardware-*` branches when done; create a release in MakeCode when the owner wants the web simulator updated (section 9); no license is set yet (ask if they want MIT); the README has no screenshots yet.

### 0.7 Branch inventory (all benchmark branches REPLACE `main.py`; master is untouched)
- `master`: the real game, README.md, NOTES.md.
- `hardware-test`: game + removable test harness block at the end of `main.py` (A cycles modes 0-4). Ran on the device.
- `hardware-bench`: benchmark v2 (18 modes). Ran. Its commented-out engine line does not compile in Python.
- `hardware-bench-v3`: benchmark with `engine_step.ts` and a saved step setting (A toggles 4/16 and restarts). Ran on the device.
- `hardware-bench-v4`: bullet/laser/hit-test isolation modes and an all-manual `fullopt` design, default step 16. RAN on 2026-11-20. Results in section 7.
- `hardware-bench-v5`: branched from v4; 13 modes incl. non-sprite bullets/shots and a gc timing column; main.py blob 8c001fba (commit a0ca406). COMPILED AND RAN on 2026-11-20 (step 16). Results in section 7.
  Its `main.py` contains working reference code for a non-sprite bullet pool (`makeCustomBullets`, `tickCustomBullets`, `customBulletTest`, `drawCustom`, `ensureRenderable`) and shot pool (`makeShotPool`, `customShotTick`, `hitTestCust`).

---

## 1. Project and working style (details)

- MakeCode Arcade, **Python** editor (preferredEditor: pyprj), target Arcade 4.1.x, runs on the Calliope gamekit. `main.ts` is just the generated transpile; `main.py` is the source of truth.
- Screen is 160x120. Stage area is 120x120 (x 0-120). HUD panel is 40x120 (x 120-160). Controls: D-pad, A, B, Menu.
- Hardware tests are possible but the owner runs them only now and then: make each session count; ask them to flash a branch, wait, and photograph the summary screen.
- The owner is blunt about quality: describe the project honestly (it is an early prototype, not "playable").

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
  `game.current_scene().physics_engine` in Python gives "types not compatible: PhysicsEngine and ArcadePhysicsEngine" (do that in a .ts file).
- VERIFIED on the device (benchmark v3, 2026-11-19): a hand-written `engine_step.ts` listed FIRST in pxt.json compiles next to `main.py` and runs before it;
  `settings.exists/readNumber/writeNumber` work (TS and Python `settings.exists/read_number/write_number`); `game.reset()` restarts the program and keeps the setting.
- VERIFIED to compile and run on the device (benchmark v5, 2026-11-20): `scene.create_renderable(z, handler)` with `def handler(target: Image, camera: scene.Camera)`, `control.gc()` (a full collection takes 4-8 ms), `control.micros()`, `Math.round`, `Image.draw_transparent_image` on the screen image inside a renderable,
  integer `//`, plain untyped lists indexed in `while` loops. NOT directly verified: that the renderable's bullets were visibly drawn (the summary screen cannot show it; the cost difference fc+120 vs fcust suggests yes). Check by eye the first time it is used in the game.
- `SpriteFlag.GHOST_THROUGH_SPRITES`, `Sprite.left/top/right/bottom`, `Math.floor`, `sprite.lifespan` compile and work.
- `sprites.set_data_number` / `read_data_number` come from the **extension** `microsoft/arcade-sprite-data` (already added to this project).
- Tiles and images are the same format (VERIFIED by decoding the jres). Tiles are 16x16; images can be any size. Sprites draw 1:1 on the 160x120 screen.
- `assets.image(...)` may return a shared image (UNSURE). HUD code clones it before drawing.
- On-screen console output is slow on the Calliope (MEASURED, frame time crept to 65+ ms with it on). Don't print in hot paths. Show diagnostics with `sprite.say_text(...)` instead
  (the bubbles themselves cost nothing measurable).
- Simulator frame time is ~20-23 ms because the loop sleeps to a ~20 ms floor (forum sources disagree between 30 and 50 Hz, both say capped). It does NOT measure your code's cost. `control.micros()` works.
- Image literals in the jres store palette **indices**, not colors. Changing a palette hex recolors all art.
- Sprite `z` is draw order; the 2nd arg of `sprites.create` is the *kind*, not a layer. Changing `z` sets a flag so the scene re-sorts all sprites before the next draw (VERIFIED in the engine source). MEASURED on the device: cheap.
- `sprites.destroy` the sprite AND remove the wrapper from any Python list, or it leaks.
- UNSURE, untested: a sprite's `x`/`y` getters may return non-integer numbers, and on the device a non-integer number may be a heap-allocated boxed double, so float maths could create garbage. The v5 gc column (flat 4-8 ms) suggests garbage is not what limits us.

**Arcade physics engine facts (VERIFIED by reading `libs/game/physics.ts` and `spritemap.ts` of pxt-common-packages v14.1.7 on 2026-11-16;
UNSURE whether the owner's editor ships exactly that version):**
- `ArcadePhysicsEngine(maxVelocity = 500, minSingleStep = 2, maxSingleStep = 4)`; frame dt is capped: `MAX_TIME_STEP = 100` ms. Above 100 ms per frame the world runs in slow motion.
- Each sprite's movement for the frame is halved until a step is <= `maxSingleStep` px, and the frame runs as many sub-steps as the fastest sprite needs.
  A 250 px/s shot moves 5-7 px at 20-27 ms frames (2 sub-steps) and 25 px at the 100 ms cap (8 sub-steps).
- After EVERY sub-step `spriteCollisions` runs. It ignores which sprites moved: it walks every filled grid cell and compares every pair of sprites in it. For each pair it creates/pushes into a per-sprite
  `_alreadyChecked` list and searches it with `indexOf` BEFORE it checks whether the two kinds have an overlap handler. Cost grows roughly with (sprites per cell)^2 x sub-steps.
- It returns immediately when no overlap handlers are registered, and a sprite is only inserted into the grid when its kind appears in some registered overlap handler AND it does not have the
  ghost-through-sprites flag (`SPRITE_NO_SPRITE_OVERLAPS = GhostThroughSprites | Destroyed | RelativeToCamera`; VERIFIED in current physics.ts; CONFIRMED on the device by benchmark mode sp+ghost).
  `Sprite.overlapsWith` also returns false for such sprites.
- Grid: cell size = clamp(8, areaSize/4, 2 x largest sprite) = 40x30 px on this screen (16 cells). The grid is cleared once per frame, but moving sprites are re-inserted every sub-step and are never removed from cells they pass through.
- Every overlap event is run with `control.runInParallel` (its own thread), and fires again each frame the sprites still overlap.
- `scene.createRenderable(z, handler(target, camera))` and `camera.drawOffsetX/Y` exist (used by the tilemap code), so things can be drawn without being sprites (CONFIRMED working in benchmark v5). `sprites.Flag.HitboxOverlaps` exists in current sprite.ts.
- A bigger max step must be set from TypeScript: `game.currentScene().physicsEngine = new ArcadePhysicsEngine(500, 2, 16)` before any sprite exists. MEASURED: max step 16 cut the crowded-cell case from 229 ms to 47 ms.

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

There is no true grey. Option A (not used) had a grey and cyan instead of skin and dark red. Rule: images store indices, so palette edits recolor everything.

## 4. Real EoSD data (from the community decompilation github.com/GensokyoClub/th06, v1.02h)

Read: `src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`. Not verified against the original game by me. Units are EoSD internal units at 60 fps. Playfield is 384x448 (from memory, UNSURE).

**Player**
- No HP: one hit kills. Deathbomb window about 6 frames. After respawn 240 frames of invulnerability.
- Speed 5 px/frame unfocused, 2.5 focused (Marisa A and B). Shot speed 12 px/frame.
- Hitbox half-size 1.25 px (2.5 px box). Item grab half-size 12. Graze adds 20 px per side.
- Scaled by playfield width (x0.3125) into this game: move ~94/47 px/s, shot ~225 px/s, hitbox ~0.8 px, grab box ~7.5 px, graze margin ~6 px, orb offsets +-24 -> +-7.5 px unfocused.

**Fire rate (my reading of the code)**
- A 30-frame cycle restarts while Shoot is held. Each stream fires when `frame % 5 == 0`, i.e. every 5 frames = 83 ms = 12 shots/s per stream, at every power level.
- Lasers have NO tick limiter: laser damage is applied every frame (60 Hz) while it overlaps an enemy, and lasers are not consumed on hit. The laser's re-fire timer is 120-330 frames.
  The on/off split lives in animation data I could not see (assume always on; trim 20-30% if too strong).

**Marisa B damage by power**

| Tier | Power | Main shot damage per volley | Laser dmg per frame (each of 2) | approx dps if all hit |
|---|---|---|---|---|
| 0 | 0-7 | 48 (1 stream) | none | 576 |
| 1 | 8-31 | 32 | 3 | 744 |
| 2 | 32-63 | 44 (2x22) | 3 | 888 |
| 3 | 64-95 | 50 (15/20/15) | 4 | ~1080 |
| 4 | 96-126 | 50 (15/20/15) | 5 | 1200 |
| 5 | 127+ | 74 (12/15/20/15/12) | 6 | 1608 |

Exact ranks: 0-7, 8-15, 16-31, 32-47, 48-63, 64-79, 80-95, 96-126, 127+. Laser cycle frames by rank (rank2..9): 120, 170, 200, 210, 230, 250, 270, 330. Laser width 10/15/20 px (scaled ~3.1/4.7/6.25 px here).

**Damage rules**
- Per frame, an enemy takes at most 70 damage.
- During boss spell cards, non-bomb damage is divided by 7 (minimum 1).
- While a bomb is active, shot damage is 1/3. Marisa B cannot shoot during her bomb.
- Touching an enemy's body kills the player and deals 10 damage to the enemy.
- Marisa A orbs are missiles that stay after hit and deal 1/4 damage.

**HP**
- Boss HP (from a 2013 forum post, shrinemaiden.org topic 15824, "obtained from the game program"; notation for some stages is unclear): Sakuya 750/1000/1100 by shot type;
  Remilia 1200/1600/1600/1300/4700-5300; stage 2 boss 1500/1400-1800/1400. Spell phases take damage / 7.
- Normal enemy HP is NOT in the decomp source (stage data). Suggested values are MY heuristics, not EoSD: small fairy ~80, mid fairy ~380, large fairy ~950.

**Items** (from EnemyManager): random drops 16 small power / 15 point / 1 large in a 32-entry table; only every 3rd killed random-drop enemy drops. Small power +1, large +10.

## 5. Conversion plan (agreed with owner)

Use EoSD damage and HP numbers as-is (they are in the same units). Convert only timing and geometry.
1. `Enemy.takeDamage(amount)` and per-projectile `damage` (DONE: damage lives in sprite data; with non-sprite shots it would live in a parallel `damage` array).
2. Fire on timestamps, not frames: every 80-83 ms (DONE roughly; `lastShot = now`). Better: add to the timestamp so the average rate stays exact at 40 ms frames.
   Hardware-friendly option: fire every ~167 ms at double damage (same dps, half the shots; less needed now that shots can be non-sprites).
3. Tier table keyed off `self.power` (tiers 0-5 DONE as `self.tier`; still set manually; should come from power).
4. Laser tick: damage = laser_dps x elapsed seconds, where laser_dps = (dmg per frame) x 60 (180 / 240 / 300 / 360 per laser). Clamp elapsed to ~100 ms. Keep a timer per (enemy, laser).
   Current code uses `damage * 40 // 16` per overlap frame, tuned for 40 ms frames; it deals half the dps at 20 ms frames.
5. Boss phases: list of HP values, `isSpell` flag applying the /7 rule. See the boss plan below.
6. Items: only `starItem` is handled; the rest of the item table is TODO (items should also be capped or non-sprite if many).
Sanity check: a 1600 HP spell phase should take ~7 s at tier 5 and ~19 s at tier 0 (if everything hits).

**Boss plan (agreed idea, small steps; none done yet).** Milestone "smallest boss" = one phase, one ring pattern, HP bar, stage clear.
- B1. Reuse `Enemy`: add a `phases` list of HP values and `phaseIndex`; when health hits 0 and another phase exists, advance instead of setting `dead`.
- B2. One hard-coded pattern: a function that fires a ring of N bullets (parameters: count, speed, angle offset). **Bullets should be non-sprite** (benchmark v5, 2026-11-20): 120 non-sprite bullets cost ~4-8 ms,
  while sprite bullets cost ~0.7-1.3 ms each (60 normal sprite bullets 93 ms, 60 ghost 47 ms). Non-sprite means integer arrays + one renderable + a manual player test; see section 7 and the reference code in `hardware-bench-v5/main.py`.
- B3. Boss HP bar: a thin image sprite at the top, redrawn only when HP changes (or drawn inside the renderable).
- B4. Phase change: clear bullets into stars (reuse `bombActive` logic: loop the bullet arrays), short invulnerability, `isSpell` flag applying the /7 damage rule, optional timer and spell name text.
- B5. Movement: reuse the existing `route` system, looping.
- B6. Intro, death, item drops, stage clear.
Suggested order of work: fix the collision/sprite cost first (section 7), then link `tier` to `power` and add power/point item drops from kills (makes the HUD power bar meaningful), then the smallest boss.

## 6. State of the code (last read: main.py blob aff1521f on master, 2026-11-16; re-confirmed unchanged on 2026-11-20) and known issues

Done: HUD with live power bar and a dirty flag that now resets (`redrawHud` clears `hudChanged`); game over screen with continue; player i-frames; time-based shooting; tiered shot with lasers
(laser damage fixed, no longer 0); one test enemy (950 HP) that spawns every 1.2 s and flies the same hard-coded route firing aimed shots; bombs that turn enemy bullets into stars
(trigger requires bombs > 0 and a 6000 ms gap); star collection; palette; sprites cropped to small images; stage background is `scene.set_background_color(6)`; debug prints,
`info.show_score` and `game.stats` removed; bullet lists iterated backwards; frame interval and own-code time are measured in `frametimes` (average divides by 60).

Known issues (priority order):
0. **Performance (see section 7): the game has none of the proven fixes yet (max step 16 via engine_step.ts, non-sprite shots and bullets with manual tests). Today the game-like test is ~499 ms at step 4; the best measured design is ~43-47 ms (`fcust`, `fc+120`).**
1. Bomb constants disagree: the trigger checks `>= 6000` but `bomb()` requires `> 6100`. In the 6000-6100 ms window `bombActive(first=True)` runs without spending a bomb (free clear).
   `playerDamaged` uses 6200 for invulnerability. Define one constant.
2. `enemyHitByLaser` damage is tuned for 40 ms frames (see section 5, step 4). It also loops over all enemies without a `break`.
3. Enemy removal loop in `projectileDestructor`: `i += 1` runs after a removal, so the index drifts; dead enemies waiting for bullets get `sprites.destroy` every frame;
   offscreen-alive enemies keep running `goRoute`. The test-projectile list loop is still forward (list is unused).
4. `playerDamaged` calls `takeDamage()` even if no bullet was found; mixes `self` and `gameObj`.
5. Game over: continues can go negative; sprites keep moving and overlaps still fire while the game over screen is up.
6. Undeclared attributes: `Enemy` (`xVel`, `yVel`, `maxSpeed`), `Game` (`lastUpdateStart`, `frameAverage`, `average`, `yes`). The first `say_text` shows `frameAverage` before it is assigned.
7. `self.tier = 5` and `Player.power = 0` are test values; the HUD power bar does not follow the tier.
8. Only `starItem` drops/collects; enemies drop nothing when killed.
9. (Dropped) Narrowing the lasers: the benchmark shows 8 px and 4 px lasers cost the same (nothing) when no shots share their cells.
10. Focus (hold B) only slows movement when lasers exist (`B and self.Lasers`), so at tier 0 it does nothing.
11. Real-time timers (`game.runtime()`) are used for spawning, firing and route waits, but physics time is capped at 100 ms per frame. At 200-300 ms frames the world moves in slow motion
    while enemies still spawn at full rate, so enemies pile up (14 alive in M3), which slows the game further. Fix: one game clock advancing at most 100 ms per frame.
12. Enemy steering costs ~5 ms of own code for 14 enemies on the device (benchmark `enemy14`); lazy time-based legs (v5 `lazy+g`) save ~4 ms. Moving enemies cost more than stationary ones (v5), so keep the enemy count small.
13. UNSURE, worth checking: `self.skin = sprites.create(assets.tile("marisa"))` has no kind argument. If the default kind is 0 (the player kind) the 16x16 skin also overlaps enemy bullets, so the
    effective hitbox would be the whole sprite instead of the tiny hitbox sprite. Test by letting a bullet touch Marisa's hat, or give the skin its own kind (the benchmark uses 97).

## 7. Performance: results, conclusions and plan

Image sizes (decoded): player shot 8x8, enemy orb (miniHakkero) 8x8, laser 8x120, star 5x5, masterSpark 47x120, HUD 40x120, gameOver 120x120.

**Hardware test harness: branch `hardware-test`** (created 2026-11-16; one commit b3d40e3 that only appends a block at the end of `main.py` between `HWTEST-BEGIN` and `HWTEST-END`; 138 additions, 0 deletions).
A cycles modes 0-4; bombs disabled; player can't be hit. It compiled and ran on the device.

**MEASURED results, game on hardware (owner's photos, 2026-11-16; files mode1-5.jpg = modes 0-4):**

| Mode | What | avg / worst frame ms | own code | shots | bullets | enemies |
|---|---|---|---|---|---|---|
| 0 | tier 0 | 27 / 38 | 1.3 ms | 6 | 0 | 0 |
| 1 | tier 5, no lasers | 206 / 255 | ~12.7 ms | 25 | 0 | 0 |
| 2 | + lasers | 246 / 268 | ~13 ms | 25 | 0 | 0 |
| 3 | + enemies (the real game) | 328 / 580 | 12.6-22.6 ms | 29 | 9 | 14 |
| 4 | same, HUD hidden | 324 / 541 | 21.5-26.8 ms | 28 | 9 | 14 |

**MEASURED results, benchmark v1/v2 (branch `hardware-bench`, 2026-11-17/19; step 4 = engine default).** Floor 26 ms; static30/move30/bubbles/lasers8/lasers4 26-27;
spawn 28; sp+data 28; sp+z 28; sp+wrap 29; sp+all 30; **sp+ovl ~215-220**; enemy14 30; full 465-468; **sp+ghost 30**; fullghst 121; sp+half 46. Modes repeated within 1-3 ms between runs.

**MEASURED results, benchmark v3 (branch `hardware-bench-v3`, owner's photos, 2026-11-19). Cells are avg/worst ms (own code ms, sprites alive):**

| Mode | step 4 (engine default) | step 16 |
|---|---|---|
| nothing | 26/36 | 26/36 |
| base | 26/36 | 26/36 |
| spawn | 29/44 (2.4, 27) | 29/41 (2.3, 30) |
| sp+all | 30/46 (5.8, 25) | 30/45 (6.0, 25) |
| **sp+ovl** | **229/271** (12.2, 25) | **47/87** (6.7, 22) |
| sp+ghost | 30/46 (6.0, 25) | 30/43 (6.0, 25) |
| sp+half | 72/129 (5.5, 10) | 27/42 (3.0, 10) |
| lasers8 | 26/35 | 26/35 |
| enemy14 | 33/46 (5.2, 14) | 33/47 (5.4, 14) |
| en+lasr | 40/50 (5.6, 16) | 38/50 (5.1, 16) |
| en+bull | 46/59 (5.8, 23) | 44/61 (5.5, 23) |
| en+ghst | 88/103 (21.7, 39) | 62/85 (16.7, 34) |
| full | 499/565 (20.7, 50) | 170/207 (18.1, 50) |
| fullghst | 127/144 (23.2, 50) | 103/122 (24.0, 50) |
| fg+half | 108/132 (16.7, 35) | 75/98 (15.5, 40) |

(sp+half at step 4 was 46/68 in v2 and 72/129 in v3: the unstable regime is noisy.)

**MEASURED results, benchmark v4 (branch `hardware-bench-v4`, owner's photo of the summary screen, 2026-11-20; step 16 only). avg/worst ms, own code ms, sprites alive at the end:**

| Mode | What | avg/worst | own code | n |
|---|---|---|---|---|
| nothing | no sprites | 26/36 | 0.0 | 0 |
| base | HUD + player + skin | 26/36 | 0.0 | 0 |
| enemy14 | 14 steering enemies | 33/44 | 5.5 | 14 |
| en+ghst | + ghost shots + v3 hit test | 63/85 | 17.1 | 29 |
| en+gnoh | + ghost shots, NO hit test | 56/81 | 11.3 | 34 |
| en+ghs2 | + ghost shots + lean hit test | 61/86 | 15.7 | 29 |
| bull9 | 9 normal bullets | 26/37 | 0.2 | 9 |
| bull9g | 9 ghost bullets + manual player test | 26/37 | 0.7 | 9 |
| bull60 | 60 normal bullets | 93/110 | 3.3 | 60 |
| bull60g | 60 ghost bullets + manual player test | 47/63 | 5.7 | 60 |
| en+lasr | enemies + 2 normal lasers | 40/52 | 5.4 | 16 |
| lasr-g | enemies + 2 ghost lasers + manual rectangle test | 34/46 | 6.2 | 16 |
| fullghst | v3 reference (shots, hit test, lasers, 9 bullets, enemies) | 103/116 | 24.1 | 50 |
| fullopt | everything manual (ghost shots + lean test, ghost lasers, 9 ghost bullets) | 91/105 | 24.1 | 50 |
| fo+b60 | fullopt with 60 bullets | 158/172 | 28.5 | 101 |

Reproducibility check against v3 at step 16: en+ghst 63 vs 62, fullghst 103 vs 103, enemy14 33 vs 33, en+lasr 40 vs 38. Photo read by Claude; digits were clear.

**MEASURED results, benchmark v5 (branch `hardware-bench-v5`, owner's photo of the summary screen, 2026-11-20; step 16). avg/worst ms, own code ms, objects alive (sprites + non-sprite bullets/shots), ms of one forced garbage collection:**

| Mode | What | avg/worst | own code | n | gc |
|---|---|---|---|---|---|
| none | no sprites | 26/36 | 0.0 | 0 | 6 |
| base | HUD + player + skin | 26/36 | 0.0 | 0 | 7 |
| e14nov | 14 float-steering enemies, NO overlap handlers | 26/37 | 5.6 | 14 | 8 |
| nov+gn | + ghost shots (wrapper objects), no handlers | 48/67 | 11.9 | 39 | 5 |
| stat+g | 14 STATIONARY enemies + ghost shots, handlers on, no hit test | 40/64 | 7.0 | 39 | 6 |
| lazy+g | enemies steered once per leg + ghost shots, handlers on | 52/73 | 7.5 | 34 | 6 |
| csh+en | float enemies + non-sprite shots + lean hit test, handlers on | 41/51 | 11.4 | 39 | 5 |
| c60 | 60 non-sprite bullets + player test | 26/35 | 0.6 | 60 | 7 |
| c120 | 120 non-sprite bullets | 26/35 | 1.2 | 120 | 4 |
| fo+c60 | ghost sprite shots + lean test, ghost lasers, float enemies, 60 non-sprite bullets | 73/103 | 19.4 | 96 | 7 |
| fcust | non-sprite shots + 60 non-sprite bullets, ghost lasers, float enemies | 43/53 | 12.3 | 96 | 5 |
| fc+120 | fcust with 120 non-sprite bullets | 47/56 | 13.3 | 156 | 4 |
| fopt9 | v4 fullopt anchor (9 ghost sprite bullets) | 91/103 | 23.8 | 45 | 5 |

fopt9 reproduces v4 fullopt (91). The summary's legend line "gc = ms of one full collection" is cut off on screen (too wide); cosmetic.

**Conclusions so far:**
- The device floor is ~26 ms (about 38 fps). **Work below ~26 ms per frame is hidden:** e14nov (5.6 ms of own code plus 14 moving sprites) is 26 ms, the same as an empty screen. So "ms over the floor" is NOT additive, and my earlier decompositions of the form
  "frame = 26 + own code + other" (in the v4 analysis) were wrong; the right reading is frame = max(~26, total work), with "other" = frame - own code. This removed most of the "unexplained ~40 ms" I reported after v4.
- **Rule of thumb that fits the data (UNSURE, fitted after the fact):** once the frame is over the floor, each live sprite costs about 0.7-1.3 ms per frame (draw + physics move; more when it is moving and in the grid), plus own code.
  Checks: bull60g 60 sprites x 0.7 + 5.7 code = 48 (measured 47); 30 moving sprites in v2 = 21 ms, hidden (measured 26); fcust ~23 sprites x 1.3 + 12.3 = 42 (measured 43); fo+b60 106 sprites x 1.2 + 28.5 = 156 (measured 158).
- **Non-sprite bullets and shots (integer arrays moved in a loop, drawn by one renderable) are 10-20x cheaper per object:** c60 and c120 sit on the floor; adding 60 more in a loaded frame (fcust 43 -> fc+120 47) costs ~4 ms, about 0.07 ms per bullet,
  against ~1.3 ms for a ghost sprite bullet in a loaded frame (fo+b60 vs fullopt: +51 sprites, +67 ms). 9 ghost sprite bullets (fopt9 91) are MORE expensive than 60 non-sprite bullets (fo+c60 73).
- **Non-sprite player shots:** csh+en 41 vs en+ghs2 61 (-20 ms); fo+c60 73 -> fcust 43 (-30 ms), with lower own code too (12.3 vs 19.4).
- **Best design so far:** `fcust` / `fc+120`: 14 enemies as sprites, 2 orbs + 2 ghost lasers as sprites, ~20 non-sprite shots, 60-120 non-sprite bullets: 43-47 ms (about 21-23 fps), against 91 ms for the all-sprite `fopt9` and ~499 ms for the game today.
  Estimate (UNSURE): with ~5 enemies instead of 14 it should be clearly better, maybe near 30-35 ms. The summary cannot show that the bullets were visibly drawn; fc+120 vs fcust (+4 ms, only ~1 ms of it own code) suggests they were. Check by eye in the game.
- **Not the cause, tested in v5:** (a) garbage collection: one forced full collection takes 4-8 ms regardless of what is alive (6 ms with nothing, 4 ms with 156 objects), so "GC grows with live objects" is refuted (how OFTEN GC runs is untested);
  (b) the collision grid is a smaller part than I thought: enemies with handlers cost ~7-8 ms (e14nov 26 vs enemy14 33; nov+gn 48 vs en+gnoh 56);
  (c) per-frame float steering and x/y reads: lazy steering (set velocity once per leg) saves only ~4 ms (52 vs 56), mostly own code.
- **Moving enemies cost much more than stationary ones:** stat+g 40 vs lazy+g 52 with the same sprites; ~12 ms for 14 enemies (~0.8 ms each). Keep the number of simultaneous enemies small and avoid sprites that do not need to move.
- Older findings that still hold: the engine analysis is confirmed quantitatively (25 shots in one cell, handlers on: 229 ms at step 4, 47 ms at step 16, ghost 30 ms at either); the v3 figure "about 1.2 ms per normal enemy bullet" is a loaded-frame sprite cost (9 bullets alone are free);
  the hit test is not the bottleneck (v3 +5.8 ms code, lean +4.4 ms); ghost lasers save ~6 ms (lasr-g 34 vs en+lasr 40).
- Python-side per-bullet code is cheap (60 bullets moved and tested in a Python loop: 0.6 ms of code in c60), so the design is "few sprites, many integers", not a wrapper/list refactor.

**Fix order (revised 2026-11-20, after v5):**
1. Max step 16 through `engine_step.ts` (listed first in pxt.json; hard-code `new ArcadePhysicsEngine(500, 2, 16)`, no settings needed). PROVEN. Matters less once shots and bullets are non-sprites, but it is harmless and still helps the enemy/item grid.
2. Enemy bullets as a non-sprite pool: parallel integer lists (x, y in 1/16 px, velocity, maybe a type index for the image), moved with integer maths using dt, drawn by ONE `scene.create_renderable`, manual box test against the player and a larger graze box. Bomb = loop the arrays and spawn star items.
   Reference code: `hardware-bench-v5/main.py` (`makeCustomBullets`, `tickCustomBullets`, `customBulletTest`, `drawCustom`, `ensureRenderable`). Put aimed/ring patterns in a function that appends to the pool (reuse free slots instead of growing lists).
3. Player shots as a non-sprite pool with the lean manual box test against enemy boxes (reference: `makeShotPool`, `customShotTick`, `hitTestCust`); damage stored in a parallel list; destroy the shot (clear its slot) on hit.
4. Lasers: 2 ghost sprites + manual rectangle test for now (saves ~6 ms vs normal sprites); later maybe draw them as rectangles in the renderable (saves 4 sprites).
5. Enemies stay sprites; keep the simultaneous count small; steer with time-based legs (lazy) instead of per-frame float maths. Items (stars/power) are sprites: cap them or make them non-sprite if many.
6. One game clock advancing at most 100 ms per frame for spawning, firing, route waits, bomb and invulnerability timers.
7. Optional: fire every ~167 ms at double damage if the frame rate is still low.

**Benchmark branches (all replace `main.py` with a standalone benchmark; master untouched; delete them when done):**
- `hardware-bench` v2 (commit 854203c): ran. Its commented-out engine line does not compile in Python.
- `hardware-bench-v3` (commits 65dd3b5, 7133294, 0eba952): ran on the device; A on the summary toggles the saved step (4/16) and restarts.
- `hardware-bench-v4` (commits d18e329 `engine_step.ts` default step 16, a441b15 `main.py`; 2026-11-20): compiled and ran; results above. 15 modes: nothing, base, enemy14, en+ghst, en+gnoh
  (ghost shots + enemies, no hit test), en+ghs2 (lean hit test), bull9 / bull9g (9 bullets normal vs ghost + manual test vs the player), bull60 / bull60g (60 bullets), en+lasr, lasr-g (ghost lasers + manual
  rectangle test), fullghst, fullopt (everything manual: ghost shots + lean hit test, ghost lasers, ghost bullets), fo+b60 (fullopt with 60 bullets). Default step 16; A toggles to 4 and back (the step 4 run was not done; optional).
- `hardware-bench-v5` (branched from v4 on 2026-11-20; commit a0ca406, main.py blob 8c001fba): compiled and ran on 2026-11-20, results above. 13 modes, 4 s warm-up + 10 s measuring each, about 3 minutes. Summary columns: mode | avg/worst ms | own code ms | n | gc ms.
  Mode names are at most 6 characters so the 26-character summary line fits the 160 px screen. "n" counts sprites plus non-sprite bullets/shots. "gc" = milliseconds for ONE forced `control.gc()` at the end of the mode with its objects still alive.
  Non-sprite objects are integers in 1/16 px moved with integer maths (`y += vy * dt * 2 // 125`) and drawn by one `scene.create_renderable(5, drawCustom)` handler (ignores camera shake; subtract `camera.draw_offset_x/y` if shake is wanted).
  Modes in the v5 file: none, base, e14nov, nov+gn, stat+g, lazy+g, csh+en, c60, c120, fo+c60, fcust, fc+120, fopt9 (see the table above for what each is).
- How the owner runs a benchmark: MakeCode editor, GitHub panel, switch to the branch (or Import URL with the branch address), Download to the gamekit, hands off for ~3.5 minutes, photograph the summary
  screen (columns: mode, avg/worst frame ms, own code ms, objects alive, and gc in v5; footer shows the physics step). If it does not compile, they screenshot the Problems panel.

## 8. Useful links

- Decompilation: https://github.com/GensokyoClub/th06 (`src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`)
- Boss HP / shot analysis thread: http://www.shrinemaiden.org/forum/index.php?topic=15824.0
- Sprite data extension: https://github.com/microsoft/arcade-sprite-data
- Arcade engine source: https://github.com/microsoft/pxt-common-packages (`libs/game/physics.ts`, `spritemap.ts`, `sprite.ts`, `scene.ts`, `basesprite.ts`)
- Rotation extensions (not used): `Marupio/arcade-cleanEdge` (best for pre-rendering rotated bullets at startup),
  `robo-technical-group/pxt-arcade-image-transform` (keeps per-sprite state that is never freed; avoid for bullets).
- MakeCode forum: Richard's Arcade Tips #6 (hitboxes and overlaps).

## 9. Web simulator (GitHub Pages) and releases

- The page https://lolmuele.github.io/touhou-calliope-gamekit/ (linked from README.md) runs a **prebuilt** file, `assets/js/binary.js`, loaded by `index.html` via `makeCodeRun`. Committing code does NOT rebuild it.
- That file (and `assets/version.txt`) is regenerated only when a **release** is created from MakeCode's GitHub window ("Commit & create release to update Pages").
  Pages then takes up to ~10 minutes, and browsers may need a hard refresh. (VERIFIED from MakeCode docs and forum threads.)
- VERIFIED state on 2026-11-13: the repo has no tags and no releases; `assets/js/binary.js` was last changed by the initial commit (2026-11-09); `assets/version.txt` is `0.0.0`.
  So the page shows the project as it was in the first commit.
- `.github/workflows/makecode-release.yml` only runs when a release is created and attaches UF2 builds (d51, f4, rpi) to the release. It does not deploy the Pages site. Which UF2 matches the Calliope gamekit is UNSURE.
- Claude's GitHub tools cannot create releases or tags, and `binary.js` is a compiled file that should not be edited by hand. The owner has to create the release in the MakeCode editor.
- README.md was rewritten by Claude on 2026-11-14 as an honest "early prototype" description (no screenshots, no license yet).

## 10. Code map of main.py on master (blob aff1521f; re-read the file to confirm before relying on details)

- File order: `class HUD`, a TODO comment block, `class Projectile`, `playerProjectile`, `redCircleProjectile`, `class Enemy`, `class Player`, global `i = 0`, `class Game`, then
  `gameObj = Game()` and `gameObj.mainLoop()` at the very end.
- `HUD`: keeps a base `hudImage` (`hudBackground` with "EOMD" printed on it), a sprite `background` (kind 999, z 999, at x 140), `buildHud(highScore, score, lives, bombs, power, graze, point)` clones the base image,
  prints labels/numbers with `image.font5`, draws star icons and the power bar (`fill_rect(6, 78, 28 * power // 128, 8, 9)`), and sets the sprite image; `buildGameOver(continues, yes)`; `gameOver(continues)` creates the overlay sprite.
- `Projectile`: `homeTo(x, y)` and `setAngle(angle)` (angle 0 = down, 180 = up, because y = cos). `playerProjectile(damage)` (kind 2, image `marisaShotImage2`, damage in sprite data, z -10, speed 250);
  `redCircleProjectile` (kind 3, image `redBall`, speed 30).
- `Enemy(spriteName, player, health = 950)`: sprite kind 4 (tile `marisa`, z 10), `projectiles` list, `route` (list of `[x, y, speed, waitMs, shootFlag]`), `goRoute()` with a `closeEnough` tolerance and wait timers, `shootHoming()`,
  `takeDamage(damage)` sets `dead` at 0 health.
- `Player`: hitbox sprite (image `hitboxImage`, kind 0) plus `skin` sprite (tile `marisa`, no kind given, see issue 13), `tier` 0-5, `power`, `health` 3, `bombs` 3, `lastHit`, `bombStart`, `lastShot`, `Lasers` flag with
  `spawnLasers(damage)` / `killLasers()` (two `miniHakkero` orbs and two kind-5 `marisaLaser` sprites, 8x120), `shoot()` fires a volley when `game.runtime() - lastShot >= 80` with the tier table from section 4,
  `bomb()`, `takeDamage()` (shake, flicker animation, i-frames), `movementController()` (speed 80, half while B is held with lasers).
- `Game`: `hud`, `player`, `enemies`, score/graze/continues, `collisionCheck()` registers four handlers once (all take Sprite args and use `gameObj`): `(4, 2) enemyDamaged` (finds wrapper by sprite scan, applies damage from the
  sprite's data), `(0, 3) playerDamaged` (i-frames 3000 ms and bomb invulnerability), `(0, 6) itemCollected` (reads data "type", 0 = star), `(4, 5) enemyHitByLaser` (damage * 40 // 16 per overlap frame).
  Other methods: `frametimes(t1, t2)` (shows own-code us and frame ms in a bubble every 60 frames), `projectileDestructor()` (removes shots/bullets/enemies that left the screen, loops backwards for shots and bullets),
  `addScore`, `bombActive(first)` (turns enemy bullets into star items kind 6 with data type 0, `follow(player, 200)`), `waves()` (spawns a test enemy every 1200 ms), `enemyActions()`, `redrawHud()`, `gameOver()`, `mainLoop()`
  (registers `onUpdate`, which runs movement, destructor, shooting, enemies, waves, bomb trigger, game over check, HUD redraw and `frametimes`).
- Sprite kinds: 0 player hitbox (and maybe skin), 1 test projectile (unused), 2 player shot, 3 enemy bullet, 4 enemy, 5 laser, 6 item, 999 HUD. Benchmarks also use 97, 98, 99.
- Image names used: `hudBackground`, `stageBackground` (flat tan, unused now), `gameOver`, `marisaShotImage2`, `redBall`, `marisaLaser`, `miniHakkero`, `starItem`, `livesStar`, `bombsStar`, `hitboxImage`, `masterSpark` (unused);
  tiles: `marisa`, `damageFlicker`, `projectile`, `hitbox`, older `redBall`/`marisaShot`.
- Repo files besides code: `README.md`, `NOTES.md`, `pxt.json` (custom palette), `images.g.jres`, `tilemap.g.jres`, `assets.json` (empty), `main.blocks` (placeholder), `_history` (MakeCode editor history),
  Pages template files (`index.html`, `_config.yml`, `Gemfile`, `Makefile`), `.github/workflows/makecode-release.yml`.
