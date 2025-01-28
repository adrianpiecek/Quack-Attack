import pygame, time, sys
from PlayerClass import Player
from ResourceManagerClass import ResourceManager
from AudioManagerClass import AudioManager
from GunBulletClass import Gun, Bullet
from ZombieClass import Zombie
from WaveManagerClass import WaveManager

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
HIGHLIGHT = (255, 255, 0)


# Ekran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("QUACK ATTACK")
clock = pygame.time.Clock()
pixel_font = pygame.font.Font("Assets/font/ByteBounce.ttf", 32)
menu_font = pygame.font.Font("Assets/font/ByteBounce.ttf", 64)

resourceManagerClass = ResourceManager()
audioManagerClass = AudioManager()

ducky_walk_animation = resourceManagerClass.load_animation("Assets/ducky_walk-sheet.png", 25, 28, 6, 2)
ducky_idle_animation = resourceManagerClass.load_animation("Assets/ducky_idle-sheet.png", 25, 28, 2, 2)
glock_shoot_animation = resourceManagerClass.load_animation("Assets/guns/glock [64x32]/glock [SHOOT].png", 39, 31, 12, 1)
submachine_shoot_animation = resourceManagerClass.load_animation("Assets/guns/Submachine - MP5A3 [80x48].png", 57, 27, 1, 0.9)
ak47_shoot_animation = resourceManagerClass.load_animation("Assets/guns/AK 47 [96x48].png", 76, 22, 1, 0.9)
guns_sprites = [glock_shoot_animation, submachine_shoot_animation, ak47_shoot_animation]
bullet_image = resourceManagerClass.load_image("Assets/guns/bullet.png")
zombie_walk_animation = resourceManagerClass.load_animation("Assets/zombie_run-sheet.png", 23, 23, 7, 2)

# Sounds
ducky_damage_sound = audioManagerClass.load_sound("Assets/sounds/ducky_damage.wav", 1)
shoot_sound = audioManagerClass.load_sound("Assets/sounds/shoot.wav", 0.4)
zombie_death_sound = audioManagerClass.load_sound("Assets/sounds/zombie_death.wav", 0.95)
background_music = audioManagerClass.load_sound("Assets/sounds/doom theme.mp3", 1)
cash_sound = audioManagerClass.load_sound("Assets/sounds/kaching.wav", 1)
background_music.play(-1)

upgrades_enum = {
    "damage": 0,
    "fire_rate": 1,
    "accuracy": 2,
    "new_gun": 3
}

def update_positions(sprites, offset_x, offset_y):
    for sprite in sprites:
        sprite.rect.x += offset_x
        sprite.rect.y += offset_y

money = 0
def add_money(amount):
    global money
    money += amount
def remove_money(amount):
    global money
    money -= amount
isPlayerDead = True

scale = 2


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


#PLAYER STATS
player_health = 10
#GUN STATS
gun_type = 0
gun_damage = 10
gun_fire_rate = 0.1
gun_accuracy = 0.1


#player sprite
player = pygame.sprite.GroupSingle(Player(player_health,ducky_walk_animation,ducky_idle_animation))
bullet_group = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()
player_bullets = []
gun = pygame.sprite.GroupSingle(Gun(gun_damage, gun_fire_rate, gun_accuracy, gun_type,guns_sprites,bullet_image,player_bullets,shoot_sound,remove_money,bullet_group,player))

wave_manager = WaveManager(zombie_walk_animation, zombie_death_sound, ducky_damage_sound, player, bullet_group, player_bullets, add_money, screen, pixel_font, display_fading_text, zombie_group)

display_scroll = [0,0]

#ground tile
ground_tile = pygame.image.load("Assets/ground_tile.png").convert_alpha()
tile_width, tile_height = ground_tile.get_size()
ground_tile = pygame.transform.scale(ground_tile, (tile_width*scale,tile_height*scale))
#barell sprite
barell_surf = pygame.image.load("Assets/barell.png").convert_alpha()
barell_width, barell_height = barell_surf.get_size()
barell_surf = pygame.transform.scale(barell_surf, (barell_width*scale,barell_height*scale))
barell_rect = barell_surf.get_rect(center=(100, 100))


