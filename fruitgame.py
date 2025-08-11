import cv2
import mediapipe as mp
import pygame
import random
import math
import time
from collections import deque

# === CONFIG ===
WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 0.35
FRUIT_SPAWN_INTERVAL = 1.4
MAX_LIVES = 3
SLICE_TRAIL_LENGTH = 15
COMBO_TIME = 1.0
SPEED_TO_SLICE = 10

# === Initialize MediaPipe Hands ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

# === Initialize Pygame ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja Air Slice")
clock = pygame.time.Clock()

# Load sounds
pygame.mixer.init()
slice_sound = pygame.mixer.Sound("slice.wav")
bomb_sound = pygame.mixer.Sound("bomb.wav")

try:
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except:
    pass

# Create colored rectangles as fruit images if files don't exist
def create_fruit_image(color, size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(surf, color, surf.get_rect())
    return surf

# Load fruit images
try:
    fruit_imgs = [
        pygame.transform.smoothscale(pygame.image.load("fruit_apple.png").convert_alpha(), (120, 120)),
        pygame.transform.smoothscale(pygame.image.load("fruit_orange.png").convert_alpha(), (120, 120)),
        pygame.transform.smoothscale(pygame.image.load("fruit_watermelon.png").convert_alpha(), (150, 150)),
        pygame.transform.smoothscale(pygame.image.load("fruit_pineapple.png").convert_alpha(), (150, 150)),
    ]
except:
    fruit_imgs = [
        create_fruit_image((255, 0, 0), (120, 120)),
        create_fruit_image((255, 165, 0), (120, 120)),
        create_fruit_image((0, 255, 0), (150, 150)),
        create_fruit_image((255, 255, 0), (150, 150)),
    ]

try:
    bomb_img = pygame.transform.smoothscale(pygame.image.load("bomb.png").convert_alpha(), (100, 100))
except:
    bomb_img = create_fruit_image((50, 50, 50), (100, 100))

def split_surface_simple(img: pygame.Surface, swipe_angle_rad: float) -> tuple[pygame.Surface, pygame.Surface]:
    """Simple fruit splitting that creates two halves along a cut line."""
    w, h = img.get_width(), img.get_height()
    
    left_half = pygame.Surface((w, h), pygame.SRCALPHA)
    right_half = pygame.Surface((w, h), pygame.SRCALPHA)
    
    left_half.blit(img, (0, 0))
    right_half.blit(img, (0, 0))
    
    center_x, center_y = w // 2, h // 2
    
    mask_left = pygame.Surface((w, h), pygame.SRCALPHA)
    mask_right = pygame.Surface((w, h), pygame.SRCALPHA)
    
    mask_left.fill((255, 255, 255, 255))
    mask_right.fill((255, 255, 255, 255))
    
    line_length = max(w, h) * 2
    dx = math.cos(swipe_angle_rad) * line_length
    dy = math.sin(swipe_angle_rad) * line_length
    
    cut_points = [
        (center_x - dx, center_y - dy),
        (center_x + dx, center_y + dy),
        (center_x + dx + dy, center_y + dy - dx),
        (center_x - dx + dy, center_y - dy - dx)
    ]
    
    pygame.draw.polygon(mask_right, (0, 0, 0, 0), cut_points)
    
    opposite_points = [
        (center_x - dx, center_y - dy),
        (center_x + dx, center_y + dy),
        (center_x + dx - dy, center_y + dy + dx),
        (center_x - dx - dy, center_y - dy + dx)
    ]
    
    pygame.draw.polygon(mask_left, (0, 0, 0, 0), opposite_points)
    
    left_half.blit(mask_left, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    right_half.blit(mask_right, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    return left_half, right_half

# Particle class for juice splashes
class Particle:
    def __init__(self, pos):
        self.pos = [pos[0], pos[1]]
        self.vel = [random.uniform(-3, 3), random.uniform(-5, -2)]
        self.radius = random.randint(3, 6)
        self.life = 24
        self.color = (255, random.randint(50, 100), 0)

    def update(self):
        self.life -= 1
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] += 0.3

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

# Explosion particle class
class ExplosionParticle:
    def __init__(self, pos):
        self.pos = [pos[0], pos[1]]
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        self.vel = [speed * math.cos(angle), speed * math.sin(angle)]
        self.radius = random.randint(4, 12)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0), (255, 255, 0)]
        self.color = random.choice(colors)

    def update(self):
        self.life -= 1
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] *= 0.95
        self.vel[1] *= 0.95
        self.vel[1] += 0.2

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color_with_alpha = (*self.color, alpha)
            
            particle_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))

