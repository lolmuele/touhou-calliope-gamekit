# Touhou (EoSD-style) for the Calliope gamekit: working notes

Written by Claude on 2026-11-13 from a long chat with the project owner.
Claude has no memory between chats. To resume: open a new chat, connect the
GitHub connector, and say "read NOTES.md and main.py in lolmuele/touhou-calliope-gamekit".

Everything here is marked as one of: VERIFIED (read in source/docs or seen in the
repo), MEASURED (owner observed it), or UNSURE (my belief, check before relying on it).

---

## 1. Project and working style

- MakeCode Arcade, **Python** editor (preferredEditor: pyprj), target Arcade 4.1.x, runs on the
  Calliope gamekit. `main.ts` is just the generated transpile; `main.py` is the source of truth.
- Screen is 160x120. Stage area is 120x120 (x 0-120). HUD panel is 40x120 (x 120-160).
- The owner wants to understand problems, not receive vibe-coded dumps. Explain the issue, point at
  the fix, and let them write it. They ask again if stuck. When they ask for code, give it.
- The owner is colorblind (blue vs purple is hard). Name colors by hex and give previews.
- Owner said not to comment on the unfinished game-over mechanic unless asked (this was early on).
- Hardware tests are rare. Make each session count (see section 7).

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
5. Boss phases: list of HP values, `isSpell` flag applying the /7 rule.
6. Items: only `starItem` is handled; the rest of the item table is TODO.
Sanity check: a 1600 HP spell phase should take ~7 s at tier 5 and ~19 s at tier 0 (if everything hits).

## 6. State of the code (last read: main.py blob 859edea5, 2026-11-13) and known issues

Done: HUD with live power bar; game over screen with continue; player i-frames; time-based shooting;
tiered shot with lasers; enemies with routes and homing shots; bombs that turn enemy bullets into stars;
star collection; palette; sprites cropped to small images; stage background is `scene.set_background_color(6)`.

Known issues (priority order):
1. **Laser damage is always 0**: `damage // 16.6 * 40` floors before multiplying. Use `damage * 40 / 16.6`
   (or the elapsed-time formula in section 5).
2. `redrawHud()` clones a 40x120 image and prints ~8 strings. It runs every frame while A is held and once per star
   collected. Use a dirty flag and redraw at most once per frame.
3. Bomb trigger: `bombActive(first=True)` and `redrawHud()` run whenever A is pressed with bombs > 0, even during
   the 6.1 s cooldown, because `bomb()` doesn't report whether it fired. Make `bomb()` return True/False.
4. Bomb constants disagree (6000 effect / 6100 cooldown / 6200 invulnerability); define once.
5. `projectileDestructor` removes from lists inside forward `range` loops (skips every other removed item), and the
   enemy loop's index `i` drifts after a removal. A dead/offscreen enemy has `sprites.destroy` called every frame
   until its bullets are gone, and offscreen-alive enemies keep running `goRoute`.
6. `playerDamaged` calls `takeDamage()` even if no bullet was found; handler mixes `self` and `gameObj`.
7. Game over: continues can go negative; `redrawHud` after continue; sprites keep moving and overlaps still fire
   while the game over screen is up.
8. Undeclared attributes in `Enemy` (`xVel`, `yVel`, `maxSpeed`) and `Game` (`average`, etc).
9. `self.tier = 5` and `Player.power = 0` are test values.
10. `info.show_score(True)` and `game.stats = True` do nothing useful; remove.
11. Enemy bullet `redBall` image may still be larger than needed. Laser art is 8x120 (two sprites, ~1920 px/frame);
    narrowing to ~4 px halves that and is closer to EoSD's scaled width.

## 7. Performance plan and the hardware test protocol

Image sizes (decoded): player shot 8x8, enemy orb (miniHakkero) 8x8, laser 8x120, star 5x5, masterSpark 47x120,
HUD 40x120, gameOver 120x120. Fixed draw cost now: HUD 4800 px, lasers 1920 px, shots 20-35 x 64 px.

Optional bigger refactor (not done): drop Python wrapper objects and lists for bullets. Damage is already stored in
sprite data, so `enemyDamaged` can read it and destroy `projSprite` directly; let the engine delete offscreen
sprites with `SpriteFlag.AUTO_DESTROY` (UNSURE of exact name, check autocomplete); `bombActive` can use
`sprites.all_of_kind(3)`; `setAngle`/`homeTo` become plain functions taking a sprite. Pooling sprites is a later step if
frame time shows garbage-collection spikes (high max with normal average).

Instrumentation to add before the session (owner is writing this):
- Frame interval average (ms), worst single frame in the window (ms), own-code average (us), via running sums
  (no lists). Show with `say_text` once per 60 frames, not the console.
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
(`control.micros()` may wrap after a long uptime, UNSURE). Fix the laser damage bug first so enemies live realistically.
Report back as a table plus whether the slowness felt steady or jerky.

## 8. Useful links

- Decompilation: https://github.com/GensokyoClub/th06 (`src/Player.cpp`, `src/BulletData.cpp`, `src/EnemyManager.cpp`)
- Boss HP / shot analysis thread: http://www.shrinemaiden.org/forum/index.php?topic=15824.0
- Sprite data extension: https://github.com/microsoft/arcade-sprite-data
- Rotation extensions (not used): `Marupio/arcade-cleanEdge` (best for pre-rendering rotated bullets at startup),
  `robo-technical-group/pxt-arcade-image-transform` (keeps per-sprite state that is never freed; avoid for bullets).
- MakeCode forum: Richard's Arcade Tips #6 (hitboxes and overlaps).