# Funkcja do wyświetlania tekstu
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Menu główne
def main_menu():
    menu_options = ["Start", "Sklep", "Wyjście"]
    selected_option = 0

    running = True
    while running:
        screen.fill(BLACK)
        draw_text("QUACK ATTACK", menu_font, RED, screen, SCREEN_WIDTH // 2, 100)
        draw_text("Zombie Quackdown", pixel_font, GREEN, screen, SCREEN_WIDTH // 2, 130)

        # Render menu options
        for i, option in enumerate(menu_options):
            color = HIGHLIGHT if i == selected_option else WHITE
            draw_text(option, pixel_font, color, screen, SCREEN_WIDTH // 2, 250 + i * 100)

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
                        display_fading_text(screen, "Wave 1", pixel_font, WHITE, 1, 1)
                        game_loop()
                    elif selected_option == 1:  # sklep
                        shop_menu()
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
                if event.key == pygame.K_ESCAPE:  # Powrót do gry
                    running = False


def shop_menu():
    shop_options = [
    "   Damage+       " , 
    "   Fire rate+       ",
    "   Accuracy+       ",
    "   NEW GUN       "]
    selected_option = 0
    upgrades = ["damage", "fire_rate", "accuracy", "new_gun"]
    
    running = True
    while running:
        screen.fill(BLACK)
        draw_text("Sklep", menu_font, WHITE, screen, SCREEN_WIDTH // 2, 100)

        # Renderowanie opcji menu
        for i, option in enumerate(shop_options):
            color = HIGHLIGHT if i == selected_option else WHITE
            draw_text(str(gun.sprite.upgrade_cost(upgrades[i]))+option+ gun.sprite.return_upgrade_level(upgrades[i]), pixel_font, color, screen, SCREEN_WIDTH // 2, 200 + i * 50)

        draw_text("$"+str(money),pixel_font,GREEN,screen ,10+len(str(money))*6, 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Powrót do menu głównego
                    running = False
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(shop_options)
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(shop_options)
                if event.key == pygame.K_RETURN:
                   if money >= gun.sprite.upgrade_cost(upgrades[selected_option]) and selected_option in upgrades_enum.values():
                        gun.sprite.upgrade(upgrades[selected_option])
                        cash_sound.play()

def handle_player_movement():
    keys = pygame.key.get_pressed()
    directions = {
        pygame.K_d: (-player.sprite.speed, 0),
        pygame.K_a: (player.sprite.speed, 0),
        pygame.K_s: (0, -player.sprite.speed),
        pygame.K_w: (0, player.sprite.speed)
    }
    for key, (dx,dy) in directions.items():
        if keys[key]:
            display_scroll[0] += dx * -player.sprite.movement.x
            display_scroll[1] += dy * -player.sprite.movement.y
            update_positions(player_bullets, dx, dy)
            update_positions(zombie_group, dx, dy)

def update_game_logic_and_draw():
    player.sprite.update()
    player.sprite.player_input()
    bullet_group.update()
    wave_manager.update()
    zombie_group.update()
    gun.sprite.update()

    screen.fill((125,125,125))
    player.draw(screen)
    bullet_group.draw(screen)
    zombie_group.draw(screen)
    gun.draw(screen)

    # HUD
    draw_text("$"+str(money),pixel_font,GREEN,screen ,10+(len(str(money))+1)*6, 10)
    draw_text(str(player.sprite.health)+"HP",pixel_font,RED,screen ,SCREEN_WIDTH-((len(str(player.sprite.health))+2)*6)-7, 10)



def game_loop():
    running = True
    for zombie in zombie_group:
        zombie.kill()
    wave_manager.reset_waves()
    player.sprite.health = player.sprite.max_health
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        handle_player_movement()

        update_game_logic_and_draw()

        pygame.display.update()
        clock.tick(FPS)
        if player.sprite.health <= 0:
            display_fading_text(screen, "Game Over", menu_font, RED, 1.5, 0.5)
            running = False

# Uruchom menu główne
main_menu()