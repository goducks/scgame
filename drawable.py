import sdl2
import sdl2.ext
import movement as mov

class Drawable(sdl2.ext.Entity):
    def __init__(self, world, width, height):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.from_color(sdl2.ext.Color(255, 255, 255), size=(width, height))
        self.sprite = sprite


class Player(Drawable):
    def __init__(self, world, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerheight = wheight * height;
        playerwidth = wwidth * width;
        playerposx = (posx * wwidth) - (playerheight + playerheight/2)
        playerposy = ((posy * wheight) - playerheight - 10)
        self.sprite = Drawable(world, int(playerwidth), int(playerheight)).sprite
        self.sprite.position = int(playerposx), int(playerposy)
        self.velocity = mov.Velocity()
    def moveLeft(self):
        self.velocity.vx = -4;
    def moveRight(self):
        self.velocity.vx = 4;
    def getInput(self, event):
        if sdl2.SDL_HasScreenKeyboardSupport:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.moveLeft();
                if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.moveRight();
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    self.velocity.vx = 0