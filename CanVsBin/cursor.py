import pygame
from pygame.locals import *
from math import sqrt, sin, cos, acos, asin, pi
from tool import spherical as sphe
from enum import Enum
import os

#cursor is from https://opengameart.org/content/pointers-part-5
class ObjState(Enum):
    unknown = -1
    pointAt = 0
    openPalm = 1
    grab = 2

class Cursor(pygame.sprite.Sprite):
    size = 50
    limit = 100
    pos = [0, 0]
    last_theta = 0
    center = [0, 0]
    player = None
    #state == True: hand full
    #state == False: hand empty
    full_state = False

    five_fingers = None
    active_hand = None
    close_hand = None
    hand = None

    def __init__(self, player, mouse_pos):
        super(Cursor, self).__init__()
        #self.surf = pygame.Surface((self.size*2, self.size*2))
        #self.surf.set_alpha(100)
        #self.surf.fill((255,255,255))

        #pygame.draw.circle(self.surf, (0, 0, 0), (self.size, self.size), self.size)

        self.player = player
        self.limit = player.armLen

        mouse2player = sphe([self.player.x, self.player.y], mouse_pos)
        if mouse2player[0] > self.limit:
            self.center[0] = self.player.x + int(self.limit * cos(mouse2player[1]))
            self.center[1] = self.player.y + int(self.limit * sin(mouse2player[1]))
        else:
            self.center[0] = mouse_pos[0]
            self.center[1] = mouse_pos[1]

        self.pos[0] = self.center[0] - self.size
        self.pos[1] = self.center[1] - self.size

        cwd = os.path.dirname(os.path.realpath(__file__))
        self.handRect = pygame.Rect(self.pos, (self.size, self.size))
        self.five_fingers = pygame.image.load(cwd+"/five_fingers.png").convert_alpha()
        self.five_fingers = pygame.transform.scale(self.five_fingers, (self.size, self.size))
        self.active_hand = pygame.image.load(cwd+"/active_hand.png").convert_alpha()
        self.active_hand = pygame.transform.scale(self.active_hand, (self.size, self.size))
        self.close_hand = pygame.image.load(cwd+"/close_hand.png").convert_alpha()
        self.close_hand = pygame.transform.scale(self.close_hand, (self.size, self.size))
        self.hand = self.active_hand

    def update(self, mouse_pos):
        v_max = 15.0

        mouse2cur = sphe(self.center, mouse_pos)
        mouse2player = sphe([self.player.x, self.player.y], mouse_pos)
        cur2player = sphe([self.player.x, self.player.y], self.center)

        if mouse2player[0] < self.limit:
            # on target
            if mouse2cur[0] < 2:
                pass
            # still far
            elif mouse2cur[0] > 20:
                self.center[0] = self.center[0] + int(v_max * cos(mouse2cur[1]))
                self.center[1] = self.center[1] - int(v_max * sin(mouse2cur[1]))
            # getting close, slow down
            else:
                self.center[0] = self.center[0] + int(mouse2cur[0] * cos(mouse2cur[1]))
                self.center[1] = self.center[1] - int(mouse2cur[0] * sin(mouse2cur[1]))
        #reach the boundary
        else:
            # still far
            if cur2player[0] < self.limit - 20:#self.limit-3:
                self.center[0] = self.center[0] + int(v_max * cos(mouse2cur[1]))
                self.center[1] = self.center[1] - int(v_max * sin(mouse2cur[1]))
            # close to boundary, slow down
            elif cur2player[0] < self.limit-3:
                v = self.limit - cur2player[0]
                self.center[0] = self.center[0] + int(v * cos(mouse2cur[1]))
                self.center[1] = self.center[1] - int(v * sin(mouse2cur[1]))
                new_cur2player = sphe([self.player.x, self.player.y], self.center)
                if new_cur2player[0] > self.limit:
                    self.center[0] = self.player.x + int(self.limit * cos(mouse2player[1]))
                    self.center[1] = self.player.y - int(self.limit * sin(mouse2player[1]))
            #move along the boundary
            elif cur2player[0] < self.limit:
                #cur2player: [dis, theta]
                cursor_theta = cur2player[1]
                if cur2player[0] < 0.0001:
                    cur2player[0] += 0.0001
                if mouse2player[0] < 0.0001:
                    mouse2player[0] += 0.0001

                # delta (angle) between two lines (cursor to playter vs. mouse to player)
                # the angle is calculated by vectors
                # cos(theta) = (\vec{u}*\vec{v}/||u||*||v||)
                #cos_delta  = (self.center[0]-self.player.x)*(mouse_pos[0]-self.player.x)
                #cos_delta += (self.center[1]-self.player.y)*(mouse_pos[1]-self.player.y)
                #cos_delta  = cos_delta/(cur2player[0] * mouse2player[0])
                ux = self.center[0] - self.player.x
                vx = mouse_pos[0] - self.player.x
                uy = self.center[1] - self.player.y
                vy = mouse_pos[1] - self.player.y
                cos_delta = ((ux*vx)+(uy*vy))/(sqrt(ux**2+uy**2)*sqrt(vx**2+vy**2))
                #### Error is here!
                # print 'ux, vx, uy, vy: ',
                # print ux, vx, uy, vy,
                # print ' cur2player + mouse2player: ',
                # print cur2player[0], mouse2player[0],
                # print ' cos_delta: ',
                # print cos_delta,
                if cos_delta >= 1.0:
                    abs_delta = 0.0
                    # print ' ***acos(cos_delta)',
                    # print ' error***'
                else:
                    # print ' acos(cos_delta) ',
                    # print acos(cos_delta)
                    abs_delta = acos(cos_delta)  # type: float
                delta = mouse2player[1] - cur2player[1]
                if delta > pi:
                    delta = delta - 2*pi
                if delta < -pi:
                    delta = 2 * pi + delta

                omega = float(v_max)/float(self.limit)
                if abs_delta < pi/32:
                    pass
                # on target
                else:
                    # delta > 0, counter-clockwise
                    if delta > 0:
                        cursor_theta += omega
                    # delta < 0, clockwise
                    else:
                        cursor_theta -= omega
                    self.center[0] = self.player.x + int(self.limit * cos(cursor_theta))
                    self.center[1] = self.player.y - int(self.limit * sin(cursor_theta))
            # in case the cursor is out side the boundary
            # (left the mouse not moving, moving the player position only will trigger this bug)
            # solution: keep the y, change the x accordingly
            else:
                y = self.center[1] - self.player.y
                new_x = int(sqrt(self.limit**2-y**2))
                # on the right
                if self.center[0] > self.player.x:
                    pass
                # on the left
                else:
                    new_x = -new_x
                self.center[0] = self.player.x + new_x

        # for screen recording only
        self.center[0] = self.player.x
        self.center[1] = self.player.y

        self.pos = [self.center[0]-self.size/2, self.center[1]-self.size/2]
