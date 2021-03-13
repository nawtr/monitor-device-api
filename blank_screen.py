import pygame

pygame.display.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
black = 0, 0, 0

is_running = True


def draw_blank_screen():
    global is_running
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                is_running = False
                break
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                is_running = False
                break
        screen.fill(black)
        pygame.display.update()


draw_blank_screen()
