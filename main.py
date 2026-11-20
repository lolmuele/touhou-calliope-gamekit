# =====================================================================
#  HARDWARE SPRITE-COST BENCHMARK v5  (branch "hardware-bench-v5")
#
#  This branch REPLACES the game with a synthetic benchmark. It does not use any game code.
#  Delete the branch afterwards; master still has the real game. (engine_step.ts and pxt.json are the same as in v4.)
#
#  It runs 13 modes by itself (4 s warm-up + 10 s measuring each, about 3 minutes) and then shows ONE summary screen.
#  Don't touch anything while it runs. The background colour changes per mode. Press A during a run to skip a mode.
#  The physics max step is 16 (engine_step.ts, default). A on the summary screen still toggles to step 4 and back, but you only NEED the step-16 summary.
#
#  Summary columns:  mode | average frame ms / worst frame ms | your update code in ms | objects alive (sprites + custom bullets/shots) | gc ms
#  "gc" = how long ONE forced full garbage collection took at the end of that mode (control.gc()). If it is big (10+ ms)
#  while many objects are alive, garbage collection is a likely culprit for the unexplained engine time in v4.
#
#  What v4 left open: ghost shots + enemies cost ~17 ms that is not my code and not the grid (en+gnoh 56 vs enemy14 33), and it grew with
#  sprite count (fullopt 91, fo+b60 158). v5 tests why, and whether bullets/shots that are NOT sprites avoid it.
#  Numbers to compare with (v4, step 16): enemy14 33, en+gnoh 56, en+ghs2 61, bull60 93, bull60g 47, fullopt 91, fo+b60 158.
#
#   0 none     no sprites at all
#   1 base     HUD + player + skin
#   2 e14nov   14 enemies steering with float maths, NO overlap handlers registered (nothing is in the collision grid)
#   3 nov+gn   e14nov + ghost shots (wrapper objects), still NO overlap handlers   -> is the extra ~17 ms about the grid/handlers? (compare 2 vs 3, and 3 vs v4 en+gnoh 56)
#   --- from here on the overlap handlers are registered (they cannot be unregistered, so modes 2 and 3 must come first) ---
#   4 stat+g   14 STATIONARY enemies + ghost shots, no hit test                   -> does enemy movement matter? (compare with v4 en+gnoh 56)
#   5 lazy+g   14 enemies that get their velocity only when a leg starts (no per-frame float maths, no per-frame x/y reads) + ghost shots
#   6 csh+en   14 float-steering enemies + shots that are NOT sprites (flat arrays, drawn by one renderable) + lean hit test   (compare with v4 en+ghs2 61)
#   7 c60      60 bullets that are NOT sprites + manual test against the player   (compare with v4 bull60g 47, bull60 93)
#   8 c120     120 non-sprite bullets
#   9 fo+c60   fullopt design (ghost sprite shots + lean hit test, ghost lasers, float enemies) with 60 NON-sprite bullets   (v4 fo+b60 was 158)
#  10 fcust    like 9 but the shots are non-sprite too (only enemies, 2 orbs and 2 lasers are sprites)
#  11 fc+120   like 10 with 120 non-sprite bullets
#  12 fopt9    v4 fullopt again (9 ghost sprite bullets) as an anchor: should be ~91 like in v4
#
#  Non-sprite objects: positions are plain integers in 1/16 px, velocities in px/s, moved with integer maths only (no floats, so no garbage),
#  and drawn by ONE scene.create_renderable handler with image.draw_transparent_image. They ignore camera shake (the benchmark never shakes).
# =====================================================================

NAMES = ["none", "base", "e14nov", "nov+gn", "stat+g", "lazy+g", "csh+en", "c60", "c120", "fo+c60", "fcust", "fc+120", "fopt9"]

