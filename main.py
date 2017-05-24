import sdl2.ext
import ctimer as ct
import player as pl
import movement as mov

width = 600
height = 800
playerwidth = width/9
playerheight = height/28
white = sdl2.ext.Color(255, 255, 255)

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

def runLoop(player):
    loopTimer = ct.CTimer()

    # our main game loop 

    # read remote inputs 
    # ...

    # read local inputs & events
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            return False
            break
        player.getInput(event)
   
    # update game state
    # ...

    # send local state to remotes

    # render or whatever

    return True

def main():
    print "--begin game--"

    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # create window
    window = sdl2.ext.Window("Space Invaders", size=(width, height))
    window.show()

    # create a sprite renderer
    spriterenderer = SoftwareRenderer(window)

    # create a movement system
    movementsystem = mov.MovementSystem(0, 0, width, height)

    # create world
    world = sdl2.ext.World()
    world.add_system(spriterenderer)
    world.add_system(movementsystem)

    # load a sprite directly from image, note: can also manually
    # create one, but this factory will do heavy lifting for now
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    # create player sprite and player object
    sprite = factory.from_color(white, size=(playerwidth, playerheight))
    player1 = pl.Player(world, sprite, (width/2) - (playerheight + playerheight/2), (height - playerheight - 10))


    running = True
    while running:
        running = runLoop(player1)
        sdl2.SDL_Delay(10)
        world.process()

    # cleanup
    sdl2.ext.quit()

    print "--end game--"

if __name__ == "__main__":
    main()
