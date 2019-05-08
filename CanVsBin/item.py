import pygame
from pygame.locals import *
from math import sqrt
import random
from enum import Enum
from tool import spherical as sphe

class ObjState(Enum):
    unknown = -1
    onTable = 0
    selected = 1
    inHand = 2
    inBin = 3

class Desk(pygame.sprite.Sprite):
    def __init__(self, desk_x, desk_y, desk_w, desk_h):
        super(Desk, self).__init__()
        self.surf = pygame.Surface((desk_w, desk_h))
        #self.surf.set_alpha(100)
        self.surf.fill((248, 224, 194))
        self.rect = self.surf.get_rect(
            topleft=(desk_x, desk_y)
        )

class Bin(pygame.sprite.Sprite):
    armLen = 200
    binFull = False
    size = 60
    selected = False

    def __init__(self, bin_x, bin_y, bin_w, bin_h, arm_len=200):
        super(Bin, self).__init__()
        self.armLen = arm_len
        self.surf = pygame.Surface((bin_w, bin_h))
        self.surf.set_alpha(100)
        self.surf.fill((100, 0, 00))
        self.rect = self.surf.get_rect(
            topleft=(bin_x, bin_y)
        )

    def update(self, player, cursor):
        # the distance between the player (center) and the
        dist = (self.rect.centerx - player.x) ** 2 \
               + (self.rect.centery - player.y) ** 2
        dist = int(sqrt(float(dist)))
        # object is reachable
        if dist < self.armLen:
            #dist2 = (self.rect.centerx - mouse_pos[0]) ** 2 \
            #        + (self.rect.centery - mouse_pos[1]) ** 2
            #dist2 = int(sqrt(float(dist2)))
            dist2 = abs(self.rect.centerx - cursor.center[0]) < self.size/2 and\
                    abs(self.rect.centery - cursor.center[1]) < self.size/2
            # reach the object by mouse
            if dist2 and player.handFull == True:
                self.surf.fill((0, 100, 255))
                self.selected = True
                # there is no way to return values from Group.update()
            # still far away
            else:
                self.selected = False
                self.surf.fill((0, 0, 100))
        else:
            self.selected = False
            self.surf.fill((100, 0, 0))

class Obj(pygame.sprite.Sprite):
    x = 0
    y = 0
    size = 20
    armLen = 200
    no = -1
    state = ObjState['onTable']
    #selected = False
    player = None

    # some color hint, in general:
    # true: change color, from red to green
    # false: does not change color
    # if the pointer is hovering on top of the obj
    select_prompt = False
    # if the obj is reachable
    range_prompt = False

    def __init__(self, x, y, no=-1, size=20, arm_len=200,color=(255,0,0)):
        super(Obj, self).__init__()
        self.armLen = arm_len
        self.size = size
        self.surf = pygame.Surface((self.size, self.size))

        #self.surf.fill((255, 0, 0))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=(x, y))
        self.no = no
        self.x = x
        self.y = y

    def inBin(self, pos):
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

    def update(self, player, cursor):
        if self.state == ObjState['onTable'] or self.state == ObjState['selected']:
            # the distance between the player (center) and the
            dist = (self.rect.centerx - player.x)**2\
                   + (self.rect.centery - player.y)**2
            dist = int(sqrt(float(dist)))
            # object is reachable
            if dist < self.armLen:
                dist2 = (self.rect.centerx - cursor.center[0]) ** 2 \
                       + (self.rect.centery - cursor.center[1]) ** 2
                dist2 = int(sqrt(float(dist2)))
                # reach the object by mouse
                if dist2 < 20 and player.handFull==False:
                    if self.range_prompt == True and self.select_prompt == True:
                        self.surf.fill((0, 255, 0))
                    self.state = ObjState['selected']
                    #there is no way to return values from Group.update()
                # still far away
                else:
                    self.state = ObjState['onTable']
                    if self.range_prompt == True:
                        self.surf.fill((0, 100, 0))
            else:
                self.surf.fill((255, 0, 0))
        elif self.state == ObjState['inHand']:
            self.surf.fill((0,100,0))
            # self.rect.centerx = cursor.center[0]
            # self.rect.centery = cursor.center[1]
            self.rect.centerx = 30
            self.rect.centery = 30
        #ObjState['inBin']
        else:
            # Now you are dead. I'm just kidding.
            pass

        self.x = self.rect.centerx
        self.y = self.rect.centery