# Explosion effect class
class Explosion:
    def __init__(self, pos):
        self.pos = pos
        self.particles = []
        self.boom_scale = 0.1
        self.boom_life = 30
        self.max_boom_life = 30
        
        for _ in range(25):
            self.particles.append(ExplosionParticle(pos))

    def update(self):
        self.boom_life -= 1
        if self.boom_life > self.max_boom_life * 0.7:
            self.boom_scale = min(1.2, self.boom_scale + 0.15)
        else:
            self.boom_scale = max(0, self.boom_scale - 0.05)
            
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        # Draw explosion particles
        for p in self.particles:
            p.draw(surface)

    def is_finished(self):
        return self.boom_life <= 0 and len(self.particles) == 0

# Base class for all game objects
class GameObject:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = img.get_width()
        self.height = img.get_height()
        self.vel_x = 0
        self.vel_y = 0
        self.angle = 0
        self.angle_vel = 0
        self.is_sliced = False
        self.particles = []

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY
        self.angle += self.angle_vel
        
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        rect = rotated_img.get_rect(center=(self.x, self.y))
        surface.blit(rotated_img, rect.topleft)
        
        for p in self.particles:
            p.draw(surface)

    def get_rect(self):
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        return rotated_img.get_rect(center=(self.x, self.y))

# Fruit class
class Fruit(GameObject):
    def __init__(self, x, y, img):
        super().__init__(x, y, img)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-10, -15)
        self.angle_vel = random.uniform(-5, 5)
        self.sliced_time = None

    def slice(self, push_dir=(1.0, 0.0), swipe_angle_rad: float = 0.0):
        if self.is_sliced:
            return []

        self.is_sliced = True
        self.sliced_time = time.time()
        
        # Play slice sound
        slice_sound.play()

        # Particles
        for _ in range(15):
            self.particles.append(Particle((self.x, self.y)))

        # Split the fruit image
        left_img, right_img = split_surface_simple(self.img, swipe_angle_rad)

        nx, ny = push_dir
        PUSH = 8.0
        ANG_BOOST = 3.0

        half1 = FruitHalf(
            left_img,
            self.x - 6 * nx, self.y - 6 * ny,
            self.vel_x + PUSH * nx, self.vel_y + PUSH * ny,
            self.angle, self.angle_vel - ANG_BOOST
        )
        half2 = FruitHalf(
            right_img,
            self.x + 6 * nx, self.y + 6 * ny,
            self.vel_x - PUSH * nx, self.vel_y - PUSH * ny,
            self.angle, self.angle_vel + ANG_BOOST
        )

        return [half1, half2]

# FruitHalf class
class FruitHalf(GameObject):
    def __init__(self, img, x, y, vel_x, vel_y, angle, angle_vel):
        super().__init__(x, y, img)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.angle = angle
        self.angle_vel = angle_vel
        self.is_sliced = True

# Bomb class
class Bomb(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, bomb_img)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-10, -15)
        self.angle_vel = random.uniform(-5, 5)

    def slice(self, *args, **kwargs):
        if not self.is_sliced:
            self.is_sliced = True
            bomb_sound.play()
            
            for _ in range(15):
                p = Particle((self.x, self.y))
                p.color = (255, 0, 0)
                p.vel = [random.uniform(-8, 8), random.uniform(-8, -2)]
                self.particles.append(p)
                
            self.vel_x *= 2
            self.vel_y *= 1.5
            self.angle_vel *= 3
            
            return [Explosion((self.x, self.y))]
        return []

def finger_touches_fruit(finger_pos, fruit_rect):
    if finger_pos is None:
        return False
    return fruit_rect.collidepoint(finger_pos)

