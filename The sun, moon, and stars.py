import os
import pygame
import math
from sys import exit
from random import randint, choice

# Set colors
COLOR_SPACE_BG = (11, 0, 26)
COLOR_NEON_CYAN = (0, 245, 255)
COLOR_NEON_GOLD = (255, 215, 0)
COLOR_TEXT_WHITE = (240, 240, 255)
COLOR_TRAIL_BLUE = (0, 191, 255)

# Get the path to the directory where the code is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper function to create absolute paths regardless of working directory
def get_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load and scale the walking images
        player_walk_1 = pygame.image.load(get_path("Graphics/player/astronaut_walk_1.png")).convert_alpha()
        player_walk_1 = pygame.transform.scale(player_walk_1, (55, 55))

        player_walk_2 = pygame.image.load(get_path("Graphics/player/astronaut_walk_2.png")).convert_alpha()
        player_walk_2 = pygame.transform.scale(player_walk_2, (55, 55))

        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0

        # Load and scale the jumping image
        player_jump = pygame.image.load(get_path("Graphics/player/astronaut_jump.png")).convert_alpha()
        self.player_jump = pygame.transform.scale(player_jump, (55, 55))

        self.image = self.player_walk[self.player_index]
        # Position the player rectangle on the ground path
        self.rect = self.image.get_rect(midbottom=(100, 320))
        self.gravity = 0

        # Sound
        self.jump_sound = pygame.mixer.Sound(get_path("Audio/jump.mp3"))
        self.jump_sound.set_volume(0.3)

        # Track particles for movement trail on the screen
        self.particles = []

    def player_input(self):
        # Check if space bar is pressed and if the player is on the ground
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 320:
            self.gravity = -16  # Adjusted jump velocity for the player
            self.jump_sound.play()

    def apply_gravity(self):
        # Apply a constant downward pull to simulate gravity
        self.gravity += 0.8
        self.rect.y += self.gravity
        # Prevent the player from falling below the ground line
        if self.rect.bottom >= 320:
            self.rect.bottom = 320

    def animation_state(self):
        # Switch between the floating image and walking frames based on the player state
        if self.rect.bottom < 320:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def handle_trail(self):
        # Generate new trail particles based on player movement state
        if self.rect.bottom < 320:
            # Spawn tiny floating sparks when jumping off the ground in the air
            if randint(0, 100) < 40:
                self.particles.append(
                    [self.rect.left + 5, self.rect.centery + 10, randint(4, 7)]
                )
        else:
            # Spawn running sparks when sprinting on the ground
            if randint(0, 100) < 25:
                self.particles.append(
                    [self.rect.left + 10, self.rect.bottom - 5, randint(3, 5)]
                )

        # Update and draw the trail particles
        for particle in self.particles[:]:
            particle[0] -= 4  # Drift backward
            particle[1] += choice([-1, 0, 1])  # Dynamic jitter
            particle[2] -= 0.15  # Shrink over time

            if particle[2] <= 0:
                self.particles.remove(particle)
            else:
                pygame.draw.circle(
                    screen,
                    COLOR_TRAIL_BLUE,
                    (int(particle[0]), int(particle[1])),
                    int(particle[2]),
                )

    def update(self):
        # Run all character functions together in each frame loop
        self.player_input()
        self.apply_gravity()
        self.animation_state()
        self.handle_trail()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, spawn_x):
        super().__init__()

        # Load obstacles and scale them to match the player dimensions
        if type == "sun":
            sun_1 = pygame.image.load(get_path("Graphics/sun/sun1.png")).convert_alpha()
            sun_1 = pygame.transform.scale(sun_1, (55, 55))
            sun_2 = pygame.image.load(get_path("Graphics/sun/sun2.png")).convert_alpha()
            sun_2 = pygame.transform.scale(sun_2, (55, 55))
            self.frames = [sun_1, sun_2]
            y_pos = 210  # Floating height for the high obstacle
        else:
            moon_1 = pygame.image.load(get_path("Graphics/moon/moon1.png")).convert_alpha()
            moon_1 = pygame.transform.scale(moon_1, (55, 55))
            moon_2 = pygame.image.load(get_path("Graphics/moon/moon2.png")).convert_alpha()
            moon_2 = pygame.transform.scale(moon_2, (55, 55))
            self.frames = [moon_1, moon_2]
            y_pos = 320  # Position for the ground obstacle

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        # Position using the spawn coordinate to prevent random stacking
        self.rect = self.image.get_rect(midbottom=(spawn_x, y_pos))

    def animation_state(self):
        # Loop through the obstacle animation frames
        self.animation_index += 0.08
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        # Remove the obstacle from memory once it clears the left side of the screen
        if self.rect.x <= -100:
            self.kill()

    def update(self):
        self.animation_state()
        self.rect.x -= 7  # Move the obstacle left across the screen
        self.destroy()

