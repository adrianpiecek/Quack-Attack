import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self,max_health=100,ducky_walk_animation=[],ducky_idle_animation=[]):
        super().__init__()
        self.walk = ducky_walk_animation
        self.idle = ducky_idle_animation
        self.image = self.idle[0]
        self.image_index = 0
        self.animation_speed = 0.1

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        self.max_health = max_health        
        self.health = self.max_health
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
        if self.health <= 0:
            pass

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