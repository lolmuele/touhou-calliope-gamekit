class HUD:

    def __init__(self):

        self.hudImage = assets.image("hudBackground")
        self.hudImage.print_center("EOMD", y = 108, color = 4, font = image.font5)
        self.background: Sprite = sprites.create(assets.image("hudBackground"), 999)
        self.background.z = 999
        self.background.set_position(140, 60)
        
        scene.set_background_color(6)
        # self.stageBackground: Sprite = sprites.create(assets.image("stageBackground"), 999)
        # self.stageBackground.z = -100
        # self.stageBackground.set_position(60, 60)
        pass

    def buildGameOver(self, continues:int, yes:bool):
        gameOverImage = assets.image("gameOver")
        gameOverImage.print_center("Game Over", y=10, color=2, font=image.font12)
        gameOverImage.print_center("Continue ?", y=45, color=1, font=image.font8)
        gameOverImage.print_center(str(continues) + " Left", y=55, color=1, font=image.font8)
        
        if yes:
            gameOverImage.print_center("> Yes <", y=70, color=5, font=image.font8)
            gameOverImage.print_center("No", y=80, color=2, font=image.font8)

        elif not yes:
            gameOverImage.print_center("Yes", y=70, color=2, font=image.font8)
            gameOverImage.print_center("> No <", y=80, color=5, font=image.font8)

        return gameOverImage
    
    def buildHud(self, highScore: int = 0, score: int = 0, lives: int = 0, bombs: int = 0, power: int = 0, graze: int = 0, point:int = 0):
        hudImage = self.hudImage.clone()
        hudImage.print_center("HiSc", y = 10, color = 9, font = image.font5)
        hudImage.print_center(str(highScore), y = 17, color = 10, font = image.font5)
        hudImage.print_center("Score", y = 23, color = 9, font = image.font5)
        hudImage.print_center(str(score), y = 29, color = 10, font = image.font5)

        hudImage.print_center("Lives", y = 35, color = 9, font = image.font5)
        for i in range(lives):
            hudImage.draw_transparent_image(assets.image("livesStar"), 7 + i * 9, 42)

        hudImage.print_center("Bombs", y = 53, color = 9, font = image.font5)
        for i in range(bombs):
            hudImage.draw_transparent_image(assets.image("bombsStar"), 7 + i * 9, 60)
            
        hudImage.print_center("Power", y = 70, color = 9, font = image.font5)
        hudImage.fill_rect(6, 78, 28 * power // 128, 8, 9)
        hudImage.print_center(str(power if power < 128 else " max") + "  ", y = 79, color = 10, font = image.font5)

        hudImage.print_center("Graze", y = 88, color = 9, font = image.font5)
        hudImage.print_center(str(graze), y = 95, color = 10, font = image.font5)
        self.background.set_image(hudImage)

    def gameOver(self, continues):
        gameOverImage = self.buildGameOver(continues, False)
        self.gameOverSprite: Sprite = sprites.create(gameOverImage, 999)
        self.gameOverSprite.z = 999
        self.gameOverSprite.set_position(60, 60)
    
        
#TODO: 

#add enemies
    #need to make pathing work -kinda implemented
    #shots can't home yet -they can now
    #need HP -works
    #handle destruction -works 

#add health/damage handling
    #player can take damage and has health -done
    #iframes after hit -works
    #game over, continue & restart -kinda, really basic but you can respawn

#add bombs -works
#add hud functionality -works
#make hitbox not move within the sprite -works i'm pretty sure

#add bosses
#visuals (ugh)
#add menu
#add drops

#had a chance to test on real hardware today and...
#performance is pretty horrendous:
#40+ ms frametime, possibly a leak:
#about double that of the ~20ms in the web simulator
#   not sure if it's actually slowing down increasingly or if on-screen console prints are so heavy on the calliope,
#   it feels like it's only slowing down when console output is on, while it was on the frametimes went to abt 65+ms gradually
#   but i feel like i shouldn't be leaking objects so idk
#are there major performance improvements i can make rn?

class Projectile:

    def __init__(self, spriteName = "projectile", spriteKind = 1, xVel = 0, yVel = 0, maxSpeed = 50):
        if spriteName == "projectile":
            self.sprite = sprites.create(assets.tile("projectile"), 1)
            self.sprite.set_kind(spriteKind)
        self.xVel = xVel
        self.yVel = yVel
        self.maxSpeed = maxSpeed

    def homeTo(self, x, y):
        diffX = x - self.sprite.x
        diffY = y - self.sprite.y

        #does this catch division by 0? idek
        if diffX == 0 and diffY == 0:
            self.xVel = 0
            self.yVel = self.maxSpeed

        elif abs(diffX) >= abs(diffY):
            self.xVel = self.maxSpeed * diffX/abs(diffX)
            self.yVel = self.xVel * (diffY/diffX)
        else:
            self.yVel = self.maxSpeed * diffY/abs(diffY)
            self.xVel = self.yVel * (diffX/diffY)

        self.sprite.set_velocity(self.xVel, self.yVel)

    def setAngle(self, angle):
        if angle < 0:
            angle += 360
        rad = angle * Math.PI / 180

        self.xVel = Math.sin(rad) * self.maxSpeed
        self.yVel = Math.cos(rad) * self.maxSpeed

        self.sprite.set_velocity(self.xVel, self.yVel)

class playerProjectile(Projectile):

    def __init__(self, damage: int = 1):
        super().__init__(spriteName = "marisaShot", maxSpeed = 250, spriteKind = 2)
        self.damage = damage
        self.sprite = sprites.create(assets.image("marisaShotImage2"), 2)
        sprites.set_data_number(self.sprite, "damage", self.damage)
        self.sprite.z = -10
        


class redCircleProjectile(Projectile):
    def __init__(self):
            super().__init__(spriteName = "redBall", maxSpeed = 30, spriteKind = 2)
            self.sprite = sprites.create(assets.image("redBall"), 3)


class Enemy:
    def __init__(self, spriteName: str, player: Player, health = 950):
        if spriteName == "test":
            self.sprite = sprites.create(assets.tile("marisa"), 4)
            self.sprite.z = 10
        self.projectiles: List[Projectile] = []
        self.health = health
        self.dead = False
        #route format:
        #[[x: int, y: int, maxSpeed:int, waitTime:int(in ms), shoot: bool], [x, y...]]
        #self.route = []
        #testroute here:
        self.route = [[60, -10, 30, 500, 1], [60, 25, 30, 2000, 1], [12, 30, 300, 800, 1], [78, 90, 90, 0, 1], [0, 0, 50, 0, 1]]
        self.sprite.set_position(self.route[0][0], self.route[0][1])
        self.routePoint = 1
        self.waitTime = 0
        self.player: Player = player
        self.pointReachedTime = 0
        


    def shoot(self):

        self.projectiles.append(redCircleProjectile())
        self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y)
        self.projectiles[len(self.projectiles)-1].setAngle(0)

    def shootHoming(self):

        self.projectiles.append(redCircleProjectile())
        self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y)
        self.projectiles[len(self.projectiles)-1].homeTo(self.player.sprite.x, self.player.sprite.y)

    def takeDamage(self, damage = 1):
        self.health -= damage
        if self.health <= 0:
            self.dead = True

    def homeTo(self, x, y):

        diffX = x - self.sprite.x
        diffY = y - self.sprite.y

        #does this catch division by 0? idek
        if diffX == 0 and diffY == 0:
            self.xVel = 0
            self.yVel = self.maxSpeed

        elif abs(diffX) >= abs(diffY):
            self.xVel = self.maxSpeed * diffX/abs(diffX)
            self.yVel = self.xVel * (diffY/diffX)
        else:
            self.yVel = self.maxSpeed * diffY/abs(diffY)
            self.xVel = self.yVel * (diffX/diffY)

        self.sprite.set_velocity(self.xVel, self.yVel)

    def closeEnough(self, x1, x2, y1, y2, speed):

        tolerance = speed // 50 if speed // 50 > 2 else 2
        diffX = abs(x1 - x2)
        diffY = abs(y1 - y2)

        if diffX <= tolerance and diffY <= tolerance:
            return True
        else:
            return False

    def goRoute(self):

        if self.dead:
            return

        if self.waitTime > 0:
            self.waitTime -= game.runtime() - self.pointReachedTime
            self.pointReachedTime = game.runtime()

        elif self.routePoint == len(self.route):
            pass

        elif self.closeEnough(self.sprite.x, self.route[self.routePoint][0], self.sprite.y, self.route[self.routePoint][1], self.route[self.routePoint][2]):
            self.pointReachedTime = game.runtime()
            self.waitTime = self.route[self.routePoint][3]

            if self.waitTime > 0:
                self.sprite.set_velocity(0, 0)
            
            if self.route[self.routePoint][4]:
                self.shootHoming()
                self.route[self.routePoint][4] = 0
            
            self.routePoint += 1

        if not self.routePoint == len(self.route) and self.waitTime <= 0:
            self.maxSpeed = self.route[self.routePoint][2]
            self.homeTo(self.route[self.routePoint][0], self.route[self.routePoint][1])



