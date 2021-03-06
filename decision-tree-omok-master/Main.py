import pygame
from pygame.locals import *
import CGameManager

def Main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((600, 600), 0, 0)
    pygame.display.set_caption('Omok')
    GameManager = CGameManager.CGameManager(screen)

    manual_mode = False
    if manual_mode:
        while True:
            for event in pygame.event.get():
                if (pygame.QUIT == event.type):
                    return

                if (pygame.KEYDOWN == event.type):
                    if (pygame.K_ESCAPE == event.key):
                        exit()
                    pass

                if (pygame.MOUSEBUTTONDOWN == event.type):
                    print(event.pos)
                    GameManager.MouseDownEvent(event)

            GameManager.UpdateScreen()
    else:
        while True:
            for event in pygame.event.get():
                if (pygame.QUIT == event.type):
                    return

                if (pygame.KEYDOWN == event.type):
                    if (pygame.K_ESCAPE == event.key):
                        exit()
                    pass
                if (pygame.MOUSEBUTTONDOWN == event.type):
                    print(event.pos)
                    GameManager.SimulationEvent()

            GameManager.UpdateScreen()







if __name__ == '__main__':
    Main()