def spawn_fruit():
    x = random.randint(150, WIDTH - 150)
    y = HEIGHT + 10

    is_bomb = (random.random() < 0.15)

    angle_deg = random.uniform(-110, -70)
    speed = random.uniform(18, 25)
    rad = math.radians(angle_deg)
    vel_x = speed * math.cos(rad)
    vel_y = speed * math.sin(rad)

    if is_bomb:
        b = Bomb(x, y)
        b.vel_x, b.vel_y = vel_x, vel_y
        return b
    else:
        img = random.choice(fruit_imgs)
        f = Fruit(x, y, img)
        f.vel_x, f.vel_y = vel_x, vel_y
        return f

# Game variables
fruits = []
explosions = []
last_spawn_time = 0
score = 0
lives = MAX_LIVES
slice_trail = deque(maxlen=SLICE_TRAIL_LENGTH)
last_slice_time = 0
combo_count = 0

font = pygame.font.SysFont("Arial", 36)
game_over = False

cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

def draw_text(surf, text, pos, color=(255,255,255)):
    txt_surf = font.render(text, True, color)
    surf.blit(txt_surf, pos)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Finger detection
    finger_pos = None
    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0]
        x = int(lm.landmark[8].x * WIDTH)
        y = int(lm.landmark[8].y * HEIGHT)
        finger_pos = (x, y)
        slice_trail.append(finger_pos)
    else:
        slice_trail.clear()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            exit()

    # Draw background
    frame_rgb = cv2.resize(rgb, (WIDTH, HEIGHT))
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    # Draw trail
    if len(slice_trail) > 1:
        trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(len(slice_trail)-1):
            start_pos = slice_trail[i]
            end_pos = slice_trail[i+1]
            pygame.draw.line(trail_surf, (255, 255, 255, 150), start_pos, end_pos, 5)
        screen.blit(trail_surf, (0, 0))

    if finger_pos:
        pygame.draw.circle(screen, (0, 255, 255), finger_pos, 8)

    # Spawn fruits
    current_time = time.time()
    if not game_over and current_time - last_spawn_time > FRUIT_SPAWN_INTERVAL:
        fruits.append(spawn_fruit())
        last_spawn_time = current_time

    # Update and draw fruits
    for fruit in fruits[:]:
        fruit.update()

        if fruit.x < -200 or fruit.x > WIDTH + 200 or fruit.y > HEIGHT + 200:
            if isinstance(fruit, Fruit) and not fruit.is_sliced:
                lives -= 1
            fruits.remove(fruit)
            continue

        fruit.draw(screen)

        # Slice detection
        if not fruit.is_sliced and finger_pos:
            if finger_touches_fruit(finger_pos, fruit.get_rect()):
                try:
                    swipe_angle = 0.0
                    if len(slice_trail) > 1:
                        p1 = slice_trail[-2]
                        p2 = slice_trail[-1]
                        seg_dx = p2[0] - p1[0]
                        seg_dy = p2[1] - p1[1]
                        swipe_angle = math.atan2(seg_dy, seg_dx)
                    
                    halves = fruit.slice(push_dir=(0, -1), swipe_angle_rad=swipe_angle)

                    now = time.time()
                    combo_count = combo_count + 1 if (now - last_slice_time) < COMBO_TIME else 1
                    last_slice_time = now

                    if isinstance(fruit, Bomb):
                        lives -= 1
                        score = max(0, score - 5)
                        if halves:
                            explosions.extend([item for item in halves if isinstance(item, Explosion)])
                            halves = [item for item in halves if not isinstance(item, Explosion)]
                    else:
                        score += 10 * combo_count

                    if fruit in fruits:
                        fruits.remove(fruit)
                    if halves:
                        fruits.extend(halves)
                        
                except Exception:
                    import traceback; traceback.print_exc()

    # Update explosions
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(screen)
        if explosion.is_finished():
            explosions.remove(explosion)

    # HUD
    draw_text(screen, f"Score: {score}", (20, 20))
    draw_text(screen, f"Lives: {lives}", (20, 60))

    if lives <= 0 and not game_over:
        game_over = True

    if game_over:
        draw_text(screen, "GAME OVER", (WIDTH//2 - 100, HEIGHT//2 - 40), (255, 50, 50))
        draw_text(screen, f"Final Score: {score}", (WIDTH//2 - 110, HEIGHT//2 + 10), (255, 255, 255))
        draw_text(screen, "Press ESC to quit", (WIDTH//2 - 110, HEIGHT//2 + 60), (255, 255, 255))

    pygame.display.update()
    clock.tick(FPS)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        break

cap.release()
pygame.quit()