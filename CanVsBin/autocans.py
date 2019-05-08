import pygame
from pygame.locals import *
import time
import pickle
import os

from human import Player
from item import *
from cursor import Cursor
from enum import Enum
from option_receiver import OptionThread, ErrorCode, ExecState
from manual_option import ManualOptionThread
from option_testscript import OptionTestThread

import pre_load

from low_level_motion_planner import get_trajectory
from low_level_motion_planner import get_feasible_move_position


A_star_Path=[(0,0),(1,1)]
flag=1;
class PositionType(Enum):
    params = 0
    full_rand = 1
    centered_random = 2
    centered_static = 3
    bottom_line = 4


def data(player, objs):
    pos = (float(player.x), float(player.y), player.handFull)
    for i in objs:
        if i.state == ObjState['inHand']:
            obj_state = True
        else:
            obj_state = False
        pos = pos + (float(i.x), float(i.y), obj_state)
    return pos

def runGame(screen, title, optionT, obj_pos):
    global A_star_Path

    debug = True
    prompt = False
    write_data = True

    # initialize pygame
    #pygame.init()

    # create the screen object
    # here we pass it a size of 800x600
    win_w = 1400; win_h = 700
    desk_w = 1200; desk_h = 250
    ## desk position (center), desk size
    dist2Desk = 10
    desk_x = (win_w-desk_w)/2; desk_y = (win_h-desk_h-64-dist2Desk)/4

    ## number of current bins and maximum bins
    ## one obj in
    max_obj = 10; column = 3
    #start with nothing in the bin
    curr_bin = 0;

    ## default arm length
    arm_len = 300

    font = pygame.font.SysFont("comicsansms", 36)
    text = font.render('Start on your call', True, (0, 0, 0))

    ## mouse position
    mousePos = pygame.mouse.get_pos()

    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))

    all_sprites = pygame.sprite.OrderedUpdates()

    desk = Desk(desk_x, desk_y, desk_w, desk_h)
    #all_sprites.add(desk)

    # create our 'player'; right now he's just a rectangle
    player = Player(win_w, win_h, desk_y, desk_h, dist2Desk, arm_len)
    all_sprites.add(player)

    mouse_start_pos = pygame.mouse.get_pos()
    cursor = Cursor(player, mouse_start_pos)
    screen.blit(cursor.hand, cursor.pos)

     ##########################################
    ### A-star search Algorithm
    ##########################################

    game_width = 1400 #100
    game_height = 700 #50
    grid_size = 10
    success = False




    objs = pygame.sprite.OrderedUpdates()
    #the number of the object
    no_objs = 0

    #pos_type = PositionType(2)
    pos_type = PositionType(0)

    if pos_type == PositionType(0):
        for i in range(max_obj + 1):
            x = obj_pos[i*3]
            y = obj_pos[i*3+1]
            if i == max_obj / 2:
                size = 60
                bin = Bin(x, y, size, size, arm_len)
                all_sprites.add(bin)
            else:
                # pick up a cell first
                size_obstacle = 60
                size_object=20
                obstacle_color= (70,0,100)
                if(x==917 and y==314):
                    new_obj = Obj(x, y, no_objs, size_obstacle , arm_len, obstacle_color)
                else:
                    new_obj = Obj(x, y, no_objs, size_object, arm_len)
                objs.add(new_obj)
                all_sprites.add(new_obj)
                objs.update(player, cursor)
                no_objs += 1
    else:
        for i in range(max_obj+1):
            # don't place anything in the middle, it's for the bin
            if i == max_obj/2:
                size = 60
                x = desk_x + i * desk_w/(max_obj+1) + (desk_w/(max_obj+1)-size)/2
                y = desk_y + desk_h / 3 + (desk_h/3-size)/2
                bin = Bin(x, y, size, size, arm_len)
                all_sprites.add(bin)
            else:
                # pick up a cell first
                size = 20
                y_cell = random.randint(0,2)
                x_left = desk_x + i*desk_w/(max_obj+1) + size
                x_right = desk_x + (i+1)*desk_w/(max_obj+1) - size
                y_top = desk_y + desk_h/3 * y_cell+size
                y_bottom = desk_y + desk_h/3 * (y_cell+1)-size

                if pos_type == PositionType.full_rand:
                    new_obj = Obj(random.randint(x_left, x_right), random.randint(y_top, y_bottom), no_objs, size, arm_len)
                elif pos_type == PositionType.centered_random:
                    new_obj = Obj(x_left+((x_right - x_left)/2), y_top+((y_bottom - y_top)/2), no_objs, size, arm_len)
                elif pos_type == PositionType.centered_static:
                    print "i havent made this one yet"
                objs.add(new_obj)
                all_sprites.add(new_obj)
                objs.update(player, cursor)
                no_objs += 1

    # prepare to start the game
    running = True
    start = False
    gameover = False
    event_flag = False
    # last_state: is the "s_prime" of the last option (will be the state/old of the next option)
    last_state = ()
    # buffer: save the state after last key event.
    # if a new event of mouse click is coming, buffered state becomes
    pos_buffer = ()
    # save 2 types of event time
    # 1. the time of finishing the last option
    # 2. the time of last key release (for move option)
    last_event_t = 0
    last_release_t = 0
    record = []
    key_presses = 0

    countdown = False

    pygame.mouse.set_pos(win_w/2, win_h/2)
    cursor.center = [win_w/2, win_h/2]

    instruction = font.render('Press Enter to continue', True, (0, 0, 0))
    now_trial = font.render(title, True, (0, 0, 0))

    optionT.worldState = data(player, objs)

    #game loop
    optionT.tLock.acquire()
    execState = ExecState.waiting
    optionT.tLock.release()
    option_text = font.render('Planning', True, (0, 0, 0))
    while running:

        optionT.tLock.acquire()
        optionState = optionT.execState
        optionT.tLock.release()
        if optionState == ExecState.waiting:
            tictac = int(time.time()*2) % 4
            if tictac == 0:
                option_text = font.render('Planning', True, (0, 0, 0))
            elif tictac == 1:
                option_text = font.render('Planning.', True, (0, 0, 0))
            elif tictac == 2:
                option_text = font.render('Planning..', True, (0, 0, 0))
            else:
                option_text = font.render('Planning...', True, (0, 0, 0))



        for event in pygame.event.get():
            # Game start, start to count the time
            if start == False:
                mouse_now_pos = pygame.mouse.get_pos()
                mouseDist = sqrt((mouse_now_pos[0]-mouse_start_pos[0])**2 + (mouse_now_pos[1]-mouse_start_pos[1])**2)

                ## EVENT:
                ## GAME START
                if event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN or mouseDist > 10:
                    last_state = data(player,objs)
                    pos_buffer = last_state
                    start_time = time.time()
                    text = font.render('Done: ' + str(curr_bin) + ', Remaining: ' + str(max_obj - curr_bin),
                                       True, (0, 0, 0))
                    last_event_t = start_time
                    last_release_t = start_time
                    start = True
                    # record.append(round(start_time, 2))

            # key down, now you cannot click on objs
            # you can still move your cursor around
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                # turn on or turn off the countdown
                if event.key == K_t:
                    print 'turn it on'
                    countdown = not countdown
            # key up, update buffered world state
            # now you can click on objs
            # -- insert the move option here --
            elif (event.type == KEYUP)\
                    or (event.type == optionT.EMUKEYUP_EVENT):
                if event.type == optionT.EMUKEYUP_EVENT:
                    # option 'moveto'

                    # This is to remove the trajectory from PYGAME display
                    A_star_Path=[]

                    optionT.tLock.acquire()
                    option = optionT.option
                    optionT.execState = ExecState.busy

                  #  print "option=",option

                    player.rect.centerx = option[1]
                    player.update()
                    optionT.worldState = data(player, objs)
                    optionT.tLock.release()
                key_presses = key_presses + 1
                #print 'buffer updated'
                pos_buffer = data(player, objs)
                last_release_t = time.time()

            elif event.type == pygame.MOUSEMOTION:
                mousePos = pygame.mouse.get_pos()

            # Now you can do this only if you stop moving
            # pygame.key.get_pressed return all keyboard states as 0 or 1
            # no key being pressed means all states equal to 0
            # -- insert place/pick option here --
            elif (event.type == pygame.MOUSEBUTTONDOWN\
                    and sum(pygame.key.get_pressed())-pygame.key.get_pressed()[300]<=0\
                    and event.button == 1)\
                    or (event.type == optionT.EMUMOUSE_EVENT):
                ## -------------------
                ## Option execute here
                ## -------------------
                if event.type == optionT.EMUMOUSE_EVENT:
                    optionT.tLock.acquire()
                    option = optionT.option
                    optionT.execState = ExecState.busy
                    #print option

                    optionT.option = None
                    optionT.tLock.release()

                    if option[0] == 'pick':
                        option_text = font.render(option[0] + ' object: ' + str(option[1]), True, (0, 0, 0))
                        A_star_Path=[]
                        Current_option=option
                        if player.handFull == False:
                            if option[1] > 9 or option[1] < 0:
                                optionT.tLock.acquire()
                                optionT.errorState = ErrorCode.pick_not_exist
                                optionT.tLock.release()
                                print 'Learn better math dude.'
                            else:
                                if objs.sprites()[option[1]].state == ObjState['onTable']:
                                    # obj is within reaching range
                                    x = objs.sprites()[option[1]].rect.centerx
                                    y = objs.sprites()[option[1]].rect.centery
                                    dist = (x - player.x) ** 2 + (y - player.y) ** 2
                                    dist = int(sqrt(float(dist)))
                                    if dist < player.armLen:


