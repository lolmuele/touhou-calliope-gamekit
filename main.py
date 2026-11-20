# =====================================================================
#  HARDWARE SPRITE-COST BENCHMARK  (branch "hardware-bench-v4")
#
#  This branch REPLACES the game with a synthetic benchmark. It does not use any game code.
#  Delete the branch afterwards; master still has the real game.
#
#  It runs 15 modes by itself (4 s warm-up + 10 s measuring each, about 3.5 minutes) and then shows ONE summary screen.
#  Don't touch anything while it runs. The background colour changes per mode. Press A during a run to skip a mode.
#
#  The physics max step is 16 in this version (engine_step.ts). On the summary screen, A switches to step 4 and runs again
#  (and back). The footer shows the current step. You only NEED the step-16 summary; the step-4 one is optional.
#
#  Summary columns:  mode | average frame ms / worst frame ms | your update code in ms | sprites alive at the end
#
#  Results of benchmark v3 at step 16 (for comparison): enemy14 33, en+lasr 38, en+bull 44, en+ghst 62, full 170, fullghst 103.
#
#   0 nothing    no sprites at all
#   1 base       HUD + player + skin
#   2 enemy14    14 enemies steering with float maths (reference)
#   3 en+ghst    enemies + ghost shots + the v3 manual hit test (reference)
#   4 en+gnoh    enemies + ghost shots, NO hit test           -> separates the hit test's own cost from engine cost
#   5 en+ghs2    like 3 with a leaner hit test (boxes pre-expanded, local variables, while loop)
#   6 bull9      9 enemy bullets as normal sprites in the collision grid
#   7 bull9g     9 bullets as ghost sprites + a manual test against the player
#   8 bull60     60 bullets, normal sprites (a boss-like pattern)
#   9 bull60g    60 bullets, ghost + manual test
#  10 en+lasr    enemies + two lasers as normal sprites (reference)
#  11 lasr-g     enemies + two lasers as ghost sprites + a manual rectangle test
#  12 fullghst   shots ghost + v3 hit test + lasers + enemies + 9 normal bullets (reference)
#  13 fullopt    EVERYTHING manual: ghost shots + lean hit test, ghost lasers + rectangle test, ghost bullets + player test
#  14 fo+b60     like 13 with 60 bullets
#
#  What I hope to learn: (a) is a bullet in the grid expensive even when uncrowded (bull9 / bull60 vs the ghost versions),
#  (b) how much of en+ghst is the hit test (4 vs 3 vs 5), (c) whether laser events matter (10 vs 11),
#  (d) how close to the ~26 ms floor "fullopt" gets, and whether a boss-like 60 bullets still fits (14).
# =====================================================================

NAMES = ["nothing", "base", "enemy14", "en+ghst", "en+gnoh", "en+ghs2", "bull9", "bull9g", "bull60", "bull60g", "en+lasr", "lasr-g", "fullghst", "fullopt", "fo+b60"]

# per mode: [base, shots, ghost, hit, lasers, enemies, bullets, bulletsGhost, overlaps, volley interval ms]
# shots: 0 none, 3 game-like wrapper shots. hit: 0 none, 1 v3 hit test, 2 lean hit test. lasers: 0 none, 1 normal sprites, 2 ghost + manual test.
# bullets: how many enemy bullets. bulletsGhost: 1 = ghost + manual test against the player.
FLAGS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 80],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 80],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 80],
    [1, 3, 1, 1, 0, 1, 0, 0, 1, 80],
    [1, 3, 1, 0, 0, 1, 0, 0, 1, 80],
    [1, 3, 1, 2, 0, 1, 0, 0, 1, 80],
    [1, 0, 0, 0, 0, 0, 9, 0, 1, 80],
    [1, 0, 0, 0, 0, 0, 9, 1, 1, 80],
    [1, 0, 0, 0, 0, 0, 60, 0, 1, 80],
    [1, 0, 0, 0, 0, 0, 60, 1, 1, 80],
    [1, 0, 0, 0, 1, 1, 0, 0, 1, 80],
    [1, 0, 0, 0, 2, 1, 0, 0, 1, 80],
    [1, 3, 1, 1, 1, 1, 9, 0, 1, 80],
    [1, 3, 1, 2, 2, 1, 9, 1, 1, 80],
    [1, 3, 1, 2, 2, 1, 60, 1, 1, 80]
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


