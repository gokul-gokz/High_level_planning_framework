import threading
import time
from option_receiver import OptionThread
import pygame

class ManualOptionThread(threading.Thread):
    flat = False
    running = False

    def __init__(self, threadID, name, inputThread):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.tLock = threading.Lock()
        self.optionT = inputThread
        self.running = False

    def run(self):
        self.runningT = True
        while self.runningT:
            keyInput = raw_input('your option:')
            self.optionT.tLock.acquire()
            if len(keyInput) > 4:
                if keyInput[:4] == 'pick' and keyInput[4:].isdigit():
                    value = int(keyInput[4:])
                    self.optionT.tupleIn = ('pick', value)
                elif keyInput[:5] == 'place' and keyInput[5:].isdigit():
                    value = int(keyInput[5:])
                    self.optionT.tupleIn = ('place', value)
                elif keyInput[:6] == 'moveto' and keyInput[6:].isdigit():
                    value = int(keyInput[6:])
                    self.optionT.tupleIn = ('moveto', value)
                else:
                    print 'command error'
            self.optionT.tLock.release()

        return


if __name__ == '__main__':
    pygame.init()
    running = True

    optionT = OptionThread(10, 'Thread for option')
    moT = ManualOptionThread(20, "Thread for manually input options", optionT)

    optionT.start()
    moT.start()
    initialT = time.time()
    while running:
        #print time.time()-initialT
        for event in pygame.event.get():
            if event.type == optionT.EMUMOUSE_EVENT:
                optionT.tLock.acquire()
                print '\n mouse event ',
                print optionT.option
                optionT.tLock.release()
            elif event.type == optionT.EMUKEYUP_EVENT:
                print '\n keyboard event ',
                optionT.tLock.acquire()
                print optionT.option
                optionT.tLock.release()
        time.sleep(1)

    time.sleep(3)
    #pygame.quit()