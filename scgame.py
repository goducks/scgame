from options import Options
import sdl2.ext
import collision
import drawable as draw
import ui
import scgameobjects as scgo

class scgame():
    def __init__(self):
        self.gameIsActive = True
        self.width = 0
        self.height = 0
        self.renderer = None
        self.window = None
        self.players = list()
        self.enemycontrol = None
        self.shields = list()
        self.lives = None
        self.score = None
        self.fpsCounter = None
        self.limitFrame = None
        self.options = Options().opts
        self.minFrameSecs = None


    # -------------------------------------------------------------------------------
    def clear(self):
        print "clearing"
        self.renderer.color = sdl2.ext.Color(0, 0, 0, 255)
        self.renderer.clear()
        self.renderer.present()

    # -------------------------------------------------------------------------------
    def gameover(self, player):
        # Empty the current drawlist
        draw.Drawable.clearAll()
        # Add ONLY the gameover text
        gameover = draw.textMaker("GAME OVER", self.width / 5, (self.height / 2) - 50, 40,
                                fontname="8-BIT WONDER.TTF")
        text = "SCORE " + str(player.score)
        score = draw.textMaker(text, self.width / 5, (self.height / 2), 30,
                             fontname="8-BIT WONDER.TTF")
        # Signal update function to end
        self.gameIsActive = False

    # -------------------------------------------------------------------------------
    def update(self, time):
        # our main game loop

        # read local inputs & events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                return False
                break
            for player in self.players:
                player.getInput(event, self.players.index(player))

        if self.gameIsActive:
            for player in self.players:
                player.update(time)
            self.enemycontrol.update(time)
            for player in self.players:
                if self.enemycontrol.checkWin(player):
                    self.gameover(player)
            for enemy in self.enemycontrol.enemies:
                enemy.update(time)
            for ebullet in self.enemycontrol.bullets:
                ebullet.update(time)
                for shield in self.shields:
                    hit = collision.checkCollision(ebullet, shield)
                    if hit:
                        self.enemycontrol.removebullet(ebullet)
                        shield.hit()
                        if shield.health <= 0:
                            shield.remove()
                            self.shields.remove(shield)
                        break

                for player in self.players:
                    hit = collision.checkCollision(ebullet, player)
                    if hit:
                        # print "enemy hit"
                        self.enemycontrol.removebullet(ebullet)
                        player.lostlife()
                        self.lives.updateLives(player.lives)
                        if player.lives <= 0:
                            self.gameover(player)
                        break

            for player in self.players:
                for bullet in player.bullets:
                    bullet.update(time)
                    for shield in self.shields:
                        hit = collision.checkCollision(bullet, shield)
                        if hit:
                            player.removebullet(bullet)
                            shield.hit()
                            if shield.health <= 0:
                                shield.remove()
                                self.shields.remove(shield)
                            break
                    for enemy in self.enemycontrol.enemies:
                        hit = collision.checkCollision(bullet, enemy)
                        if hit:
                            player.score += enemy.points
                            self.score.updateScore(player.score)
                            enemy.remove()
                            self.enemycontrol.enemies.remove(enemy)
                            player.removebullet(bullet)
                            break
            if len(self.enemycontrol.enemies) < 1:
                self.enemycontrol.reset()

        return True

    # -------------------------------------------------------------------------------
    def render(self):
        # clear to black
        self.renderer.color = sdl2.ext.Color(0, 0, 0, 255)
        self.renderer.clear()

        # iterate the global draw list
        for di in draw.Drawable.drawList:
            di.render()

        # test.renderTexture(image, renderer, 0, 0)
        # present renderer results
        self.renderer.present()

    # -------------------------------------------------------------------------------
    def setup(self):
        # create window
        self.width = self.options.width
        self.height = self.options.height
        self.window = sdl2.ext.Window("Space Invaders", size=(self.width, self.height))
        self.window.show()

        # create renderer starting with a base sdl2ext renderer
        self.renderer = sdl2.ext.Renderer(self.window)
        # set all our renderer instance types
        draw.filledRect.setRenderer(self.renderer)
        draw.spriteMaker.setRenderer(self.renderer)
        draw.textMaker.setRenderer(self.renderer)

        ###########################################################################

        ###########################################################################
        # Our game object setup
        ###########################################################################
        # create player object
        player1 = scgo.Player(self.width, self.height, 0.25, 1.0, 66, 28.8)
        player2 = scgo.Player(self.width, self.height, 0.75, 1.0, 66, 28.8)
        self.players.append(player1)
        self.players.append(player2)

        self.lives = ui.renderLives(player1.lives, 5, 5)
        self.score = ui.renderScore(player1.score, self.width - (self.width / 3) - 25, 5)

        self.enemycontrol = scgo.EnemyController(self.width, self.height)

        # creates shields
        x = .1
        while x <= .75:
            shield = scgo.Shield(x, .8, self.width, self.height)
            self.shields.append(shield)
            x += .30

        self.limitFrame = False
        frameRateLimit = 1.0
        if (self.options.limitFrameRate):
            self.limitFrame = True
            frameRateLimit = self.options.limitFrameRate
            print "--frame rate limit(%d)--" % frameRateLimit
        self.minFrameSecs = 1.0 / frameRateLimit

        if self.options.debug:
            self.fpsCounter = draw.textMaker("FPS: 0", self.width - 55,
                                           self.height - 14, 12, fontname="Arial.ttf")

    def run(self, lastDelta):
        running = True
        # Update only if active
        if self.gameIsActive:
            running = self.update(lastDelta)

        # Setup framerate if enabled
        if self.options.debug and lastDelta > 0.0:
            self.fpsCounter.setText("FPS: " + str(int(1.0 / lastDelta)))

        # Always render
        self.render()

        return running

    def shutdown(self):
        # add anything needed for cleanup here
        pass
