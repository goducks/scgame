import time

# CTimer class is a simple scope-based timer. On instance creation
# it stamps internal time, upon destruction calculates delta and prints
class CTimer:
    def __init__(self):
        self.start = time.clock()

    def display(self):
        delta = time.clock() - self.start
        os = "{:.5f}".format(delta) 
        # print "Partial:", os

    def __del__(self):
        delta = time.clock() - self.start
        os = "{:.5f}".format(delta) 
        # print "Elapsed:", os
