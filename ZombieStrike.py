import pygame
import random
import spriteSheet
from itertools import cycle
import math
import resourceManager

# Inicjalizacja Pygame
pygame.init()
pygame.mixer.init()

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

resourceManager = resourceManager.ResourceManager()

ducky_walk_animation = resourceManager.load_animation("Assets/ducky_walk-sheet.png", 25, 28, 6, 2)
ducky_idle_animation = resourceManager.load_animation("Assets/ducky_idle-sheet.png", 25, 28, 2, 2)
glock_shoot_animation = resourceManager.load_animation("Assets/guns/glock [64x32]/glock [SHOOT].png", 39, 31, 12, 1)
ducky_damage_sound = pygame.mixer.Sound("Assets/sounds/ducky_damage.wav")
bullet_image = resourceManager.load_image("Assets/guns/bullet.png")
shoot_sound = pygame.mixer.Sound("Assets/sounds/shoot.wav")
shoot_sound.set_volume(0.4)
zombie_walk_animation = resourceManager.load_animation("Assets/zombie_run-sheet.png", 23, 23, 7, 2)
zombie_death_sound = pygame.mixer.Sound("Assets/sounds/zombie_death.wav")
zombie_death_sound.set_volume(0.8)
background_music = pygame.mixer.Sound("Assets/sounds/doom theme.mp3")
background_music.play(-1)

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

        self.health = 100
        self.speed = 4
        self.direction = 1
        self.movement = pygame.Vector2(0, 0)

    def update(self):
        self.image_index += self.animation_speed

        if self.movement.length() > 0:
            #self.rect.move_ip(self.movement * self.speed)
            if self.image_index >= len(self.walk):
                self.image_index = 0
            self.image = self.walk[int(self.image_index)] if self.direction == 1 else pygame.transform.flip(self.walk[int(self.image_index)], True, False).convert_alpha()
        else:
            if self.image_index >= len(self.idle):
                self.image_index = 0
            self.image = self.idle[int(self.image_index)] if self.direction == 1 else pygame.transform.flip(self.idle[int(self.image_index)], True, False).convert_alpha()

    def player_input(self):
        keys = pygame.key.get_pressed()
        self.movement = pygame.Vector2(0, 0)
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
        if self.movement.x != 0 and self.movement.y != 0:
            self.movement *= 0.77 # mathematicly accurate normalization (0.707) felt too slow when moving diagonally

    def get_position(self):
        return self.rect.center

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        self.image = bullet_image
        self.angle = direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=position)
        self.direction = direction
        self.speed = 15
    
    def update(self):  
        self.rect.move_ip(self.direction * self.speed)
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()
            player_bullets.remove(self)

class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.shoot_anim = glock_shoot_animation
        self.image = self.shoot_anim[0]
        self.flipped_image = pygame.transform.flip(self.shoot_anim[0], True, False).convert_alpha()
        self.rect = self.image.get_rect(midleft=player.sprite.get_position()+pygame.Vector2(0, 10))
        self.fire_rate = 0.1
        self.last_shot = 0

    def shoot(self,direction):
        bullet = Bullet(self.rect.center, direction)
        bullet_group.add(bullet)
        player_bullets.append(bullet)
        shoot_sound.play()

    def update(self):
        self.rect.midleft = player.sprite.get_position() +pygame.Vector2(-10, 13)
        mouse_pos = pygame.mouse.get_pos()
        player_pos = player.sprite.get_position()
        direction = pygame.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]) # vector from player to mouse
        angle = direction.angle_to(pygame.Vector2(1, 0)) # angle between direction and x axis

        if angle > 0: 
            self.rect.y -= self.rect.height/4

        if mouse_pos[0] < player_pos[0]: #aiming left
            self.image = pygame.transform.rotate(pygame.transform.flip(self.shoot_anim[0], False, True).convert_alpha(), angle).convert_alpha()
            self.rect.x -= self.rect.width/2
        elif mouse_pos[0] > player_pos[0]: #aiming right
            self.image = pygame.transform.rotate(self.shoot_anim[0], angle).convert_alpha()

        if pygame.mouse.get_pressed()[0]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.fire_rate * 1000:
                self.shoot(direction.normalize())
                self.last_shot = current_time
            
class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.walk = zombie_walk_animation
        self.image = self.walk[0]
        self.image_index = 0
        self.animation_speed = 0.1

        self.health = 20

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

        self.speed = 2
        self.direction = pygame.Vector2(0, 0)

    def update(self):
        self.image_index += self.animation_speed
        if self.image_index >= len(self.walk):
            self.image_index = 0
        self.image = self.walk[int(self.image_index)]

        player_pos = player.sprite.get_position()
        self.direction = pygame.Vector2(player_pos[0] - self.rect.center[0], player_pos[1] - self.rect.center[1])
        self.direction = self.direction.normalize()
        self.rect.move_ip(self.direction * self.speed * random.uniform(0.80, 1.20))

        if self.rect.colliderect(player.sprite.rect):
            ducky_damage_sound.play()
            player.sprite.health -= 10
            self.kill()
        for bullet in bullet_group:
            if self.rect.colliderect(bullet.rect):
                self.health -= 10
                bullet.kill()
                player_bullets.remove(bullet)
        if self.health <= 0:
            self.kill()
            zombie_death_sound.play()

def zombieSpawn(delay=15):
    zombie = Zombie()
    if pygame.time.get_ticks() % delay == 0:
        zombie_group.add(zombie)

#player sprite
player = pygame.sprite.GroupSingle(Player())
gun = pygame.sprite.GroupSingle(Gun())
bullet_group = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

display_scroll = [0,0]
player_bullets = []

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

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]:
        display_scroll[0] -= player.sprite.speed * -player.sprite.movement.x
        for bullet in player_bullets:
            bullet.rect.x += player.sprite.speed
        for zombie in zombie_group:
            zombie.rect.x += player.sprite.speed
    if keys[pygame.K_d]:
        display_scroll[0] += player.sprite.speed * player.sprite.movement.x
        for bullet in player_bullets:
            bullet.rect.x -= player.sprite.speed
        for zombie in zombie_group:
            zombie.rect.x -= player.sprite.speed
    if keys[pygame.K_w]:
        display_scroll[1] -= player.sprite.speed * -player.sprite.movement.y
        for bullet in player_bullets:
            bullet.rect.y += player.sprite.speed
        for zombie in zombie_group:
            zombie.rect.y += player.sprite.speed
    if keys[pygame.K_s]:
        display_scroll[1] += player.sprite.speed * player.sprite.movement.y
        for bullet in player_bullets:
            bullet.rect.y -= player.sprite.speed
        for zombie in zombie_group:
            zombie.rect.y -= player.sprite.speed

    # for x in range(0, SCREEN_WIDTH, tile_width):
    #     for y in range(0, SCREEN_HEIGHT, tile_height):
    #         screen.blit(ground_tile, (x-display_scroll[0], y-display_scroll[1])) 



    screen.fill((125,125,125))
    screen.blit(barell_surf, (barell_rect.x - display_scroll[0], barell_rect.y - display_scroll[1]))
    player.draw(screen)
    player.sprite.player_input()
    player.sprite.update()

    bullet_group.draw(screen)
    bullet_group.update()


    zombieSpawn()
    zombie_group.draw(screen)
    zombie_group.update()

    gun.draw(screen)
    gun.sprite.update()

    

    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)