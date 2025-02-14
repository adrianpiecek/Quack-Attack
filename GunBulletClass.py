import pygame
import random
from enum import Enum

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.mixer.init()


class Upgrades(Enum):
    damage = 0
    fire_rate = 1
    accuracy = 2
    new_gun = 3


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction, damage, bullet_image, player_bullets):
        super().__init__()
        self.image = bullet_image
        self.angle = direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=position)
        self.direction = direction
        self.speed = 15
        self.damage = damage
        self.player_bullets = player_bullets

    def update(self):
        self.rect.move_ip(self.direction * self.speed)
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()
            self.player_bullets.remove(self)


class Gun(pygame.sprite.Sprite):
    def __init__(self, damage, fire_rate, accuracy, gun_type, guns_sprites, bullet_image, player_bullets, shoot_sound, remove_money, bullet_group, player):
        super().__init__()
        self.shoot_anim = guns_sprites[gun_type]
        self.image = self.shoot_anim[0]
        self.flipped_image = pygame.transform.flip(
            self.image, False, True).convert_alpha()
        self.rect = self.image.get_rect(
            midleft=player.sprite.get_position()+pygame.Vector2(0, 10))
        self.fire_rate = fire_rate
        self.last_shot = 0
        self.accuracy = accuracy  # 0 - best accuracy, 1 - worst accuracy
        self.gun_damage = damage

        self.upgrade_level = [1, 1, 1]
        self.gun_type = gun_type  # 0 - glock, 1 - submachine, 2 - ak47

        self.player_bullets = player_bullets
        self.shoot_sound = shoot_sound
        self.remove_money = remove_money
        self.player = player
        self.bullet_group = bullet_group
        self.bullet_image = bullet_image
        self.guns_sprites = guns_sprites

    def shoot(self, direction):
        bullet = Bullet(self.rect.center, direction, self.gun_damage,
                        self.bullet_image, self.player_bullets)
        self.bullet_group.add(bullet)
        self.player_bullets.append(bullet)
        self.shoot_sound.play()

    def upgrade(self, upgrade_type):
        if upgrade_type == Upgrades.damage.value and self.upgrade_level[Upgrades.damage.value] < 5:
            self.remove_money(self.upgrade_cost(upgrade_type))
            self.gun_damage += 5
            self.upgrade_level[0] += 1
        elif upgrade_type == Upgrades.fire_rate.value and self.upgrade_level[Upgrades.fire_rate.value] < 5:
            self.remove_money(self.upgrade_cost(upgrade_type))
            self.fire_rate *= 0.9
            self.upgrade_level[1] += 1
        elif upgrade_type == Upgrades.accuracy.value and self.upgrade_level[Upgrades.accuracy.value] < 5:
            self.remove_money(self.upgrade_cost(upgrade_type))
            self.accuracy -= 0.04
            self.upgrade_level[2] += 1
        elif upgrade_type == Upgrades.new_gun.value and self.gun_type < 2:
            self.remove_money(self.upgrade_cost(upgrade_type))
            self.upgrade_level = [1, 1, 1]
            self.gun_type += 1
            if self.gun_type == 1:
                self.gun_damage = 20
                self.fire_rate = 0.06
                self.accuracy = 0.35
                self.shoot_anim = self.guns_sprites[1]
                self.flipped_image = pygame.transform.flip(
                    self.shoot_anim[0], False, True).convert_alpha()
            elif self.gun_type == 2:
                self.gun_damage = 30
                self.fire_rate = 0.04
                self.accuracy = 0.25
                self.shoot_anim = self.guns_sprites[2]
                self.flipped_image = pygame.transform.flip(
                    self.shoot_anim[0], False, True).convert_alpha()

    def upgrade_cost(self, upgrade_type):
        if upgrade_type == Upgrades.damage.value:
            return 50*(self.gun_type+1)*self.upgrade_level[0]
        elif upgrade_type == Upgrades.fire_rate.value:
            return 50*(self.gun_type+1)*self.upgrade_level[1]
        elif upgrade_type == Upgrades.accuracy.value:
            return 50*(self.gun_type+1)*self.upgrade_level[2]
        elif upgrade_type == Upgrades.new_gun.value:
            return (1000 * (self.gun_type+1))

    def return_upgrade_level(self, upgrade_type):
        if upgrade_type == Upgrades.damage.value:
            if self.upgrade_level[0] < 5:
                return str(self.upgrade_level[0])
            else:
                return "MAX"
        elif upgrade_type == Upgrades.fire_rate.value:
            if self.upgrade_level[1] < 5:
                return str(self.upgrade_level[1])
            else:
                return "MAX"
        elif upgrade_type == Upgrades.accuracy.value:
            if self.upgrade_level[2] < 5:
                return str(self.upgrade_level[2])
            else:
                return "MAX"
        elif upgrade_type == Upgrades.new_gun.value:
            if self.gun_type == 0:
                return "Glock"
            elif self.gun_type == 1:
                return "MP5"
            elif self.gun_type == 2:
                return "AK47"

    def update(self):
        self.rect.midleft = self.player.sprite.get_position() + pygame.Vector2(-10, 13)
        mouse_pos = pygame.mouse.get_pos()
        player_pos = self.player.sprite.get_position()
        # vector from player to mouse with accuracy error
        direction = pygame.Vector2(
            (mouse_pos[0] - player_pos[0]), (mouse_pos[1] - player_pos[1]))
        # angle between direction and x axis
        angle = direction.angle_to(pygame.Vector2(1, 0))

        if angle > 0:
            self.rect.y -= self.rect.height/4

        if mouse_pos[0] < player_pos[0]:  # aiming left
            self.image = pygame.transform.rotate(
                self.flipped_image.convert_alpha(), angle).convert_alpha()
            self.rect.x -= self.rect.width/2
        elif mouse_pos[0] > player_pos[0]:  # aiming right
            self.image = pygame.transform.rotate(
                self.shoot_anim[0], angle).convert_alpha()

        if pygame.mouse.get_pressed()[0]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.fire_rate * 2000:
                self.shoot(pygame.Vector2(direction[0] + random.uniform(-100*self.accuracy, 100*self.accuracy),
                           direction[1] + random.uniform(-100*self.accuracy, 100*self.accuracy)).normalize())
                self.last_shot = current_time
