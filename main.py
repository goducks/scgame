import sdl2.ext
import drawable as draw
from optparse import OptionParser
import timeit as ti
import time

#-------------------------------------------------------------------------------
class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)
# -------------------------------------------------------------------------------
def update(player, bullets, time):
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
    player.update(time)
    for bullet in bullets:
        bullet.update(time)


    # update game state
    # ...

    # send local state to remotes

    return True
# -------------------------------------------------------------------------------
def render(world):
    world.process()

# -------------------------------------------------------------------------------
def main():
    print "--begin game--"

    ###########################################################################
    # set up command line arguments using optparse library
    ###########################################################################
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage, version="%prog 0.1")
    parser.add_option("-x", "--width", type="int", dest="width", default=600,
                      help="set window width [600]")
    parser.add_option("-y", "--height", type="int", dest="height", default=800,
                      help="set window height [800]")
    parser.add_option("-l", "--limitframe", type="float", dest="limitFrameRate",
                      help="limit framerate to specified value [NO DEFAULT]")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="enable debug print output")
    (options, args) = parser.parse_args()

    # extract window size variables
    width = options.width
    height = options.height
    print "--window size(%d, %d)--" % (width, height)

    # extract limited framerate settings
    limitFrame = False
    frameRateLimit = 1.0
    if (options.limitFrameRate):
        limitFrame = True
        frameRateLimit = options.limitFrameRate
        print "--frame rate limit(%d)--" % (frameRateLimit)
    ###########################################################################

    ###########################################################################
    # SDL setup
    ###########################################################################
    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # create window
    window = sdl2.ext.Window("Space Invaders", size=(width, height))
    window.show()

    # create world
    world = sdl2.ext.World()

    # create a sprite renderer
    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)

    ###########################################################################

    ###########################################################################
    # Our game object setup
    ###########################################################################
    # create player object
    player1 = draw.Player(world, width, height, 0.5, 1.0, .11, .036)
    bullets = player1.bullets
    ###########################################################################

    running = True
    minFrameSecs = 1.0 / frameRateLimit
    lastDelta = 0.0
    while running:
        start = ti.default_timer()

        #######################################################################
        # add all per-frame work here
        running = update(player1, bullets, lastDelta)
        render(world)
        #######################################################################

        stop = ti.default_timer()
        lastDelta = stop - start
        # Sleep if frame rate is higher than desired
        if (limitFrame and (lastDelta < minFrameSecs)):
            time.sleep(minFrameSecs - lastDelta)
            stop = ti.default_timer()
            lastDelta = stop - start
        if (options.debug):
            print "Update: ", lastDelta

    # cleanup
    sdl2.ext.quit()

    print "--end game--"
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------
