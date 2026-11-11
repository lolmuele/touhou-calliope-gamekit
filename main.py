class HUD:

    def __init__(self):
        self.livesStars: List[Sprite] = []
        self.bombsStars: List[Sprite] = []
        self.powerBar: List[Sprite] = []
        #self.hudImage = assets.image("hudBackground")
        self.background: Sprite = sprites.create(assets.image("hudBackground"), 999)
        self.background.z = 999
        self.background.set_position(140, 60)
        
        self.stageBackground: Sprite = sprites.create(assets.image("stageBackground"), 999)
        self.stageBackground.z = -100
        self.stageBackground.set_position(60, 60)
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
    
    def buildHud(self, highScore: int = 0, score: int = 0, lives: int = 3, bombs: int = 3, power: int = 100, graze: int = 0, point:int = 0):
        hudImage = assets.image("hudBackground")
        hudImage.print_center("HiSc", y = 10, color = 9, font = image.font5)
        hudImage.print_center(str(highScore), y = 17, color = 10, font = image.font5)
        hudImage.print_center("Score", y = 23, color = 9, font = image.font5)
        hudImage.print_center(str(score), y = 29, color = 10, font = image.font5)

        hudImage.print_center("Lives", y = 35, color = 9, font = image.font5)
        for i in range(lives):
            star = sprites.create(assets.image("livesStar"))
            star.set_position(131 + i * 9, 46)
            star.z = 1000
            self.livesStars.append(star)

        hudImage.print_center("Bombs", y = 53, color = 9, font = image.font5)
        for i in range(bombs):
            star = sprites.create(assets.image("bombsStar"))
            star.set_position(131 + i * 9, 64)
            star.z = 1000
            self.bombsStars.append(star)
            
        hudImage.print_center("Power", y = 70, color = 9, font = image.font5)
        
        # for i in range((128 // power if power != 0 else 0) * 28):
        #     barPart = sprites.create(assets.image("barPart"))
        #     barPart.set_position(127 + i, 81)
        #     barPart.z = 999
        #     self.powerBar.append(barPart)

        hudImage.fill_rect(127, 81, 100, 8, 9)

        hudImage.print_center(str(power if power < 128 else "max") + "  ", y = 79, color = 10, font = image.font5)

        


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

#add bombs
#add hud functionality
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

    def __init__(self):
        super().__init__(spriteName = "marisaShot", maxSpeed = 250, spriteKind = 2)
        #self.sprite = sprites.create(assets.tile("marisaShot"), 2)
        self.sprite = sprites.create(assets.image("marisaShotImage2"), 2)
        #self.sprite.set_scale(1, ScaleAnchor.MIDDLE)

class marisaLaser(Projectile):
    def __init__(self):
        super().__init__(spriteName = "marisaLaser", maxSpeed = 250, spriteKind = 2)
        #self.sprite = sprites.create(assets.tile("marisaShot"), 2)
        self.sprite = sprites.create(assets.image("marisaLaser"), 2)
        #self.sprite.set_scale(1, ScaleAnchor.MIDDLE)

class redCircleProjectile(Projectile):
    def __init__(self):
            super().__init__(spriteName = "redBall", maxSpeed = 30, spriteKind = 2)
            self.sprite = sprites.create(assets.tile("redBall"), 3)
            #self.sprite.set_scale(0.8, ScaleAnchor.MIDDLE)


class Enemy:
    def __init__(self, spriteName: str, player: Player, health = 5):
        if spriteName == "test":
            self.sprite = sprites.create(assets.tile("marisa"), 4)
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

    def takeDamage(self):
        self.health -= 1
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
        self.sprite = sprites.create(assets.tile("""hitbox"""), SpriteKind.player)
        self.sprite.set_stay_in_screen(True)
        self.sprite.set_kind(0)
        self.level = 0
        self.projectiles = []
        self.slowDownVariable = 0
        self.skin = sprites.create(assets.tile("""marisa"""))
        self.skin.set_position(self.sprite.x , self.sprite.y - 1)
        self.health = 3
        self.lastHit = -3000 #so you're not invincible at the start of the game
        #self.spawnLasers()
        self.Lasers = False
        
    
    
    def takeDamage(self):
        self.health -= 1
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

        if controller.B.is_pressed():
            xVel = int(xVel / 2)
            yVel = int(yVel / 2)
            self.sprite.z = 10
        
        else:
            self.sprite.z = 0

        if controller.A.is_pressed():
            self.bomb()

        self.sprite.set_velocity(xVel, yVel)
        self.skin.set_position(self.sprite.x, self.sprite.y)
        if self.Lasers:
            self.l1.set_position(self.sprite.x - 12, self.sprite.y)
            self.l2.set_position(self.sprite.x + 12, self.sprite.y)

    def spawnLasers(self):

        self.Lasers = True
        self.l1 = sprites.create(assets.image("""miniHakkero"""))
        self.l2 = sprites.create(assets.image("""miniHakkero"""))
        self.l1.set_position(self.sprite.x - 12, self.sprite.y)
        self.l2.set_position(self.sprite.x + 12, self.sprite.y)

    def killLasers(self):
        self.Lasers = False
        sprites.destroy(self.l1)
        sprites.destroy(self.l2)

    def shootLasers(self):
        self.projectiles.append(marisaLaser())
        self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x - 12, self.sprite.y)
        self.projectiles[len(self.projectiles)-1].setAngle(180)
        self.projectiles.append(marisaLaser())
        self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x + 12, self.sprite.y)
        self.projectiles[len(self.projectiles)-1].setAngle(180)

    def shoot(self):
        if self.slowDownVariable == 2:

            if self.level == 0:
                self.projectiles.append(playerProjectile())
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.slowDownVariable = 0

            if self.level == 1:
                self.projectiles.append(playerProjectile())
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.shootLasers()
                self.slowDownVariable = 0

            if self.level == 2:
                self.projectiles.append(playerProjectile())
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(185)
                self.projectiles.append(playerProjectile())
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(180)
                self.projectiles.append(playerProjectile())
                self.projectiles[len(self.projectiles)-1].sprite.set_position(self.sprite.x, self.sprite.y-8)
                self.projectiles[len(self.projectiles)-1].setAngle(175)
                self.slowDownVariable = 0
        else:
            self.slowDownVariable += 1

    def bomb(self):
        print("bomb")
        pass

