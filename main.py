import sdl2.ext
import drawable as draw
from optparse import OptionParser
import collision
import timeit as ti
import time
import ui

keeprunning = True
width = 0
height = 0
renderer = None


def clear(renderer):
    print "clearing"
    renderer.color = sdl2.ext.Color(0, 0, 0, 255)
    renderer.clear()
    renderer.present()


def gameover(renderer):
    del draw.Drawable.drawList[:]
    gameover = ui.textMaker(renderer, "GAME OVER", width / 5, (height / 2) - 50, 40)
    count = 0
    while count < 1000:
        render(renderer)
        count += 1
    # time.sleep(2)
    sdl2.ext.quit()
    quit()


def reset(player, bullets, enemyblock, enemies):
    savelives = player.lives
    savescore = player.score
    player1 = draw.Player(renderer, width, height, 0.5, 1.0, 66, 28.8)
    player1.score = savescore
    player1.lives = savelives
    del bullets[:]
    bullets = player1.bullets

    del enemies[:]
    yoffset = .05
    xoffset = .1
    scorecountdown = 15
    points = 40
    y = yoffset
    while y < .4:
        x = xoffset
        while x < .85:
            if scorecountdown == 0 and not points == 10:
                points -= 10
                scorecountdown = 15
            enemy = draw.Enemy(renderer, points, width, height, x, y, 0.075, 0.03)
            enemies.append(enemy)
            scorecountdown -= 1
            x += xoffset
        y += yoffset

    # creates rectangle with enemies
    # uses first block in list and last block in list (top left and bottom right)
    left = enemies[0].sprite.x
    top = enemies[0].sprite.y
    bottom = enemies[-1].sprite.y + enemies[-1].sprite.height
    right = enemies[-1].sprite.x + enemies[-1].sprite.width
    enemyblock = draw.EnemyBlock(right, bottom, left, top)
    return player1, bullets, enemyblock, enemies


# -------------------------------------------------------------------------------
def update(player, lives, score, bullets, enemyblock, enemies, shields, time):
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
    if keeprunning:
        player.update(time)
        enemyblock.update(time, enemies)
        for enemy in enemies:
            enemy.update(time)
        for ebullet in enemyblock.bullets:
            ebullet.update(time)
            for shield in shields:
                hit = collision.checkCollision(ebullet, shield)
                if hit:
                    ebullet.remove()
                    enemyblock.bullets.remove(ebullet)
                    shield.hit()
                    if shield.health <= 0:
                        shield.remove()
                        shields.remove(shield)
                    break
            hit = collision.checkCollision(ebullet, player)
            if hit:
                # print "enemy hit"
                enemyblock.removebullet(ebullet)
                player.lostlife()
                lives.updateLives(player.lives)
                if player.lives <= 0:
                    keeprunning = False
                break
        for bullet in bullets:
            bullet.update(time)
            for shield in shields:
                hit = collision.checkCollision(bullet, shield)
                if hit:
                    bullet.remove()
                    bullets.remove(bullet)
                    shield.hit()
                    if shield.health <= 0:
                        shield.remove()
                        shields.remove(shield)
                    break
            for enemy in enemies:
                hit = collision.checkCollision(bullet, enemy)
                if hit:
                    player.score += enemy.points
                    score.updateScore(player.score)
                    enemy.remove()
                    enemies.remove(enemy)
                    bullet.remove()
                    bullets.remove(bullet)
                    break
        if len(enemies) == 0:
            sdl2.SDL_Delay(1000)
            # reset here

    # update game state
    # ...

    # send local state to remotes

    return True


# -------------------------------------------------------------------------------
def render(renderer):
    # clear to black
    renderer.color = sdl2.ext.Color(0, 0, 0, 255)
    renderer.clear()

    # iterate the global draw list
    for di in draw.Drawable.drawList:
        di.render(renderer)

    # test.renderTexture(image, renderer, 0, 0)
    # present renderer results
    renderer.present()


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
    global width
    global height
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

    # create a sprite renderer starting with a base sdl2ext renderer
    global renderer
    renderer = sdl2.ext.Renderer(window)

    ###########################################################################

    ###########################################################################
    # Our game object setup
    ###########################################################################
    # create player object
    player1 = draw.Player(renderer, width, height, 0.5, 1.0, 66, 28.8)
    bullets = player1.bullets

    lives = ui.renderLives(renderer, player1.lives, 5, 5)
    score = ui.renderScore(renderer, player1.score, width - (width / 3) - 10, 5)

    # create enemies
    enemies = list()
    yoffset = .05
    xoffset = .1
    scorecountdown = 15
    points = 40
    y = yoffset
    while y < .4:
        x = xoffset
        while x < .85:
            if scorecountdown == 0 and not points == 10:
                points -= 10
                scorecountdown = 15
            enemy = draw.Enemy(renderer, points, width, height, x, y, 0.075, 0.03)
            enemies.append(enemy)
            scorecountdown -= 1
            x += xoffset
        y += yoffset

    # creates rectangle with enemies
    # uses first block in list and last block in list (top left and bottom right)
    left = enemies[0].sprite.x
    top = enemies[0].sprite.y
    bottom = enemies[-1].sprite.y + enemies[-1].sprite.height
    right = enemies[-1].sprite.x + enemies[-1].sprite.width
    enemyblock = draw.EnemyBlock(right, bottom, left, top)

    # creates shields
    shields = list()
    x = .1
    while x <= .75:
        shield = draw.Shield(renderer, x, .75, width, height)
        shields.append(shield)
        x += .30

    ###########################################################################

    running = True
    minFrameSecs = 1.0 / frameRateLimit
    lastDelta = 0.0
    while running:
        start = ti.default_timer()

        #######################################################################
        # add all per-frame work here
        if not keeprunning:
            clear(renderer)
            gameover(renderer)
        else:
            running = update(player1, lives, score, bullets, enemyblock, enemies, shields, lastDelta)
            render(renderer)
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
