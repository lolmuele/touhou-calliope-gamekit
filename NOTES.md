# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written by Claude on 2026-11-13 from a long chat with the project owner. Section 5-7 refreshed by Claude on
2026-11-13 (second session) after re-reading main.py blob 740e28a1. Section 9 (web simulator) added the same day.
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
- Overlap events fire every frame two sprites overlap (UNSURE on exact semantics, but behavior matches).
  Overlaps are pixel-perfect per a MakeCode forum post (Richard's Arcade Tips #6), so transparent padding
  does not enlarge hitboxes.
- Tiles and images are the same format (VERIFIED by decoding the jres). Tiles are 16x16; images can be any size.
  Sprites draw 1:1 on the 160x120 screen. Smaller images draw faster (fewer pixels) (UNSURE on exact cost).
- `assets.image(...)` may return a shared image (UNSURE). HUD code clones it before drawing.
- On-screen console output is slow on the Calliope (MEASURED, frame time crept to 65+ ms with it on).
  Don't print in hot paths. Show diagnostics with `sprite.say_text(...)` instead.
- Simulator frame time is ~20-23 ms because the loop sleeps to a ~20 ms floor (forum sources disagree
  between 30 and 50 Hz, both say capped). It does NOT measure your code's cost. `control.micros()` works.
- Hardware was ~40 ms per frame with the test projectile spray enabled (MEASURED).
- Image literals in the jres store palette **indices**, not colors. Changing a palette hex recolors all art.
- Sprite `z` is draw order; the 2nd arg of `sprites.create` is the *kind*, not a layer.
- `sprites.destroy` the sprite AND remove the wrapper from any Python list, or it leaks.

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
Suggested order of work: fix `hudChanged` reset -> link `tier` to `power` and add power/point item drops from kills
(makes the HUD power bar meaningful) -> smallest boss -> hardware test.

## 6. State of the code (last read: main.py blob 740e28a1, 2026-11-13) and known issues

Done: HUD with live power bar and dirty flag; game over screen with continue; player i-frames; time-based shooting;
tiered shot with lasers (laser damage fixed, no longer 0); enemies with routes and homing shots; bombs that turn enemy
bullets into stars (bomb trigger now requires bombs > 0 and cooldown); star collection; palette; sprites cropped to
small images (`redBall` is now an image); stage background is `scene.set_background_color(6)`; debug prints,
`info.show_score` and `game.stats` removed; player and enemy bullet lists are iterated backwards; frame interval is shown.

Known issues (priority order):
1. **`hudChanged` is never reset to False.** `onUpdate` does `if self.hudChanged: self.redrawHud()` and nothing clears the
   flag, so after the first score/hit/bomb the HUD is cloned and redrawn (about 8 text prints) EVERY frame. One-line fix:
   set it back to False after redrawing. Do this before the hardware test.
2. Bomb constants disagree: the trigger checks `>= 6000` but `bomb()` requires `> 6100`. In the 6000-6100 ms window
   `bombActive(first=True)` runs without spending a bomb (free clear). `playerDamaged` uses 6200 for invulnerability.
   Define one constant.
3. `enemyHitByLaser` damage is tuned for 40 ms frames (see section 5, step 4).
4. Enemy removal loop in `projectileDestructor`: `i += 1` runs after a removal, so the index drifts; dead enemies waiting for
   bullets get `sprites.destroy` every frame; offscreen-alive enemies keep running `goRoute`. The test-projectile list loop
   is still forward (list is unused).
5. `playerDamaged` calls `takeDamage()` even if no bullet was found; mixes `self` and `gameObj`.
6. Game over: continues can go negative; sprites keep moving and overlaps still fire while the game over screen is up.
7. Undeclared attributes: `Enemy` (`xVel`, `yVel`, `maxSpeed`), `Game` (`lastUpdateStart`, `frameAverage`, `average`, `yes`).
8. `frametimes`: divides the frame average by 59 when the list has 60 entries, and `frameAverage` is undefined on the first display.
9. `self.tier = 5` and `Player.power = 0` are test values; the HUD power bar does not follow the tier.
10. Only `starItem` drops/collects; enemies drop nothing when killed.
11. Laser art is 8x120 (two sprites, ~1920 px/frame); narrowing to ~4 px halves that and is closer to EoSD's scaled width.

## 7. Performance plan and the hardware test protocol

Image sizes (decoded): player shot 8x8, enemy orb (miniHakkero) 8x8, laser 8x120, star 5x5, masterSpark 47x120,
HUD 40x120, gameOver 120x120. Fixed draw cost now: HUD 4800 px, lasers 1920 px, shots 20-35 x 64 px.

Optional bigger refactor (not done): drop Python wrapper objects and lists for bullets. Damage is already stored in
sprite data, so `enemyDamaged` can read it and destroy `projSprite` directly; let the engine delete offscreen
sprites with `SpriteFlag.AUTO_DESTROY` (UNSURE of exact name, check autocomplete); `bombActive` can use
`sprites.all_of_kind(3)`; `setAngle`/`homeTo` become plain functions taking a sprite. Pooling sprites is a later step if
frame time shows garbage-collection spikes (high max with normal average). Boss patterns will multiply bullets, so decide
on this refactor before adding dense patterns.

Instrumentation (partly done): frame interval average and own-code average are shown with `say_text` (using lists; running sums
would avoid allocation). Still to add: worst single frame, sprite counts, `TEST_MODE`.
- Sprite counts: `len(sprites.all_of_kind(k))` for kinds 2, 3, 4, plus `len(player.projectiles)`.
- `TEST_MODE` constant at the top of main.py (one flash per mode).

| Mode | Tier | Lasers | Enemy spawns |
|---|---|---|---|
| 0 | 0 | off | off |
| 1 | 5 | off | off |
| 2 | 5 | on | off |
| 3 | 5 | on | on (the real game) |
| 4 | 5 | on | on, HUD sprite hidden (`SpriteFlag.INVISIBLE`) |

Procedure: player still at bottom center, no B, no A, no bomb, no console output. Record frame ms / max ms /
own us / shots / bullets / enemies at 10 s, 20 s and 30 s. A rising reading means something accumulates.
Plus one 3-minute run of mode 3 with readings at 0:30, 1:00, 2:00, 3:00 and list-vs-sprite counts. Reboot the device first
(`control.micros()` may wrap after a long uptime, UNSURE). Fix the `hudChanged` bug first so the HUD isn't redrawn every frame.
Report back as a table plus whether the slowness felt steady or jerky. The owner expects to have hardware access in a week or so
(as of 2026-11-13).

## 8. Useful links

- Decompilation: https://github.com/GensokyoClub/th06 (`src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`)
- Boss HP / shot analysis thread: http://www.shrinemaiden.org/forum/index.php?topic=15824.0
- Sprite data extension: https://github.com/microsoft/arcade-sprite-data
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
