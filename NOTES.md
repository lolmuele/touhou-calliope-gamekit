# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written and maintained by Claude (the owner's assistant in a long chat that started 2026-11-13). Last full handoff rewrite: 2026-11-20.
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
  a README, the GitHub Pages explanation, and a long series of **hardware performance tests** that found and confirmed the cause of the very low frame rate (section 7).
- The owner wants to understand things and write the code themselves. They bring me screenshots/photos and ask for diagnosis, plans, tests and notes.

### 0.2 First steps in a new chat
1. Read this whole file. Do not summarise it back at length; the owner knows it.
2. Use the GitHub connector: list branches, list the latest commits, read `main.py` on `master` (compare its blob sha with section 6; if it changed, refresh sections 6 and 10).
3. Look for new files on `master` (for example `engine_step.ts`) and on the benchmark branches.
4. Ask the owner (one short question) what happened since: did they run benchmark v4, did they start the game fixes, did anything fail to compile?
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
- When the owner sends photos of the Calliope screen, read them carefully: perspective can shift the right-hand columns by a row, glare can hide digits; state what is uncertain.
- After doing work in the repo, tell the owner in a few lines what changed and give the commit link.

### 0.4 How to work with the repo and tools
- Read with `get_file_contents` (a directory path lists files with blob shas). Write with `create_or_update_file`: it replaces the WHOLE file and needs the current blob sha, so copy the file exactly,
  then verify with `get_commit` (include_diff) that only the intended lines changed.
- Experiments go on branches. `master` only gets NOTES.md updates, and the README (written on request). Never push game code to `master` unless asked.
- The tools cannot create releases or tags. MakeCode compiles only in the owner's browser; I cannot compile. Never claim code compiles unless the owner ran it.
- I can read other public repos (for example `microsoft/pxt-common-packages`, `GensokyoClub/th06`). Check engine claims against the source instead of guessing. `web_search` is for docs and forum posts.
- Keep this file accurate: update it after anything settled (results, decisions, new branches, new gotchas). Rewrite the whole file with the latest sha, keep all sections, mark confidence.

### 0.5 Where things stand (2026-11-20)
- **Cause of the slow game is known and confirmed on hardware** (section 7): the Arcade physics engine's collision scan with ~25 player shots crowded into one grid cell, repeated per physics sub-step.
- Two fixes are PROVEN on the device: (1) physics max step 16 through a TypeScript file (`engine_step.ts`), (2) player shots flagged ghost-through-sprites with a manual hit test.
  Together they take the game-like test from ~499 ms to ~103 ms per frame. That is still too slow (the bare device floor is ~26 ms), and ~50 ms of the rest is not yet explained.
- Enemy bullets as normal sprites looked expensive in benchmark v3 (~1.2 ms each). **Benchmark v4 is built and waiting for the owner to run it** (section 7).
- The game on `master` has none of the performance fixes yet. The owner intends to write them themselves.

### 0.6 Next steps / what we are waiting on (in order)
1. The owner runs `hardware-bench-v4` and posts the summary photo(s). Interpret them (section 7 lists the questions), record the numbers in section 7, and decide the design for enemy bullets, lasers and the hit test.
2. The owner applies the proven fixes in the game: add `engine_step.ts` (hard-coded 16, listed first in `pxt.json`), flag shots `GHOST_THROUGH_SPRITES`, replace the `enemyDamaged` overlap with a lean manual box test.
   (Offered, not done: I can add `engine_step.ts` and the `pxt.json` line to a game branch if asked.) After that, re-run `hardware-test` modes on the game to confirm.
3. Fix the other known issues in section 6 (bomb constants, game clock, laser damage per frame, enemy removal loop, undeclared attributes).
4. Link `tier` to `power` and add item drops, then the smallest boss (section 5). Dense boss patterns need the bullet design from step 1.
5. Housekeeping: delete the `hardware-*` branches when done; create a release in MakeCode when the owner wants the web simulator updated (section 9); no license is set yet (ask if they want MIT); the README has no screenshots yet.

