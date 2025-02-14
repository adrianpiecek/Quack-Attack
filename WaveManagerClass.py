import pygame
from ZombieClass import Zombie


class WaveManager:
    def __init__(self, zombie_walk_animation, zombie_death_sound, ducky_damage_sound, player, bullet_group, player_bullets, add_money, screen, pixel_font, display_fading_text, zombie_group):
        self.wave_number = 1
        self.zombies_to_spawn = 5
        self.spawned_zombies = 0
        self.zombies_killed = 0
        self.zombie_hp = 20
        self.zombie_speed = 1.3
        self.zombie_damage = 10
        self.spawn_delay = 1000  # milliseconds
        self.last_spawn_time = pygame.time.get_ticks()

        self.zombie_group = zombie_group
        self.add_money = add_money
        self.screen = screen
        self.pixel_font = pixel_font
        self.display_fading_text = display_fading_text
        self.screen = screen

        # Zombie contructor params
        self.zombie_walk_animation = zombie_walk_animation
        self.zombie_death_sound = zombie_death_sound
        self.ducky_damage_sound = ducky_damage_sound
        self.player = player
        self.bullet_group = bullet_group
        self.player_bullets = player_bullets

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_spawn_time > self.spawn_delay and self.spawned_zombies < self.zombies_to_spawn:
            zombie = Zombie(self.zombie_hp, self.zombie_speed, self.zombie_damage, self.zombie_walk_animation, self.zombie_death_sound,
                            self.ducky_damage_sound, self, self.player, self.bullet_group, self.player_bullets, self.add_money)
            self.zombie_group.add(zombie)
            self.spawned_zombies += 1
            self.last_spawn_time = current_time

        if self.zombies_killed >= self.zombies_to_spawn:
            self.next_wave()

    def reset_waves(self):
        self.wave_number = 1
        self.zombies_to_spawn = 5
        self.spawned_zombies = 0
        self.zombies_killed = 0
        self.zombie_hp = 20
        self.zombie_speed = 1.3
        self.zombie_damage = 10
        self.spawn_delay = 1000  # milliseconds
        self.last_spawn_time = pygame.time.get_ticks()

    def next_wave(self):
        self.wave_number += 1
        self.zombies_to_spawn += 5
        self.spawned_zombies = 0
        self.zombies_killed = 0
        self.zombie_hp += 5
        if self.zombie_speed <= 4.5:
            self.zombie_speed += 0.2
        self.display_fading_text(self.screen, f"Wave {self.wave_number}", self.pixel_font, (255, 255, 255), 1, 1)

    def zombie_killed(self):
        self.zombies_killed += 1