# per mode: [base, shots, hit, lasers, enemies, nBullets, bulletKind, overlaps]
# shots: 0 none, 1 ghost sprites with wrapper objects (as v4), 2 non-sprite shots.  hit: 0 none, 2 lean hit test (for whichever shot kind).
# lasers: 0 none, 2 ghost sprites + manual test.  enemies: 0 none, 1 float steering every frame (v4), 2 stationary, 3 lazy (velocity once per leg).
# nBullets / bulletKind: 1 = ghost sprites + manual test (v4 style), 2 = non-sprite.  overlaps: 1 = register the overlap handlers.
FLAGS = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 0, 2, 0, 0, 1],
    [1, 1, 0, 0, 3, 0, 0, 1],
    [1, 2, 2, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 60, 2, 1],
    [1, 0, 0, 0, 0, 120, 2, 1],
    [1, 1, 2, 2, 1, 60, 2, 1],
    [1, 2, 2, 2, 1, 60, 2, 1],
    [1, 2, 2, 2, 1, 120, 2, 1],
    [1, 1, 2, 2, 1, 9, 1, 1]
]
WARM = 4000
MEASURE = 10000
POOL = 48


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
        self.lastFrame = 0
        self.gapSum = 0
        self.gapCount = 0
        self.gapMax = 0
        self.codeSum = 0
        self.codeCount = 0
        self.lastSpawn = 0
        self.interval = 80
        self.hits = 0
        self.ovlDone = False
        self.rendDone = False
        self.base: List[Sprite] = []
        self.lasers: List[Sprite] = []
        self.enemies: List[Sprite] = []
        self.misc: List[Sprite] = []
        self.wp = []
        self.box = []
        self.legEnd = []
        self.wraps: List[BenchShot] = []
        # non-sprite bullets (1/16 px integers)
        self.cn = 0
        self.bx = []
        self.by = []
        self.bvy = []
        # non-sprite shots (pool of POOL slots)
        self.custShots = 0
        self.sNext = 0
        self.scx = []
        self.scy = []
        self.scvx = []
        self.scvy = []
        self.sact = []
        self.ballImg = assets.image("redBall")
        self.shotImg = assets.image("marisaShotImage2")
        self.ang = [189, 185, 180, 175, 171]
        self.vx = []
        self.vy = []
        self.ivx = []
        self.ivy = []
        self.rAvg = []
        self.rMax = []
        self.rCode = []
        self.rN = []
        self.rGc = []
        for a in self.ang:
            r = a * Math.PI / 180
            self.vx.append(Math.sin(r) * 250)
            self.vy.append(Math.cos(r) * 250)
            self.ivx.append(Math.round(Math.sin(r) * 250))
            self.ivy.append(Math.round(Math.cos(r) * 250))


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
    B.legEnd = []
    B.wraps = []
    B.cn = 0
    B.custShots = 0


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


# ---------- ghost sprite shots (same as v4) ----------

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


# ---------- enemies ----------

def makeEnemies():
    for i in range(14):
        e = sprites.create(assets.tile("marisa"), 4)
        e.z = 10
        e.set_position(10 + i * 8, 10 + (i % 4) * 20)
        B.enemies.append(e)
        B.wp.append(i % 4)
        B.legEnd.append(0)
    for j in range(56):
        B.box.append(0)


def enemyTick():
    # v4 steering: float maths and set_velocity on every enemy, every frame
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


def steerTo(e: Sprite, i: int):
    # lazy steering: work out the velocity and the time the leg takes ONCE, when the leg starts
    dx = WPX[B.wp[i]] - e.x
    dy = WPY[B.wp[i]] - e.y
    dist = Math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        dist = 1
    e.set_velocity(30 * dx / dist, 30 * dy / dist)
    B.legEnd[i] = game.runtime() + Math.floor(dist * 1000 / 30)


def startLazy():
    for i in range(len(B.enemies)):
        steerTo(B.enemies[i], i)


def enemyTickLazy():
    # per frame: one clock read and 14 integer comparisons, nothing else
    now = game.runtime()
    for i in range(len(B.enemies)):
        if now >= B.legEnd[i]:
            B.wp[i] = (B.wp[i] + 1) % 4
            steerTo(B.enemies[i], i)


