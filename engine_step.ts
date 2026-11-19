// engine_step.ts  (benchmark only)
// Runs before main.py (it is listed first in pxt.json).
// Chooses the physics engine's maximum single step in px from the saved setting "bstep" (default 4, which equals the engine's default).
// main.py writes the setting when you press A on the summary screen, then restarts, so one flash gives both runs.
{
    let bstep = 4
    if (settings.exists("bstep")) {
        bstep = settings.readNumber("bstep")
    }
    game.currentScene().physicsEngine = new ArcadePhysicsEngine(500, 2, bstep)
}
