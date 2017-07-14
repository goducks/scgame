import zmq
import time
import timeit as ti
from helper import Proto, switch
import scgame

# Globals
g_zmqhwm = 100

class Server():
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
        print "Server bound to port: " + str(server_port)

    def run(self, runtime):
        print "Server: start run"

        # Server's idle loop
        # Note: artificially running for a fixed number of seconds
        timeout = 1 # int(1.0/60.0)
        running = True
        lastDelta = 0.0
        quitLimit = 2.0
        quitTimer = 0.0
        game = scgame.scgame()
        game.setup()
        while running:
            start = ti.default_timer()

            if not game.gameIsActive:
                quitTimer += lastDelta
                if (quitTimer >= quitLimit):
                    break

            # Read incoming
            sockets = dict(self.poller.poll(timeout))
            if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                id, data = self.socket.recv_multipart()
                self.parseMsg(id, data)

            running = game.run(lastDelta)

            # Send outgoing
            for x in range(10):
                for id in self.clientmap.iterkeys():
                    work = b"workload" + str(x)
                    self.send(id, Proto.str, work)

            stop = ti.default_timer()
            lastDelta = stop - start
            # Sleep if frame rate is higher than desired
            if (game.limitFrame and (lastDelta < game.minFrameSecs)):
                time.sleep(game.minFrameSecs - lastDelta)
                stop = ti.default_timer()
                lastDelta = stop - start

        game.shutdown()

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

        # Check if client is registered -- this is messy
        if not id in self.clientmap and not header == Proto.greet:
            print "Server: recv'd msg from unregistered client"
            # TODO: debug
            return

        for case in switch(header):
            if case(Proto.greet):
                self.addClient(id, body)
                break
            if case(Proto.str):
                print "Server: string: (" + id + ") " + body
                break
            if case(Proto.clientstop):
                self.removeClient(id, body)
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
            self.clientmap[id] = {'imc': 0, 'ibr': 0, 'omc': 0, 'obs': 0}
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