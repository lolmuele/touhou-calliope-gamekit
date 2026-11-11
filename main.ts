class HUD {
    background: Sprite
    stageBackground: Sprite
    gameOverSprite: Sprite
    constructor() {
        this.background = sprites.create(assets.image`hudBackground`, 999)
        this.background.z = 999
        this.background.setPosition(140, 60)
        this.stageBackground = sprites.create(assets.image`stageBackground`, 999)
        this.stageBackground.z = -100
        this.stageBackground.setPosition(60, 60)
        
    }
    
    public buildGameOver(continues: number, yes: boolean): Image {
        let gameOverImage = assets.image`gameOver`
        gameOverImage.printCenter("Game Over", 10, 2, image.font12)
        gameOverImage.printCenter("Continue ?", 45, 1, image.font8)
        gameOverImage.printCenter("" + continues + " Left", 55, 1, image.font8)
        if (yes) {
            gameOverImage.printCenter("> Yes <", 70, 5, image.font8)
            gameOverImage.printCenter("No", 80, 6, image.font8)
        } else if (!yes) {
            gameOverImage.printCenter("Yes", 70, 6, image.font8)
            gameOverImage.printCenter("> No <", 80, 5, image.font8)
        }
        
        return gameOverImage
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
// add bombs
// add hud functionality
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
    constructor() {
        super("marisaShot", 2, 0, 0, 250)
        // self.sprite = sprites.create(assets.tile("marisaShot"), 2)
        this.sprite = sprites.create(assets.image`marisaShotImage2`, 2)
    }
    
}

// self.sprite.set_scale(1, ScaleAnchor.MIDDLE)
class redCircleProjectile extends Projectile {
    constructor() {
        super("redBall", 2, 0, 0, 30)
        this.sprite = sprites.create(assets.tile`redBall`, 3)
        this.sprite.setScale(0.8, ScaleAnchor.Middle)
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
    constructor(spriteName: string, player: Player, health: number = 5) {
        if (spriteName == "test") {
            this.sprite = sprites.create(assets.tile`marisa`, 4)
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
    
    public takeDamage() {
        this.health -= 1
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
    level: number
    projectiles: Projectile[]
    slowDownVariable: number
    skin: Sprite
    health: number
    lastHit: number
    Lasers: boolean
    l1: Sprite
    l2: Sprite
    constructor() {
        this.sprite = sprites.create(assets.tile`hitbox`, SpriteKind.Player)
        this.sprite.setStayInScreen(true)
        this.sprite.setKind(0)
        this.level = 1
        this.projectiles = []
        this.slowDownVariable = 0
        this.skin = sprites.create(assets.tile`marisa`)
        // self.skin.follow(self.sprite)
        this.skin.setPosition(this.sprite.x, this.sprite.y - 1)
        this.health = 3
        this.lastHit = -3000
    }
    
    // so you're not invincible at the start of the game
    public takeDamage() {
        this.health -= 1
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
        
        if (controller.B.isPressed()) {
            xVel = Math.trunc(xVel / 2)
            yVel = Math.trunc(yVel / 2)
            this.sprite.z = 10
        } else {
            this.sprite.z = 0
        }
        
        if (controller.A.isPressed()) {
            this.bomb()
        }
        
        this.sprite.setVelocity(xVel, yVel)
        this.skin.setPosition(this.sprite.x, this.sprite.y)
        if (this.Lasers) {
            this.l1.setPosition(this.sprite.x - 12, this.sprite.y)
            this.l2.setPosition(this.sprite.x + 12, this.sprite.y)
        }
        
    }
    
    public spawnLasers() {
        this.Lasers = true
        this.l1 = sprites.create(assets.image`miniHakkero`)
        this.l2 = sprites.create(assets.image`miniHakkero`)
        this.l1.setPosition(this.sprite.x - 12, this.sprite.y)
        this.l2.setPosition(this.sprite.x + 12, this.sprite.y)
    }
    
    public killLasers() {
        this.Lasers = false
        sprites.destroy(this.l1)
        sprites.destroy(this.l2)
    }
    
    public shoot() {
        if (this.slowDownVariable == 2) {
            if (this.level == 0) {
                this.projectiles.push(new playerProjectile())
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.slowDownVariable = 0
            }
            
            if (this.level == 1) {
                this.projectiles.push(new playerProjectile())
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.slowDownVariable = 0
            }
            
            if (this.level == 2) {
                this.projectiles.push(new playerProjectile())
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(185)
                this.projectiles.push(new playerProjectile())
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(180)
                this.projectiles.push(new playerProjectile())
                this.projectiles[this.projectiles.length - 1].sprite.setPosition(this.sprite.x, this.sprite.y - 8)
                this.projectiles[this.projectiles.length - 1].setAngle(175)
                this.slowDownVariable = 0
            }
            
        } else {
            this.slowDownVariable += 1
        }
        
    }
    
    public bomb() {
        console.log("bomb")
        
    }
    
}

let i = 0
class Game {
    hud: HUD
    player: Player
    projectiles: Projectile[]
    enemies: Enemy[]
    frameTimeList: number[]
    gameOverActive: boolean
    continues: number
    lives: number
    yes: boolean
    prevRunTime: number
    constructor() {
        this.hud = new HUD()
        this.player = new Player()
        this.projectiles = []
        this.enemies = [new Enemy("test", this.player)]
        this.frameTimeList = []
        info.showScore(true)
        this.gameOverActive = false
        this.continues = 3
        this.lives = 3
    }
    
    public gameOver() {
        if (!this.gameOverActive) {
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
        }
        
    }
    
    public collisionHandler() {
        // print("collided!")
        
    }
    
    public collisionCheck() {
        // spritekinds:
        // 0 = player
        // 1 = test projectile
        // 2 = player projectile
        // 3 = enemy projectile
        // 4 = enemy
        // 999 = hud
        sprites.onOverlap(0, 1, function testOverlap() {
            this.collisionHandler()
        })
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
                hitEnemy.takeDamage()
            }
            
            if (hitProjectile != null) {
                sprites.destroy(hitProjectile.sprite)
                gameObj.player.projectiles.removeAt(pos)
            }
            
        })
        sprites.onOverlap(0, 3, function playerDamaged(playerSprite: Sprite, projSprite: Sprite) {
            let hitProjectile : Projectile = null
            if (game.runtime() - this.player.lastHit >= 3000) {
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
            }
            
        })
    }
    
    public frametimes(t1: number, t2: number) {
        let average: number;
        this.frameTimeList.push(t2 - t1)
        this.prevRunTime = game.runtime()
        if (this.frameTimeList.length == 60) {
            average = 0
            for (let i of this.frameTimeList) {
                average += i
            }
            average = average / 60
            // print("average frametime last 100 frames:" + str(average))
            this.player.skin.sayText("" + Math.trunc(average))
            this.frameTimeList = []
        }
        
    }
    
    public projectileTest() {
        let curO: Projectile;
        
        if (i % 5 == 0) {
            this.projectiles.push(new Projectile("projectile"))
            // self.projectiles.homeTo(self.player.sprite.x, self.player.sprite.y)
            for (let g = 0; g < this.projectiles.length; g++) {
                curO = this.projectiles[g]
                this.projectiles[this.projectiles.length - 1].setAngle(i)
                if (i >= 360) {
                    i = 0
                }
                
            }
        }
        
        i = i + 1
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
            for (i = 0; i < this.player.projectiles.length; i++) {
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
                for (i = 0; i < g.projectiles.length; i++) {
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
    
    public waves() {
        
    }
    
    public enemyActions() {
        for (let obj of this.enemies) {
            obj.goRoute()
        }
    }
    
    public mainLoop() {
        this.prevRunTime = 0
        this.collisionCheck()
        game.stats = true
        game.onUpdate(function onUpdate() {
            // print("frametime: " + str(game.runtime() - self.prevRunTime))
            let startOfUpdate = control.micros()
            if (!this.gameOverActive) {
                this.projectileTest()
                this.player.movementController()
                this.projectileDestructor()
                this.player.shoot()
                if (this.player.sprite.x > 115) {
                    [this.player.sprite.setPosition(115, this.player.sprite.y), this.player.skin.setPosition(115, this.player.sprite.y)]
                }
                
                this.enemyActions()
            }
            
            if (this.player.health <= 0) {
                this.gameOver()
            }
            
            this.frametimes(startOfUpdate, control.micros())
        })
    }
    
}

let gameObj = new Game()
gameObj.mainLoop()