def spawnTick(kind: int, ghost: bool):
    now = game.runtime()
    if now - B.lastSpawn >= B.interval:
        B.lastSpawn = now
        for k in range(5):
            w = BenchShot(ghost)
            w.sprite.set_position(60, 92)
            w.setAngle(B.ang[k])
            B.wraps.append(w)
    for i in range(len(B.wraps) - 1, -1, -1):
        c: BenchShot = B.wraps[i]
        if c.sprite.x < -15 or c.sprite.x > 145 or c.sprite.y < -15 or c.sprite.y > 135:
            sprites.destroy(c.sprite)
            B.wraps.remove_at(i)


def makeLasers(ghost: bool):
    for xx in [48, 72]:
        orb = sprites.create(assets.image("miniHakkero"), 99)
        orb.set_position(xx, 100)
        orb.z = -10
        las = sprites.create(assets.image("marisaLaser"), 5)
        las.set_position(xx, 40)
        las.z = -10
        if ghost:
            las.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, True)
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
    # v3 version (reference): boxes read once per frame, then every shot against every enemy box.
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


def hitTest2():
    # leaner version: the +-3 / +-13 margins are added to the boxes once, the inner loop is a while loop with a local index.
    bx = B.box
    k = 0
    for e in B.enemies:
        bx[k] = Math.floor(e.left) - 3
        bx[k + 1] = Math.floor(e.top) - 13
        bx[k + 2] = Math.floor(e.right) + 3
        bx[k + 3] = Math.floor(e.bottom) + 13
        k += 4
    for c in B.wraps:
        x = Math.floor(c.sprite.x)
        y = Math.floor(c.sprite.y)
        j = 0
        while j < k:
            if x >= bx[j] and x <= bx[j + 2] and y >= bx[j + 1] and y <= bx[j + 3]:
                B.hits += 1
            j += 4


def laserTest():
    # ghost lasers: test every enemy against the two laser columns by hand
    for e in B.enemies:
        ex = Math.floor(e.x)
        ey = Math.floor(e.y)
        if (ex >= 36 and ex <= 60) or (ex >= 60 and ex <= 84):
            if ey >= -20 and ey <= 100:
                B.hits += 1


def makeBullets(n: int, ghost: bool):
    for i in range(n):
        b = sprites.create(assets.image("redBall"), 3)
        b.set_position(5 + (i * 7) % 110, (i * 13) % 120)
        b.set_velocity(0, 30 + (i % 3) * 15)
        if ghost:
            b.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, True)
        B.misc.append(b)


def tickBullets():
    for b in B.misc:
        if b.y > 130:
            b.y = -10


def bulletTest():
    # ghost bullets: one test per bullet against the single player hitbox (player sits at 60,100)
    for b in B.misc:
        bx = Math.floor(b.x)
        by = Math.floor(b.y)
        if bx >= 57 and bx <= 63 and by >= 97 and by <= 103:
            B.hits += 1


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
    B.interval = f[9]
    scene.set_background_color((m % 15) + 1)
    if f[0] == 1 and len(B.base) == 0:
        createBase()
    if f[8] == 1:
        registerOverlaps()
    if f[4] > 0:
        makeLasers(f[4] == 2)
    if f[5] == 1:
        makeEnemies()
    if f[6] > 0:
        makeBullets(f[6], f[7] == 1)


def tickMode(m: int):
    f = FLAGS[m]
    if f[1] > 0:
        spawnTick(f[1], f[2] == 1)
    if f[5] == 1:
        enemyTick()
    if f[6] > 0:
        tickBullets()
        if f[7] == 1:
            bulletTest()
    if f[3] == 1:
        hitTest()
    elif f[3] == 2:
        hitTest2()
    if f[4] == 2:
        laserTest()


def pad(text: str, n: int):
    while len(text) < n:
        text = text + " "
    return text


def currentStep():
    if settings.exists("bstep"):
        return settings.read_number("bstep")
    return 16


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
        if currentStep() == 16:
            settings.write_number("bstep", 4)
        else:
            settings.write_number("bstep", 16)
        game.reset()
    else:
        B.modeStart = game.runtime() - WARM - MEASURE


game.on_update(benchUpdate)
controller.A.on_event(ControllerButtonEvent.PRESSED, onA)
