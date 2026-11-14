# Touhou Calliope (working title: "Touhou 6.5")

A fan-made bullet hell in the style of *Embodiment of Scarlet Devil*, built for the **Calliope gamekit**
with [MakeCode Arcade](https://arcade.makecode.com/) (Python).

> **Status: work in progress** (November 2026). Playable, but plenty is unfinished. See [What's planned](#whats-planned).

## Play

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

## What works so far

- Auto-fire shot with six power tiers, from a single stream up to a five-way spread, plus two lasers from tier 1.
  Damage values follow the numbers in the original game.
- Enemies that fly along scripted routes and shoot homing bullets, and spawn in waves.
- Lives, invulnerability frames, a continue screen, and bombs.
- Star items that clear into score when collected.
- A HUD panel with hi-score, score, lives, bombs, a power bar and graze (some counters are not wired up yet).
- A custom 16-colour palette derived from screenshots of the original game.

The current build is a development build: it starts at the strongest shot tier for testing.

## What's planned

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
