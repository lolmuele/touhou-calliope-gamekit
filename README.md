# Touhou Calliope (working title: "Touhou 6.5")

A fan-made bullet hell in the style of *Embodiment of Scarlet Devil*, built for the **Calliope gamekit**
with [MakeCode Arcade](https://arcade.makecode.com/) (Python).

> **Status: early prototype (pre-alpha), November 2026.** This is a tech demo, not a finished game. There are no stages,
> bosses or menus yet, and expect rough edges and bugs everywhere. See [What's planned](#whats-planned).

## Try it

- **In the browser:** [lolmuele.github.io/touhou-calliope-gamekit](https://lolmuele.github.io/touhou-calliope-gamekit/)
  The web version is only rebuilt when a release is created, so it can lag behind the latest code.
- **On a Calliope gamekit:** open the project in MakeCode (see below) and use **Download** to flash it.
- **Edit the code:** open [arcade.makecode.com](https://arcade.makecode.com/), click **Import**, then **Import URL**, and paste
  `https://github.com/lolmuele/touhou-calliope-gamekit`.

## Controls

| Input | Action |
|---|---|
| D-pad | Move |
| Hold **B** | Focus: slower movement and the lasers move in closer (needs the laser shot tiers) |
| **A** | Bomb (turns enemy bullets into star items; you are invulnerable while it lasts) |
| Shooting | Automatic |
| Up / Down, then **A** | Choose Yes / No on the continue screen |

## What exists so far

- **Player:** movement, auto-fire, six shot tiers from a single stream up to a five-way spread, and two lasers from tier 1.
  Damage values are based on the numbers in the original game. The current build starts at the strongest tier for testing.
- **Enemies:** one test enemy that spawns on a timer and flies the same hard-coded route every time, firing a few aimed shots.
- **Survival:** lives, invulnerability frames after a hit, a continue screen, and bombs.
- **Items:** star items (from bombed bullets) that give score when collected.
- **HUD:** hi-score, score, lives, bombs, a power bar and graze. Some counters are not wired up yet.
- **Look:** a custom 16-colour palette derived from screenshots of the original game. Most art is placeholder.

## What's planned

- Different enemy types and real waves, instead of one enemy repeating.
- Power and point items dropped by enemies, with the shot tier driven by collected power.
- Bosses with several phases, spell cards and an HP bar.
- A title menu, nicer visuals and sound.
- Performance work on real hardware. A few ms matter a lot on a Calliope, and bullet counts are the main cost.

## How it's built

- MakeCode Arcade with the **Python** editor. The source is `main.py`; `main.ts` is generated from it.
- Screen layout: a 120x120 play area and a 40x120 HUD panel on the right (the screen is 160x120).
- Uses the [`arcade-sprite-data`](https://github.com/microsoft/arcade-sprite-data) extension.
- Gameplay numbers (shot damage, fire rate, boss HP) come from community research on the original game.
- Developer notes and the current to-do list are in [`NOTES.md`](NOTES.md).

## Credits and disclaimer

*Touhou Project* and *Embodiment of Scarlet Devil* are created by ZUN / Team Shanghai Alice. This is an unofficial,
non-commercial fan project and is not affiliated with or endorsed by them.

Reference material for game data:

- [GensokyoClub/th06](https://github.com/GensokyoClub/th06), a community decompilation of the original game.
- A [Shrine Maiden forum thread](http://www.shrinemaiden.org/forum/index.php?topic=15824.0) on boss HP and shot analysis.

Made with [MakeCode Arcade](https://arcade.makecode.com/) by Microsoft.

#### Metadata (used for search, rendering)

* for PXT/arcade
<script src="https://makecode.com/gh-pages-embed.js"></script><script>makeCodeRender("{{ site.makecode.home_url }}", "{{ site.github.owner_name }}/{{ site.github.repository_name }}");</script>
