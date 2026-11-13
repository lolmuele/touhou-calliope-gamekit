class HUD {
    hudImage: Image
    background: Sprite
    gameOverSprite: Sprite
    constructor() {
        this.hudImage = assets.image`hudBackground`
        this.hudImage.printCenter("EOMD", 108, 4, image.font5)
        this.background = sprites.create(assets.image`hudBackground`, 999)
        this.background.z = 999
        this.background.setPosition(140, 60)
        scene.setBackgroundColor(6)
        //  self.stageBackground: Sprite = sprites.create(assets.image("stageBackground"), 999)
        //  self.stageBackground.z = -100
        //  self.stageBackground.set_position(60, 60)
        
    }
    
    public buildGameOver(continues: number, yes: boolean): Image {
        let gameOverImage = assets.image`gameOver`
        gameOverImage.printCenter("Game Over", 10, 2, image.font12)
        gameOverImage.printCenter("Continue ?", 45, 1, image.font8)
        gameOverImage.printCenter("" + continues + " Left", 55, 1, image.font8)
        if (yes) {
            gameOverImage.printCenter("> Yes <", 70, 5, image.font8)
            gameOverImage.printCenter("No", 80, 2, image.font8)
        } else if (!yes) {
            gameOverImage.printCenter("Yes", 70, 2, image.font8)
            gameOverImage.printCenter("> No <", 80, 5, image.font8)
        }
        
        return gameOverImage
    }
    
    public buildHud(highScore: number = 0, score: number = 0, lives: number = 0, bombs: number = 0, power: number = 0, graze: number = 0, point: number = 0) {
        let i: number;
        let hudImage = this.hudImage.clone()
        hudImage.printCenter("HiSc", 10, 9, image.font5)
        hudImage.printCenter("" + highScore, 17, 10, image.font5)
        hudImage.printCenter("Score", 23, 9, image.font5)
        hudImage.printCenter("" + score, 29, 10, image.font5)
        hudImage.printCenter("Lives", 35, 9, image.font5)
        for (i = 0; i < lives; i++) {
            hudImage.drawTransparentImage(assets.image`livesStar`, 7 + i * 9, 42)
        }
        hudImage.printCenter("Bombs", 53, 9, image.font5)
        for (i = 0; i < bombs; i++) {
            hudImage.drawTransparentImage(assets.image`bombsStar`, 7 + i * 9, 60)
        }
        hudImage.printCenter("Power", 70, 9, image.font5)
        hudImage.fillRect(6, 78, Math.idiv(28 * power, 128), 8, 9)
        hudImage.printCenter("" + (power < 128 ? power : " max") + "  ", 79, 10, image.font5)
        hudImage.printCenter("Graze", 88, 9, image.font5)
        hudImage.printCenter("" + graze, 95, 10, image.font5)
        this.background.setImage(hudImage)
    }
    
    public gameOver(continues: number) {
        let gameOverImage = this.buildGameOver(continues, false)
        this.gameOverSprite = sprites.create(gameOverImage, 999)
        this.gameOverSprite.z = 999
        this.gameOverSprite.setPosition(60, 60)
    }
    
}

// TODO: 
// add enemies
// need to make pathing work -kinda implemented
// shots can't home yet -they can now
// need HP -works
// handle destruction -works 
// add health/damage handling
// player can take damage and has health -done
// iframes after hit -works
// game over, continue & restart -kinda, really basic but you can respawn
// add bombs -works
// add hud functionality -works
// make hitbox not move within the sprite -works i'm pretty sure
// add bosses
// visuals (ugh)
// add menu
// add drops
// had a chance to test on real hardware today and...
// performance is pretty horrendous:
// 40+ ms frametime, possibly a leak:
// about double that of the ~20ms in the web simulator
//    not sure if it's actually slowing down increasingly or if on-screen console prints are so heavy on the calliope,
//    it feels like it's only slowing down when console output is on, while it was on the frametimes went to abt 65+ms gradually
//    but i feel like i shouldn't be leaking objects so idk
// are there major performance improvements i can make rn?
class Projectile {
    sprite: Sprite
    xVel: number
    yVel: number
    maxSpeed: number
    constructor(spriteName: string = "projectile", spriteKind: number = 1, xVel: number = 0, yVel: number = 0, maxSpeed: number = 50) {
        if (spriteName == "projectile") {
            this.sprite = sprites.create(assets.tile`projectile`, 1)
            this.sprite.setKind(spriteKind)
        }
        
        this.xVel = xVel
        this.yVel = yVel
        this.maxSpeed = maxSpeed
    }
    
