import pygame
import random
import math
# pixels from the edge of the screen where zombies can spawn
EXCLUDED_WIDTH, EXCLUDED_HEIGHT = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

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


class Zombie(pygame.sprite.Sprite):
    def __init__(self,hp, speed, damage, zombie_walk_animation, zombie_death_sound, ducky_damage_sound, wave_manager, player, bullet_group, player_bullets, add_money):
        super().__init__()
        self.walk = zombie_walk_animation
        self.image = self.walk[0]
        self.image_index = 0
        self.animation_speed = 0.1
        self.money = 500
        self.damage = damage

        self.max_health = hp
        self.health = hp

        self.rect = self.image.get_rect()
        self.rect.center = random_position(SCREEN_WIDTH, SCREEN_HEIGHT, EXCLUDED_WIDTH, EXCLUDED_HEIGHT)

        self.speed = speed
        self.direction = pygame.Vector2(0, 0)

        self.zombie_death_sound = zombie_death_sound
        self.ducky_damage_sound = ducky_damage_sound
        self.wave_manager = wave_manager
        self.player = player
        self.bullet_group = bullet_group
        self.player_bullets = player
        self.player_bullets = player_bullets
        self.add_money = add_money

    def change_color(self, image, health_ratio):
        colored_image = image.copy()
        pixels = pygame.PixelArray(colored_image)
        red_intensity = int(200 * (1 - health_ratio))
        for x in range(pixels.shape[0]):
            for y in range(pixels.shape[1]):
                # getting color of pixel
                color = colored_image.unmap_rgb(pixels[x, y])
                # if pixel is not transparent
                if color.a > 0:
                    # mixing colors with red
                    new_color = (
                        min(255, color.r + red_intensity),
                        max(0, color.g - red_intensity),
                        max(0, color.b - red_intensity),
                        color.a
                    )
                    pixels[x, y] = new_color
        return colored_image

    def update(self):
        self.image_index += self.animation_speed
        if self.image_index >= len(self.walk):
            self.image_index = 0

        health_ratio = max(0, self.health / self.max_health)  # Procent zdrowia (0-1)
        changed_image = self.change_color(self.walk[int(self.image_index)], health_ratio)
        self.image = changed_image

        player_pos = self.player.sprite.get_position()
        self.direction = pygame.Vector2(player_pos[0] - self.rect.center[0], player_pos[1] - self.rect.center[1])
        self.direction = self.direction.normalize()
        self.rect.move_ip(self.direction * self.speed * random.uniform(0.80, 1.20))

        if self.rect.colliderect(self.player.sprite.rect):
            self.ducky_damage_sound.play()
            self.player.sprite.health -= self.damage
            self.health = 0
        for bullet in self.bullet_group:
            if self.rect.colliderect(bullet.rect):
                self.health -= 10
                bullet.kill()
                self.player_bullets.remove(bullet)
        if self.health <= 0:
            self.kill()
            self.wave_manager.zombie_killed()
            self.zombie_death_sound.play()
            self.add_money(self.money)