#-------------------------------------------------Low level planner(A-star) called to execute the action -----------------------------------------------------------
                                        A_star_start_position=(player.y,player.x)
                                        A_star_end_position=(y,x)
                                        test_objects=[(314-50,917-50,100,100)]
                                        success, path = get_trajectory(game_width, game_height, grid_size, A_star_start_position,A_star_end_position, test_objects)
                                        global flag

                                        ##Temp making the option fail
                                        failed_pick=7
                                        if(option[1]==failed_pick and flag):
                                             success=0
                                             flag=0
                                        # Convert mihir's path to pygame input path
                                        if(success):
                                            objs.sprites()[option[1]].rect.centerx = 0
                                            objs.sprites()[option[1]].rect.centery = 0
                                            objs.sprites()[option[1]].state = ObjState['inHand']
                                            #path_ = [] # dict of dict

                                            for i in path:
                                                point_ = [i[1], i[0]]
                                                A_star_Path.append(point_)

                                            player.handFull = True
                                            optionT.tLock.acquire()
                                            optionT.worldState = data(player, objs)
                                            optionT.tLock.release()

                                        elif(not success):
                                            #Store the failed option
                                            previous_option=option
                                            PDDL_data = pickle.load(open("PPDDL_Generation/PDDL_Domains/bins_PDDL_C_2.p", "rb"))
                                            # PDDL_data = pickle.load(open("PPDDL_Generation/option_data.p", "rb"))

                                            #scaler = pickle.load(open("game/data_generation/gamescaler.p", "rb"))


                                            P = PDDL_data['P']

                                            preconditions = PDDL_data['preconditions']
                                            pre_pick = preconditions['pick'+str(failed_pick)]
                                            pmasks = PDDL_data['pmasks']
                                            for i in range(len(pre_pick)):
                                                for symbol_name in pre_pick[i]:
                                                    #print P[symbol_name].sample(10)
                                                    # print points
                                                    masks = pmasks[symbol_name]
                                                    #print masks
                                                    masks_count = 0
                                                    index = -1
                                                    for i in range(len(masks)):
                                                        if masks[i]:
                                                            masks_count += 1
                                                            if i % 3 == 0:
                                                                index = i

                                                    if masks_count == 1 and index != -1:
                                                        # print "x-----------: "
                                                        # print "This is the option: ", symbol_name
                                                        points = P[symbol_name].sample(10)
                                                        #print points
                                                        minimum=(min(points) + 1) * game_width/2
                                                        maximum=(max(points) + 1) * game_width/2
                                                        mid=(minimum+maximum)/2
                                                        # print "Mid_point",mid
                                                        symbol_info = (minimum, mid, maximum)
                                                    else:
                                                        pass
                                                        #print "Not this symbol."


                                            #Extract the position of move

                                            success_move,move_pos,path=get_feasible_move_position(game_width, game_height, grid_size, A_star_start_position,A_star_end_position, test_objects,symbol_info)
                                            #success_move=False
                                            if success_move:
                                               #Execute the move option
                                               # print "Position", move_pos


                                                optionT.tLock.acquire()
                                                print("Sampling points in the initiation set of next option")
                                                time.sleep(1)
                                                print("Success... Found a feasible trajectory")
                                                pygame.draw.circle(screen,BLACK,(move_pos,player.y),10)
                                                pygame.display.flip()
                                                time.sleep(3)
                                                option = ('moveto',move_pos)
                                                optionT.execState = ExecState.busy
                                                #print "option=",option
                                                option_text = font.render(option[0] + ': ' + str(option[1]), True, (0, 0, 0))
                                                player.rect.centerx = option[1]
                                                player.update()
                                               # print("Moving")
                                                #-----------------------------------------------------------------------------------------------------------#
                                                # update background (background and desk)
                                                # update background (background and desk)
                                                screen.blit(background, (0, 0))
                                                screen.blit(desk.surf, desk.rect)


                                                objs.update(player, cursor)
                                                bin.update(player, cursor)
                                                cursor.update(mousePos)
                                                screen.blit(player.halo, player.posHalo)
                                                for entity in all_sprites:
                                                    screen.blit(entity.surf, entity.rect)

                                                screen.blit(cursor.hand, cursor.pos)

                                                screen.blit(now_trial, (30, win_h - text.get_height()-30))

                                                screen.blit(text,\
                                                            (win_w - text.get_width()-30, win_h - text.get_height()-15))
                                                screen.blit(option_text, \
                                                            (win_w/2 - option_text.get_width()/2, win_h - option_text.get_height() - 15))

                                                pygame.display.flip()
                                                optionT.worldState = data(player, objs)
                                                #optionT.tLock.release()

                                                # Execute the move option
                                                #optionT.tLock.acquire()

                                                option = Current_option
                                                print option
                                                time.sleep(2)
                                                #optionT.execState = ExecState.busy

                                               # time.sleep((5))
                                                optionT.tLock.release()



                                            if success_move:
                                                A_star_start_position=(player.y,player.x)
                                                A_star_end_position=(y,x)
                                                test_objects=[(0,0,100,100)]
                                                success_repick, path = get_trajectory(game_width, game_height, grid_size, A_star_start_position,A_star_end_position, test_objects)

                                                if success_repick:
                                                    option=previous_option
                                                    optionT.tLock.acquire()
                                                    optionT.execState = ExecState.busy
                                                    objs.sprites()[option[1]].rect.centerx = 0
                                                    objs.sprites()[option[1]].rect.centery = 0
                                                    objs.sprites()[option[1]].state = ObjState['inHand']
                                                    #path_ = [] # dict of dict
                                                    A_star_Path=[]
                                                    for i in path:
                                                        point_ = [i[1], i[0]]

                                                        A_star_Path.append(point_)

                                                    player.handFull = True

                                                    option_text = font.render(option[0] + ' object: ' + str(option[1]), True, (0, 0, 0))
                                                    optionT.worldState = data(player, objs)
                                                    time.sleep(2)
                                                    optionT.tLock.release()








                                            elif  not  success_move or not success_repick:
                                                tictac = int(time.time()*2) % 4
                                                if tictac == 0:
                                                    option_text = font.render('Replanning', True, (0, 0, 0))
                                                elif tictac == 1:
                                                    option_text = font.render('Replanning.', True, (0, 0, 0))
                                                elif tictac == 2:
                                                    option_text = font.render('Replanning..', True, (0, 0, 0))
                                                else:
                                                    option_text = font.render('Replanning...', True, (0, 0, 0))
                                                optionT.tLock.acquire()
                                                optionT.errorState = ErrorCode.obstacle

                                                #This stores the obstacle information
                                                optionT.errorInfo = failed_pick-1
                                                time.sleep(2)
                                                #-------------------------------------
                                                optionT.tLock.release()
                                                print 'Error: Cannot execute the low level motion planner because of obstacle'
                                                time.sleep(3)