# ---------- hit tests ----------

def hitTest2():
    # v4 lean test for sprite shots: the +-3 / +-13 margins are added to the boxes once, the inner loop is a while loop with a local index.
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


def hitTestCust():
    # same test for non-sprite shots (integers only)
    bx = B.box
    k = 0
    for e in B.enemies:
        bx[k] = Math.floor(e.left) - 3
        bx[k + 1] = Math.floor(e.top) - 13
        bx[k + 2] = Math.floor(e.right) + 3
        bx[k + 3] = Math.floor(e.bottom) + 13
        k += 4
    sx = B.scx
    sy = B.scy
    sa = B.sact
    i = 0
    while i < POOL:
        if sa[i] == 1:
            x = sx[i] // 16
            y = sy[i] // 16
            j = 0
            while j < k:
                if x >= bx[j] and x <= bx[j + 2] and y >= bx[j + 1] and y <= bx[j + 3]:
                    B.hits += 1
                j += 4
        i += 1


def laserTest():
    # ghost lasers: test every enemy against the two laser columns by hand
    for e in B.enemies:
        ex = Math.floor(e.x)
        ey = Math.floor(e.y)
        if (ex >= 36 and ex <= 60) or (ex >= 60 and ex <= 84):
            if ey >= -20 and ey <= 100:
                B.hits += 1


# ---------- ghost sprite bullets (v4) ----------

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


# ---------- NON-sprite bullets and shots ----------

def makeCustomBullets(n: int):
    B.bx = []
    B.by = []
    B.bvy = []
    for i in range(n):
        B.bx.append((5 + (i * 7) % 110) * 16)
        B.by.append(((i * 13) % 120) * 16)
        B.bvy.append(30 + (i % 3) * 15)
    B.cn = n


def tickCustomBullets(dt: int):
    # y moves by vy px/s * dt ms; in 1/16 px that is vy * dt * 16 / 1000 = vy * dt * 2 / 125
    n = B.cn
    by = B.by
    vy = B.bvy
    k = dt * 2
    i = 0
    while i < n:
        y = by[i] + vy[i] * k // 125
        if y > 2080:
            y = -160
        by[i] = y
        i += 1


def customBulletTest():
    # player box x 57..63, y 97..103 px = 912..1008 and 1552..1648 in 1/16 px
    n = B.cn
    bx = B.bx
    by = B.by
    i = 0
    while i < n:
        if bx[i] >= 912 and bx[i] <= 1008 and by[i] >= 1552 and by[i] <= 1648:
            B.hits += 1
        i += 1


def makeShotPool():
    B.scx = []
    B.scy = []
    B.scvx = []
    B.scvy = []
    B.sact = []
    for i in range(POOL):
        B.scx.append(0)
        B.scy.append(0)
        B.scvx.append(0)
        B.scvy.append(0)
        B.sact.append(0)
    B.sNext = 0
    B.custShots = 1


def customShotTick(dt: int):
    now = game.runtime()
    if now - B.lastSpawn >= B.interval:
        B.lastSpawn = now
        for k in range(5):
            j = B.sNext
            tries = 0
            while B.sact[j] == 1 and tries < POOL:
                j = (j + 1) % POOL
                tries += 1
            B.scx[j] = 60 * 16
            B.scy[j] = 92 * 16
            B.scvx[j] = B.ivx[k]
            B.scvy[j] = B.ivy[k]
            B.sact[j] = 1
            B.sNext = (j + 1) % POOL
    kk = dt * 2
    sx = B.scx
    sy = B.scy
    vx = B.scvx
    vy = B.scvy
    sa = B.sact
    i = 0
    while i < POOL:
        if sa[i] == 1:
            x = sx[i] + vx[i] * kk // 125
            y = sy[i] + vy[i] * kk // 125
            if x < -240 or x > 2320 or y < -240 or y > 2160:
                sa[i] = 0
            else:
                sx[i] = x
                sy[i] = y
        i += 1