    public homeTo(x: number, y: number) {
        let diffX = x - this.sprite.x
        let diffY = y - this.sprite.y
        // does this catch division by 0? idek
        if (diffX == 0 && diffY == 0) {
            this.xVel = 0
            this.yVel = this.maxSpeed
        } else if (Math.abs(diffX) >= Math.abs(diffY)) {
            this.xVel = this.maxSpeed * diffX / Math.abs(diffX)
            this.yVel = this.xVel * (diffY / diffX)
        } else {
            this.yVel = this.maxSpeed * diffY / Math.abs(diffY)
            this.xVel = this.yVel * (diffX / diffY)
        }
        
        this.sprite.setVelocity(this.xVel, this.yVel)
    }
    
    public setAngle(angle: number) {
        if (angle < 0) {
            angle += 360
        }
        
        let rad = angle * Math.PI / 180
        this.xVel = Math.sin(rad) * this.maxSpeed
        this.yVel = Math.cos(rad) * this.maxSpeed
        this.sprite.setVelocity(this.xVel, this.yVel)
    }
    
}

class playerProjectile extends Projectile {
    damage: number
    constructor(damage: number = 1) {
        super("marisaShot", 2, 0, 0, 250)
        this.damage = damage
        this.sprite = sprites.create(assets.image`marisaShotImage2`, 2)
        sprites.setDataNumber(this.sprite, "damage", this.damage)
        this.sprite.z = -10
    }
    
}

class redCircleProjectile extends Projectile {
    constructor() {
        super("redBall", 2, 0, 0, 30)
        this.sprite = sprites.create(assets.image`redBall`, 3)
    }
    
}

class Enemy {
    sprite: Sprite
    projectiles: Projectile[]
    health: number
    dead: boolean
    route: number[][]
    routePoint: number
    waitTime: number
    player: Player
    pointReachedTime: number
    xVel: number
    yVel: number
    maxSpeed: number
    constructor(spriteName: string, player: Player, health: number = 950) {
        if (spriteName == "test") {
            this.sprite = sprites.create(assets.tile`marisa`, 4)
            this.sprite.z = 10
        }
        
        this.projectiles = []
        this.health = health
        this.dead = false
        // route format:
        // [[x: int, y: int, maxSpeed:int, waitTime:int(in ms), shoot: bool], [x, y...]]
        // self.route = []
        // testroute here:
        this.route = [[60, -10, 30, 500, 1], [60, 25, 30, 2000, 1], [12, 30, 300, 800, 1], [78, 90, 90, 0, 1], [0, 0, 50, 0, 1]]
        this.sprite.setPosition(this.route[0][0], this.route[0][1])
        this.routePoint = 1
        this.waitTime = 0
        this.player = player
        this.pointReachedTime = 0
    }
    
