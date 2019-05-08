import pygame
from pygame.locals import *
import time
from enum import Enum
import threading

class OptionTestThread(threading.Thread):
    optionT = None

    def __init__(self, threadID, name, providedThread):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.optionT = providedThread

    def run(self):
        while self.optionT.worldState == None:
            time.sleep(1)

        time.sleep(1)
        # read from
        dists = [850, 275, 375, 475, 600, 800, 925, 1025, 1150, 1250]
        #dists = [150, 275, 375, 475, 600, 800, 925, 1025, 1150, 1250]
        center = 700
        for i in range(10):
            #move
            self.optionT.tLock.acquire()
            self.optionT.tupleIn = ('moveto', dists[i])
            self.optionT.tLock.release()
            time.sleep(0.1)
            #print self.optionT.worldState
            #pick
            self.optionT.tLock.acquire()
            self.optionT.tupleIn = ('pick', i)
            self.optionT.tLock.release()
            time.sleep(0.1)
            #print self.optionT.worldState
            #move
            self.optionT.tLock.acquire()
            self.optionT.tupleIn = ('moveto', center)
            self.optionT.tLock.release()
            time.sleep(0.1)
            #print self.optionT.worldState
            #place
            self.optionT.tLock.acquire()
            self.optionT.tupleIn = ('place', i)
            self.optionT.tLock.release()
            time.sleep(0.1)
            #print self.optionT.worldState
