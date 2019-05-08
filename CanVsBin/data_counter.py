import pickle
import sys
import time

f = open('record.p', 'r')
plan = []
cnt = 0

while 1:
    try:
        plan = pickle.load(f)
        print plan
        cnt = cnt+1
        print 'cnt: ' + str(cnt)

    except EOFError:
        break