class Star(pygame.sprite.Sprite):
    def __init__(self, forced_y=None, spawn_x=950):
        super().__init__()
        # Load and scale the frames for the animated star item
        star_1 = pygame.image.load(get_path("Graphics/star/star1.png")).convert_alpha()
        star_1 = pygame.transform.scale(star_1, (35, 35))

        star_2 = pygame.image.load(get_path("Graphics/star/star2.png")).convert_alpha()
        star_2 = pygame.transform.scale(star_2, (35, 35))

        self.frames = [star_1, star_2]
        self.animation_index = 0
        self.image = self.frames[self.animation_index]

        # Controls where the star spawns (high, middle, or low)
        if forced_y:
            random_y = forced_y
        else:
            random_y = choice([180, 240, 300])

        self.rect = self.image.get_rect(center=(spawn_x, random_y))

    def animation_state(self):
        # Loops smoothly through the star frames to make it twinkle
        self.animation_index += 0.08
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 5
        if self.rect.x <= -100:
            self.kill()

def display_score():
    # Update the current score based on how many stars are collected
    score_surface = test_font.render(f"STARS CLAIMED: {score}", False, COLOR_NEON_GOLD)
    score_rectangle = score_surface.get_rect(center=(400, 50))
    screen.blit(score_surface, score_rectangle)

def collision_sprite():
    # Check for overlap between the player and any obstacles
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        star_group.empty()
        return False
    else:
        return True

def check_star_collections():
    global score
    # Check if player touches a star, remove the star from the group, and add to score
    collided_stars = pygame.sprite.spritecollide(player.sprite, star_group, True)
    if collided_stars:
        score += len(collided_stars)
        # Play a sound effect when claiming a star
        star_sound.play()

# Initialize Game
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Cosmic Parkour")
clock = pygame.time.Clock()
test_font = pygame.font.Font(get_path("Font/Pixeltype.ttf"), 50)

game_active = False
score = 0

# Music & Sound Effects
bg_music = pygame.mixer.Sound(get_path("Audio/music.wav"))
bg_music.set_volume(0.3)
bg_music.play(loops=-1)

# Add a placeholder audio file path for collecting stars
star_sound = pygame.mixer.Sound(get_path("Audio/jump.mp3"))
star_sound.set_volume(0.2)

# Sprite Groups to handle rendering and code together
player = pygame.sprite.GroupSingle()
player.add(Player())
obstacle_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()

# Create coordinates and twinkling effect for a starfield background
background_stars = []
for i in range(45):
    # Format: [X pos, Y pos, scroll speed, twinkle speed offset]
    background_stars.append(
        [randint(0, 800), randint(0, 400), randint(1, 3), randint(0, 100)]
    )

# Tracker for a cyber style moving ground
grid_scroll = 0

# Background Setup
try:
    space_background = pygame.image.load(get_path("Graphics/space_bg.png")).convert()
    has_bg_image = True
except:
    has_bg_image = False

# Intro Screen Elements
player_stand = pygame.image.load(get_path("Graphics/player/astronaut_stand.png")).convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 0.6)
player_stand_rectangle = player_stand.get_rect(center=(400, 200))

game_name = test_font.render("COSMIC PARKOUR", False, COLOR_NEON_CYAN)
game_name_rectangle = game_name.get_rect(center=(400, 60))

