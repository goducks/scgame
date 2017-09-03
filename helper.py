###############################################################################
# This class is used to give switch statement like behavior from C/C++
# There's no magic here, other than making code elsewhere readable
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
###############################################################################

class Proto():
    # this is just a namespace for storing protocol IDs
    # TODO: this is ghetto
    headerlen   = 6
    greet       =     b'0x0001'
    str         =     b'0x0002'
    ping        =     b'0x0003'
    serverstop  =     b'0x000A'
    clientstop  =     b'0x000B'
    clientmove  =     b'0x000C'
    clientfire  =     b'0x000D'
    addtoclient =     b'0x000E'
    moveother   =     b'0x000F'
    fireother   =     b'0x0004'
    lostlife    =     b'0x0005'
    scoreup     =     b'0x0006'
    enemyfire   =     b'0x0007'