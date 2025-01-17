import pygame
import random
import spriteSheet
from itertools import cycle
import math
import resourceManager
import time
import sys

# Inicjalizacja Pygame
pygame.init()
pygame.mixer.init()

# Parametry gry
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# pixels from the edge of the screen where zombies can spawn
EXCLUDED_WIDTH, EXCLUDED_HEIGHT = 20, 20
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
HIGHLIGHT = (255, 255, 0)

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
zombie_death_sound.set_volume(0.95)
background_music = pygame.mixer.Sound("Assets/sounds/doom theme.mp3")
background_music.play(-1)

# random position but with excluded area
def random_position(screen_width, screen_height, excluded_width, excluded_height):
    allowed_areas = [
        # Górny obszar (nad wykluczoną strefą)
        (0, excluded_height, 0, screen_width),
        # Dolny obszar (pod wykluczoną strefą)
        (screen_height - excluded_height, screen_height, 0, screen_width),
        # Lewy obszar (na lewo od wykluczonej strefy)
        (excluded_height, screen_height - excluded_height, 0, excluded_width),
        # Prawy obszar (na prawo od wykluczonej strefy)
        (excluded_height, screen_height - excluded_height, screen_width - excluded_width, screen_width),
    ]
    
    # Wybierz losowy obszar
    area = random.choice(allowed_areas)
    y = random.randint(area[0], area[1])  # Wysokość (y)
    x = random.randint(area[2], area[3])  # Szerokość (x)
    return x, y

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
    def __init__(self, position, direction, damage):
        super().__init__()
        self.image = bullet_image
        self.angle = direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=position)
        self.direction = direction
        self.speed = 15
        self.damage = damage
    
    def update(self):  
        self.rect.move_ip(self.direction * self.speed)
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()
            player_bullets.remove(self)

class Gun(pygame.sprite.Sprite):
    def __init__(self, damage=10):
        super().__init__()
        self.shoot_anim = glock_shoot_animation
        self.image = self.shoot_anim[0]
        self.flipped_image = pygame.transform.flip(self.shoot_anim[0], False, True).convert_alpha()
        self.rect = self.image.get_rect(midleft=player.sprite.get_position()+pygame.Vector2(0, 10))
        self.fire_rate = 0.1
        self.last_shot = 0
        self.accuracy = 0.5 # 0 - best accuracy, 1 - worst accuracy
        self.gun_damage = damage

    def shoot(self,direction):
        bullet = Bullet(self.rect.center, direction, self.gun_damage)
        bullet_group.add(bullet)
        player_bullets.append(bullet)
        shoot_sound.play()
        #self.image = self.shoot_anim[0]
        #self.flipped_image = pygame.transform.flip(self.image, False, True).convert_alpha()
        # self.rect = self.image.get_rect(center=player.sprite.get_position()+pygame.Vector2(0, 9))
        # self.rect = self.image.get_rect(center=player.sprite.get_position()+pygame.Vector2(0, 10))
        #screen.blit(self.image, self.rect)

    def update(self):
        self.rect.midleft = player.sprite.get_position() +pygame.Vector2(-10, 13)
        mouse_pos = pygame.mouse.get_pos()
        player_pos = player.sprite.get_position()
        direction = pygame.Vector2((mouse_pos[0] - player_pos[0]) , (mouse_pos[1] - player_pos[1])) # vector from player to mouse with accuracy error
        angle = direction.angle_to(pygame.Vector2(1, 0)) # angle between direction and x axis

        if angle > 0: 
            self.rect.y -= self.rect.height/4

        if mouse_pos[0] < player_pos[0]: #aiming left
            #self.image = pygame.transform.rotate(pygame.transform.flip(self.shoot_anim[0], False, True).convert_alpha(), angle).convert_alpha()
            self.image = pygame.transform.rotate(self.flipped_image.convert_alpha(), angle).convert_alpha()
            self.rect.x -= self.rect.width/2
        elif mouse_pos[0] > player_pos[0]: #aiming right
            self.image = pygame.transform.rotate(self.shoot_anim[0], angle).convert_alpha()

        if pygame.mouse.get_pressed()[0]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.fire_rate * 2000:
                self.shoot(pygame.Vector2(direction[0]+ random.uniform(-100*self.accuracy,100*self.accuracy),direction[1]+ random.uniform(-100*self.accuracy,100*self.accuracy)).normalize())
                #self.shoot(pygame.Vector2(direction.normalize()[0],direction.normalize()[1]))
                self.last_shot = current_time
            
class Zombie(pygame.sprite.Sprite):
    def __init__(self,hp, speed, damage):
        super().__init__()
        self.walk = zombie_walk_animation
        self.image = self.walk[0]
        self.image_index = 0
        self.animation_speed = 0.1

        self.health = hp

        self.rect = self.image.get_rect()
        self.rect.center = random_position(SCREEN_WIDTH, SCREEN_HEIGHT, EXCLUDED_WIDTH, EXCLUDED_HEIGHT)

        self.speed = speed
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
            wave_manager.zombie_killed()
            zombie_death_sound.play()

