import time
from threading import Thread
from server import Server
from client import Client
from options import Options

# -------------------------------------------------------------------------------
def main():
    print "--begin game--"
    options = Options()
    server_port = 5556
    # server mode takes precedence
    if (options.opts.server):
        print "--server only mode--"
        # start the server
        server = Server(server_port)
        server.run(options.opts.runtime)
    elif (options.opts.client):
        print "--client only mode--"
        # start the client
        client = Client(server_port)
        client.run()
    else:
        print "--client and server mode--"
        # start server
        server = Server(server_port)
        Thread(target=server.run, args=['options.runtime']).start()
        time.sleep(1)
        client = Client(server_port)
        Thread(target=client.run, args='').start()

    print "--end game--"


# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------