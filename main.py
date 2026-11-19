# =====================================================================
#  HARDWARE SPRITE-COST BENCHMARK  (branch "hardware-bench-v3")
#
#  This branch REPLACES the game with a synthetic benchmark. It does not use any game code.
#  Delete the branch afterwards; master still has the real game.
#
#  It runs 15 modes by itself (4 s warm-up + 10 s measuring each, about 3.5 minutes) and then shows ONE summary screen.
#  Don't touch anything while it runs. The background colour changes per mode so you can see it advancing.
#  Press A during a run to skip the current mode.
#
#  TWO RUNS FROM ONE FLASH: on the summary screen, press A. The program saves a setting, restarts, and runs again with a
#  different physics max step (engine_step.ts reads the setting before any sprite exists). The footer shows "step 4" or
#  "step 16". Photograph BOTH summaries. (Step 4 is the engine default; 16 is the proposed fix 1.)
#
#  Summary columns:  mode | average frame ms / worst frame ms | your update code in ms | sprites alive at the end
#
#  What each mode is (everything except "nothing" also has the HUD image + player + skin on screen):
#   0 nothing    no sprites at all (the bare engine floor)
#   1 base       HUD + player + skin
#   2 spawn      5 plain sprites every 80 ms (engine deletes them after 450 ms)
#   3 sp+all     like the game's shots: Python object + list + data + z + trig angle + Python delete loop. No overlap handlers yet.
#   4 sp+ovl     like 3, with the 4 overlap handlers registered (they stay registered for all later modes)
#   5 sp+ghost   like 4, but every shot is GHOST_THROUGH_SPRITES (not in the collision grid)
#   6 sp+half    like 4, a volley every 160 ms (half as many shots)
#   7 lasers8    two 8x120 lasers + two orbs, nothing else
#   8 enemy14    14 enemy sprites steering with float maths
#   9 en+lasr    14 enemies + the two lasers (laser-vs-enemy overlap events; no shots)           <- new
#  10 en+bull    14 enemies + 9 enemy bullets (no lasers, no shots)                              <- new
#  11 en+ghst    14 enemies + ghost shots + the manual shot-vs-enemy box test (no lasers/bullets) <- new
#  12 full       shots + lasers + 14 enemies + 9 enemy bullets, normal (like game mode M3)
#  13 fullghst   like 12 but shots are ghost + manual box test (the proposed game fix)
#  14 fg+half    like 13 with a volley every 160 ms
#
#  Last run (step 4): fullghst was 121 ms while sp+ghost and enemy14 were ~30 ms each. The new modes 9, 10, 11 split
#  that remaining ~90 ms into laser-vs-enemy events, enemy bullets, and the hit test.
# =====================================================================

NAMES = ["nothing", "base", "spawn", "sp+all", "sp+ovl", "sp+ghost", "sp+half", "lasers8", "enemy14", "en+lasr", "en+bull", "en+ghst", "full", "fullghst", "fg+half"]

# per mode: [base, shots, ghost, hit, lasers, enemies, bullets, overlaps, volley interval ms]
# shots: 0 none, 1 plain sprites, 3 game-like wrapper shots
FLAGS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 80],
    [1, 0, 0, 0, 0, 0, 0, 0, 80],
    [1, 1, 0, 0, 0, 0, 0, 0, 80],
    [1, 3, 0, 0, 0, 0, 0, 0, 80],
    [1, 3, 0, 0, 0, 0, 0, 1, 80],
    [1, 3, 1, 0, 0, 0, 0, 1, 80],
    [1, 3, 0, 0, 0, 0, 0, 1, 160],
    [1, 0, 0, 0, 1, 0, 0, 1, 80],
    [1, 0, 0, 0, 0, 1, 0, 1, 80],
    [1, 0, 0, 0, 1, 1, 0, 1, 80],
    [1, 0, 0, 0, 0, 1, 1, 1, 80],
    [1, 3, 1, 1, 0, 1, 0, 1, 80],
    [1, 3, 0, 0, 1, 1, 1, 1, 80],
    [1, 3, 1, 1, 1, 1, 1, 1, 80],
    [1, 3, 1, 1, 1, 1, 1, 1, 160]
]
WARM = 4000
MEASURE = 10000


class BenchShot:
    def __init__(self, ghost: bool):
        self.xVel = 0
        self.yVel = 0
        self.maxSpeed = 250
        self.sprite: Sprite = sprites.create(assets.image("marisaShotImage2"), 2)
        sprites.set_data_number(self.sprite, "damage", 12)
        self.sprite.z = -10
        if ghost:
            self.sprite.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, True)

    def setAngle(self, angle):
        if angle < 0:
            angle += 360
        rad = angle * Math.PI / 180
        self.xVel = Math.sin(rad) * self.maxSpeed
        self.yVel = Math.cos(rad) * self.maxSpeed
        self.sprite.set_velocity(self.xVel, self.yVel)


