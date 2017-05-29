import sdl2
import sdl2.ext
import movement as mov


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
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