i = 0

class Game:
    def __init__(self):
        self.hud = HUD()
        self.player = Player()
        self.projectiles: List[Projectile] = []
        self.enemies: List[Enemy] = []
        self.frameTimeList = []
        info.show_score(True)
        self.gameOverActive = False
        self.continues = 3
        self.lives = 3
        self.nextWave = 0

    def gameOver(self):

        if not self.gameOverActive:
            self.yes = False
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
                

    def collisionHandler(self):
        #print("collided!")
        pass

    def collisionCheck(self):
        #spritekinds:
        #0 = player
        #1 = test projectile
        #2 = player projectile
        #3 = enemy projectile
        #4 = enemy
        #999 = hud

        def testOverlap():
            self.collisionHandler()

        sprites.on_overlap(0, 1, testOverlap)

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
                hitEnemy.takeDamage()

            if hitProjectile != None:
                sprites.destroy(hitProjectile.sprite)
                gameObj.player.projectiles.remove_at(pos)
        
        sprites.on_overlap(4, 2, enemyDamaged)

        def playerDamaged(playerSprite: Sprite, projSprite: Sprite):
            hitProjectile: Projectile = None

            if game.runtime() - self.player.lastHit >= 3000: #invulnerability handling
                for enemy in gameObj.enemies:     
                    for i in range(len(enemy.projectiles)):
                        if enemy.projectiles[i].sprite == projSprite:
                            hitProjectile = enemy.projectiles[i]
                            if hitProjectile != None:
                                sprites.destroy(hitProjectile.sprite)
                                enemy.projectiles.remove_at(i)
                            break

                gameObj.player.takeDamage()

        sprites.on_overlap(0, 3, playerDamaged)

    def frametimes(self, t1, t2):
        self.frameTimeList.append((t2 - t1))
        self.prevRunTime = game.runtime()
        if len(self.frameTimeList) == 60:
            average = 0
            for i in self.frameTimeList:
                average += i
            average = average / 60
            #print("average frametime last 100 frames:" + str(average))
            self.player.skin.say_text(str(int(average)))
            
            self.frameTimeList = []


    
    def projectileTest(self):
        global i

        if i % 5 == 0:
            self.projectiles.append(Projectile(spriteName = "projectile"))
            #self.projectiles.homeTo(self.player.sprite.x, self.player.sprite.y)
            for g in range(len(self.projectiles)):
                curO: Projectile = self.projectiles[g]
                self.projectiles[len(self.projectiles)-1].setAngle(i)
                if i >= 360: i = 0

        i = i+1

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
            for i in range(len(self.player.projectiles)):
                cur1: Projectile = self.player.projectiles[i]
                if cur1.sprite.x < 0 - 15 or cur1.sprite.x > width - 15 or cur1.sprite.y < 0 - 15 or cur1.sprite.y > height + 15:
                    sprites.destroy(cur1.sprite)
                    self.player.projectiles.remove_at(i)
                   
        #enemy projectiles
        if len(self.enemies) > 0:
            for g in self.enemies:
                for i in range(len(g.projectiles)):
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
        game.stats = True
        self.hud.buildHud()
        def onUpdate():
            #print("frametime: " + str(game.runtime() - self.prevRunTime))
            startOfUpdate = control.micros()
            if not self.gameOverActive:
                self.projectileTest()
                self.player.movementController()
                self.projectileDestructor()
                self.player.shoot()
                if self.player.sprite.x > 115: self.player.sprite.set_position(115, self.player.sprite.y), self.player.skin.set_position(115, self.player.sprite.y)
                self.enemyActions()
                self.waves()
            if self.player.health <= 0: self.gameOver()
            self.frametimes(startOfUpdate, control.micros())



        game.on_update(onUpdate)




gameObj = Game()
gameObj.mainLoop()
