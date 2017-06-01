import sdl2
import sdl2.ext
import localmath as lm
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

    def update(self, time):
        pass


class Player(Drawable):

    def __init__(self, world, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerwidth, playerheight = lm.NDCToSC(width, height, wwidth, wheight)
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
        print len(self.bullets)
        for bullet in self.bullets:
            if bullet.sprite.y < -16:
                self.bullets.remove(bullet)
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
        bulletwidth, bulletheight = lm.NDCToSC(.015, .020, wwidth, wheight)
        super(Bullet, self).__init__(world, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        Bullet.maxheight = wheight
        Bullet.vy = -.5

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)
