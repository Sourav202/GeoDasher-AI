import pygame as pg
from GA import tint_image
import matplotlib as plt

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 0.8
SCROLL_SPD = 7
DEF_GROUND_LVL = 380
BUFFER = 15
COLORS = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Magenta": (255, 0, 255),
    "Cyan": (0, 255, 255),
    "Maroon": (128, 0, 0),
    "Dark Green": (0, 128, 0),
    "Navy": (0, 0, 128),
    "Olive": (128, 128, 0),
    "Purple": (128, 0, 128),
    "Teal": (0, 128, 128),
    "Orange": (255, 165, 0),
    "Hot Pink": (255, 105, 180),
    "Indigo": (75, 0, 130),
    "Light Coral": (240, 128, 128),
    "Steel Blue": (70, 130, 180),
    "Yellow Green": (154, 205, 50),
    "Red-Orange": (255, 69, 0),
    "Deep Sky Blue": (0, 191, 255),
    "Light Green": (144, 238, 144),
    "Medium Violet Red": (199, 21, 133),
    "Moccasin": (255, 228, 181),
    "Light Sea Green": (32, 178, 170),
    "Chocolate": (210, 105, 30),
    "Medium Purple": (147, 112, 219),
    "Deep Pink": (255, 20, 147),
    "Medium Slate Blue": (123, 104, 238),
    "Dark Slate Blue": (72, 61, 139),
    "Green Yellow": (173, 255, 47),
    "Peach Puff": (255, 218, 185),
    "Orchid": (218, 112, 214),
    "Cornflower Blue": (100, 149, 237),
    "Saddle Brown": (139, 69, 19),
    "Dark Olive Green": (85, 107, 47),
    "Salmon": (250, 128, 114),
    "Sandy Brown": (244, 164, 96),
    "Sea Green": (46, 139, 87),
    "Gray": (128, 128, 128),
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Light Slate Gray": (119, 136, 153),
    "Tan": (210, 180, 140),
    "Dark Green (Alternative)": (0, 100, 0),
    "Navajo White": (255, 222, 173),
    "Turquoise": (64, 224, 208),
    "Aquamarine": (127, 255, 212),
    "Light Goldenrod Yellow": (250, 250, 210),
    "Dark Orange": (255, 140, 0),
    "Light Steel Blue": (176, 196, 222),
}
COLORS_LIST = list(COLORS.values())

#Initialize 
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("GeoDasher")

#Load images and sounds
bg_img = pg.image.load('assets/images/background.png').convert()
ground_img = pg.image.load('assets/images/ground.png').convert()
player_img = pg.image.load('assets/images/player.png').convert_alpha()
spike_img = pg.image.load('assets/images/spike.png').convert_alpha()
spikebed_img = pg.image.load('assets/images/spikebed.png').convert_alpha()
block_img = pg.image.load('assets/images//block.png').convert_alpha()
block02_img = pg.image.load('assets/images/block02.png').convert_alpha()
platform_img = pg.image.load('assets/images/reg_platform.png').convert_alpha()
goal_img = pg.image.load('assets/images/goal.png').convert_alpha()

# Player class
class Player(pg.sprite.Sprite):
    def __init__(self, genome, idx):
        super().__init__()
        scaled_image = pg.transform.scale(player_img, (50, 50))
        self.image = tint_image(scaled_image, COLORS_LIST[idx % len(COLORS)])
        self.rect = self.image.get_rect()
        self.ground_level = DEF_GROUND_LVL
        self.rect.x, self.rect.y = 200, self.ground_level
        self.velocity = 0
        self.is_jumping = False
        
        #Genetic Algorithm Component
        self.genome = genome
        self.current_jump = 0
        self.penalty = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        if self.rect.y >= self.ground_level + 1:
            self.rect.y = self.ground_level
            self.is_jumping = False
            self.velocity = 0

    def jump(self):
        # Allow jumping only when the player is on the ground or a platform
        if not self.is_jumping and self.velocity < 1 and self.velocity >= 0:
            self.velocity = -13
            self.is_jumping = True
            
class Ground(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ground_img
        self.rect = self.image.get_rect(topleft=(x, y))
        #self.drop_speed = 0  # Initial drop speed

    def update(self):
        # Move ground horizontally (scrolling effect)
        self.rect.x -= SCROLL_SPD
        # Move ground downward to simulate upward player motion
        #self.rect.y += self.drop_speed

        # Reset ground horizontally when it scrolls out of view
        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.top > HEIGHT:
            #self.drop_speed = 0
            self.kill()
            
class Large_Platform(pg.sprite.Sprite):
    def __init__(self, x, y, platform_dim):
        super().__init__()
        self.image = pg.transform.scale(block02_img, platform_dim)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD
        if self.rect.right < 0:
            self.kill()

class Small_Platform(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(platform_img, (50, 25))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD
        if self.rect.right < 0:
            self.kill()

class Block(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(block_img, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD
        if self.rect.right < 0:
            self.kill()

class Spike(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(spike_img, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD
        if self.rect.right < 0:
            self.kill()

class SpikeBed(pg.sprite.Sprite):
    def __init__(self, x, y, dim):
        super().__init__()
        self.image = pg.transform.scale(spikebed_img, dim)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD
        if self.rect.right < 0:
            self.kill()

# Progress bar class
class ProgressBar:
    def __init__(self, total_length):
        self.total_length = total_length
        self.current_progress = 0

    def update(self, progress):
        self.current_progress = progress

    def draw(self, screen):
        progress_width = int((self.current_progress / self.total_length) * 300)
        pg.draw.rect(screen, COLORS["Black"], (WIDTH - 320, 20, 300, 10), 2)
        pg.draw.rect(screen, (0, 255, 0), (WIDTH - 320, 20, progress_width, 10))

class Goal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.transform.scale(goal_img, (50, 50))  # Scale as needed
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x -= SCROLL_SPD  # Scroll with the game world