class Bench:
    def __init__(self):
        self.mode = -1
        self.phase = 0
        self.modeStart = 0
        self.lastT = -1
        self.gapSum = 0
        self.gapCount = 0
        self.gapMax = 0
        self.codeSum = 0
        self.codeCount = 0
        self.lastSpawn = 0
        self.interval = 80
        self.hits = 0
        self.ovlDone = False
        self.base: List[Sprite] = []
        self.lasers: List[Sprite] = []
        self.enemies: List[Sprite] = []
        self.misc: List[Sprite] = []
        self.wp = []
        self.box = []
        self.wraps: List[BenchShot] = []
        self.ang = [189, 185, 180, 175, 171]
        self.vx = []
        self.vy = []
        self.rAvg = []
        self.rMax = []
        self.rCode = []
        self.rN = []
        for a in self.ang:
            r = a * Math.PI / 180
            self.vx.append(Math.sin(r) * 250)
            self.vy.append(Math.cos(r) * 250)


B = Bench()
WPX = [20, 100, 100, 20]
WPY = [20, 20, 80, 80]


def clearKind(k: int):
    while len(sprites.all_of_kind(k)) > 0:
        sprites.destroy(sprites.all_of_kind(k)[0])


def clearAll():
    for k in [2, 3, 4, 5, 99]:
        clearKind(k)
    B.lasers = []
    B.enemies = []
    B.misc = []
    B.wp = []
    B.box = []
    B.wraps = []


def createBase():
    hud = sprites.create(assets.image("hudBackground"), 999)
    hud.z = 999
    hud.set_position(140, 60)
    plyr = sprites.create(assets.image("hitboxImage"), 0)
    plyr.set_position(60, 100)
    skin = sprites.create(assets.tile("marisa"), 97)
    skin.set_position(60, 100)
    B.base.append(hud)
    B.base.append(plyr)
    B.base.append(skin)


def plainShot(vx: number, vy: number):
    s = sprites.create(assets.image("marisaShotImage2"), 2)
    s.set_position(60, 92)
    s.set_velocity(vx, vy)
    s.lifespan = 450


def spawnTick(kind: int, ghost: bool):
    now = game.runtime()
    if now - B.lastSpawn >= B.interval:
        B.lastSpawn = now
        for k in range(5):
            if kind == 1:
                plainShot(B.vx[k], B.vy[k])
            else:
                w = BenchShot(ghost)
                w.sprite.set_position(60, 92)
                w.setAngle(B.ang[k])
                B.wraps.append(w)
    if kind == 3:
        for i in range(len(B.wraps) - 1, -1, -1):
            c: BenchShot = B.wraps[i]
            if c.sprite.x < -15 or c.sprite.x > 145 or c.sprite.y < -15 or c.sprite.y > 135:
                sprites.destroy(c.sprite)
                B.wraps.remove_at(i)


def makeLasers():
    for xx in [48, 72]:
        orb = sprites.create(assets.image("miniHakkero"), 99)
        orb.set_position(xx, 100)
        orb.z = -10
        las = sprites.create(assets.image("marisaLaser"), 5)
        las.set_position(xx, 40)
        las.z = -10
        B.lasers.append(orb)
        B.lasers.append(las)


def makeEnemies():
    for i in range(14):
        e = sprites.create(assets.tile("marisa"), 4)
        e.z = 10
        e.set_position(10 + i * 8, 10 + (i % 4) * 20)
        B.enemies.append(e)
        B.wp.append(i % 4)
    for j in range(56):
        B.box.append(0)


def enemyTick():
    for i in range(len(B.enemies)):
        e = B.enemies[i]
        dx = WPX[B.wp[i]] - e.x
        dy = WPY[B.wp[i]] - e.y
        if abs(dx) < 3 and abs(dy) < 3:
            B.wp[i] = (B.wp[i] + 1) % 4
        else:
            if abs(dx) >= abs(dy):
                vx = 30 * dx / abs(dx)
                vy = vx * (dy / dx)
            else:
                vy = 30 * dy / abs(dy)
                vx = vy * (dx / dy)
            e.set_velocity(vx, vy)


def hitTest():
    # the proposed replacement for the engine's shot-vs-enemy overlap: enemy boxes are read once per frame,
    # then every shot is tested against every enemy box with plain whole-number comparisons. Hits are only counted.
    k = 0
    for e in B.enemies:
        B.box[k] = Math.floor(e.left)
        B.box[k + 1] = Math.floor(e.top)
        B.box[k + 2] = Math.floor(e.right)
        B.box[k + 3] = Math.floor(e.bottom)
        k += 4
    for c in B.wraps:
        x = Math.floor(c.sprite.x)
        y = Math.floor(c.sprite.y)
        for j in range(len(B.enemies)):
            if x + 3 >= B.box[4 * j] and x - 3 <= B.box[4 * j + 2] and y + 13 >= B.box[4 * j + 1] and y - 13 <= B.box[4 * j + 3]:
                B.hits += 1