#----------------------------------------------------------------------------------------------------------------------------------------------------
                                    else:
                                        optionT.tLock.acquire()
                                        optionT.errorState = ErrorCode.pick_too_far
                                        optionT.tLock.release()
                                        print 'Error: You are not Luffy with extendable arms'
                                else:
                                    optionT.tLock.acquire()
                                    optionT.errorState = ErrorCode.pick_in_bin
                                    optionT.tLock.release()
                                    print "Error: Don't dig in the bin."
                        else:
                            optionT.tLock.acquire()
                            optionT.errorState = ErrorCode.pick_too_many_objs
                            optionT.tLock.release()
                            print "Error: A bear can only have one corn at one time."
                    elif option[0] == 'place':
                        A_star_Path=[]
                        if player.handFull == True:
                            option_text = font.render(option[0] + ' object: ' + str(option[1]), True, (0, 0, 0))
                            if option[1] > 9 or option[1] < 0:
                                optionT.tLock.acquire()
                                optionT.errorState = ErrorCode.place_not_exist
                                optionT.tLock.release()
                                print 'Error: Learn better math dude.'
                            else:
                                dist = (bin.rect.centerx - player.x) ** 2 \
                                       + (bin.rect.centery - player.y) ** 2
                                dist = int(sqrt(float(dist)))
                                if dist < player.armLen:
                                    if objs.sprites()[option[1]].state == ObjState['inHand']:
                                        player.handFull = False
                                        objs.sprites()[option[1]].state = ObjState['inBin']
                                        objs.sprites()[option[1]].rect.centerx = bin.rect.centerx
                                        objs.sprites()[option[1]].rect.centery = bin.rect.centery
                                        objs.sprites()[option[1]].update(player, cursor)

                                        optionT.tLock.acquire()
                                        optionT.worldState = data(player, objs)
                                        optionT.tLock.release()

                                        curr_bin += 1
                                        #print 'done by option: ' + str(curr_bin)
                                        optionT.tLock.acquire()
                                      #  print optionT.worldState
                                        optionT.tLock.release()
                                        text = font.render('Done: ' + str(curr_bin) + ', Remaining: ' + str(max_obj - curr_bin),\
                                                           True, (0, 0, 0))

                                        if curr_bin == max_obj:
                                            currTime = time.time() - start_time
                                            text = font.render('Total time: ' + str(round(currTime, 2)) + 's', True, (0, 0, 0))
                                            print 'end by option'
                                            optionT.runningT = False
                                            gameover = True
                                    else:
                                        optionT.tLock.acquire()
                                        optionT.errorState = ErrorCode.place_on_table
                                        optionT.tLock.release()
                                        print "Error: Even Magneto can't move this obj on the table into the bin."
                                else:
                                    optionT.tLock.acquire()
                                    optionT.errorState = ErrorCode.place_too_far
                                    optionT.tLock.release()
                                    print "Error: You can't throw it."
                        else:
                            optionT.tLock.acquire()
                            optionT.errorState = ErrorCode.place_hand_empty
                            optionT.tLock.release()
                            print 'Error: Generating cans from ether... failed.'

                else:
                    key_presses = key_presses + 1
                    #print key_pressing
                    # hands empty, go and pick things up
                    if player.handFull == False:
                        for i in objs.sprites():
                            ## EVENT:
                            ## PICK AN OBJ UP
                            if i.state == ObjState['selected']:
                                ## record the move option first, if it exist.
                                ## buffered data goes to s
                                ## now data goes to s'
                                ## pick == false
                                if last_state[0]!=pos_buffer[0] or last_state[1]!=pos_buffer[1]:
                                    s = last_state
                                    o = 'move'
                                    r = round(last_release_t - last_event_t, 3) #reward
                                    s_prime = data(player, objs)
                                    #s_prime = pos_buffer + (0.0,)
                                    record.append((s, o, r, s_prime))
                                    print (s, o, r, s_prime)
                                    #update
                                    last_event_t = last_release_t
                                    last_state = s_prime

                                i.state = ObjState['inHand']
                                cursor.hand = cursor.close_hand
                                i.update(player, cursor)
                                player.handFull = True

                                now_time = time.time()
                                # record pick event
                                s = last_state
                                r = round(now_time - last_event_t,3) #reward
                                o = 'pick'
                                s_prime = data(player, objs)
                                #s_prime = s[0:-1]+(100.0, )
                                record.append((s, o, r, s_prime))
                                print (s, o, r, s_prime)
                                last_event_t = now_time
                                last_state = s_prime

                                # -- update world state here for option --

                    # hands full, you have to drop the thing
                    else:
                        if bin.selected == True:
                            for i in objs.sprites():
                                ## EVENT:
                                ## PUT AN OBJ DOWN
                                if i.state == ObjState['inHand']:
                                    ## record the MOVE option first, if it exist.
                                    ## buffered data goes to s
                                    ## now data goes to s'
                                    ## pick == true
                                    if last_state[0]!=pos_buffer[0] or last_state[1]!=pos_buffer[1]:
                                        s = last_state
                                        o = 'move'
                                        r = round(last_release_t-last_event_t, 3)  # reward
                                        # update the now place
                                        #i.update(player,cursor)
                                        #pos_buffer = data(player, objs)
                                        s_prime = data(player, objs)
                                        #s_prime = pos_buffer + (100.0,)
                                        record.append((s, o, r, s_prime))
                                        print(s, o, r, s_prime)
                                        last_event_t = last_release_t
                                        last_state = s_prime

                                    i.state = ObjState['inBin']
                                    cursor.hand = cursor.active_hand
                                    player.handFull = False
                                    i.inBin(cursor.center)
                                    curr_bin+=1

                                    now_time = time.time()
                                    # record place event
                                    s = last_state
                                    r = round(now_time-last_event_t, 3) #reward
                                    o = 'place'
                                    i.update(player, cursor)
                                    s_prime = data(player, objs)
                                    #s_prime =  pos_buffer + (0.0,)
                                    record.append((s, o, r, s_prime))
                                    print(s, o, r, s_prime)
                                    last_event_t = now_time
                                    last_state = s_prime

                                    text = font.render('Done: ' + str(curr_bin) + ', Remaining: ' + str(max_obj - curr_bin),\
                                                       True, (0, 0, 0))
                                    if curr_bin == max_obj:
                                        currTime = time.time() - start_time
                                        text = font.render('Total time: ' + str(round(currTime, 2)) + 's', True, (0, 0, 0))
                                        gameover = True
            elif event.type == QUIT:
                running = False

        # pointer hovering on top of one item?
        ptr_on_item = []
        for i in objs:
            if i.state == ObjState.selected:
                ptr_on_item.append(1)
                cursor.hand = cursor.five_fingers
            else:
                ptr_on_item.append(0)
        if sum(ptr_on_item) < 1 and cursor.hand != cursor.close_hand:
            cursor.hand = cursor.active_hand

        optionT.tLock.acquire()
        optionT.worldState = data(player, objs)
        optionT.tLock.release()

        # update background (background and desk)
        screen.blit(background, (0, 0))
        screen.blit(desk.surf, desk.rect)

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        objs.update(player, cursor)
        bin.update(player, cursor)
        cursor.update(mousePos)
        screen.blit(player.halo, player.posHalo)
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        screen.blit(cursor.hand, cursor.pos)

        screen.blit(now_trial, (30, win_h - text.get_height()-30))

        screen.blit(text,\
                    (win_w - text.get_width()-30, win_h - text.get_height()-15))
        screen.blit(option_text, \
                    (win_w/2 - option_text.get_width()/2, win_h - option_text.get_height() - 15))

        # Code to show the trajectory
        BLUE = (0, 0, 255)
        BLACK = (0, 0, 0)

        if (len(A_star_Path)!=0):

            pygame.draw.lines(screen, BLACK, False, A_star_Path, 5)

        pygame.display.flip()


        if gameover == True:

            screen.blit(instruction, (win_w/2 - text.get_width()/2, win_h/2 - text.get_height()/2))

        pygame.display.flip()


        if gameover==True and write_data==True:
            running = False


    return record, currTime, key_presses

if __name__=='__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i, %i' % (200, 200)
    win_w = 1400
    win_h = 700
    pygame.init()
    screen = pygame.display.set_mode((win_w, win_h))

    win_size = screen.get_size()

    clock = pygame.time.Clock()
    running = True
    optionT = OptionThread(10, 'Thread for input options')
    optionT.start()
    # input option manually
    #moT = ManualOptionThread(20, 'Thread for input option manually', optionT)
    #moT.start()
    aoT = OptionTestThread(30, 'Thread for input option automatically', optionT)
    aoT.start()

    runGame(screen, 'auto')
    print 'all done'
    #moT.runningT = False
    optionT.runningT = False

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