def zombieSpawn(delay=100):
    zombie = Zombie()
    if pygame.time.get_ticks() % delay == 0:
        zombie_group.add(zombie)

def display_fading_text(screen, text, font, color, duration, fade_duration):

    # Renderowanie tekstu
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    # Stwórz powierzchnię do obsługi przezroczystości
    alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    alpha_surface.blit(text_surface, (0, 0))
    
    # Wyświetlanie pełnego tekstu przez `duration` sekund
    start_time = time.time()
    while time.time() - start_time < duration:
        screen.fill((0, 0, 0))  # Wyczyść ekran
        screen.blit(alpha_surface, text_rect.topleft)
        pygame.display.flip()
        pygame.time.delay(10)
    
    # Zanikanie tekstu przez `fade_duration` sekund
    fade_steps = 255
    fade_step_duration = fade_duration / fade_steps
    
    for alpha in range(255, -1, -1):  # Od pełnej widoczności (255) do całkowitego zniknięcia (0)
        screen.fill((0, 0, 0))  # Wyczyść ekran
        alpha_surface.set_alpha(alpha)  # Ustaw przezroczystość
        screen.blit(alpha_surface, text_rect.topleft)
        pygame.display.flip()
        pygame.time.delay(int(fade_step_duration * 1000))  # Konwersja na milisekundy    

class WaveManager:
    def __init__(self):
        self.wave_number = 1
        self.zombies_to_spawn = 5
        self.spawned_zombies = 0
        self.zombies_killed = 0
        self.zombie_hp = 20
        self.zombie_speed = 1.3
        self.zombie_damage = 10
        self.spawn_delay = 1000  # milliseconds
        self.last_spawn_time = pygame.time.get_ticks()


    def update(self):
        current_time = pygame.time.get_ticks()        

        if current_time - self.last_spawn_time > self.spawn_delay and self.spawned_zombies < self.zombies_to_spawn:
            zombie = Zombie(self.zombie_hp, self.zombie_speed, self.zombie_damage)
            zombie_group.add(zombie)
            self.spawned_zombies += 1
            self.last_spawn_time = current_time

        if self.zombies_killed >= self.zombies_to_spawn:
            self.next_wave()
            

    def next_wave(self):
        self.wave_number += 1
        self.zombies_to_spawn += 5
        self.spawned_zombies = 0
        self.zombies_killed = 0
        self.zombie_hp += 5
        if self.zombie_speed <= 4.5:
            self.zombie_speed += 0.2
        #self.spawn_delay = max(200, self.spawn_delay - 100)  # Decrease spawn delay but not below 200ms
        display_fading_text(screen, f"Wave {self.wave_number}", pixel_font, WHITE, 3, 1)
        
        print(f"Wave {self.wave_number}")

    def zombie_killed(self):
        self.zombies_killed += 1


#player sprite
player = pygame.sprite.GroupSingle(Player())
gun = pygame.sprite.GroupSingle(Gun())
bullet_group = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

wave_manager = WaveManager()

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


# Ustawienia ekranu
pygame.display.set_caption("Menu Główne")

# Funkcja do wyświetlania tekstu
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Menu główne
def main_menu():
    menu_options = ["Start", "Opcje", "Wyjście"]
    selected_option = 0

    running = True
    while running:
        screen.fill(BLACK)
        draw_text("Menu Główne", pixel_font, WHITE, screen, SCREEN_WIDTH // 2, 100)

        # Renderowanie opcji menu
        for i, option in enumerate(menu_options):
            color = HIGHLIGHT if i == selected_option else WHITE
            draw_text(option, pixel_font, color, screen, SCREEN_WIDTH // 2, 200 + i * 100)

        pygame.display.flip()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Start gry
                        #display_fading_text(screen, "Wave 1", pixel_font, WHITE, 3, 1)
                        game_loop()
                    elif selected_option == 1:  # Opcje
                        options_menu()
                    elif selected_option == 2:  # Wyjście
                        pygame.quit()
                        sys.exit()

# Opcje
def options_menu():
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("Opcje", pixel_font, WHITE, screen, SCREEN_WIDTH // 2, 100)
        draw_text("Naciśnij ESC, aby wrócić", pixel_font, WHITE, screen, SCREEN_WIDTH // 2, 300)
        pygame.display.flip()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Powrót do menu głównego
                    running = False






def game_loop():
    running = True
    while running:
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

        wave_manager.update()

        zombie_group.draw(screen)
        zombie_group.update()


        gun.draw(screen)
        gun.sprite.update()

        screen.blit(text, (10, 10))

        pygame.display.update()
        clock.tick(FPS)

# Uruchom menu główne
main_menu()