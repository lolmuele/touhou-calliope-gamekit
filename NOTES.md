# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written by Claude on 2026-11-13 from a long chat with the project owner. Sections 6-7 refreshed on 2026-11-16 after
re-reading main.py blob aff1521f; the first hardware results and the engine analysis (section 2 and 7) were added the same day.
Section 9 (web simulator) added 2026-11-13.
Claude has no memory between chats. To resume: open a new chat, connect the
GitHub connector, and say "read NOTES.md and main.py in lolmuele/touhou-calliope-gamekit".

Everything here is marked as one of: VERIFIED (read in source/docs or seen in the
repo), MEASURED (owner observed it), or UNSURE (my belief, check before relying on it).

---

**Standing permission (owner, 2026-11-13):** Claude may edit this file whenever it sees fit, without asking. Scope is this file only. Other files in the repo are only changed when the owner asks.

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
- `sprites.set_data_number` / `read_data_number` come from the **extension**
  `microsoft/arcade-sprite-data` (already added to this project).
- Tiles and images are the same format (VERIFIED by decoding the jres). Tiles are 16x16; images can be any size.
  Sprites draw 1:1 on the 160x120 screen.
- `assets.image(...)` may return a shared image (UNSURE). HUD code clones it before drawing.
- On-screen console output is slow on the Calliope (MEASURED, frame time crept to 65+ ms with it on).
  Don't print in hot paths. Show diagnostics with `sprite.say_text(...)` instead.
- Simulator frame time is ~20-23 ms because the loop sleeps to a ~20 ms floor (forum sources disagree
  between 30 and 50 Hz, both say capped). It does NOT measure your code's cost. `control.micros()` works.
- Hardware was ~40 ms per frame with the test projectile spray enabled (MEASURED, earlier session).
- Image literals in the jres store palette **indices**, not colors. Changing a palette hex recolors all art.
- Sprite `z` is draw order; the 2nd arg of `sprites.create` is the *kind*, not a layer. Changing `z` sets a flag so the scene
  re-sorts all sprites (full sort with a callback) before the next draw (VERIFIED in basesprite.ts / scene.ts, pxt-common-packages v14.1.7).
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
  some registered overlap handler. So the cost only exists once `sprites.on_overlap` has been called for those kinds.
- Grid: cell size = clamp(8, areaSize/4, 2 x largest sprite) = 40x30 px on this 160x120 screen (16 cells). The grid is cleared once per
  frame, but moving sprites are re-inserted every sub-step and are never removed from the cells they pass through.
- Every overlap event is run with `control.runInParallel` (its own thread), and fires again each frame the sprites still overlap.
- A one-line mitigation exists: construct `ArcadePhysicsEngine(500, 2, 16)` (bigger max step) before any sprite is created and assign it
  to the scene's physics engine (the report's Fix 1). UNSURE whether the Python spelling compiles. `maxStep` also has a setter.
- `scene.createRenderable(z, handler(target, camera))` and `camera.drawOffsetX/Y` exist (used by the tilemap code), so things can be drawn
  without being sprites.

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
   Hardware-friendly option: fire every ~167 ms at double damage (same dps, half the sprites).
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
  Keep a constant cap on bullets alive until hardware numbers are in.
- B3. Boss HP bar: a thin image sprite at the top, redrawn only when HP changes.
- B4. Phase change: clear bullets into stars (reuse `bombActive` logic), short invulnerability, `isSpell` flag applying
  the /7 damage rule, optional timer and spell name text.
- B5. Movement: reuse the existing `route` system, looping.
- B6. Intro, death, item drops, stage clear.
Suggested order of work: link `tier` to `power` and add power/point item drops from kills
(makes the HUD power bar meaningful) -> smallest boss -> hardware test results decide the bullet refactor.
NOTE (2026-11-16): the hardware results in section 7 say sprite collision cost is the dominant problem, so bosses/dense patterns
must wait until the engine-side fixes in section 7 are tried.

## 6. State of the code (last read: main.py blob aff1521f on master, 2026-11-16) and known issues

