import sdl2.ext
import drawable as draw
import collision
import ui
from options import Options

class scgame():
    def __init__(self):
        self.gameIsActive = True
        self.width = 0
        self.height = 0
        self.renderer = None
        self.window = None
        self.players = list()
        self.playersbullets = list()
        self.enemycontrol = None
        self.shields = list()
        self.lives = None
        self.score = None
        self.fpsCounter = None
        self.limitFrame = None
        self.options = Options().opts
        self.minFrameSecs = None


    # -------------------------------------------------------------------------------
    def clear(self, renderer):
        print "clearing"
        renderer.color = sdl2.ext.Color(0, 0, 0, 255)
        renderer.clear()
        renderer.present()

    # -------------------------------------------------------------------------------
    def gameover(self, renderer, player):
        # Empty the current drawlist
        draw.Drawable.clearAll()
        # Add ONLY the gameover text
        # TODO: should also display final score!
        gameover = ui.textMaker(renderer, "GAME OVER", self.width / 5, (self.height / 2) - 50, 40,
                                fontname="8-BIT WONDER.TTF")
        text = "SCORE " + str(player.score)
        print type(text)
        score = ui.textMaker(renderer, text, self.width / 5, (self.height / 2), 30,
                             fontname="8-BIT WONDER.TTF")
        # Signal update function to end
        self.gameIsActive = False

    # -------------------------------------------------------------------------------
    def update(self, players, lives, score, bullets, enemycontrol, shields, time):
        # our main game loop

        # read remote inputs
        # ...

        # read local inputs & events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                return False
                break
            for player in players:
                player.getInput(event, players.index(player))
        if self.gameIsActive:
            for player in players:
                player.update(time)
            enemycontrol.update(time)
            for player in players:
                if enemycontrol.checkWin(player):
                    self.gameover(self.renderer, player)
            for enemy in enemycontrol.enemies:
                enemy.update(time)
            for ebullet in enemycontrol.bullets:
                ebullet.update(time)
                for shield in shields:
                    hit = collision.checkCollision(ebullet, shield)
                    if hit:
                        ebullet.remove()
                        enemycontrol.bullets.remove(ebullet)
                        shield.hit()
                        if shield.health <= 0:
                            shield.remove()
                            shields.remove(shield)
                        break
                for player in players:
                    hit = collision.checkCollision(ebullet, player)
                    if hit:
                        # print "enemy hit"
                        enemycontrol.removebullet(ebullet)
                        player.lostlife()
                        lives.updateLives(player.lives)
                        if player.lives <= 0:
                            self.gameover(renderer, player)
                        break
            for player in players:
                for bullet in player.bullets:
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
                    for enemy in enemycontrol.enemies:
                        hit = collision.checkCollision(bullet, enemy)
                        if hit:
                            player.score += enemy.points
                            score.updateScore(player.score)
                            enemy.remove()
                            enemycontrol.enemies.remove(enemy)
                            bullet.remove()
                            bullets.remove(bullet)
                            break
            if len(enemycontrol.enemies) < 1:
                enemycontrol.reset()

        # send local state to remotes

        return True

    # -------------------------------------------------------------------------------
    def render(self, renderer):
        # clear to black
        renderer.color = sdl2.ext.Color(0, 0, 0, 255)
        renderer.clear()

        # iterate the global draw list
        for di in draw.Drawable.drawList:
            print type(di)
            di.render()

        # test.renderTexture(image, renderer, 0, 0)
        # present renderer results
        renderer.present()

    # -------------------------------------------------------------------------------
    def setup(self):

        ###########################################################################
        # SDL setup
        ###########################################################################
        RESOURCES = sdl2.ext.Resources(__file__, "resources")
        sdl2.ext.init()

        # create window
        width = self.options.width
        height = self.options.height
        self.window = sdl2.ext.Window("Space Invaders", size=(width, height))
        self.window.show()

        # create a sprite renderer starting with a base sdl2ext renderer
        self.renderer = sdl2.ext.Renderer(self.window)

        ###########################################################################

        ###########################################################################
        # Our game object setup
        ###########################################################################
        # create player object
        player1 = draw.Player(self.renderer, self.width, self.height, 0.25, 1.0, 66, 28.8)
        player2 = draw.Player(self.renderer, self.width, self.height, 0.75, 1.0, 66, 28.8)
        self.players.append(player1)
        self.players.append(player2)
        for player in self.players:
            bullets = player.bullets
            self.playersbullets.append(bullets)

        self.lives = ui.renderLives(self.renderer, player1.lives, 5, 5)
        self.score = ui.renderScore(self.renderer, player1.score, self.width - (self.width / 3) - 25, 5)

        self.enemycontrol = draw.EnemyController(self.renderer, self.width, self.height)

        # creates shields
        x = .1
        while x <= .75:
            shield = draw.Shield(self.renderer, x, .8, self.width, self.height)
            self.shields.append(shield)
            x += .30

        ###########################################################################

        self.limitFrame = False
        frameRateLimit = 1.0
        if (self.options.limitFrameRate):
            self.limitFrame = True
            frameRateLimit = self.options.limitFrameRate
            print "--frame rate limit(%d)--" % frameRateLimit
        self.minFrameSecs = 1.0 / frameRateLimit
        if self.options.debug:
            self.fpsCounter = ui.textMaker(self.renderer, "FPS: 0", width - 55, height - 14, 12,
                                      fontname="Arial.ttf")

    def run(self, running, lastDelta):
        #######################################################################
        if self.gameIsActive:
            running = self.update(self.players, self.lives, self.score, self.playersbullets, self.enemycontrol, self.shields, lastDelta)
        if self.options.debug:
            self.fpsCounter.setText("FPS: " + str(int(1.0 / lastDelta)))
        # Always render
        self.render(self.renderer)
        #######################################################################

    def shutdown(self):
        # cleanup
        sdl2.ext.quit()

