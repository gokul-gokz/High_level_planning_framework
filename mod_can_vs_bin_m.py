import pygame
from pygame.locals import *
import time
import pickle

from human import Player
from item import *
from cursor import Cursor
from a_star_plan import execute_planner


def data(player, objs):
    pos = (float(player.x), float(player.y), player.handFull)
    for i in objs:
        if i.state == ObjState['inHand']:
            obj_state = True
            print "Position of object inHand", i.x, i.y
        else:
            obj_state = False
        pos = pos + (float(i.x), float(i.y), obj_state)
    return pos

debug = True
prompt = False
write_data = True

# initialize pygame
pygame.init()

# sound effects are from https://freesound.org/
# credit to https://freesound.org/people/jomse/sounds/428663/
effect_dump = pygame.mixer.Sound('428663__jomse__pickupbook4.wav')
# credit to https://freesound.org/people/dkiller2204/sounds/422971/
effect_pick = pygame.mixer.Sound('422971__dkiller2204__sfxkeypickup.wav')
# credit to https://freesound.org/people/Breviceps/sounds/445978/
#effect_error = pygame.mixer.Sound('445978__breviceps__error-signal-2.wav')

# create the screen object
# here we pass it a size of 800x600
win_w = 1400; win_h = 700
desk_w = 1300; desk_h = 250
## desk position (center), desk size
dist2Desk = 10
desk_x = (win_w-desk_w)/2; desk_y = (win_h-desk_h-64-dist2Desk)/4

## number of current bins and maximum bins
## one obj in
max_obj = 8; column = 3
#start with nothing in the bin
curr_bin = 0;

## default arm length
arm_len = 300

font = pygame.font.SysFont("comicsansms", 36)
text = font.render('Start on your call', True, (0, 0, 0))

## mouse position
mousePos = pygame.mouse.get_pos()

screen = pygame.display.set_mode((win_w, win_h))

background = pygame.Surface(screen.get_size())
background.fill((255, 255, 255))

all_sprites = pygame.sprite.Group()

desk = Desk(desk_x, desk_y, desk_w, desk_h)
#all_sprites.add(desk)

# create our 'player'; right now he's just a rectangle
player = Player(win_w, win_h, desk_y, desk_h, dist2Desk, arm_len)
all_sprites.add(player)

mouse_start_pos = pygame.mouse.get_pos()
cursor = Cursor(player, mouse_start_pos)
screen.blit(cursor.hand, cursor.pos)

objs = pygame.sprite.Group()
#the number of the object
no_objs = 0
objs_loc = []
###########################################################
###########################################################
##                   Object Placement                    ##
###########################################################
###########################################################

