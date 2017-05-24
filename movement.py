import sdl2
import sdl2.ext

# velocity class to be used for movement
class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, world, componentsets):
        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            # position + sprite size
            posx = sprite.x + swidth
            posy = sprite.y + sheight

            # if the position + sprite size extends past max, stop it there
            if posx > self.maxx:
                sprite.x = self.maxx - swidth
            if posy > self.maxy:
                sprite.y = self.maxy - sheight