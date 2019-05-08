import pygame
from pygame.locals import *
import time


def start(screen):
    font = pygame.font.SysFont('Arial', 240)
    clock = pygame.time.Clock()

    background = pygame.Surface(screen.get_size())
    background.fill((255, 255, 255))

    win_size = screen.get_size()
    pygame.mouse.set_pos(win_size[0]/2, win_size[1]/2)

    running = True
    i = 3
    cnt = 0
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        if i < 0:
            running = False
        else:
            text = font.render(str(i), True, (0, 0, 0))

            screen.blit(background, (0, 0))
            screen.blit(text,
                        (win_size[0]/2 - text.get_width()/2, win_size[1]/2 - text.get_height()/2))
            pygame.display.flip()
            if cnt < 1000:
                cnt += clock.tick(30)
            else:
                i -= 1
                cnt = 0


if __name__ == '__main__':
    pygame.init()
    win_size = (800, 600)
    screen = pygame.display.set_mode(win_size)
    start(screen)

    screen.fill(pygame.color.Color('white'))
    font = pygame.font.SysFont('Arial', 60)
    text = font.render('game starts here', True, (0, 0, 0))
    screen.blit(text,
                (win_size[0] / 2 - text.get_width() / 2, win_size[1] / 2 - text.get_height() / 2))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False