for i in range(max_obj+1):
    # don't place anything in the middle, it's for the bin

    # for bin
    if i == max_obj/2:
        size = 60
        x = desk_x + i * desk_w/(max_obj+1) + (desk_w/(max_obj+1)-size)/2
        y = desk_y + desk_h / 3 + (desk_h/3-size)/2
        bin = Bin(x, y, size, size, arm_len)
        all_sprites.add(bin)

    ## for placing blocks

    else:
        # placing cells

        # obj A placing
        if i==0:
            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            obj_A = Obj(x_right, y_top, no_objs, size, arm_len)
            #objs_loc.append((x_right, x_left, size, size))
            objs_loc.append((obj_A.rect.topleft[1], obj_A.rect.topleft[0], size, size))
            objs.add(obj_A)
            all_sprites.add(obj_A)
            objs.update(player, cursor)
            no_objs += 1
        # obj B placing
        elif i==1:
            i = 0
            size = 60
            y_cell = 1
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i+1, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom, "Object B"
            obj_B = Obj(x_right, y_top, no_objs, size, arm_len)
            print "my values : ", x_right, y_top
            print "top left : >>>>>>>>", obj_B.rect.topleft
            print "bottom left : >>>>>>>>", obj_B.rect.bottomleft
            print "bottom right : >>>>>>>>>", obj_B.rect.bottomright
            print "top right : >>>>>>>>>", obj_B.rect.topright
            objs_loc.append((obj_B.rect.topleft[1], obj_B.rect.topleft[0], size, size))
            objs.add(obj_B)
            all_sprites.add(obj_B)
            objs.update(player, cursor)
            no_objs += 1
            i = 1
        elif i ==2:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(375, 220, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
            objs.add(new_obj)
            all_sprites.add(new_obj)
            objs.update(player, cursor)
            no_objs += 1
        elif i ==3:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(580, 200, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
            objs.add(new_obj)
            all_sprites.add(new_obj)
            objs.update(player, cursor)
            no_objs += 1
        elif i ==5:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(840, 200, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
            objs.add(new_obj)
            all_sprites.add(new_obj)
            objs.update(player, cursor)
            no_objs += 1
        elif i ==6:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(1000, 300, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
            objs.add(new_obj)
            all_sprites.add(new_obj)
            objs.update(player, cursor)
            no_objs += 1
        elif i ==7:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(1100, 135, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
            objs.add(new_obj)
            all_sprites.add(new_obj)
            objs.update(player, cursor)
            no_objs += 1
        elif i ==8:

            size = 20
            y_cell = 0
            x_left = desk_x + i * desk_w / (max_obj + 1) + size
            x_right = desk_x + (i + 1) * desk_w / (max_obj + 1) - size
            y_top = desk_y + desk_h / 3 * y_cell + size
            y_bottom = desk_y + desk_h / 3 * (y_cell + 1) - size
            print "Obj", i, "x_left :", x_left, "x_right : ", x_right, "y_top : ", y_top, "y_bottom : ", y_bottom
            new_obj = Obj(1300, 145, no_objs, size, arm_len)
            objs_loc.append((new_obj.rect.topleft[1], new_obj.rect.topleft[0], size, size))
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

countdown = False

pygame.mouse.set_pos(win_w/2, win_h/2)
cursor.center = [win_w/2, win_h/2]

pressed_keys = 0
last_key = 0

global start_g
global goal_g
global path_seg

start_g = (0,0)
goal_g = (0,0)
path_seg = [[0,0],[1,1]]


#game loop
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            pressed_keys = event.key
        if event.type == KEYUP:
            pressed_keys = 0
        #if not pressed_keys in[97, 100, 275, 176]:
        #    pressed_keys = 0

        # Game start, start to count the time
        if start == False:
            mouse_now_pos = pygame.mouse.get_pos()
            mouseDist = sqrt((mouse_now_pos[0]-mouse_start_pos[0])**2 + (mouse_now_pos[1]-mouse_start_pos[1])**2)

            ## EVENT:bin
            ## GAME START
            if event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN or mouseDist > 10:
                last_state = data(player,objs)
                pos_buffer = last_state
                start_time = time.time()
                text = font.render('Done: ' + str(curr_bin) + ', Remaining: ' + str(max_obj - curr_bin), \
                                   True, (0, 0, 0))
                last_event_t = start_time
                last_release_t = start_time
                start = True
                record.append(round(start_time, 2))

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
        elif event.type == KEYUP:
            #print 'buffer updated'
            pos_buffer = data(player, objs)
            last_release_t = time.time()

        elif event.type == pygame.MOUSEMOTION:
            mousePos = pygame.mouse.get_pos()


        # Now you can do this only if you stop moving
        # pygame.key.get_pressed return all keyboard states as 0 or 1
        # no key being pressed means all states equal to 0
        elif event.type == pygame.MOUSEBUTTONDOWN\
                and sum(pygame.key.get_pressed())-pygame.key.get_pressed()[300]<=0\
                and event.button == 1:
            #print key_pressing
            # hands empty, go and pick things up
            if player.handFull == False:
                for i in objs.sprites():
                    ## EVENT:
                    ## PICK AN OBJ UP
                    if i.state == ObjState['selected']:
                        ## record the move option first, if it exist.
                        ## buffered  data goes to s
                        ## now data goes to s'
                        ## pick == false
                        if last_state[0]!=pos_buffer[0] or last_state[1]!= pos_buffer[1]:
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

                        #####################################
                        ## Planning Code
                        #####################################

                        mouse_now_pos = pygame.mouse.get_pos()

                        start_point = (player.y, player.x)
                        goal_pose = (i.rect.topleft[1], i.rect.topleft[0])

                        plan_dist = sqrt((mouse_now_pos[0] - start_point[0]) ** 2 + (mouse_now_pos[1] - start_point[1]) ** 2)
                        print "player_pose : ", player.x, player.y
                        print "goal_pose : ", goal_pose[1], goal_pose[0]
                        print "plan_dist : ", plan_dist

                        ##########################################
                        ### A-star search Algorithm
                        ##########################################

                        game_width = 1400 #100
                        game_height = 700 #50
                        grid_size = 10
                        success = False
                        print "robot_location : ", start_point
                        #object_loc = (11, 50)

                        test_objects = [(207, 104, 60, 60)]  # List of objects position in terms of rectangles (x, y, height, width)

                        # objs_loc has all the objects positions

                        ## calling a-star plan
                        success, path = execute_planner(game_width, game_height, grid_size, start_point, goal_pose, test_objects)

                        if success:
                            print 'path =>>', path, '<='

                        # Convert mihir's path to pygame input path
                        path_ = [] # dict of dict
                        for i in path:
                            point_ = [i[1], i[0]]
                            path_.append(point_)

                        print "path_ =>>", path_

                        global start_g
                        global goal_g
                        global path_seg

                        start_g = (start_point[1], start_point[0])
                        goal_g = (goal_pose[1], goal_pose[0])
                        path_seg = path_

                        #BLUE = (0, 0, 255)
                        #BLACK = (0, 0, 0)
                        #pygame.draw.line(screen, BLUE, [player.x, player.y], [mouse_now_pos[0], mouse_now_pos[1]], 10)
                        # Draw lines segments
                        #pygame.draw.lines(screen, BLACK, False, path_, 10)
                        #pygame.display.flip()
                        #pygame.display.update()

                        ########################################

                        #i.update(player, cursor)
                        player.handFull = True

                        now_time = time.time()
                        # record pick event
                        s = last_state
                        r = round(now_time - last_event_t, 3) #reward
                        o = 'pick'
                        s_prime = data(player, objs)
                        #s_prime = s[0:-1]+(100.0, )
                        record.append((s, o, r, s_prime))
                        print (s, o, r, s_prime)
                        last_event_t = now_time
                        last_state = s_prime

                        #soundtrack
                        effect_pick.play()

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
                                text = font.render('Total time: ' + str(round(currTime,2)) + 's', True, (0, 0, 0))
                                gameover = True
                            effect_dump.play()
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

    # update background (background and desk)
    screen.blit(background, (0, 0))
    screen.blit(desk.surf, desk.rect)


    #pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    objs.update(player, cursor)
    bin.update(player, cursor)
    cursor.update(mousePos)
    screen.blit(player.halo, player.posHalo)
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    #screen.blit(player.surfHalo, player.posHalo)gam

    screen.blit(cursor.hand, cursor.pos)

    screen.blit(text,\
                (win_w - text.get_width()-30, win_h - text.get_height()-30))

    #if countdown == True:
    #    if start == True:
    #        timer_text = font.render(str(round(time.time() - start_time, 2)) + 's', True, (0, 0, 0))
    #    else:
    #        timer_text = font.render('0s', True, (0, 0, 0))
    #else:
    #    timer_text = font.render(' ', True, (0, 0, 0))
    #screen.blit(timer_text,\
    #            (win_w - text.get_width() - 30, win_h - text.get_height() - 70))


    ###############################
    ###  Code for showing Path
    ###############################

    global start_g
    global goal_g
    global path_seg

    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    pygame.draw.lines(screen, BLACK, False, path_seg, 5)
    pygame.display.flip()

    #if event_flag==True:
    #    s_prime = data(player, objs)
    #    record.append((s, o, r, s_prime))
    #    event_flag = False
    #    print (s, o, r, s_prime)

    if gameover==True and write_data==True:
        f = open('record_jakub_comf.p', 'a')
        print record
        pickle.dump(record, f)
        f.close()
        running = False

# end of the game
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                waiting = False
