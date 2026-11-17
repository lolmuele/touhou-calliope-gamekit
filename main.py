# =====================================================================
#  HARDWARE SPRITE-COST BENCHMARK  (branch "hardware-bench")
#
#  This branch REPLACES the game with a synthetic benchmark. It does not use any game code.
#  Delete the branch afterwards; master still has the real game.
#
#  It runs 15 modes by itself, one after another (4 s warm-up + 10 s measuring each, about 3.5 minutes in total).
#  Don't touch anything. The background colour changes with every mode so you can see it advancing.
#  While it runs nothing is drawn on top (no bubbles), so the measurement is not disturbed.
#  At the end it shows ONE summary screen. Photograph that screen and send it.
#  Press A during a run to skip the current mode. Press A on the summary screen to run it again.
#
#  Summary columns:  mode | average frame ms / worst frame ms | your update code in ms | sprites alive at the end
#
#   0 nothing    no sprites at all (the bare engine floor)
#   1 hud+plyr   the HUD image + player + skin, like the game at rest. They stay for all later modes.
#   2 bubbles    three speech bubbles, like the old harness (shows how much the measurement itself cost)
#   3 static30   30 static 8x8 sprites (pure cost of "sprites exist")
#   4 move30     30 moving 8x8 sprites, wrapped around in Python (cost of motion)
#   5 spawn      5 plain sprites every 80 ms, engine deletes them after 450 ms (cost of creating/destroying)
#   6 sp+data    like spawn, plus sprites.set_data_number on each
#   7 sp+z       like spawn, plus sprite.z = -10 on each
#   8 sp+wrap    like spawn, but each shot is a Python object in a list and a Python loop deletes it
#   9 sp+all     like the game: wrapper + list + data + z + trig angle + Python delete loop
#  10 sp+ovl     like 9, with the 4 overlap handlers registered (they stay registered for modes 11-14)
#  11 lasers8    two 8x120 laser sprites + two orbs, nothing else
#  12 lasers4    the same with 4x120 solid lasers (half the area)
#  13 enemy14    14 enemy sprites (16x16) steering with float maths every frame
#  14 full       9 + lasers8 + enemy14 + 9 enemy bullets (should look like game mode M3)
#
#  Compare for example: 5 vs 3 (churn), 6/7 vs 5 (data / z), 8 vs 5 (Python objects), 9 vs 8, 10 vs 9 (overlaps),
#  12 vs 11 (laser area), and 14 vs the game's own 328 ms.
# =====================================================================

NAMES = ["nothing", "hud+plyr", "bubbles", "static30", "move30", "spawn", "sp+data", "sp+z", "sp+wrap", "sp+all", "sp+ovl", "lasers8", "lasers4", "enemy14", "full"]
WARM = 4000
MEASURE = 10000


class BenchShot:
    def __init__(self, useData: bool, useZ: bool):
        self.xVel = 0
        self.yVel = 0
        self.maxSpeed = 250
        self.sprite: Sprite = sprites.create(assets.image("marisaShotImage2"), 2)
        if useData:
            sprites.set_data_number(self.sprite, "damage", 12)
        if useZ:
            self.sprite.z = -10

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
        self.lastBubble = 0
        self.ovlDone = False
        self.base: List[Sprite] = []
        self.sp: List[Sprite] = []
        self.lasers: List[Sprite] = []
        self.enemies: List[Sprite] = []
        self.misc: List[Sprite] = []
        self.wp = []
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
    for k in [2, 3, 4, 5, 98, 99]:
        clearKind(k)
    B.sp = []
    B.lasers = []
    B.enemies = []
    B.misc = []
    B.wp = []
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


def makeBubbles():
    for yy in [20, 46, 90]:
        lab = sprites.create(image.create(1, 1), 98)
        lab.set_position(60, yy)
        lab.z = 1000
        B.sp.append(lab)


