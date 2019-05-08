import pygame
from pygame.locals import *
import time
from enum import Enum
import threading

class ExecState(Enum):
    busy = 0
    waiting = 1
    success = 2
    fail = 3

class ErrorCode(Enum):
    no_error = 0
    pick_not_exist = 1
    pick_too_far = 2
    pick_in_bin = 3
    pick_too_many_objs = 4
    place_not_exist = 5
    place_on_table = 6
    place_too_far = 7
    place_hand_empty = 8
    obstacle = 9


class OptionThread(threading.Thread):
    # tuple is a string (move/pick/place) follow by an int.
    tupleIn = None
    tLock = None
    option = None
    kbInput = None
    runningT = False
    worldState = None
    errorState = None
    execState = None
    errorInfo = None   # This variable is to store obstacle information

    def __init__(self, threadID, name, kbInputT = None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.tLock = threading.Lock()
        self.EMUKEYUP_EVENT = pygame.USEREVENT + 1
        self.EMUMOUSE_EVENT = pygame.USEREVENT + 2
        self.runningT = False
        self.errorState = ErrorCode.no_error
        self.execState = ExecState.waiting

    def run(self):
        self.runningT = True
        while self.runningT:
            self.tLock.acquire()
            if self.tupleIn != None:
                # tirgger your event here
                self.option = self.tupleIn
                if self.tupleIn[0] == 'pick':
                    click_event = pygame.event.Event(self.EMUMOUSE_EVENT, message="DO NOT CLICK")
                    print self.option
                    pygame.event.post(click_event)
                elif self.tupleIn[0] == 'place':
                    click_event = pygame.event.Event(self.EMUMOUSE_EVENT, message="DO NOT CLICK")
                    print self.option
                    pygame.event.post(click_event)
                elif self.tupleIn[0] == 'moveto':
                    key_event = pygame.event.Event(self.EMUKEYUP_EVENT, message="DO NOT PRESS THE BUTTON")
                    print self.option
                    pygame.event.post(key_event)
                self.tupleIn = None
            self.tLock.release()

        return

if __name__ == '__main__':

    pygame.init()
    clock = pygame.time.Clock()
    running = True
    optionT = OptionThread(1, "Thread for input options")

    optionT.start()
    initialT = time.time()
    while running:
        print time.time()-initialT
        optionT.tLock.acquire()
        optionT.option = ['pick', 1]
        optionT.tLock.release()

        for event in pygame.event.get():
            if event.type == optionT.EMUMOUSE_EVENT:
                print 'I heard a click'

        time.sleep(1)

    time.sleep(3)
    #pygame.quit()
