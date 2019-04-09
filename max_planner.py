# Finally Max decide to plan by himself.
import os
import pygame

from CanVsBin.autocans import *

from CanVsBin.option_receiver import OptionThread
from CanVsBin.option_testscript import OptionTestThread

from Plan_PDDL_Thread import *
from game.data_generation.helpers import *
from plan_helpers import *

import pre_load

def table_cleaner():
    # create the screen object
    # here we pass it a size of 800x600
    win_w = 1400;
    win_h = 700
    desk_w = 1200;
    desk_h = 250
    ## desk position (center), desk size
    dist2Desk = 10
    desk_x = (win_w - desk_w) / 2;
    desk_y = (win_h - desk_h - 64 - dist2Desk) / 4

    ## number of current bins and maximum bins
    ## one obj in
    max_obj = 10;
    column = 3

    pos_type = PositionType(2)

    all_pos = []

    for i in range(max_obj+1):
        # don't place anything in the middle, it's for the bin
        if i == max_obj/2:
            size = 60
            x = desk_x + i * desk_w/(max_obj+1) + (desk_w/(max_obj+1)-size)/2
            y = desk_y + desk_h / 3 + (desk_h/3-size)/2
            all_pos.append(x)
            all_pos.append(y)
        elif i == 4 or i==3 or i==2:
            size = 20
            y_cell = random.randint(0, 2)
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            # print pos_type
            pos_type = PositionType.bottom_line
            if pos_type == PositionType.full_rand:
                all_pos.append(random.randint(x_left, x_right))
                all_pos.append(random.randint(y_top, y_bottom))
            elif pos_type == PositionType.centered_random:
                all_pos.append(x_left + ((x_right - x_left) / 2))
                all_pos.append(y_top + ((y_bottom - y_top) / 2))
            elif pos_type == PositionType.centered_static:
                print "i havent made this one yet"
            elif pos_type == PositionType.bottom_line:
                all_pos.append(x_left + ((x_right - x_left) / 2))
                all_pos.append(desk_y + desk_h - 30)
        elif i <= 8 and i > 6:
            size = 20
            y_cell = random.randint(0, 2)
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            # print pos_type
            pos_type = PositionType.bottom_line
            if pos_type == PositionType.full_rand:
                all_pos.append(random.randint(x_left, x_right))
                all_pos.append(random.randint(y_top, y_bottom))
            elif pos_type == PositionType.centered_random:
                all_pos.append(x_left + ((x_right - x_left) / 2))
                all_pos.append(y_top + ((y_bottom - y_top) / 2))
            elif pos_type == PositionType.centered_static:
                print "i havent made this one yet"
            elif pos_type == PositionType.bottom_line:
                all_pos.append(x_left + ((x_right - x_left) / 2))
                all_pos.append(desk_y + desk_h - 30)
        # elif i == 6:
        #     size = 20
        #     y_cell = random.randint(0, 2)
        #     x_left = desk_x + i * desk_w / (max_obj + 1) + size
        #     x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
        #     y_top = desk_y + desk_h / 3 * y_cell + size
        #     y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
        #     # print pos_type
        #     all_pos.append(x_left + ((x_right - x_left) / 2+20))
        #     all_pos.append(desk_y + 10)
        else:
            # pick up a cell first
            size = 20
            y_cell = random.randint(0, 2)
            x_left = desk_x + i*desk_w/(max_obj+1) + size
            x_right = desk_x + (i+1)*desk_w/(max_obj+1) - size
            y_top = desk_y + desk_h/3 * y_cell+size
            y_bottom = desk_y + desk_h/3 * (y_cell+1)-size
            #print pos_type
            pos_type = PositionType.centered_random
            if pos_type == PositionType.full_rand:
                all_pos.append(random.randint(x_left, x_right))
                all_pos.append(random.randint(y_top, y_bottom))
            elif pos_type == PositionType.centered_random:
                if y_cell == 0:
                    y_top += 50
                all_pos.append(x_left+((x_right - x_left)/2))
                all_pos.append(y_top+((y_bottom - y_top)/2))
            elif pos_type == PositionType.centered_static:
                print "i havent made this one yet"
            elif pos_type == PositionType.bottom_line:
                all_pos.append(x_left+((x_right - x_left)/2))
                all_pos.append(desk_y + desk_h - 30)

        all_pos.append(False)
    # a special case
    #all_pos = [154, 314, False, 263, 314, False, 372, 314, False, 481, 314, False, 590, 314, False, 669, 188, False, 808, 314, False, 917, 314, False, 1026, 314, False, 1135, 314, False, 1245, 314, False]
    all_pos = [170, 301, False,
               263, 160, False,
               372, 314, False,
               481, 255, False,
               590, 314, False,
               669, 188, False,
               808, 301, False,
               917, 314, False,
               1000, 185, False,
               1125, 268, False,
               1245, 218, False]

    print all_pos
    return all_pos


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i, %i' % (25, 50)
    win_w = 1400
    win_h = 700
    pygame.init()
    screen = pygame.display.set_mode((win_w, win_h))

    win_size = screen.get_size()

    clock = pygame.time.Clock()
    running = True

    initWorldState = table_cleaner()

    pre_load.init(initWorldState)

    optionT = OptionThread(10, 'Thread for input options')
    optionT.start()
    plannerT = PlannerThread(20, "Thread for input options", optionT)
    plannerT.start()

    plannerT.hl_start, plannerT.hl_end = pre_load.hl_start, pre_load.hl_end
    runGame(screen, 'auto', optionT, initWorldState)


    while running:
       for event in pygame.event.get():
           if event.type == KEYDOWN:
               if event.key == K_ESCAPE:
                   running = False