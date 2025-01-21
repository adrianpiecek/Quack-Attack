import pygame
import spriteSheet

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sheets = {}
        self.animations = {}
    
    def load_image(self, path):
        if path not in self.images:
            self.images[path] = pygame.image.load(path).convert_alpha()
        return self.images[path]
    
    def load_sprite_sheet(self, path, sprite_width, sprite_height, frame_count):
        if path not in self.sheets:
            sheet_image = self.load_image(path)
            sprite_sheet = spriteSheet.SpriteSheet(sheet_image)
            frames = [sprite_sheet.get_image(i, sprite_width, sprite_height, 1) for i in range(frame_count)]
            self.sheets[path] = frames
        return self.sheets[path]
    
    def load_animation(self, path, sprite_width, sprite_height, frame_count, scale):
        if path not in self.animations:
            sheet_image = self.load_image(path)
            sprite_sheet = spriteSheet.SpriteSheet(sheet_image)
            frames = [sprite_sheet.get_image(i, sprite_width, sprite_height, scale) for i in range(frame_count)]
            self.animations[path] = frames
        return self.animations[path]
    