    public shoot() {
        this.projectiles.push(new redCircleProjectile())
        this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y)
        this.projectiles[this.projectiles.length - 1].setAngle(0)
    }
    
    public shootHoming() {
        this.projectiles.push(new redCircleProjectile())
        this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y)
        this.projectiles[this.projectiles.length - 1].homeTo(this.player.sprite.x, this.player.sprite.y)
    }
    
    public takeDamage(damage: number = 1) {
        this.health -= damage
        if (this.health <= 0) {
            this.dead = true
        }
        
    }
    
    public homeTo(x: number, y: number) {
        let diffX = x - this.sprite.x
        let diffY = y - this.sprite.y
        // does this catch division by 0? idek
        if (diffX == 0 && diffY == 0) {
            this.xVel = 0
            this.yVel = this.maxSpeed
        } else if (Math.abs(diffX) >= Math.abs(diffY)) {
            this.xVel = this.maxSpeed * diffX / Math.abs(diffX)
            this.yVel = this.xVel * (diffY / diffX)
        } else {
            this.yVel = this.maxSpeed * diffY / Math.abs(diffY)
            this.xVel = this.yVel * (diffX / diffY)
        }
        
        this.sprite.setVelocity(this.xVel, this.yVel)
    }
    
    public closeEnough(x1: number, x2: number, y1: number, y2: number, speed: number): boolean {
        let tolerance = Math.idiv(speed, 50) > 2 ? Math.idiv(speed, 50) : 2
        let diffX = Math.abs(x1 - x2)
        let diffY = Math.abs(y1 - y2)
        if (diffX <= tolerance && diffY <= tolerance) {
            return true
        } else {
            return false
        }
        
    }
    
    public goRoute() {
        if (this.dead) {
            return
        }
        
        if (this.waitTime > 0) {
            this.waitTime -= game.runtime() - this.pointReachedTime
            this.pointReachedTime = game.runtime()
        } else if (this.routePoint == this.route.length) {
            
        } else if (this.closeEnough(this.sprite.x, this.route[this.routePoint][0], this.sprite.y, this.route[this.routePoint][1], this.route[this.routePoint][2])) {
            this.pointReachedTime = game.runtime()
            this.waitTime = this.route[this.routePoint][3]
            if (this.waitTime > 0) {
                this.sprite.setVelocity(0, 0)
            }
            
            if (this.route[this.routePoint][4]) {
                this.shootHoming()
                this.route[this.routePoint][4] = 0
            }
            
            this.routePoint += 1
        }
        
        if (!(this.routePoint == this.route.length) && this.waitTime <= 0) {
            this.maxSpeed = this.route[this.routePoint][2]
            this.homeTo(this.route[this.routePoint][0], this.route[this.routePoint][1])
        }
        
    }
    
}

class Player {
    sprite: Sprite
    tier: number
    projectiles: Projectile[]
    slowDownVariable: number
    skin: Sprite
    health: number
    bombs: number
    power: number
    lastHit: number
    Lasers: boolean
    bombStart: number
    lastShot: number
    l1: Sprite
    l2: Sprite
    l1Laser: Sprite
    l2Laser: Sprite
    constructor() {
        this.sprite = sprites.create(assets.image`hitboxImage`, SpriteKind.Player)
        this.sprite.setStayInScreen(true)
        this.sprite.setKind(0)
        this.tier = 5
        this.projectiles = []
        this.slowDownVariable = 0
        this.skin = sprites.create(assets.tile`marisa`)
        this.skin.setPosition(this.sprite.x, this.sprite.y - 1)
        this.health = 3
        this.bombs = 3
        this.power = 0
        this.lastHit = -3000
        // so you're not invincible at the start of the game
        // self.spawnLasers()
        this.Lasers = false
        this.bombStart = -10000
        this.lastShot = 0
    }
    
    public takeDamage() {
        this.health -= 1
        this.bombs = 3
        // don't question it, this is how EOSD works, even if you have more than 3 
        scene.cameraShake(2, 300)
        // visual feedback for getting hit
        this.lastHit = game.runtime()
        animation.runImageAnimation(this.skin, [assets.tile`damageFlicker`, assets.tile`marisa`, assets.tile`damageFlicker`, assets.tile`marisa`, assets.tile`damageFlicker`, assets.tile`marisa`, assets.tile`damageFlicker`, assets.tile`marisa`, assets.tile`damageFlicker`, assets.tile`marisa`, assets.tile`damageFlicker`, assets.tile`marisa`], 250, false)
    }
    
