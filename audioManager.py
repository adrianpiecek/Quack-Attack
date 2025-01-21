import pygame

class AudioManager:
    def __init__(self):
        self.sounds = {}
    
    def load_sound(self, path, volume):
        if path not in self.sounds:
            self.sounds[path] = pygame.mixer.Sound(path)
            self.sounds[path].set_volume(volume)
        return self.sounds[path]
    
    def play(self,name):
        self.sounds[name].play()