class Player:
    def __init__(self):
        self.sprite = sprites.create(assets.image("""hitboxImage"""), SpriteKind.player)
        self.sprite.set_stay_in_screen(True)
        self.sprite.set_kind(0)
        self.tier = 5
        self.projectiles = []
        self.slowDownVariable = 0
        self.skin = sprites.create(assets.tile("""marisa"""))
        self.skin.set_position(self.sprite.x , self.sprite.y - 1)
        self.health = 3
        self.bombs = 3
        self.power = 0
        self.lastHit = -3000 #so you're not invincible at the start of the game
        #self.spawnLasers()
        self.Lasers = False
        self.bombStart = -10000
        self.lastShot = 0
    
    
    def takeDamage(self):
        self.health -= 1
        self.bombs = 3 #don't question it, this is how EOSD works, even if you have more than 3 
        scene.camera_shake(2, 300) #visual feedback for getting hit
        self.lastHit = game.runtime()
        animation.run_image_animation(self.skin,  #visual feedback for i-frames
        [assets.tile("""damageFlicker"""), assets.tile("""marisa"""),
        assets.tile("""damageFlicker"""), assets.tile("""marisa"""),
        assets.tile("""damageFlicker"""), assets.tile("""marisa"""),
        assets.tile("""damageFlicker"""), assets.tile("""marisa"""),
        assets.tile("""damageFlicker"""), assets.tile("""marisa"""),
        assets.tile("""damageFlicker"""), assets.tile("""marisa""")], 
        250, False)


    def movementController(self):

        xVel = 0
        yVel = 0

        if controller.up.is_pressed():
            yVel -= 80

        if controller.down.is_pressed():
            yVel += 80

        if controller.left.is_pressed():
            xVel -= 80

        if controller.right.is_pressed():
            xVel += 80

        if controller.B.is_pressed() and self.Lasers:
            xVel = int(xVel / 2)
            yVel = int(yVel / 2)
            self.sprite.z = 10

            self.l1.set_position(self.sprite.x - 5, self.sprite.y - 10)
            self.l2.set_position(self.sprite.x + 5, self.sprite.y - 10)
            self.l1Laser.set_position(self.sprite.x - 5, self.sprite.y -70 )
            self.l2Laser.set_position(self.sprite.x + 5, self.sprite.y -70 )
        
        else:
            self.sprite.z = 0


        self.sprite.set_velocity(xVel, yVel)
        self.skin.set_position(self.sprite.x, self.sprite.y)
        if self.Lasers and not controller.B.is_pressed():
            self.l1.set_position(self.sprite.x - 12, self.sprite.y)
            self.l2.set_position(self.sprite.x + 12, self.sprite.y)
            self.l1Laser.set_position(self.sprite.x - 12, self.sprite.y -60 )
            self.l2Laser.set_position(self.sprite.x + 12, self.sprite.y -60 )

    def spawnLasers(self, damage = 3):

        self.Lasers = True
        self.l1 = sprites.create(assets.image("""miniHakkero"""))
        self.l2 = sprites.create(assets.image("""miniHakkero"""))
        self.l1.set_position(self.sprite.x - 12, self.sprite.y)
        self.l2.set_position(self.sprite.x + 12, self.sprite.y)
        self.l1Laser = sprites.create(assets.image("marisaLaser"), 5)
        self.l1Laser.set_position(self.sprite.x - 12, self.sprite.y-60)
        sprites.set_data_number(self.l1Laser, "damage", damage)
        self.l2Laser = sprites.create(assets.image("marisaLaser"), 5)
        self.l2Laser.set_position(self.sprite.x + 12, self.sprite.y-60)
        sprites.set_data_number(self.l2Laser, "damage", damage)
        self.l1.z = -10
        self.l2.z = -10
        self.l1Laser.z = -10
        self.l2Laser.z = -10

    def killLasers(self):
        self.Lasers = False
        sprites.destroy(self.l1)
        sprites.destroy(self.l2)
        sprites.destroy(self.l1Laser)
        sprites.destroy(self.l2Laser)

    


    def shoot(self):
        if game.runtime() - self.lastShot >= 80:

            if self.tier == 0:
                self.projectiles.append(playerProjectile(48))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                

            elif self.tier == 1:
                self.projectiles.append(playerProjectile(32))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                if not self.Lasers:
                    self.spawnLasers(3)
                

            elif self.tier == 2:
                self.projectiles.append(playerProjectile(22))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(183)
                self.projectiles.append(playerProjectile(22))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(177)
                if not self.Lasers:
                    self.spawnLasers(3)

            elif self.tier == 3:
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(185)
                self.projectiles.append(playerProjectile(20))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(175)
                if not self.Lasers:
                    self.spawnLasers(4)

            elif self.tier == 4:
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(185)
                self.projectiles.append(playerProjectile(20))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(175)
                if not self.Lasers:
                    self.spawnLasers(5)

            elif self.tier == 5:
                self.projectiles.append(playerProjectile(7))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(189)
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(185)
                self.projectiles.append(playerProjectile(20))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.projectiles.append(playerProjectile(15))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(175)
                self.projectiles.append(playerProjectile(7))
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(171)
                if not self.Lasers:
                    self.spawnLasers(6)

            self.lastShot = game.runtime()

    def bomb(self):
        if self.bombs > 0 and game.runtime() - self.bombStart > 6100:
            self.bombStart = game.runtime()
            self.bombs -= 1
            
        pass

