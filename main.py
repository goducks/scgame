import sdl2.ext
import time
import drawable as draw
import movement as mov
import sys

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

def update(player, time):
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

def render(world):
    world.process()

def main():
    print "--begin game--"

    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # temp variables until command line works
    width = int(sys.argv[1])
    height = int(sys.argv[2])

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

    # create player object
    player1 = draw.Player(world, width, height, 0.5, 1.0, .11, .036)


    running = True
    startTime = 0.0
    delta = 0.0
    while running:
        startTime = time.clock()
        running = update(player1, delta)
        render(world)
        delta = time.clock() - startTime

    # cleanup
    sdl2.ext.quit()

    print "--end game--"

if __name__ == "__main__":
    print(sys.argv)
    main()