def drawCustom(target: Image, camera: scene.Camera):
    ball = B.ballImg
    n = B.cn
    bx = B.bx
    by = B.by
    i = 0
    while i < n:
        target.draw_transparent_image(ball, bx[i] // 16 - 4, by[i] // 16 - 4)
        i += 1
    if B.custShots == 1:
        shot = B.shotImg
        sx = B.scx
        sy = B.scy
        sa = B.sact
        i = 0
        while i < POOL:
            if sa[i] == 1:
                target.draw_transparent_image(shot, sx[i] // 16 - 4, sy[i] // 16 - 4)
            i += 1


def ensureRenderable():
    if not B.rendDone:
        scene.create_renderable(5, drawCustom)
        B.rendDone = True


# ---------- mode handling ----------

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
    B.lastFrame = game.runtime()
    B.gapSum = 0
    B.gapCount = 0
    B.gapMax = 0
    B.codeSum = 0
    B.codeCount = 0
    B.lastSpawn = 0
    B.hits = 0
    f = FLAGS[m]
    B.interval = 80
    scene.set_background_color((m % 15) + 1)
    if f[0] == 1 and len(B.base) == 0:
        createBase()
    if f[7] == 1:
        registerOverlaps()
    if f[3] == 2:
        makeLasers(True)
    if f[4] > 0:
        makeEnemies()
    if f[4] == 3:
        startLazy()
    if f[1] == 2:
        makeShotPool()
        ensureRenderable()
    if f[5] > 0:
        if f[6] == 1:
            makeBullets(f[5], True)
        else:
            makeCustomBullets(f[5])
            ensureRenderable()


def tickMode(m: int, dt: int):
    f = FLAGS[m]
    if f[1] == 1:
        spawnTick(1, True)
    elif f[1] == 2:
        customShotTick(dt)
    if f[4] == 1:
        enemyTick()
    elif f[4] == 3:
        enemyTickLazy()
    if f[5] > 0:
        if f[6] == 1:
            tickBullets()
            bulletTest()
        else:
            tickCustomBullets(dt)
            customBulletTest()
    if f[2] == 2:
        if f[1] == 2:
            hitTestCust()
        else:
            hitTest2()
    if f[3] == 2:
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
    alive = len(sprites.all_of_kind(2)) + len(sprites.all_of_kind(3)) + len(sprites.all_of_kind(4)) + len(sprites.all_of_kind(5)) + B.cn
    if B.custShots == 1:
        for s in range(POOL):
            if B.sact[s] == 1:
                alive += 1
    # time ONE forced full garbage collection with this mode's objects still alive
    gcStart = control.micros()
    control.gc()
    gcMs = (control.micros() - gcStart) // 1000
    B.rAvg.append(avg)
    B.rMax.append(B.gapMax // 1000)
    B.rCode.append(code)
    B.rN.append(alive)
    B.rGc.append(gcMs)
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
    summaryImg.print_center(pad("mode", 7) + pad("avg/max", 8) + pad("code", 5) + pad("n", 4) + "gc", y=1, color=15, font=image.font5)
    for i in range(len(NAMES)):
        codeStr = str(B.rCode[i] // 1000) + "." + str((B.rCode[i] % 1000) // 100)
        gcv = B.rGc[i]
        if gcv > 99:
            gcv = 99
        line = pad(NAMES[i], 7) + pad(str(B.rAvg[i]) + "/" + str(B.rMax[i]), 8) + pad(codeStr, 5) + pad(str(B.rN[i]), 4) + str(gcv)
        summaryImg.print_center(line, y=8 + i * 7, color=15, font=image.font5)
    summaryImg.print_center("gc = ms of one full collection", y=103, color=15, font=image.font5)
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

    now = game.runtime()
    dt = now - B.lastFrame
    B.lastFrame = now
    if dt > 100:
        dt = 100
    if dt < 1:
        dt = 1

    tickMode(B.mode, dt)
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
