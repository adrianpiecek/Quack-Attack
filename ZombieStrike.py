import pygame
from random import randint
import spriteSheet
from itertools import cycle
import math

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
player_sheet_image = pygame.image.load("Assets/player_run_sheet.png").convert_alpha()
ducky_walk_sheet_image = pygame.image.load("Assets/ducky_walk-sheet.png").convert_alpha()
ducky_idle_sheet_image = pygame.image.load("Assets/ducky_idle-sheet.png").convert_alpha()
ducky_walk_sprite_sheet = spriteSheet.SpriteSheet(ducky_walk_sheet_image)
ducky_idle_sprite_sheet = spriteSheet.SpriteSheet(ducky_idle_sheet_image)
ducky_walk_animation = [ducky_walk_sprite_sheet.get_image(i, 32, 32, 2) for i in range(6)]
ducky_idle_animation = [ducky_idle_sprite_sheet.get_image(i, 32, 32, 2) for i in range(2)]

scale = 2
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.walk = ducky_walk_animation
        self.idle = ducky_idle_animation
        self.image = self.idle[0]
        self.image_index = 0
        self.animation_speed = 0.1

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        self.speed = 3
        self.direction = 1
        movement = pygame.Vector2(0, 0)

    def update(self):
        keys = pygame.key.get_pressed()
        self.image_index += self.animation_speed

        if self.movement.length() > 0:
            self.movement.normalize_ip()
            self.rect.move_ip(self.movement * self.speed)
            if self.image_index >= len(self.walk):
                self.image_index = 0
            self.image = self.walk[int(self.image_index)] if self.direction == 1 else pygame.transform.flip(self.walk[int(self.image_index)], True, False).convert_alpha()
        else:
            if self.image_index >= len(self.idle):
                self.image_index = 0
            self.image = self.idle[int(self.image_index)] if self.direction == 1 else pygame.transform.flip(self.idle[int(self.image_index)], True, False).convert_alpha()

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.movement.y = -1
        if keys[pygame.K_s]:
            self.movement.y = 1
        if keys[pygame.K_a]:
            self.movement.x = -1
            self.direction = -1
        if keys[pygame.K_d]:
            self.movement.x = 1
            self.direction = 1
        if not keys[pygame.K_w] and not keys[pygame.K_s] and not keys[pygame.K_a] and not keys[pygame.K_d]:
            self.movement = pygame.Vector2(0, 0)
#player sprite
player = pygame.sprite.GroupSingle(Player())
#ground tile
ground_tile = pygame.image.load("Assets/ground_tile.png").convert_alpha()
tile_width, tile_height = ground_tile.get_size()
ground_tile = pygame.transform.scale(ground_tile, (tile_width*scale,tile_height*scale))
#barell sprite
barell_surf = pygame.image.load("Assets/barell.png").convert_alpha()
barell_width, barell_height = barell_surf.get_size()
barell_surf = pygame.transform.scale(barell_surf, (barell_width*scale,barell_height*scale))
barell_rect = barell_surf.get_rect(center=(100, 100))

text = pixel_font.render("Zombie Strike", True, WHITE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    for x in range(0, SCREEN_WIDTH, tile_width):
        for y in range(0, SCREEN_HEIGHT, tile_height):
            screen.blit(ground_tile, (x, y))    
    screen.blit(barell_surf, barell_rect)
    player.draw(screen)
    player.sprite.player_input()
    player.sprite.update()
    

    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)