    // visual feedback for i-frames
    public movementController() {
        let xVel = 0
        let yVel = 0
        if (controller.up.isPressed()) {
            yVel -= 80
        }
        
        if (controller.down.isPressed()) {
            yVel += 80
        }
        
        if (controller.left.isPressed()) {
            xVel -= 80
        }
        
        if (controller.right.isPressed()) {
            xVel += 80
        }
        
        if (controller.B.isPressed() && this.Lasers) {
            xVel = Math.trunc(xVel / 2)
            yVel = Math.trunc(yVel / 2)
            this.sprite.z = 10
            this.l1.setPosition(this.sprite.x - 5, this.sprite.y - 10)
            this.l2.setPosition(this.sprite.x + 5, this.sprite.y - 10)
            this.l1Laser.setPosition(this.sprite.x - 5, this.sprite.y - 70)
            this.l2Laser.setPosition(this.sprite.x + 5, this.sprite.y - 70)
        } else {
            this.sprite.z = 0
        }
        
        this.sprite.setVelocity(xVel, yVel)
        this.skin.setPosition(this.sprite.x, this.sprite.y)
        if (this.Lasers && !controller.B.isPressed()) {
            this.l1.setPosition(this.sprite.x - 12, this.sprite.y)
            this.l2.setPosition(this.sprite.x + 12, this.sprite.y)
            this.l1Laser.setPosition(this.sprite.x - 12, this.sprite.y - 60)
            this.l2Laser.setPosition(this.sprite.x + 12, this.sprite.y - 60)
        }
        
    }
    
    public spawnLasers(damage: number = 3) {
        this.Lasers = true
        this.l1 = sprites.create(assets.image`miniHakkero`)
        this.l2 = sprites.create(assets.image`miniHakkero`)
        this.l1.setPosition(this.sprite.x - 12, this.sprite.y)
        this.l2.setPosition(this.sprite.x + 12, this.sprite.y)
        this.l1Laser = sprites.create(assets.image`marisaLaser`, 5)
        this.l1Laser.setPosition(this.sprite.x - 12, this.sprite.y - 60)
        sprites.setDataNumber(this.l1Laser, "damage", damage)
        this.l2Laser = sprites.create(assets.image`marisaLaser`, 5)
        this.l2Laser.setPosition(this.sprite.x + 12, this.sprite.y - 60)
        sprites.setDataNumber(this.l2Laser, "damage", damage)
        this.l1.z = -10
        this.l2.z = -10
        this.l1Laser.z = -10
        this.l2Laser.z = -10
    }
    
    public killLasers() {
        this.Lasers = false
        sprites.destroy(this.l1)
        sprites.destroy(this.l2)
        sprites.destroy(this.l1Laser)
        sprites.destroy(this.l2Laser)
    }
    
    public shoot() {
        if (game.runtime() - this.lastShot >= 80) {
            if (this.tier == 0) {
                this.projectiles.push(new playerProjectile(48))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
            } else if (this.tier == 1) {
                this.projectiles.push(new playerProjectile(32))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                if (!this.Lasers) {
                    this.spawnLasers(3)
                }
                
            } else if (this.tier == 2) {
                this.projectiles.push(new playerProjectile(22))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(183)
                this.projectiles.push(new playerProjectile(22))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(177)
                if (!this.Lasers) {
                    this.spawnLasers(3)
                }
                
            } else if (this.tier == 3) {
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(185)
                this.projectiles.push(new playerProjectile(20))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(175)
                if (!this.Lasers) {
                    this.spawnLasers(4)
                }
                
            } else if (this.tier == 4) {
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(185)
                this.projectiles.push(new playerProjectile(20))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(175)
                if (!this.Lasers) {
                    this.spawnLasers(5)
                }
                
            } else if (this.tier == 5) {
                this.projectiles.push(new playerProjectile(12))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(189)
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(185)
                this.projectiles.push(new playerProjectile(20))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.projectiles.push(new playerProjectile(15))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(175)
                this.projectiles.push(new playerProjectile(12))
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(171)
                if (!this.Lasers) {
                    this.spawnLasers(6)
                }
                
            }
            
            this.lastShot = game.runtime()
        }
        
    }
    
