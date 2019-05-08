# import the pygame module
import pygame
import platform
import os

# import random for random numbers!
from math import sqrt

# import pygame.locals for easier access to key coordinates
from pygame.locals import *

from enum import Enum

#class PlayerState(Enum):
#    empty = 0
#    full = 1

class Player(pygame.sprite.Sprite):
    x = 0
    y = 0
    xsize = 64
    ysize = 64
    win_w = 0
    win_h = 0
    armLen = 200
    speed = 10
    handFull = False
    posHalo = (0, 0)

    def __init__(self, w, h, desk_y, desk_h, dist_desk, arm_len):
        super(Player, self).__init__()

        # Linux
        if platform.system() == 'Linux':
            self.speed = 1
        # Mac OS
        elif platform.system() == 'Darwin':
            self.speed = 10
        # Windows (haven't tried yet)
        else:
            self.speed = 10

        self.win_w = w
        self.win_h = h
        self.armLen = arm_len

        self.x = w/2
        self.y = desk_y + desk_h + dist_desk + self.ysize/2
        self.surf = pygame.Surface((self.xsize, self.ysize))
        self.surf.fill((0, 0, 255))
        self.rect = self.surf.get_rect(center = (self.x, self.y))

        #self.surfHalo = pygame.Surface((self.armLen*2, self.armLen*2))
        self.posHalo = (self.x - self.armLen, self.y - self.armLen)
        #self.surfHalo.set_alpha(50)
        #pygame.draw.circle(self.surfHalo, (0, 255, 0), (self.armLen, self.armLen), self.armLen)

        self.haloRect = pygame.Rect(self.posHalo, (self.armLen*2, self.armLen*2))
        cwd = os.path.dirname(os.path.realpath(__file__))
        self.halo = pygame.image.load(cwd+"/range.png").convert_alpha()
        #self.halo = pygame.transform.scale(self.halo, self.haloRect.size)
        #self.halo = self.halo.convert()


    def update(self, pressed_keys = None):
        # can only move right and left
        #if pressed_keys[K_UP]:
        #    self.rect.move_ip(0, -5)
        #if pressed_keys[K_DOWN]:
        #    self.rect.move_ip(0, 5)
        if pressed_keys != None:
            if pressed_keys[K_LEFT] or pressed_keys[K_a]:
                self.rect.move_ip(-self.speed, 0)
            if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
                self.rect.move_ip(self.speed, 0)

        # Keep player within the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.win_w:
            self.rect.right = self.win_w
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= self.win_h:
            self.rect.bottom = self.win_h

        ## Keep the player from the desk
        #if self.rect.left < 0:
        #    self.rect.left = 0
        #elif self.rect.right > win_w:
        #    self.rect.right = win_w
        #if self.rect.top <= 0:
        #    self.rect.top = 0
        #elif self.rect.bottom >= win_h:
        #    self.rect.bottom = win_h

        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.posHalo = (self.x-self.armLen, self.y-self.armLen)