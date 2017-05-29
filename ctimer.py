import time

#------------------------------------------------------------------------------
# CTimer class timer class. It can be used in two ways:
# 1) As a simple scope-based timer. On instance creation -- it stamps internal
#    time, upon destruction calculates delta and prints. Update method
#    is not used in this form
# 2) As a simple frame or update timer -- in this case, use update method
class CTimer:
    def __init__(self, debugprint=False):
        self.debugprint = debugprint
        now = time.clock()
        self.create = now
        self.start = now
        self.delta = 0.0

    def getDelta(self):
        return self.delta

    def update(self):
        now = time.clock()
        self.delta = now - self.start
        self.start = now
        if (self.debugprint):
            os = "{:.5f}".format(self.delta)
            print "Update:", os

    def __del__(self):
        if (self.debugprint):
            os = "{:.5f}".format(time.clock() - self.create)
            print "Total Elapsed:", os
#------------------------------------------------------------------------------