i = 0

class Game:
    def __init__(self):
        self.hud = HUD()
        self.hudChanged = False
        self.player = Player()
        self.projectiles: List[Projectile] = []
        self.enemies: List[Enemy] = []
        self.frameTimeList = []
        self.codeTimeList = []
        self.gameOverActive = False
        self.continues = 3
        self.lives = 3
        self.nextWave = 0
        self.highScore = 0
        self.score = 0
        self.graze = 0
        self.blockBomb = False

    def redrawHud(self):
        self.hud.buildHud(highScore = self.highScore, score = self.score, lives = self.player.health, bombs = self.player.bombs, power = self.player.power, graze = self.graze)

    def gameOver(self):

        if not self.gameOverActive:
            self.yes = False
            self.blockBomb = True
            self.player.sprite.set_velocity(0, 0)
            self.hud.gameOver(self.continues)
            self.gameOverActive = True

        else:
        
            if controller.up.is_pressed():
                
                self.hud.gameOverSprite.set_image(self.hud.buildGameOver(self.continues, True))  # = sprites.create(self.hud.buildGameOver(self.continues, True), 999)

                self.yes = True
                    
            elif controller.down.is_pressed():
                
                # i also know that selecting no still makes you respawn, will fix that too
                self.hud.gameOverSprite.set_image(self.hud.buildGameOver(self.continues, False))

                self.yes = False

            elif controller.A.is_pressed() and self.yes:
                
                self.continues -= 1 # i know you basically have infinite continues because you can go negative, i'll fix it later but it's not pressing rn
                self.player.health = self.lives
                self.player.lastHit = game.runtime() 
                sprites.destroy(self.hud.gameOverSprite)
                self.gameOverActive = False
                self.hudChanged = True

    def collisionCheck(self):
        #spritekinds:
        #0 = player
        #1 = test projectile
        #2 = player projectile
        #3 = enemy projectile
        #4 = enemy
        #5 = playerLaser
        #6 = item
        #999 = hud

        def enemyDamaged(enemySprite: Sprite, projSprite: Sprite):
            #print("in handler")
            hitEnemy: Enemy = None
            hitProjectile: Projectile = None
            pos = -1

            #print("enemies: " + str(len(gameObj.enemies)))
            for i in range(len(gameObj.enemies)):
                #print("checking " + str(i))
                if gameObj.enemies[i].sprite == enemySprite:
                    #print("after comparison")
                    hitEnemy = gameObj.enemies[i]
                    #print("after assignment")
                    break
            
            for i in range(len(gameObj.player.projectiles)):
                pos += 1
                if gameObj.player.projectiles[i].sprite == projSprite:
                    hitProjectile = gameObj.player.projectiles[i]
                    break

            if hitEnemy != None:
                hitEnemy.takeDamage(sprites.read_data_number(projSprite, "damage"))

            if hitProjectile != None:
                sprites.destroy(hitProjectile.sprite)
                gameObj.player.projectiles.remove_at(pos)
        
        sprites.on_overlap(4, 2, enemyDamaged)

        def playerDamaged(playerSprite: Sprite, projSprite: Sprite):
            hitProjectile: Projectile = None

            if game.runtime() - self.player.lastHit >= 3000 and game.runtime() - self.player.bombStart >= 6200: #invulnerability handling
                for enemy in gameObj.enemies:     
                    for i in range(len(enemy.projectiles)):
                        if enemy.projectiles[i].sprite == projSprite:
                            hitProjectile = enemy.projectiles[i]
                            if hitProjectile != None:
                                sprites.destroy(hitProjectile.sprite)
                                enemy.projectiles.remove_at(i)
                            break

                gameObj.player.takeDamage()
                self.hudChanged = True

        sprites.on_overlap(0, 3, playerDamaged)

        def itemCollected(playerSprite: Sprite, itemSprite: Sprite):
            #0 = starItem
            #1 = powerItemSmall
            #2 = powerItemLarge
            #3 = pointItem
            #4 = extraLife
            #5 = extraBomb
            itemType = sprites.read_data_number(itemSprite, "type")

            if itemType == 0:
                self.addScore(item = "starItem")




            sprites.destroy(itemSprite)
            pass
        
        sprites.on_overlap(0, 6, itemCollected)

        def enemyHitByLaser(enemySprite: Sprite, laserSprite: Sprite):
            hitProjectile: Projectile = None

            for i in range(len(gameObj.enemies)):
                if gameObj.enemies[i].sprite == enemySprite:
                    gameObj.enemies[i].takeDamage((sprites.read_data_number(laserSprite, "damage")) * 40 // 16) #last measured frametime on the calliope was 40ms



        sprites.on_overlap(4, 5, enemyHitByLaser)

    def frametimes(self, t1, t2):
        if self.lastUpdateStart == None:
            self.lastUpdateStart = game.runtime()

        else:
            self.frameTimeList.append(game.runtime() - self.lastUpdateStart)
            self.lastUpdateStart = game.runtime()

        if len(self.frameTimeList) == 60:
            self.frameAverage = 0
            for o in self.frameTimeList:
                self.frameAverage += o
            self.frameAverage = self.frameAverage // 59
            self.frameTimeList = []

        self.codeTimeList.append((t2 - t1))
        if len(self.codeTimeList) == 60:
            self.average = 0
            for i in self.codeTimeList:
                self.average += i
            self.average = self.average / 60
            #print("average frametime last 100 frames:" + str(average))
            self.player.skin.say_text(str(int(self.average)) + "ft:" + str(self.frameAverage))
            
            self.codeTimeList = []



    

    def projectileDestructor(self):
        width = scene.screen_width()
        height = scene.screen_height()
        #test projectiles
        if len(self.projectiles) > 0:
            for i in range(len(self.projectiles)):
                curO: Projectile = self.projectiles[i]
                if curO.sprite.x < 0 - 15 or curO.sprite.x > width -15 or curO.sprite.y < 0 - 15 or curO.sprite.y > height + 15:
                    sprites.destroy(curO.sprite)
                    self.projectiles.remove_at(i)
                
        #player projectiles
        if len(self.player.projectiles) > 0:
            for i in range(len(self.player.projectiles)-1, -1, -1):
                cur1: Projectile = self.player.projectiles[i]
                if cur1.sprite.x < 0 - 15 or cur1.sprite.x > width - 15 or cur1.sprite.y < 0 - 15 or cur1.sprite.y > height + 15:
                    sprites.destroy(cur1.sprite)
                    self.player.projectiles.remove_at(i)
                   
        #enemy projectiles
        if len(self.enemies) > 0:
            for g in self.enemies:
                for i in range(len(g.projectiles)-1, -1, -1):
                    cur2: Projectile = g.projectiles[i]
                    if cur2.sprite.x < 0 - 15 or cur2.sprite.x > width - 15 or cur2.sprite.y < 0 - 15 or cur2.sprite.y > height + 15:
                        sprites.destroy(cur2.sprite)
                        g.projectiles.remove_at(i)
                        
        #enemies
        if len(self.enemies) > 0:
            i = 0
            for enemy in self.enemies:
                cur3: Enemy = enemy
                if cur3.sprite.x < -15 or cur3.sprite.x > width - 15 or cur3.sprite.y < -15 or cur3.sprite.y > height + 15 or cur3.dead == True:
                    sprites.destroy(cur3.sprite)
                    if len(cur3.projectiles) == 0:
                        self.enemies.remove_at(i)
                        
                i += 1

    def addScore(self, score:int = 0, item:str = ""):
        if item == "":
            self.score += score
        elif item == "starItem":
            self.score += 5

        self.hudChanged = True


    def bombActive(self, first: bool = False):
        if len(self.enemies) > 0:
            for g in self.enemies:
                for i in range(len(g.projectiles) -1, -1, -1):
                    cur2: Projectile = g.projectiles[i]
                    if first:
                        starItem = sprites.create(assets.image("starItem"), 6)
                        sprites.set_data_number(starItem, "type", 0)
                        starItem.set_position(cur2.sprite.x, cur2.sprite.y)
                        starItem.follow(self.player.sprite, speed = 200)
                        
                        
                    sprites.destroy(cur2.sprite)
                    g.projectiles.remove_at(i)


    def waves(self):
        if game.runtime() > self.nextWave:
            self.enemies.append(Enemy("test", self.player))
            self.nextWave = game.runtime() + 1200
        pass

    def enemyActions(self):
        for obj in self.enemies:
            obj.goRoute()


    def mainLoop(self):
        self.prevRunTime = 0
        self.collisionCheck()
        self.hud.buildHud(highScore = self.highScore, score = self.score, lives = self.player.health, bombs = self.player.bombs, power = self.player.power, graze = self.graze)
        
        def onUpdate():
            #print("frametime: " + str(game.runtime() - self.prevRunTime))
            startOfUpdate = control.micros()
            if not self.gameOverActive:
                self.player.movementController()
                self.projectileDestructor()
                self.player.shoot()
                if self.player.sprite.x > 115: self.player.sprite.set_position(115, self.player.sprite.y), self.player.skin.set_position(115, self.player.sprite.y)
                self.enemyActions()
                self.waves()
                #bombing
                if controller.A.is_pressed() and not self.blockBomb and self.player.bombs > 0 and game.runtime() - self.player.bombStart >= 6000: self.player.bomb(); self.bombActive(first = True); self.hudChanged = True
                elif self.blockBomb and not controller.A.is_pressed(): self.blockBomb = False
                if game.runtime() - self.player.bombStart <= 6000: self.bombActive()
            if self.player.health <= 0: self.gameOver()
            if self.hudChanged: self.redrawHud()
            self.frametimes(startOfUpdate, control.micros())
            


        game.on_update(onUpdate)




gameObj = Game()
gameObj.mainLoop()