def tickBubbles():
    if game.runtime() - B.lastBubble >= 1000:
        B.lastBubble = game.runtime()
        B.sp[0].say_text("M2 206/255 c4639")
        B.sp[1].say_text("s25/25 b0 e0 t12")
        B.sp[2].say_text("12718ft:81")


def makeStatic(moving: bool):
    for i in range(30):
        s = sprites.create(assets.image("marisaShotImage2"), 2)
        s.set_position(8 + (i % 10) * 10, 10 + (i // 10) * 35)
        if moving:
            s.set_velocity(0, -60)
        B.sp.append(s)


def tickMove():
    for s in B.sp:
        if s.y < -10:
            s.y = 130


def plainShot(vx: number, vy: number, useData: bool, useZ: bool):
    s = sprites.create(assets.image("marisaShotImage2"), 2)
    s.set_position(60, 92)
    s.set_velocity(vx, vy)
    s.lifespan = 450
    if useData:
        sprites.set_data_number(s, "damage", 12)
    if useZ:
        s.z = -10


def spawnTick(kind: int):
    now = game.runtime()
    if now - B.lastSpawn >= 80:
        B.lastSpawn = now
        for k in range(5):
            if kind <= 7:
                plainShot(B.vx[k], B.vy[k], kind == 6, kind == 7)
            elif kind == 8:
                w = BenchShot(False, False)
                w.sprite.set_position(60, 92)
                w.sprite.set_velocity(B.vx[k], B.vy[k])
                B.wraps.append(w)
            else:
                w2 = BenchShot(True, True)
                w2.sprite.set_position(60, 92)
                w2.setAngle(B.ang[k])
                B.wraps.append(w2)
    if kind >= 8:
        for i in range(len(B.wraps) - 1, -1, -1):
            c: BenchShot = B.wraps[i]
            if c.sprite.x < -15 or c.sprite.x > 145 or c.sprite.y < -15 or c.sprite.y > 135:
                sprites.destroy(c.sprite)
                B.wraps.remove_at(i)


def makeLasers(laserImg: Image):
    for xx in [48, 72]:
        orb = sprites.create(assets.image("miniHakkero"), 99)
        orb.set_position(xx, 100)
        orb.z = -10
        las = sprites.create(laserImg, 5)
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
    B.lastBubble = 0
    scene.set_background_color(m + 1)
    if m == 1:
        createBase()
    elif m == 2:
        makeBubbles()
    elif m == 3:
        makeStatic(False)
    elif m == 4:
        makeStatic(True)
    elif m == 10:
        registerOverlaps()
    elif m == 11:
        makeLasers(assets.image("marisaLaser"))
    elif m == 12:
        thin = image.create(4, 120)
        thin.fill(5)
        makeLasers(thin)
    elif m == 13:
        makeEnemies()
    elif m == 14:
        makeLasers(assets.image("marisaLaser"))
        makeEnemies()
        makeBullets()


def tickMode(m: int):
    if m == 2:
        tickBubbles()
    elif m == 4:
        tickMove()
    elif m >= 5 and m <= 10:
        spawnTick(m)
    elif m == 13:
        enemyTick()
    elif m == 14:
        spawnTick(9)
        enemyTick()
        tickBullets()


def pad(text: str, n: int):
    while len(text) < n:
        text = text + " "
    return text


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
    summaryImg.print_center("mode    avg/max  code n", y=2, color=15, font=image.font5)
    for i in range(len(NAMES)):
        codeStr = str(B.rCode[i] // 1000) + "." + str((B.rCode[i] % 1000) // 100)
        line = pad(NAMES[i], 8) + pad(str(B.rAvg[i]) + "/" + str(B.rMax[i]), 8) + pad(codeStr, 5) + str(B.rN[i])
        summaryImg.print_center(line, y=10 + i * 7, color=15, font=image.font5)
    summaryImg.print_center("A = run again", y=114, color=15, font=image.font5)
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
        game.reset()
    else:
        B.modeStart = game.runtime() - WARM - MEASURE


game.on_update(benchUpdate)
controller.A.on_event(ControllerButtonEvent.PRESSED, onA)
