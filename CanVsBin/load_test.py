import pickle
import pygame
from pygame.locals import *
import sys
import time


class Thing(pygame.sprite.Sprite):
    surf = None
    def __init__(self, x, y):
        super(Thing, self).__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.set_alpha(80)
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(
            center=(x, y)
        )

    def update(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

f = open('raw_record.p', 'r')
plan = []
cnt = 0
pygame.init()

win_w = 1400/2 + 200
win_h = 700/2
screen = pygame.display.set_mode((win_w, win_h))

background = pygame.Surface(screen.get_size())
#background.set_alpha(0)
background.fill((255, 255, 255))
all_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsansms", 10)
s = []#font.render('', True, (0, 0, 0))
s_prime = []#font.render('', True, (0, 0, 0))
o = font.render('', True, (0,0,0))
loading = True
while loading:
    try:
        plan = pickle.load(f)
        print plan
        cnt = cnt+1
        print 'cnt: ' + str(cnt)
        # 1 human + some objs
        for i in range(len(plan[1][0])/3):
            new_th = Thing(plan[1][0][i*3]/2, plan[1][0][i*3+1]/2)
            all_sprites.add(new_th)

        screen.blit(background, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        #pygame.display.flip()

        i = 1
        running = True

        no_text = font.render('trial ' + str(cnt), True, (0,0,0))
        screen.blit(no_text, (win_w-100, 25))
        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    # exit the game
                    if event.key == K_ESCAPE:
                        for k in all_sprites:
                            k.kill()
                        running = False
                        #f.close()
                        loading = False
                        break

                    # go back
                    if event.key == K_LEFT:
                        i-=2
                        if i < 1:
                            i = 1
                    # end this trial
                    if event.key == K_DOWN:
                        i = len(plan)
                    #clock.tick(1000)
                    screen.blit(background, (0, 0))
                    print 'i=' + str(i)
                    if i < len(plan):
                        print plan[i]
                    if i < len(plan):
                        del s[:]
                        del s_prime[:]
                        j = 0
                        for k in all_sprites:
                            # update using s_prime
                            if plan[i][3][j*3] != plan[i][0][j*3] or plan[i][3][j*3+1] != plan[i][0][j*3+1] or plan[i][3][j*3+2] != plan[i][0][j*3+2]:
                                k.surf.fill((255, 0, 0))
                                x = plan[i][0]
                                s_str = '('+ str(int(x[j*3])) + ',' + str(int(x[j*3+1])) + ',' + str(x[j*3+2]) + ')'
                                s.append(font.render(s_str, True, (255, 0, 0)))
                                x = plan[i][3]
                                s_prime_str = '('+ str(int(x[j*3])) + ',' + str(int(x[j*3+1])) + ',' + str(x[j*3+2])  + ')'
                                s_prime.append(font.render(s_prime_str, True, (255, 0, 0)))
                            else:
                                k.surf.fill((0, 0, 0))
                                x = plan[i][0]
                                s_str = '(' + str(int(x[j * 3])) + ',' + str(int(x[j * 3 + 1])) + ',' + str(x[j*3+2])  + ')'
                                s.append(font.render(s_str, True, (0, 0, 0)))
                                x = plan[i][3]
                                s_prime_str = '(' + str(int(x[j * 3])) + ',' + str(int(x[j * 3 + 1])) + ',' + str(x[j*3+2])  + ')'
                                s_prime.append(font.render(s_prime_str, True, (0, 0, 0)))

                            k.update(plan[i][3][j*3]/2, plan[i][3][j*3+1]/2)
                            j+=1

                            #s = font.render(str(plan[i][0]), True, (0, 0, 0))
                            #s_prime = font.render(str(plan[i][3]), True, (0, 0, 0))
                            #o = font.render(plan[i][1],True, (0,0,0))


                        o = font.render(plan[i][1], True, (0,0,0))

                        for entity in all_sprites:
                            screen.blit(entity.surf, entity.rect)

                        for j in range(len(s)):
                            screen.blit(s[j], (25+ j*80, win_h - 80))
                            screen.blit(s_prime[j], (25 + j*80, win_h - 60))
                        screen.blit(o, (25, win_h - 40))

                        screen.blit(no_text, (win_w-100, 25))

                        pygame.display.flip()
                        i+=1
                    else:
                        for k in all_sprites:
                            k.kill()
                        running = False

    except EOFError:
        break

f.close()
#print len(plan)