    public bomb() {
        if (this.bombs > 0 && game.runtime() - this.bombStart > 6100) {
            this.bombStart = game.runtime()
            this.bombs -= 1
        }
        
        
    }
    
}

let i = 0
class Game {
    hud: HUD
    hudChanged: boolean
    player: Player
    projectiles: Projectile[]
    enemies: Enemy[]
    frameTimeList: any[]
    codeTimeList: number[]
    gameOverActive: boolean
    continues: number
    lives: number
    nextWave: number
    highScore: number
    score: number
    graze: number
    blockBomb: boolean
    yes: boolean
    lastUpdateStart: number
    frameAverage: number
    average: number
    prevRunTime: number
    constructor() {
        this.hud = new HUD()
        this.hudChanged = false
        this.player = new Player()
        this.projectiles = []
        this.enemies = []
        this.frameTimeList = []
        this.codeTimeList = []
        this.gameOverActive = false
        this.continues = 3
        this.lives = 3
        this.nextWave = 0
        this.highScore = 0
        this.score = 0
        this.graze = 0
        this.blockBomb = false
    }
    
    public redrawHud() {
        this.hud.buildHud(this.highScore, this.score, this.player.health, this.player.bombs, this.player.power, this.graze)
        this.hudChanged = false
    }
    
    public gameOver() {
        if (!this.gameOverActive) {
            this.yes = false
            this.blockBomb = true
            this.player.sprite.setVelocity(0, 0)
            this.hud.gameOver(this.continues)
            this.gameOverActive = true
        } else if (controller.up.isPressed()) {
            this.hud.gameOverSprite.setImage(this.hud.buildGameOver(this.continues, true))
            //  = sprites.create(self.hud.buildGameOver(self.continues, True), 999)
            this.yes = true
        } else if (controller.down.isPressed()) {
            //  i also know that selecting no still makes you respawn, will fix that too
            this.hud.gameOverSprite.setImage(this.hud.buildGameOver(this.continues, false))
            this.yes = false
        } else if (controller.A.isPressed() && this.yes) {
            this.continues -= 1
            //  i know you basically have infinite continues because you can go negative, i'll fix it later but it's not pressing rn
            this.player.health = this.lives
            this.player.lastHit = game.runtime()
            sprites.destroy(this.hud.gameOverSprite)
            this.gameOverActive = false
            this.hudChanged = true
        }
        
    }
    
