// engine_step.ts  (benchmark only)
// Runs before main.py (it is listed first in pxt.json).
// Chooses the physics engine's maximum single step in px from the saved setting "bstep".
// Default in v4 is 16 (the proposed fix). main.py writes the setting when you press A on the summary screen
// (16 <-> 4) and restarts, so one flash can give both runs.
{
    let bstep = 16
    if (settings.exists("bstep")) {
        bstep = settings.readNumber("bstep")
    }
    game.currentScene().physicsEngine = new ArcadePhysicsEngine(500, 2, bstep)
}
