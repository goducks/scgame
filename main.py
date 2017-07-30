import sdl2
import sdl2.ext
import time
from threading import Thread
from server import Server
from client import Client
from options import Options

# -------------------------------------------------------------------------------
def main():
    print "--begin game--"

    # SDL setup
    sdl2.ext.init()

    options = Options()
    server_port = 5556
    # server mode takes precedence
    if (options.opts.server):
        print "--server only mode--"
        # start the server
        server = Server(server_port)
        server.serverrun(options.opts.runtime)
    elif (options.opts.client):
        print "--client only mode--"
        # start the client
        client = Client(server_port)
        client.clientrun()
    else:
        print "--client and server mode--"
        # start server
        server = Server(server_port)
        Thread(target=server.run, args=['options.runtime']).start()
        time.sleep(1)
        client = Client(server_port)
        Thread(target=client.run, args='').start()

    # SDL shutdown
    sdl2.ext.quit()

    print "--end game--"


# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------