    public collisionCheck() {
        // spritekinds:
        // 0 = player
        // 1 = test projectile
        // 2 = player projectile
        // 3 = enemy projectile
        // 4 = enemy
        // 5 = playerLaser
        // 6 = item
        // 999 = hud
        sprites.onOverlap(4, 2, function enemyDamaged(enemySprite: Sprite, projSprite: Sprite) {
            let i: number;
            // print("in handler")
            let hitEnemy : Enemy = null
            let hitProjectile : Projectile = null
            let pos = -1
            // print("enemies: " + str(len(gameObj.enemies)))
            for (i = 0; i < gameObj.enemies.length; i++) {
                // print("checking " + str(i))
                if (gameObj.enemies[i].sprite == enemySprite) {
                    // print("after comparison")
                    hitEnemy = gameObj.enemies[i]
                    // print("after assignment")
                    break
                }
                
            }
            for (i = 0; i < gameObj.player.projectiles.length; i++) {
                pos += 1
                if (gameObj.player.projectiles[i].sprite == projSprite) {
                    hitProjectile = gameObj.player.projectiles[i]
                    break
                }
                
            }
            if (hitEnemy != null) {
                hitEnemy.takeDamage(sprites.readDataNumber(projSprite, "damage"))
            }
            
            if (hitProjectile != null) {
                sprites.destroy(hitProjectile.sprite)
                gameObj.player.projectiles.removeAt(pos)
            }
            
        })
        sprites.onOverlap(0, 3, function playerDamaged(playerSprite: Sprite, projSprite: Sprite) {
            let hitProjectile : Projectile = null
            if (game.runtime() - this.player.lastHit >= 3000 && game.runtime() - this.player.bombStart >= 6200) {
                // invulnerability handling
                for (let enemy of gameObj.enemies) {
                    for (let i = 0; i < enemy.projectiles.length; i++) {
                        if (enemy.projectiles[i].sprite == projSprite) {
                            hitProjectile = enemy.projectiles[i]
                            if (hitProjectile != null) {
                                sprites.destroy(hitProjectile.sprite)
                                enemy.projectiles.removeAt(i)
                            }
                            
                            break
                        }
                        
                    }
                }
                gameObj.player.takeDamage()
                this.hudChanged = true
            }
            
        })
        sprites.onOverlap(0, 6, function itemCollected(playerSprite: Sprite, itemSprite: Sprite) {
            // 0 = starItem
            // 1 = powerItemSmall
            // 2 = powerItemLarge
            // 3 = pointItem
            // 4 = extraLife
            // 5 = extraBomb
            let itemType = sprites.readDataNumber(itemSprite, "type")
            if (itemType == 0) {
                this.addScore(0, "starItem")
            }
            
            sprites.destroy(itemSprite)
            
        })
        // last measured frametime on the calliope was 40ms
        sprites.onOverlap(4, 5, function enemyHitByLaser(enemySprite: Sprite, laserSprite: Sprite) {
            let hitProjectile : Projectile = null
            for (let i = 0; i < gameObj.enemies.length; i++) {
                if (gameObj.enemies[i].sprite == enemySprite) {
                    gameObj.enemies[i].takeDamage(Math.idiv(sprites.readDataNumber(laserSprite, "damage") * 40, 16))
                }
                
            }
        })
    }
    
    public frametimes(t1: number, t2: number) {
        if (this.lastUpdateStart == null) {
            this.lastUpdateStart = game.runtime()
        } else {
            this.frameTimeList.push(game.runtime() - this.lastUpdateStart)
            this.lastUpdateStart = game.runtime()
        }
        
        if (this.frameTimeList.length == 60) {
            this.frameAverage = 0
            for (let o of this.frameTimeList) {
                this.frameAverage += o
            }
            this.frameAverage = Math.idiv(this.frameAverage, 60)
            this.frameTimeList = []
        }
        
        this.codeTimeList.push(t2 - t1)
        if (this.codeTimeList.length == 60) {
            this.average = 0
            for (let i of this.codeTimeList) {
                this.average += i
            }
            this.average = this.average / 60
            // print("average frametime last 100 frames:" + str(average))
            this.player.skin.sayText("" + Math.trunc(this.average) + "ft:" + ("" + this.frameAverage))
            this.codeTimeList = []
        }
        
    }
    