### 0.7 Branch inventory (all benchmark branches REPLACE `main.py`; master is untouched)
- `master`: the real game, README.md, NOTES.md.
- `hardware-test`: game + removable test harness block at the end of `main.py` (A cycles modes 0-4). Ran on the device.
- `hardware-bench`: benchmark v2 (18 modes). Ran. Its commented-out engine line does not compile in Python.
- `hardware-bench-v3`: benchmark with `engine_step.ts` and a saved step setting (A toggles 4/16 and restarts). Ran on the device.
- `hardware-bench-v4`: benchmark with bullet/laser/hit-test isolation modes and an all-manual `fullopt` design, default step 16. NOT run yet.

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
- `scene.createRenderable(z, handler(target, camera))` and `camera.drawOffsetX/Y` exist (used by the tilemap code), so things can be drawn without being sprites. `sprites.Flag.HitboxOverlaps` exists in current sprite.ts.
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
1. `Enemy.takeDamage(amount)` and per-projectile `damage` (DONE: damage lives in sprite data).
2. Fire on timestamps, not frames: every 80-83 ms (DONE roughly; `lastShot = now`). Better: add to the timestamp so the average rate stays exact at 40 ms frames.
   Hardware-friendly option: fire every ~167 ms at double damage (same dps, half the sprites; MEASURED: helps a lot in the crowded-cell case).
3. Tier table keyed off `self.power` (tiers 0-5 DONE as `self.tier`; still set manually; should come from power).
4. Laser tick: damage = laser_dps x elapsed seconds, where laser_dps = (dmg per frame) x 60 (180 / 240 / 300 / 360 per laser). Clamp elapsed to ~100 ms. Keep a timer per (enemy, laser).
   Current code uses `damage * 40 // 16` per overlap frame, tuned for 40 ms frames; it deals half the dps at 20 ms frames.
5. Boss phases: list of HP values, `isSpell` flag applying the /7 rule. See the boss plan below.
6. Items: only `starItem` is handled; the rest of the item table is TODO.
Sanity check: a 1600 HP spell phase should take ~7 s at tier 5 and ~19 s at tier 0 (if everything hits).

**Boss plan (agreed idea, small steps; none done yet).** Milestone "smallest boss" = one phase, one ring pattern, HP bar, stage clear.
- B1. Reuse `Enemy`: add a `phases` list of HP values and `phaseIndex`; when health hits 0 and another phase exists, advance instead of setting `dead`.
- B2. One hard-coded pattern: a function that fires a ring of N bullets with `setAngle` (parameters: count, speed, angle offset). Keep a constant cap on bullets alive until hardware numbers are in.
  Enemy bullets as normal sprites in the collision grid looked expensive in benchmark v3 (about 1.2 ms each, see section 7); benchmark v4 tests ghost bullets with a manual test against the player.
- B3. Boss HP bar: a thin image sprite at the top, redrawn only when HP changes.
- B4. Phase change: clear bullets into stars (reuse `bombActive` logic), short invulnerability, `isSpell` flag applying the /7 damage rule, optional timer and spell name text.
- B5. Movement: reuse the existing `route` system, looping.
- B6. Intro, death, item drops, stage clear.
Suggested order of work: fix the collision cost first (section 7), then link `tier` to `power` and add power/point item drops from kills (makes the HUD power bar meaningful), then the smallest boss.

## 6. State of the code (last read: main.py blob aff1521f on master, 2026-11-16) and known issues

Done: HUD with live power bar and a dirty flag that now resets (`redrawHud` clears `hudChanged`); game over screen with continue; player i-frames; time-based shooting; tiered shot with lasers
(laser damage fixed, no longer 0); one test enemy (950 HP) that spawns every 1.2 s and flies the same hard-coded route firing aimed shots; bombs that turn enemy bullets into stars
(trigger requires bombs > 0 and a 6000 ms gap); star collection; palette; sprites cropped to small images; stage background is `scene.set_background_color(6)`; debug prints,
`info.show_score` and `game.stats` removed; bullet lists iterated backwards; frame interval and own-code time are measured in `frametimes` (average divides by 60).

Known issues (priority order):
0. **Performance (see section 7): the game has none of the proven fixes yet (max step 16 via engine_step.ts, ghost shots with a manual hit test). Best measured combination of both is still ~103 ms for the game-like case.**
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
12. Enemy steering costs ~5 ms of own code for 14 enemies on the device (benchmark `enemy14`); fine for now.
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