def makeBullets():
    for i in range(9):
        b = sprites.create(assets.image("redBall"), 3)
        b.set_position(10 + i * 12, 10 + (i % 3) * 30)
        b.set_velocity(0, 30)
        B.misc.append(b)


def tickBullets():
    for b in B.misc:
        if b.y > 130:
            b.y = -10


def ovNoop(a: Sprite, b: Sprite):
    pass


def registerOverlaps():
    if not B.ovlDone:
        sprites.on_overlap(0, 3, ovNoop)
        sprites.on_overlap(4, 2, ovNoop)
        sprites.on_overlap(4, 5, ovNoop)
        sprites.on_overlap(0, 6, ovNoop)
        B.ovlDone = True


def enterMode(m: int):
    clearAll()
    B.mode = m
    B.modeStart = game.runtime()
    B.lastT = -1
    B.gapSum = 0
    B.gapCount = 0
    B.gapMax = 0
    B.codeSum = 0
    B.codeCount = 0
    B.lastSpawn = 0
    B.hits = 0
    f = FLAGS[m]
    B.interval = f[8]
    scene.set_background_color((m % 15) + 1)
    if f[0] == 1 and len(B.base) == 0:
        createBase()
    if f[7] == 1:
        registerOverlaps()
    if f[4] == 1:
        makeLasers()
    if f[5] == 1:
        makeEnemies()
    if f[6] == 1:
        makeBullets()


def tickMode(m: int):
    f = FLAGS[m]
    if f[1] > 0:
        spawnTick(f[1], f[2] == 1)
    if f[5] == 1:
        enemyTick()
    if f[6] == 1:
        tickBullets()
    if f[3] == 1:
        hitTest()


def pad(text: str, n: int):
    while len(text) < n:
        text = text + " "
    return text


def currentStep():
    if settings.exists("bstep"):
        return settings.read_number("bstep")
    return 4


def finishMode():
    avg = 0
    code = 0
    if B.gapCount > 0:
        avg = B.gapSum // (B.gapCount * 1000)
    if B.codeCount > 0:
        code = B.codeSum // B.codeCount
    alive = len(sprites.all_of_kind(2)) + len(sprites.all_of_kind(3)) + len(sprites.all_of_kind(4)) + len(sprites.all_of_kind(5))
    B.rAvg.append(avg)
    B.rMax.append(B.gapMax // 1000)
    B.rCode.append(code)
    B.rN.append(alive)
    if B.mode + 1 < len(NAMES):
        enterMode(B.mode + 1)
    else:
        showSummary()


def showSummary():
    B.phase = 1
    clearAll()
    for s in B.base:
        sprites.destroy(s)
    B.base = []
    scene.set_background_color(1)
    summaryImg = image.create(160, 120)
    summaryImg.fill(1)
    summaryImg.print_center("mode    avg/max  code n", y=1, color=15, font=image.font5)
    for i in range(len(NAMES)):
        codeStr = str(B.rCode[i] // 1000) + "." + str((B.rCode[i] % 1000) // 100)
        line = pad(NAMES[i], 8) + pad(str(B.rAvg[i]) + "/" + str(B.rMax[i]), 8) + pad(codeStr, 5) + str(B.rN[i])
        summaryImg.print_center(line, y=8 + i * 7, color=15, font=image.font5)
    summaryImg.print_center("step " + str(currentStep()) + "   A = other step", y=114, color=15, font=image.font5)
    box = sprites.create(summaryImg, 100)
    box.set_position(80, 60)
    box.z = 1000


def benchUpdate():
    t1 = control.micros()
    if B.phase != 0:
        return
    if B.mode < 0:
        enterMode(0)
        return

    tickMode(B.mode)
    t2 = control.micros()

    elapsed = game.runtime() - B.modeStart
    if elapsed >= WARM:
        if B.lastT >= 0:
            gap = t1 - B.lastT
            if gap >= 0:
                B.gapSum += gap
                B.gapCount += 1
                if gap > B.gapMax:
                    B.gapMax = gap
        B.lastT = t1
        B.codeSum += t2 - t1
        B.codeCount += 1
    if elapsed >= WARM + MEASURE:
        finishMode()


def onA():
    if B.phase == 1:
        if currentStep() == 4:
            settings.write_number("bstep", 16)
        else:
            settings.write_number("bstep", 4)
        game.reset()
    else:
        B.modeStart = game.runtime() - WARM - MEASURE


game.on_update(benchUpdate)
controller.A.on_event(ControllerButtonEvent.PRESSED, onA)
