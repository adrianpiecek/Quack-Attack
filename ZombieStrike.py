import pygame
from random import randint


# Inicjalizacja Pygame
pygame.init()

# Parametry gry
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Ekran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Strike")
clock = pygame.time.Clock()
pixel_font = pygame.font.Font("Assets/font/ByteBounce.ttf", 32)

scale = 2
#player sprite
player = pygame.image.load("Assets/player.png")
player_width, player_height = player.get_size()
player = pygame.transform.scale(player, (player_width*scale,player_height*scale))
player_x_pos = SCREEN_WIDTH/2 - player_width
player_y_pos = SCREEN_HEIGHT/2 - player_height/2
#ground tile
ground_tile = pygame.image.load("Assets/ground_tile.png")
tile_width, tile_height = ground_tile.get_size()
ground_tile = pygame.transform.scale(ground_tile, (tile_width*scale,tile_height*scale))
#barell sprite
barell = pygame.image.load("Assets/barell.png")
barell_width, barell_height = barell.get_size()
barell = pygame.transform.scale(barell, (barell_width*scale,barell_height*scale))

text = pixel_font.render("Zombie Strike", True, WHITE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    for x in range(0, SCREEN_WIDTH, tile_width):
        for y in range(0, SCREEN_HEIGHT, tile_height):
            screen.blit(ground_tile, (x, y))    
    screen.blit(player, (player_x_pos, player_y_pos))
    screen.blit(barell, (100, 100))
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)