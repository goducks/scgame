import sdl2
import sdl2.ext
import localmath as lm
import random
import os
from abc import ABCMeta, abstractmethod


class GameObject(sdl2.ext.Entity):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, time):
        pass


class Drawable(GameObject):
    def __init__(self, world, renderer, width, height):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        # sprite = factory.from_color(sdl2.ext.Color(255, 255, 255), size=(width, height))
        # rect = sdl2.SDL_Rect(0, 0, width, height)
        # sdl2.SDL_RenderDrawRect(renderer.sdlrenderer, rect)
        sdl2.SDL_SetRenderDrawColor(renderer.renderer, 255, 255, 255, 255)
        sprite = factory.create_texture_sprite(renderer, size=(width, height))
        self.sprite = sprite
        self.sprite.height = height
        self.sprite.width = width

    def update(self, time):
        pass


class Player(Drawable):

    def __init__(self, world, renderer, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerwidth, playerheight = lm.SC(width, height)
        playerposx, playerposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        playerposx -= playerheight + playerheight / 2
        playerposy -= playerheight + 10
        super(Player, self).__init__(world, renderer, int(playerwidth), int(playerheight))
        self.sprite.position = int(playerposx), int(playerposy)
        Player.vx = 0
        Player.renderer = renderer
        Player.width = playerwidth
        Player.height = playerheight
        Player.maxwidth = wwidth
        Player.maxheight = wheight
        Player.bullets = list()
        Player.lives = 3

    def fire(self):
        for bullet in self.bullets:
            if bullet.sprite.y < -16:
                self.bullets.remove(bullet)
                bullet.delete()
        if len(self.bullets) < 2:
            self.bullets.append(Bullet(self.world, self.renderer, int(self.sprite.x + self.width / 2),
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
    def __init__(self, world, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(Bullet, self).__init__(world, renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        Bullet.maxheight = wheight
        Bullet.vy = -.5

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        self.delete()

class Enemy(Drawable):
    def __init__(self, world, renderer, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        enemywidth, enemyheight = lm.NDCToSC(width, height, wwidth, wheight)
        enemyposx, enemyposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        super(Enemy, self).__init__(world, renderer, int(enemywidth), int(enemyheight))
        self.sprite.position = int(enemyposx), int(enemyposy)
        Enemy.renderer = renderer
        Enemy.width = enemywidth
        Enemy.height = enemyheight
        Enemy.maxwidth = wwidth - lm.NDCToSC_x(.05, wwidth)
        Enemy.minwidth = lm.NDCToSC_x(.05, wwidth)
        Enemy.maxheight = wheight
        Enemy.vx = .25
        Enemy.vy = 0
        Enemy.move = True

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(Enemy.vy * time, self.maxheight)
        if self.move:
            self.sprite.x += lm.NDCToSC_x(Enemy.vx * time, self.maxwidth)

    def shoot(self):
        for bullet in EnemyBlock.bullets:
            if bullet.sprite.y > self.maxheight:
                EnemyBlock.bullets.remove(bullet)
                bullet.delete()
        if len(EnemyBlock.bullets) < 1:
            EnemyBlock.bullets.append(EnemyBullet(self.world, self.renderer, int(self.sprite.x + self.width / 2),
                                            self.sprite.y, self.maxwidth, self.maxheight))

    def remove(self):
        self.delete()

class EnemyBlock(Drawable):
    def __init__(self, world, width, height, posx, posy):
        EnemyBlock.top = posy
        EnemyBlock.left = posx
        EnemyBlock.right = width
        EnemyBlock.bottom = height
        EnemyBlock.counter = 0
        EnemyBlock.timer = 0
        EnemyBlock.bullets = list()
        EnemyBlock.shoottime = random.randint(30, 40)

    def update(self, time, enemies):
        Enemy.vy = 0
        temp = self.left
        EnemyBlock.left = enemies[0].sprite.x
        distancemoved = self.left - temp
        EnemyBlock.right += distancemoved
        if EnemyBlock.right > Enemy.maxwidth or EnemyBlock.left < Enemy.minwidth:
            Enemy.vx = -Enemy.vx
            Enemy.vy = .5
            EnemyBlock.counter = 15
        if EnemyBlock.timer == self.shoottime:
            shooter = random.randint(0, len(enemies) - 1)
            enemies[shooter].shoot()
            EnemyBlock.timer = 0
        if EnemyBlock.counter == 15:
            Enemy.move = True
            EnemyBlock.counter = 0
        else:
            Enemy.move = False
            EnemyBlock.counter += 1
        EnemyBlock.timer += 1


class EnemyBullet(Drawable):
    def __init__(self, world, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(EnemyBullet, self).__init__(world, renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        EnemyBullet.height = bulletheight
        EnemyBullet.maxheight = wheight
        EnemyBullet.vy = .5

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        self.delete()