Done: HUD with live power bar and a dirty flag that now resets (`redrawHud` clears `hudChanged`); game over screen with
continue; player i-frames; time-based shooting; tiered shot with lasers (laser damage fixed, no longer 0); one test enemy
(950 HP) that spawns every 1.2 s and flies the same hard-coded route firing aimed shots; bombs that turn enemy bullets into
stars (trigger requires bombs > 0 and a 6000 ms gap); star collection; palette; sprites cropped to small images; stage
background is `scene.set_background_color(6)`; debug prints, `info.show_score` and `game.stats` removed; bullet lists
iterated backwards; frame interval and own-code time are measured in `frametimes` (average now divides by 60).

Known issues (priority order):
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
9. Laser art is 8x120 (two sprites, ~1920 px/frame); narrowing to ~4 px halves that and is closer to EoSD's scaled width.
10. Focus (hold B) only slows movement when lasers exist (`B and self.Lasers`), so at tier 0 it does nothing.
11. Real-time timers (`game.runtime()`) are used for spawning, firing and route waits, but physics time is capped at 100 ms per frame.
    At 200-300 ms frames the world moves in slow motion while enemies still spawn at full rate, so enemies pile up (14 alive in M3),
    which slows the game further. Fix: one game clock advancing at most 100 ms per frame.

## 7. Performance plan and the hardware test

Image sizes (decoded): player shot 8x8, enemy orb (miniHakkero) 8x8, laser 8x120, star 5x5, masterSpark 47x120,
HUD 40x120, gameOver 120x120. Fixed draw cost now: HUD 4800 px, lasers 1920 px, shots 20-35 x 64 px.

**Hardware test harness: branch `hardware-test`** (created 2026-11-16, owner asked for it to be removable and to leave master unchanged).
- Master is untouched. The branch is master plus one commit (b3d40e3) that only APPENDS a block at the end of `main.py`, between
  `HWTEST-BEGIN` and `HWTEST-END` markers (VERIFIED from the commit stats: 138 additions, 0 deletions). Remove it by deleting the
  branch, or by deleting the block. It compiled and ran on the device.
- Behavior: after the first frame it takes over. **A cycles the mode (0-4)**; bombs are disabled (bombs forced to 0) and the player
  can't be hit (`lastHit` refreshed every frame). Each mode change clears all enemies and bullets, resets the player to bottom centre,
  and restarts the harness's measurement window (the owner's own `frametimes` window is NOT reset, so its `ft:` and part of its
  own-code number straddle two modes; trust the harness's M-line for frame time).

| Mode | Shot tier | Lasers | Enemies | HUD |
|---|---|---|---|---|
| 0 | 0 | off | off | shown (engine baseline) |
| 1 | 5 | off (1x1 invisible stand-ins stop real lasers spawning) | off | shown |
| 2 | 5 | on | off | shown |
| 3 | 5 | on | on | shown (the real game) |
| 4 | 5 | on | on | hidden (`SpriteFlag.INVISIBLE`) |

- Display, refreshed every 60 frames: upper bubble `M<mode> <avg frame ms>/<worst frame ms> c<own onUpdate us>`;
  lower bubble `s<shot sprites>/<shots in list> b<enemy bullets> e<enemies> t<seconds in this mode>`.
  If `s` and the list count drift apart, something leaks.

