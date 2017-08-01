import zmq
import time
import timeit as ti
from helper import Proto, switch
import scgame
import sdl2
import collision
import ui
import drawable as draw
import scgameobjects as scgo

# Globals
g_zmqhwm = 1024

class Server(scgame.scgame):
    # To track clients, use dictionary of connections where:
    # key = client assigned identity
    # value = 4 element nested dict of:
    #    imc = incoming message count
    #    ibr = incoming bytes recv'd,
    #    omc = outgoing message count
    #    obs = outgoing bytes sent

    def __init__(self, server_port):
        context = zmq.Context().instance()
        self.socket = context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.SNDHWM, g_zmqhwm)
        self.socket.setsockopt(zmq.RCVHWM, g_zmqhwm)
        self.socket.bind("tcp://*:%s" % server_port)
        # set up a read poller
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.clientmap = dict()
        # remove later
        self.vx = 0.0
        self.fire = False
        print "Server bound to port: " + str(server_port)

    def serverrun(self, runtime):
        print "Server: start run"

        # Server's idle loop
        # Note: artificially running for a fixed number of seconds
        timeout = 1 # int(1.0/60.0)
        running = True
        self.lastDelta = 0.0
        quitLimit = 2.0
        quitTimer = 0.0
        super(Server, self).__init__()
        self.setup()
        while running:
            start = ti.default_timer()

            if not self.gameIsActive:
                quitTimer += self.lastDelta
                if (quitTimer >= quitLimit):
                    break

            # Read incoming
            sockets = dict(self.poller.poll(timeout))
            if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                id, data = self.socket.recv_multipart()
                self.parseMsg(id, data)

            running = self.run()

            # Send outgoing
            for x in range(10):
                for id in self.clientmap.iterkeys():
                    work = b"workload" + str(x)
                    self.send(id, Proto.str, work)

            stop = ti.default_timer()
            self.lastDelta = stop - start
            # Sleep if frame rate is higher than desired
            if (self.limitFrame and (self.lastDelta < self.minFrameSecs)):
                time.sleep(self.minFrameSecs - self.lastDelta)
                stop = ti.default_timer()
                self.lastDelta = stop - start

        self.shutdown()

        # Force disconnect/kill all clients
        print "Server: shutting down..."
        for id in self.clientmap.iterkeys():
            self.send(id, Proto.serverstop)

        print self.clientmap
        self.socket.close()
        print "Server: end run"

    def send(self, id, proto, data = b''):
        final = proto + data
        self.socket.send_multipart([id, final])
        # update send stats
        usage = self.clientmap[id]
        usage['omc'] += 1
        usage['obs'] += len(final)

    def parseMsg(self, id, msg):
        header = msg[0:Proto.headerlen]
        body = msg[Proto.headerlen:]
        # if header != Proto.str:
            # print "Proto: " + header + " data: " + body

        # Check if client is registered -- this is messy
        if not id in self.clientmap and not header == Proto.greet:
            print "Server: recv'd msg from unregistered client"
            # TODO: debug
            return

        for case in switch(header):
            if case(Proto.greet):
                print body
                colorsplit = body.split(":")
                print colorsplit
                color = sdl2.ext.Color(int(colorsplit[0]), int(colorsplit[1]), int(colorsplit[2]), 255)
                self.addClient(id, color)
                break
            if case(Proto.str):
                # print "Server: string: (" + id + ") " + body
                break
            if case(Proto.clientstop):
                self.removeClient(id, body)
                break
            if case(Proto.clientmove):
                self.clientmap[id]['vx'] = float(body)
                # print "Moving client. vx = " + str(self.vx)
                break
            if case(Proto.clientfire):
                self.clientmap[id]['fire'] = True
                break
            if case():  # default
                print "Server: received undefined message!"
                # TODO: debug

        # update receive stats
        usage = self.clientmap[id]
        usage['imc'] += 1
        usage['ibr'] += (Proto.headerlen + len(body))

    def addClient(self, id, body):
        if id in self.clientmap:
            print "Server: recv'd duplicate client reg"
            # TODO: debug
        else:
            print "Server: registering new client"
            global game
            self.addPlayer(id, body)
            self.clientmap[id] = {'imc': 0, 'ibr': 0, 'omc': 0, 'obs': 0, 'vx': 0,
                                  'fire': False, 'color': None}
            # reply with ack
            self.send(id, Proto.greet)
            print self.clientmap

    def removeClient(self, id, body):
        if id in self.clientmap:
            print "Server: removing client (" + id + ")"
            del self.clientmap[id]
        else:
            print "Attempt to remove unregistered client"
            # TODO: debug

    def run(self):
        running = True
        # Update only if active
        if self.gameIsActive:
            running = self.update(self.lastDelta)

        # Setup framerate if enabled
        if self.options.debug and self.lastDelta > 0.0:
            self.fpsCounter.setText("FPS: " + str(int(1.0 / self.lastDelta)))

        # Always render
        self.render()

        return running

    def update(self, time):
        # our main game loop

        # read local inputs & events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                return False
                break

        if self.gameIsActive:
            for player in self.players:
                # associate velocity with id in dictionary
                # print self.clientmap[player.id]['vx']
                player.vx = self.clientmap[player.id]['vx']
                if self.clientmap[player.id]['fire']:
                    player.fire()
                    self.clientmap[player.id]['fire'] = False
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
        # player = scgo.Player(self.width, self.height, 0, 0.5, 1.0, 66, 28.8)
        # self.players.append(player)

        # self.lives = ui.renderLives(player.lives, 5, 5)
        # self.score = ui.renderScore(player.score, self.width - (self.width / 3) - 25, 5)
        self.lives = ui.renderLives(0, 5, 5)
        self.score = ui.renderScore(0, self.width - (self.width / 3) - 25, 5)

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
            self.fpsCounter = draw.textMaker("FPS: 0", self.width - 55, self.height - 14, 12,
                                      fontname="Arial.ttf")