**Conclusions so far:**
- The device floor is ~26 ms (about 38 fps). Sprites existing, moving, being created/destroyed at ~60/s, having data, `z` or Python wrapper objects add only ~0-4 ms.
  Draw cost, garbage collection, data objects, `z`, Python loops, bubbles and the HUD are all small.
- **The engine analysis is confirmed quantitatively.** With 25 shots in one cell and overlap handlers registered, max step 4 gives ~229 ms; max step 16 gives 47 ms (4.9x),
  matching my prediction (~23 ms per collision scan, one scan per frame at step 16 = 26 + ~23). Ghost shots give 30 ms at either step.
- At step 16, adding pieces to enemy14 (33 ms): two normal lasers +5 ms; 9 normal enemy bullets **+11 ms** (about 1.2 ms per bullet, even though they are slow and spread out);
  25 ghost shots + the manual hit test +29 ms (own code +11, engine +18). UNEXPLAINED: why grid bullets cost that much when 14 enemies cost ~1.6 ms of engine time, and why ghost shots
  cost engine time only when enemies exist. Sub-step count matters even for ghost shots (en+ghst 88 at step 4 vs 62 at step 16).
- **Best measured full case (step 16 + ghost shots + manual hit test) is still 103 ms (~10 fps)**: ~26 floor + ~24 own code (the v3 hit test is ~10-16 ms of that) + ~53 engine. Not good enough.
- If bullets in the grid really cost ~1.2 ms each, a boss pattern with 100 bullets would cost over 100 ms. Benchmark v4 tests this directly.
- Python-side per-bullet code is NOT the main problem, so the wrapper/list refactor is not worth doing for speed, but the hit-test loop is worth making leaner.

**Fix order (revised 2026-11-20):**
1. Max step 16 through `engine_step.ts` (listed first in pxt.json; hard-code `new ArcadePhysicsEngine(500, 2, 16)`, no settings needed). PROVEN. Check tunnelling (overlaps are pixel-perfect, tiny player hitbox).
2. Player shots as ghost-through-sprites plus a manual swept box test against enemy boxes (replaces the `enemyDamaged` overlap). PROVEN for the shot part. Make the hit test lean
   (benchmark v4 `hitTest2`: margins pre-added to the boxes, local variables, while loop).
3. Enemy bullets and lasers: decide from benchmark v4 (ghost + manual test against the player / manual rectangle test vs the normal sprite versions) before building boss patterns.
4. One game clock advancing at most 100 ms per frame for spawning, firing, route waits, bomb and invulnerability timers.
5. Halve the shot count if still needed (fire every ~167 ms at double damage); small items: `break` in `enemyHitByLaser`.

**Benchmark branches (all replace `main.py` with a standalone benchmark; master untouched; delete them when done):**
- `hardware-bench` v2 (commit 854203c): ran. Its commented-out engine line does not compile in Python.
- `hardware-bench-v3` (commits 65dd3b5, 7133294, 0eba952): ran on the device; A on the summary toggles the saved step (4/16) and restarts.
- `hardware-bench-v4` (commits d18e329 `engine_step.ts` default step 16, a441b15 `main.py`; 2026-11-20; UNSURE it compiles, not run yet). 15 modes: nothing, base, enemy14, en+ghst, en+gnoh
  (ghost shots + enemies, no hit test), en+ghs2 (lean hit test), bull9 / bull9g (9 bullets normal vs ghost + manual test vs the player), bull60 / bull60g (60 bullets), en+lasr, lasr-g (ghost lasers + manual
  rectangle test), fullghst, fullopt (everything manual: ghost shots + lean hit test, ghost lasers, ghost bullets), fo+b60 (fullopt with 60 bullets). Default step 16; A toggles to 4 and back.
  Questions it answers: is a grid bullet expensive even uncrowded; how much of en+ghst is the hit test; do laser events matter; how close does an all-manual design get to the ~26 ms floor and does a boss-like 60 bullets fit.
- How the owner runs a benchmark: MakeCode editor, GitHub panel, switch to the branch (or Import URL with the branch address), Download to the gamekit, hands off for ~3.5 minutes, photograph the summary
  screen (columns: mode, avg/worst frame ms, own code ms, sprites alive; footer shows the physics step). If it does not compile, they screenshot the Problems panel.

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