**MEASURED results (owner's photos, 2026-11-16; one reading per mode, 12-28 s after the mode started; files mode1-5.jpg = modes 0-4):**

| Mode | avg / worst frame ms | ~fps | own code | shots | bullets | enemies |
|---|---|---|---|---|---|---|
| 0 | 27 / 38 | 37 | 1.3 ms | 6 | 0 | 0 |
| 1 | 206 / 255 | 5 | ~12.7 ms | 25 | 0 | 0 |
| 2 | 246 / 268 | 4 | ~13 ms | 25 | 0 | 0 |
| 3 | 328 / 580 | 3 | 12.6-22.6 ms | 29 | 9 | 14 |
| 4 | 324 / 541 | 3 | 21.5-26.8 ms | 28 | 9 | 14 |

(own-code numbers disagree between the harness and the owner's bubble in modes 1, 3, 4 because of the unreset window; ranges shown.)

**Current best explanation (2026-11-16).** The owner's friend had another AI write a performance report (PDF, not in the repo). I checked its
central claims against the engine source (facts in section 2) and they hold: collision work scales with the number of sprites sharing a grid
cell squared, times the number of physics sub-steps, and sub-steps grow with frame time up to the 100 ms cap, which makes a feedback loop.
It fits the data: the five-way spread keeps ~25 shots in one 40 px column cell; two 120 px lasers join those cells (+2 sprites on 25 is
about +17% pair work, measured +19%: 206 -> 246 ms); hiding the HUD changes nothing. What is still UNSURE: the per-pair cost, the share
of garbage collection (worst-frame spikes of 541/580 ms in modes 3/4 hint at it), the chip, and how much the baseline 27 ms is screen transfer.
Unverified claims in that report: the hitbox pixel scan on `sprites.create`, the exact `eventcontext.ts` line for the 20 ms sleep, and that
`HitboxOverlaps` exists in this version. Its Fix 1 tunnelling argument uses bounding boxes, but overlaps are pixel-perfect and the player
hitbox is tiny, so a 16 px max step could let thin sprites slip through at very low frame rates.

**Fix order (agreed idea, nothing applied yet):**
1. One line: a physics engine with a bigger max step, e.g. `ArcadePhysicsEngine(500, 2, 16)` (8 is a safer first try: 1 sub-step at normal
   frames, 4 at the cap), set before any sprite is created. Measure, then check for shots or bullets passing through things.
2. A game clock that advances at most 100 ms per frame, used for spawning, firing, route waits, bomb and invulnerability timers.
3. Only if still needed: player shots as plain numbers in lists (fixed point, swept box test against enemy boxes, drawn from a
   `scene.createRenderable` callback that subtracts `camera.drawOffsetX/Y`). Big rewrite; the owner wants to write it themselves.
4. Small: `break` in `enemyHitByLaser`, narrower lasers, don't set `z` on every new sprite.
5. Last resort: three streams instead of five, or one volley every ~167 ms at double damage.
(That report's PDF has clipped code lines at the right margin, so don't copy its example verbatim.)

**Benchmark branch `hardware-bench`** (commit 9a00c1e, created 2026-11-16, replaces `main.py` with a standalone sprite-cost benchmark; master untouched;
UNSURE it compiles, not run yet). Runs 15 modes automatically (4 s warm-up + 10 s measure each, ~3.5 min), then shows one summary screen
(mode, avg/worst frame ms, own code ms, sprites alive). A skips a mode; A on the summary restarts. Modes: 0 nothing, 1 hud+player,
2 bubbles, 3 static30, 4 move30, 5 spawn (plain sprites created/destroyed, 5 per 80 ms, `lifespan` 450), 6 +data, 7 +z, 8 +Python wrapper/list/loop,
9 all of the game's shot pattern, 10 same with 4 overlap handlers registered (they stay registered), 11 lasers8, 12 lasers4, 13 enemy14, 14 full.
Prediction from the engine source: because `spriteCollisions` returns immediately and sprites are not inserted into the grid until overlap
handlers exist, modes 3-9 should stay cheap and the big jump should appear at mode 10. If modes 5-9 are already slow, the theory is wrong.
To test Fix 1 on the bench, flash it a second time with the engine line added as the first line of `main.py` and compare modes 10-14.

Procedure used for the earlier test: do not touch the D-pad; photograph the screen after the readings settle. Reboot the device first
(`control.micros()` may wrap after a long uptime, UNSURE). Still to do: the 3-minute run in mode 3 of `hardware-test`.
After testing is finished, delete the `hardware-test` and `hardware-bench` branches.

## 8. Useful links

- Decompilation: https://github.com/GensokyoClub/th06 (`src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`)
- Boss HP / shot analysis thread: http://www.shrinemaiden.org/forum/index.php?topic=15824.0
- Sprite data extension: https://github.com/microsoft/arcade-sprite-data
- Arcade engine source: https://github.com/microsoft/pxt-common-packages (`libs/game/physics.ts`, `spritemap.ts`, `scene.ts`, `basesprite.ts`)
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
