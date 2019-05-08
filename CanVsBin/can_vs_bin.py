import pygame
from pygame.locals import *
import time
import pickle
import os

from human import Player
from item import *
from cursor import Cursor
from enum import Enum


class PositionType(Enum):
    full_rand = 1
    centered_random = 2
    centered_static = 3


def data(player, objs):
    pos = (float(player.x), float(player.y), player.handFull)
    for i in objs:
        if i.state == ObjState['inHand']:
            obj_state = True
        else:
            obj_state = False
        pos = pos + (float(i.x), float(i.y), obj_state)
    return pos

def runGame(screen, title):

    debug = True
    prompt = False
    write_data = True

    # initialize pygame
    #pygame.init()

    # sound effects are from https://freesound.org/
    # credit to https://freesound.org/people/jomse/sounds/428663/
    effect_dump = pygame.mixer.Sound('428663__jomse__pickupbook4.wav')
    # credit to https://freesound.org/people/dkiller2204/sounds/422971/
    effect_pick = pygame.mixer.Sound('422971__dkiller2204__sfxkeypickup.wav')

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

    all_sprites = pygame.sprite.Group()

    desk = Desk(desk_x, desk_y, desk_w, desk_h)
    #all_sprites.add(desk)

    # create our 'player'; right now he's just a rectangle
    player = Player(win_w, win_h, desk_y, desk_h, dist2Desk, arm_len)
    all_sprites.add(player)

    mouse_start_pos = pygame.mouse.get_pos()
    cursor = Cursor(player, mouse_start_pos)
    screen.blit(cursor.hand, cursor.pos)

    objs = pygame.sprite.OrderedUpdates()
    #the number of the object
    no_objs = 0

    pos_type = PositionType(2)

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
            # print pos_type
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

    #game loop
    while running:

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
                    text = font.render('Done: ' + str(curr_bin) + ', Remaining: ' + str(max_obj - curr_bin), \
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
            elif event.type == KEYUP:
                key_presses = key_presses + 1
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


        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        objs.update(player, cursor)
        bin.update(player, cursor)
        cursor.update(mousePos)
        screen.blit(player.halo, player.posHalo)
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        #screen.blit(player.surfHalo, player.posHalo)

        screen.blit(cursor.hand, cursor.pos)

        screen.blit(now_trial, (30, win_h - text.get_height()-30))

        screen.blit(text,\
                    (win_w - text.get_width()-30, win_h - text.get_height()-15))

        if gameover == True:
            screen.blit(instruction, (win_w/2 - text.get_width()/2, win_h/2 - text.get_height()/2))

        #if countdown == True:
        #    if start == True:
        #        timer_text = font.render(str(round(time.time() - start_time, 2)) + 's', True, (0, 0, 0))
        #    else:
        #        timer_text = font.render('0s', True, (0, 0, 0))
        #else:
        #    timer_text = font.render(' ', True, (0, 0, 0))
        #screen.blit(timer_text,\
        #            (win_w - text.get_width() - 30, win_h - text.get_height() - 70))

        pygame.display.flip()

        #if event_flag==True:
        #    s_prime = data(player, objs)
        #    record.append((s, o, r, s_prime))
        #    event_flag = False
        #    print (s, o, r, s_prime)

        if gameover==True and write_data==True:
            # f = open('raw_record_C.p', 'a')

            running = False

    # end of the game

    #waiting = True
    #while waiting:
    #    for event in pygame.event.get():
    #        if event.type == KEYDOWN:
    #            if event.key == K_ESCAPE:
    #                #pygame.quit()
    #
    #                waiting = False

    return record, currTime, key_presses

if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i, %i' % (200, 200)
    win_w = 1400
    win_h = 700
    pygame.init()
    screen = pygame.display.set_mode((win_w, win_h))

    win_size = screen.get_size()

    runGame(screen, 'auto')
