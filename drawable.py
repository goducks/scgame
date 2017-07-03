import sdl2
import sdl2.ext
import localmath as lm
import spritedrawer
from random import randint
from abc import ABCMeta, abstractmethod

class GameObject():
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, time):
        pass

class Drawable(GameObject):
    # the "static" draw list
    drawList = list()

    def __init__(self, renderer, width, height, type = ""):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.create_texture_sprite(renderer, size=(width, height))
        self.type = type
        self.renderer = renderer
        self.sprite = sprite
        self.sprite.height = height
        self.sprite.width = width
        # set a random color
        self.sprite.color = sdl2.ext.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        # add to global drawList
        Drawable.drawList.append(self)

    # on class instance destroy, remove from drawList
    def delete(self):
        # print "removing from drawlist"
        Drawable.drawList.remove(self)

    def update(self, time):
        pass

    def render(self, renderer):
        # if self.type == "player":
            # spritedrawer.drawPlayer(renderer)
        # else:
            renderer.color = self.sprite.color
            # for now, we're only drawing filled rectangles. we can specialize this function as necessary
            # draw_rect will draw outline only, fill fills them in
            # renderer.draw_rect([(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)])
            renderer.fill([(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)])

class Player(Drawable):

    def __init__(self, renderer, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerwidth, playerheight = lm.SC(width, height)
        playerposx, playerposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        playerposx -= playerheight + playerheight / 2
        playerposy -= playerheight + 10
        super(Player, self).__init__(renderer, int(playerwidth), int(playerheight), "player")
        self.sprite.position = int(playerposx), int(playerposy)
        Player.score = 0
        Player.vx = 0
        Player.width = playerwidth
        Player.height = playerheight
        Player.maxwidth = wwidth
        Player.maxheight = wheight
        Player.bullets = list()
        Player.lives = 3

    def delete(self):
        super(Player, self).delete()

    def fire(self):
        for bullet in self.bullets:
            if bullet.sprite.y < -16:
                self.bullets.remove(bullet)
        if len(self.bullets) < 2:
            self.bullets.append(Bullet(self.renderer, int(self.sprite.x + self.width / 2),
                                       self.sprite.y, self.maxwidth, self.maxheight))

    def getInput(self, event):
        if sdl2.SDL_HasScreenKeyboardSupport:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    Player.vx = -.75
                if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    Player.vx = .75
                if event.key.keysym.sym == sdl2.SDLK_SPACE:
                    Player.fire(self)
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    Player.vx = 0

    def lostlife(self):
        Player.lives -= 1

    def update(self, time):
        # width and height of sprite so it can stay in bounds
        swidth, sheight = self.sprite.size
        # move sprite
        self.sprite.x += lm.NDCToSC_x(self.vx * time, self.maxwidth)
        # checks if sprite is past the min (0)
        self.sprite.x = max(0, self.sprite.x)
        # position + sprite size
        posx = self.sprite.x + swidth
        # if the position + sprite size extends past max, stop it there
        if posx > self.maxwidth:
            self.sprite.x = self.maxwidth - swidth

class Bullet(Drawable):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(Bullet, self).__init__(renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        Bullet.maxheight = wheight
        Bullet.vy = -.5

    def delete(self):
        super(Bullet, self).delete()

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        # print "removing bullet"
        self.delete()

class Enemy(Drawable):
    def __init__(self, renderer, points, speed, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        enemywidth, enemyheight = lm.NDCToSC(width, height, wwidth, wheight)
        enemyposx, enemyposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        super(Enemy, self).__init__(renderer, int(enemywidth), int(enemyheight))
        self.sprite.position = int(enemyposx), int(enemyposy)
        self.points = points
        Enemy.width = enemywidth
        Enemy.height = enemyheight
        Enemy.maxwidth = wwidth - lm.NDCToSC_x(.05, wwidth)
        Enemy.minwidth = lm.NDCToSC_x(.05, wwidth)
        Enemy.maxheight = wheight
        Enemy.vx = speed
        Enemy.vy = 0
        Enemy.move = True

    def delete(self):
        super(Enemy, self).delete()

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(Enemy.vy * time, self.maxheight)
        if self.move:
            self.sprite.x += lm.NDCToSC_x(Enemy.vx * time, self.maxwidth)

    def shoot(self):
        for bullet in EnemyController.bullets:
            if bullet.sprite.y > self.maxheight:
                EnemyController.bullets.remove(bullet)
        if len(EnemyController.bullets) < 1:
            EnemyController.bullets.append(EnemyBullet(self.renderer, int(self.sprite.x + self.width / 2),
                                            self.sprite.y, self.maxwidth, self.maxheight))

    def remove(self):
        # print "removing enemy"
        self.delete()

class EnemyController(GameObject):
    def __init__(self, renderer, wwidth, wheight):
        EnemyController.level = 1
        EnemyController.enemies = self.createEnemies(renderer, wwidth, wheight)
        EnemyController.top = self.enemies[0].sprite.y
        EnemyController.left = self.enemies[0].sprite.x
        EnemyController.right = self.enemies[-1].sprite.x + self.enemies[-1].sprite.width
        EnemyController.bottom = self.enemies[-1].sprite.y + self.enemies[-1].sprite.height
        EnemyController.renderer = renderer
        EnemyController.wwidth = wwidth
        EnemyController.wheight = wheight
        EnemyController.counter = 0
        EnemyController.timer = 0
        EnemyController.bullets = list()
        EnemyController.shoottime = randint(90, 100)
        EnemyController.UFOactive = False
        EnemyController.UFOtime = randint(400, 500)
        EnemyController.UFOcounter = 0

    def createEnemies(self, renderer, wwidth, wheight):
        enemies = list()
        yoffset = .05
        xoffset = .1
        scorecountdown = 15
        points = 40
        speed = .25 * self.level
        y = .125
        while y < .4:
            x = xoffset
            while x < .85:
                if scorecountdown == 0 and not points == 10:
                    points -= 10
                    scorecountdown = 15
                enemy = Enemy(renderer, points, speed, wwidth, wheight, x, y, 0.075, 0.03)
                enemies.append(enemy)
                scorecountdown -= 1
                x += xoffset
            y += yoffset
        return enemies

    def update(self, time):
        Enemy.vy = 0
        if Enemy.move:
            distancemoved = lm.NDCToSC_x(Enemy.vx * time, self.wwidth)
        else:
            distancemoved = 0
        EnemyController.left += distancemoved
        EnemyController.right += distancemoved
        if EnemyController.right > Enemy.maxwidth or EnemyController.left < Enemy.minwidth:
            Enemy.vx = -Enemy.vx
            Enemy.vy = .5
            EnemyController.counter = 15
        if EnemyController.timer == self.shoottime:
            shooter = randint(0, len(self.enemies) - 1)
            if type(self.enemies[shooter]) == Enemy:
                self.enemies[shooter].shoot()
            else:
                shooter = randint(0, len(self.enemies) - 1)
                self.enemies[shooter].shoot()
            EnemyController.timer = 0
        if EnemyController.UFOcounter >= self.UFOtime and not EnemyController.UFOactive:
            ufo = UFO(self.renderer, self.wwidth, self.wheight)
            EnemyController.UFOactive = True
            EnemyController.UFOcounter = 0
            EnemyController.enemies.append(ufo)
        if EnemyController.counter == 15:
            Enemy.move = True
            EnemyController.counter = 0
        else:
            Enemy.move = False
            EnemyController.counter += 1
        EnemyController.timer += 1
        EnemyController.UFOcounter += 1

    def checkWin(self, player):
        enemyheight = self.enemies[-1].sprite.y + self.enemies[0].height
        if enemyheight >= player.sprite.y:
            return True
        else:
            return False

    def removebullet(self, bullet):
        EnemyController.bullets.remove(bullet)
        bullet.remove()

    def reset(self):
        EnemyController.level += .8
        del self.enemies[:]
        EnemyController.enemies = self.createEnemies(self.renderer, self.wwidth, self.wheight)
        EnemyController.top = self.enemies[0].sprite.y
        EnemyController.left = self.enemies[0].sprite.x
        EnemyController.right = self.enemies[-1].sprite.x + self.enemies[-1].sprite.width
        EnemyController.bottom = self.enemies[-1].sprite.y + self.enemies[-1].sprite.height

class UFO(Drawable):
    def __init__(self, renderer, wwidth, wheight):
        enemywidth, enemyheight = lm.NDCToSC(.075, .03, wwidth, wheight)
        super(UFO, self).__init__(renderer, int(enemywidth), int(enemyheight))
        self.sprite.y = lm.NDCToSC_y(.075, wheight)
        UFO.width = self.sprite.width
        pickside = randint(0, 1)
        if pickside == 0:
            UFO.vx = -0.25
            self.sprite.x = lm.NDCToSC_x(1, wwidth)
        if pickside == 1:
            UFO.vx = 0.25
            self.sprite.x = -self.width
        UFO.points = 100

    def remove(self):
        super(UFO, self).delete()

    def update(self, time):
        self.sprite.x += lm.NDCToSC_x(UFO.vx * time, Enemy.maxwidth)
        if UFO.vx < 0 and self.sprite.x < -UFO.width:
            self.delete()
            EnemyController.enemies.remove(self)
            EnemyController.UFOactive = False
        elif UFO.vx > 0 and self.sprite.x > Enemy.maxwidth:
            self.delete()
            EnemyController.enemies.remove(self)
            EnemyController.UFOactive = False

class EnemyBullet(Drawable):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(EnemyBullet, self).__init__(renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        EnemyBullet.height = bulletheight
        EnemyBullet.maxheight = wheight
        EnemyBullet.vy = .5

    def delete(self):
        super(EnemyBullet, self).delete()

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        # print "removing enemybullet"
        self.delete()

class Shield(Drawable):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        shieldwidth, shieldheight = lm.NDCToSC(.135, .08, wwidth, wheight)
        shieldposx, shieldposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        super(Shield, self).__init__(renderer, int(shieldwidth), int(shieldheight))
        self.sprite.position = int(shieldposx), int(shieldposy)
        Shield.health = 5
        print self.sprite.color

    def hit(self):
        self.health -= 1
        self.sprite.color._r += 40

    def remove(self):
        self.delete()