    public projectileDestructor() {
        let i: number;
        let curO: Projectile;
        let cur1: Projectile;
        let cur2: Projectile;
        let cur3: Enemy;
        let width = scene.screenWidth()
        let height = scene.screenHeight()
        // test projectiles
        if (this.projectiles.length > 0) {
            for (i = 0; i < this.projectiles.length; i++) {
                curO = this.projectiles[i]
                if (curO.sprite.x < 0 - 15 || curO.sprite.x > width - 15 || curO.sprite.y < 0 - 15 || curO.sprite.y > height + 15) {
                    sprites.destroy(curO.sprite)
                    this.projectiles.removeAt(i)
                }
                
            }
        }
        
        // player projectiles
        if (this.player.projectiles.length > 0) {
            for (i = this.player.projectiles.length - 1; i > -1; i += -1) {
                cur1 = this.player.projectiles[i]
                if (cur1.sprite.x < 0 - 15 || cur1.sprite.x > width - 15 || cur1.sprite.y < 0 - 15 || cur1.sprite.y > height + 15) {
                    sprites.destroy(cur1.sprite)
                    this.player.projectiles.removeAt(i)
                }
                
            }
        }
        
        // enemy projectiles
        if (this.enemies.length > 0) {
            for (let g of this.enemies) {
                for (i = g.projectiles.length - 1; i > -1; i += -1) {
                    cur2 = g.projectiles[i]
                    if (cur2.sprite.x < 0 - 15 || cur2.sprite.x > width - 15 || cur2.sprite.y < 0 - 15 || cur2.sprite.y > height + 15) {
                        sprites.destroy(cur2.sprite)
                        g.projectiles.removeAt(i)
                    }
                    
                }
            }
        }
        
        // enemies
        if (this.enemies.length > 0) {
            i = 0
            for (let enemy of this.enemies) {
                cur3 = enemy
                if (cur3.sprite.x < -15 || cur3.sprite.x > width - 15 || cur3.sprite.y < -15 || cur3.sprite.y > height + 15 || cur3.dead == true) {
                    sprites.destroy(cur3.sprite)
                    if (cur3.projectiles.length == 0) {
                        this.enemies.removeAt(i)
                    }
                    
                }
                
                i += 1
            }
        }
        
    }
    
    public addScore(score: number = 0, item: string = "") {
        if (item == "") {
            this.score += score
        } else if (item == "starItem") {
            this.score += 5
        }
        
        this.hudChanged = true
    }
    
    public bombActive(first: boolean = false) {
        let cur2: Projectile;
        let starItem: Sprite;
        if (this.enemies.length > 0) {
            for (let g of this.enemies) {
                for (let i = g.projectiles.length - 1; i > -1; i += -1) {
                    cur2 = g.projectiles[i]
                    if (first) {
                        starItem = sprites.create(assets.image`starItem`, 6)
                        sprites.setDataNumber(starItem, "type", 0)
                        starItem.setPosition(cur2.sprite.x, cur2.sprite.y)
                        starItem.follow(this.player.sprite, 200)
                    }
                    
                    sprites.destroy(cur2.sprite)
                    g.projectiles.removeAt(i)
                }
            }
        }
        
    }
    
    public waves() {
        if (game.runtime() > this.nextWave) {
            this.enemies.push(new Enemy("test", this.player))
            this.nextWave = game.runtime() + 1200
        }
        
        
    }
    
    public enemyActions() {
        for (let obj of this.enemies) {
            obj.goRoute()
        }
    }
    
    public mainLoop() {
        this.prevRunTime = 0
        this.collisionCheck()
        this.hud.buildHud(this.highScore, this.score, this.player.health, this.player.bombs, this.player.power, this.graze)
        game.onUpdate(function onUpdate() {
            // print("frametime: " + str(game.runtime() - self.prevRunTime))
            let startOfUpdate = control.micros()
            if (!this.gameOverActive) {
                this.player.movementController()
                this.projectileDestructor()
                this.player.shoot()
                if (this.player.sprite.x > 115) {
                    [this.player.sprite.setPosition(115, this.player.sprite.y), this.player.skin.setPosition(115, this.player.sprite.y)]
                }
                
                this.enemyActions()
                this.waves()
                // bombing
                if (controller.A.isPressed() && !this.blockBomb && this.player.bombs > 0 && game.runtime() - this.player.bombStart >= 6000) {
                    this.player.bomb()
                    this.bombActive(true)
                    this.hudChanged = true
                } else if (this.blockBomb && !controller.A.isPressed()) {
                    this.blockBomb = false
                }
                
                if (game.runtime() - this.player.bombStart <= 6000) {
                    this.bombActive()
                }
                
            }
            
            if (this.player.health <= 0) {
                this.gameOver()
            }
            
            if (this.hudChanged) {
                this.redrawHud()
            }
            
            this.frametimes(startOfUpdate, control.micros())
        })
    }
    
}

let gameObj = new Game()
gameObj.mainLoop()
