import sdl2
import sdl2.ext
import localmath as lm
import time as t
from abc import ABCMeta, abstractmethod


class GameObject(sdl2.ext.Entity):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, time):
        pass


class Drawable(GameObject):
    def __init__(self, world, width, height):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.from_color(sdl2.ext.Color(255, 255, 255), size=(width, height))
        self.sprite = sprite
        self.sprite.height = height
        self.sprite.width = width

    def update(self, time):
        pass


class Player(Drawable):

    def __init__(self, world, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerwidth, playerheight = lm.SC(width, height)
        playerposx, playerposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        playerposx -= playerheight + playerheight / 2
        playerposy -= playerheight + 10
        super(Player, self).__init__(world, int(playerwidth), int(playerheight))
        self.sprite.position = int(playerposx), int(playerposy)
        # set velocity to 0
        Player.vx = 0
        # save things for use in later functions
        Player.width = playerwidth
        Player.height = playerheight
        Player.maxwidth = wwidth
        Player.maxheight = wheight
        Player.bullets = list()

    def fire(self):
        for bullet in self.bullets:
            if bullet.sprite.y < -16:
                self.bullets.remove(bullet)
                bullet.delete()
        if len(self.bullets) < 5:
            self.bullets.append(Bullet(self.world, int(self.sprite.x + self.width / 2),
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
    def __init__(self, world, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.005, .025, wwidth, wheight)
        super(Bullet, self).__init__(world, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        Bullet.maxheight = wheight
        Bullet.vy = -.5

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def hit(self):
        self.delete()

class Enemy(Drawable):
    def __init__(self, world, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        enemywidth, enemyheight = lm.NDCToSC(width, height, wwidth, wheight)
        enemyposx, enemyposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        super(Enemy, self).__init__(world, int(enemywidth), int(enemyheight))
        self.sprite.position = int(enemyposx), int(enemyposy)
        Enemy.maxwidth = wwidth - lm.NDCToSC_x(.1, wwidth)
        Enemy.minwidth = lm.NDCToSC_x(.1, wwidth)
        Enemy.maxheight = wheight
        Enemy.vx = .25
        Enemy.vy = 0

    def update(self, time):
        Enemy.vy = 0
        if self.sprite.x > self.maxwidth or self.sprite.x < self.minwidth:
            Enemy.vx = -Enemy.vx
            Enemy.vy = .25
        self.sprite.y += lm.NDCToSC_y(Enemy.vy * time, self.maxheight)
        self.sprite.x += lm.NDCToSC_x(Enemy.vx * time, self.maxwidth)


    def hit(self):
        self.delete()
