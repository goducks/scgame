import time
import timeit as ti
import uuid
import zmq
from helper import Proto, switch
import scgame

# Globals
g_zmqhwm = 1024

class Client(scgame.scgame):
    # client registration string

    def __init__(self, ipaddr, server_port):
        context = zmq.Context().instance()
        self.socket = context.socket(zmq.DEALER)
        # generate a universally unique client ID -- slicing last 12
        # characters of the UUID4 just to keep it shorter
        self.id = str(uuid.uuid4())[-12:]
        self.socket.setsockopt(zmq.IDENTITY, str(self.id))
        self.socket.setsockopt(zmq.SNDHWM, g_zmqhwm)
        self.socket.setsockopt(zmq.RCVHWM, g_zmqhwm)
        self.socket.connect("tcp://%s:%s" % (ipaddr, server_port))
        # set up a read poller
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.svr_connect = False
        super(Client, self).__init__()
        self.setup()
        color = self.players[0].colormod
        colorstr = "%s:%s:%s" % (color.r, color.g, color.b)
        # send connection message that will register server with client
        print "Connecting to server..."
        self.send(Proto.greet, colorstr)
        # blocking read
        msg = self.socket.recv()
        self.parseMsg(msg)

        print "Client: " + str(self.id) + " connected to: " + ipaddr + str(server_port)

    def clientrun(self):
        print "Client: start run"

        # Client's idle loop
        timeout = 1
        total = 0
        self.lastDelta = 0.0
        quitLimit = 2.0
        quitTimer = 0.0

        while True:
            start = ti.default_timer()

            if not self.gameIsActive:
                quitTimer += self.lastDelta
                if (quitTimer >= quitLimit):
                    break

            # Read incoming
            sockets = dict(self.poller.poll(timeout))
            if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                msg = self.socket.recv()
                total += 1
                if not self.parseMsg(msg):
                    break

            super(Client, self).run()

            if self.svr_connect:
                # will only have one local player, specify if player is local w/variable
                for player in self.players:
                    if player.move:
                        movevx = str(player.vx)
                        # print "Sending move message"
                        self.send(Proto.clientmove, movevx)
                    if player.shoot:
                        # print "Sending fire message"
                        self.send(Proto.clientfire)
                        player.shoot = False
                # Send outgoing
                # work = b"workload" + str(total)
                # self.send(Proto.str, work)

            stop = ti.default_timer()
            self.lastDelta = stop - start
            # Sleep if frame rate is higher than desired
            if (self.limitFrame and (self.lastDelta < self.minFrameSecs)):
                time.sleep(self.minFrameSecs - self.lastDelta)
                stop = ti.default_timer()
                self.lastDelta = stop - start

        self.shutdown()

        print("Client: total messages received: %s" % total)
        print "Client: end run"
        self.socket.close()

    def send(self, proto, data = b''):
        try:
            # if proto != Proto.str:
                # print "Proto: " + proto + " data: " + data
            if not self.socket.send(proto + data, zmq.NOBLOCK) == None:
                print "Client: socket send failed"
        except zmq.ZMQError:
            print "Client: socket send failed, disconnecting"
            self.svr_connect = False

    def parseMsg(self, msg):
        ret = True
        header = msg[0:Proto.headerlen]
        body = msg[Proto.headerlen:]
        for case in switch(header):
            if case(Proto.greet):
                print "Client: server greet"
                self.svr_connect = True
                break
            if case(Proto.str):
                # print "Client: string: " + body
                break
            if case(Proto.serverstop):
                print "Client: serverstop"
                # Send reply to delete client
                self.svr_connect = False
                self.send(Proto.clientstop)
                ret = False
                break
            if case():  # default
                print "Client: received undefined message!"
                # TODO: debug
        return ret