import sdl2.ext
import drawable as draw
from optparse import OptionParser
import collision
import timeit as ti
import time
import ui

keeprunning = True
window = None
world = None

# -------------------------------------------------------------------------------
class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

class TextureRenderer(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, renderer):
        super(TextureRenderer, self).__init__(renderer)
        self.renderer = renderer

def clear(world, enemies):
    print "clearing"
    for enemy in enemies:
        enemy.remove()
    del enemies[:]
    render(world)
    # renderer = sdl2.SDL_CreateRenderer(window.window, -1, 0)
    # sdl2.SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255)
    # sdl2.SDL_RenderFillRect(renderer, None)
    # sdl2.SDL_RenderPresent(renderer)

def gameover():
    sdl2.SDL_Delay(1000)
    # time.sleep(2)
    sdl2.ext.quit()
    quit()


# -------------------------------------------------------------------------------
def update(player, bullets, enemyblock, enemies, time):
    global keeprunning
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
#    if not keeprunning:
#        clear()
#        gameover()
    if keeprunning:
        player.update(time)
        enemyblock.update(time, enemies)
        for enemy in enemies:
            enemy.update(time)
        for ebullet in enemyblock.bullets:
            ebullet.update(time)
            hit = collision.checkCollision(ebullet, player)
            if hit:
                ebullet.delete()
                enemyblock.bullets.remove(ebullet)
                player.lostlife()
                if player.lives <= 0:
                    keeprunning = False
                break
        for bullet in bullets:
            bullet.update(time)
            for enemy in enemies:
                hit = collision.checkCollision(bullet, enemy)
                if hit:
                    enemy.remove()
                    enemies.remove(enemy)
                    bullet.remove()
                    bullets.remove(bullet)
                    break

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
    global window
    window = sdl2.ext.Window("Space Invaders", size=(width, height))
    window.show()

    # create world
    world = sdl2.ext.World()

    # create a sprite renderer
    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)

    renderer = sdl2.SDL_CreateRenderer(window.window, -1, 0)
    ui.textMaker(renderer, "kill me")

    ###########################################################################

    ###########################################################################
    # Our game object setup
    ###########################################################################
    # create player object
    player1 = draw.Player(world, width, height, 0.5, 1.0, 66, 28.8)
    bullets = player1.bullets

    # create enemies
    enemies = list()
    yoffset = .05
    xoffset = .1
    y = yoffset
    while y < .4:
        x = xoffset
        while x < .85:
            enemy = draw.Enemy(world, width, height, x, y, 0.075, 0.03)
            enemies.append(enemy)
            x += xoffset
        y += yoffset

    # creates rectangle with enemies
    # uses first block in list and last block in list (top left and bottom right)
    left = enemies[0].sprite.x
    top = enemies[0].sprite.y
    bottom = enemies[-1].sprite.y + enemies[-1].sprite.height
    right = enemies[-1].sprite.x + enemies[-1].sprite.width
    enemyblock = draw.EnemyBlock(world, right, bottom, left, top)

    ###########################################################################

    running = True
    minFrameSecs = 1.0 / frameRateLimit
    lastDelta = 0.0
    while running:
        start = ti.default_timer()

        #######################################################################
        # add all per-frame work here
        if not keeprunning:
            clear(world, width, height, enemies)
            gameover()
        else:
            running = update(player1, bullets, enemyblock, enemies, lastDelta)
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