game_message = test_font.render("PRESS SPACE TO LAUNCH", False, COLOR_TEXT_WHITE)
game_message_rectangle = game_message.get_rect(center=(400, 350))

# Spawn Timer running every 1.1 seconds to keep object flow consistent
spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_timer, 1100)

# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.sprite.rect.bottom >= 320:
                    player.sprite.gravity = -16
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_active = True
                    score = 0  # Reset collected star scores upon game launch

        if game_active:
            if event.type == spawn_timer:
                # Choose a randomized layout mode to swap patterns
                spawn_mode = choice(
                    [
                        "only_star",
                        "moon_and_high_star",
                        "sun_and_low_star",
                        "just_obstacle",
                    ]
                )

                base_x = randint(900, 1000)

                if spawn_mode == "only_star":
                    # Spawns a single star at a random height
                    star_group.add(Star(spawn_x=base_x))

                elif spawn_mode == "moon_and_high_star":
                    # Spawns a moon on the ground and floats a star high up in the air so the player grabs the star when
                    # they jump over the moon
                    obstacle_group.add(Obstacle("moon", base_x))
                    star_group.add(Star(forced_y=180, spawn_x=base_x + 30))

                elif spawn_mode == "sun_and_low_star":
                    # Spawns a sun high up in the sky and puts a star low on the ground so the player has to stay on the
                    # ground to get the star and avoid the sun
                    obstacle_group.add(Obstacle("sun", base_x))
                    star_group.add(Star(forced_y=300, spawn_x=base_x + 30))

                elif spawn_mode == "just_obstacle":
                    # Spawns a single enemy (randomly picks either a sun or a moon) with no stars
                    obstacle_group.add(Obstacle(choice(["sun", "moon"]), base_x))

    if game_active:
        # Draw Background Layers
        if has_bg_image:
            screen.blit(space_background, (0, 0))
        else:
            screen.fill(COLOR_SPACE_BG)

            # Animate and draw the starfield background
            for star in background_stars:
                star[0] -= star[2] * 0.4
                if star[0] < 0:
                    star[0] = 800
                    star[1] = randint(0, 400)

                # Calculate the glowing pulses
                star_pulse = int(
                    125
                    + 130
                    * math.sin(pygame.time.get_ticks() * 0.004 + star[3])
                )
                star_pulse = max(0, min(255, star_pulse))

                pygame.draw.circle(
                    screen,
                    (star_pulse, star_pulse, 255),
                    (int(star[0]), star[1]),
                    star[2],
                )

            pygame.draw.line(screen, (75, 50, 140), (0, 320), (800, 320), 4)
            pygame.draw.line(screen, (40, 25, 80), (0, 326), (800, 326), 2)

            # Animate the moving ground
            grid_scroll = (grid_scroll - 7) % 40
            for vertical_x in range(grid_scroll, 800, 40):
                pygame.draw.line(
                    screen,
                    (30, 20, 65),
                    (vertical_x, 326),
                    (vertical_x - 30, 400),
                    2,
                )

        # Update and Draw objects
        star_group.draw(screen)
        star_group.update()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        # Collisions & Score Calculations
        check_star_collections()
        game_active = collision_sprite()

        # UI Score Tracking
        display_score()

    # Intro / Game Over Menu
    else:
        screen.fill(COLOR_SPACE_BG)

        # Draw a beautiful backdrop behind the exact UI positions to group them together perfectly
        pygame.draw.rect(screen, (18, 5, 40), (130, 30, 540, 340), border_radius=20)
        pygame.draw.rect(screen, COLOR_NEON_CYAN, (130, 30, 540, 340), width=2, border_radius=20)

        screen.blit(player_stand, player_stand_rectangle)

        score_message = test_font.render(f"STARS CAPTURED: {score}", False, COLOR_NEON_GOLD)
        score_rectangle = score_message.get_rect(center=(400, 350))
        screen.blit(game_name, game_name_rectangle)

        if score == 0:
            screen.blit(game_message, game_message_rectangle)
        else:
            screen.blit(score_message, score_rectangle)

    pygame.display.update()
    clock.tick(60)