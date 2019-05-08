"""
This code is used to recording data from subjects
input at the beginning the user id # and the game condition
(1=natural, 2 = speed, 3 = min errors)
the game will run 10 times, between each the user will be prompted to start the next game
"""


import pickle
import os
from can_vs_bin import *
from start_screen import start

subject_num = raw_input("Enter subject #: ")
condition_num = raw_input("Enter trial condition #: ")
file_id = 'record' + subject_num + '_' + condition_num + '_C.p'

trial_data = {}

os.environ['SDL_VIDEO_WINDOW_POS'] = '%i, %i' % (200, 200)
win_w = 1400; win_h = 700
pygame.init()
screen = pygame.display.set_mode((win_w, win_h))

win_size = screen.get_size()

font = pygame.font.SysFont('Arial', 60)
background = pygame.Surface(screen.get_size())
background.fill((255, 255, 255))
text = font.render('Please press Enter', True, (0, 0, 0))
screen.blit(background, (0, 0))
screen.blit(text,
            (win_size[0]/2 - text.get_width()/2, win_size[1]/2 - text.get_height()/2))
pygame.display.flip()

for i in range(10):
    #raw_input("Press Enter to begin game...")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    running = False
                elif event.key == K_ESCAPE:
                    #quit here?
                    pass
    start(screen)
    data, time, presses = runGame(screen, 'sub_num = ' + str(subject_num) + ', condition = ' + str(condition_num) + ', trial: ' + str(i+1))
    trial_data[i] = [data, time, presses]


f = open(os.path.join('Trial_Data', file_id), 'w')
pickle.dump(trial_data, f)
f.close()
