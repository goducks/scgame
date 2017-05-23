# small test change
# sarah's test
import sdl2.ext
import ctimer as ct

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy

def runLoop():
    loopTimer = ct.CTimer()

    # our main game loop 

    # read remote inputs 
    # ...

    # read local inputs & events
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            return False
        # else:
            # print "sdl event type: %s" % event.type
   
    # update game state
    # ...

    # send local state to remotes

    # render or whatever

    return True

def main():
    print "--begin game--"

    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # create window based on image size(tuple)
    window = sdl2.ext.Window("Space Invaders", size=(500, 800))
    window.show()

    # create a sprite renderer
    spriterenderer = SoftwareRenderer(window)

    # create world
    world = sdl2.ext.World()
    world.add_system(spriterenderer)

    # load a sprite directly from image, note: can also manually
    # create one, but this factory will do heavy lifting for now
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    # debug check of supported image formats
    # print formats
    sprite = factory.from_color(sdl2.ext.Color(255, 255, 255), size=(50, 50))
    player1 = Player(world, sprite, 0, 0)


    running = True
    while running:
        running = runLoop()

    # cleanup
    sdl2.ext.quit()

    print "--end game--"

if __name__ == "__main__":
    main()
