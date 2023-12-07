import pygame
import random
# individual.genes=[move1,move2,speed,size,MoveBias1,MoveBias2] veya biaslar ayrı bir arrayde de tutulabilir [MoveBias1,MoveBias2]
#sensory olcuak 4 yanını [0,0,0,0] tarzı bir arrayle görücek 0 ise boş 1 ise dolu demek olucak o grid
#Crossover moveler çapraz şekilde biaslarıyla birlikte alınır sonra speed ve size değerlerinin tek tek ortalamaları alınıp yerleştirilir
#mutasyonda movement genleri değişecek speed size a belirli bir aralıkta verilen random sayılar eklenip çıkacak ayrıca biaslarda değişebiliecek mutasyonla
# Constants
FAUNA_WIDTH, FAUNA_HEIGHT = 800, 800
BUTTON_AREA_WIDTH = 400
FPS = 30
YELLOW = (255,236,0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (109, 206, 70)
LGREEN = (95, 191, 56)
GREY = (194,194,194)
BLUE = (0, 0, 255)
LIFE_TIME = 300
Population=100
time_scale = 1
min_time_scale = 0.1  # Set a minimum time scale to prevent stopping


class Individual(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(YELLOW)  # Green color
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, FAUNA_WIDTH)
        self.rect.y = random.randint(0, FAUNA_HEIGHT)
        self.speed = random.randint(3, 5)
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def update(self):
        self.rect.x += self.direction[0] * self.speed * time_scale
        self.rect.y += self.direction[1] * self.speed * time_scale

        # Collision barrier for the fauna area
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, FAUNA_WIDTH)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, FAUNA_HEIGHT)

def draw_circle(center, radius, surface, color):
    pygame.draw.circle(surface, color, center, radius)

def draw_square(top_left, size, surface, color):
    pygame.draw.rect(surface, color, pygame.Rect(top_left, (size, size)))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text = self.font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def check_hover(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def update_generation(steps):
    generation_time = steps*time_scale // (FPS * 10 )  # Calculate generation time based on FPS (game speed)
    return f"Generation: {int(generation_time)}   "\
           f"Speed: {int(time_scale)}"




class SpeedUpButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def increase_speed(self):
        # This function increases the simulation speed when the button is clicked
        global time_scale
        time_scale = time_scale + 0.1   # Increase the time scale factor within the limit of 1.0

class SlowDownButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def decrease_speed(self):
        # This function decreases the simulation speed when the button is clicked
        global time_scale
        if time_scale > 0.1:
            time_scale = max(min_time_scale,time_scale - 0.1)  # Decrease the time scale factor but not below the minimum


class NormalSpeedButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def reset_speed(self):
        global time_scale
        time_scale = 1
pygame.init()
screen = pygame.display.set_mode((FAUNA_WIDTH + BUTTON_AREA_WIDTH, FAUNA_HEIGHT))
pygame.display.set_caption("Evolution Simulation")
clock = pygame.time.Clock()

fauna_area = pygame.Rect(0, 0, FAUNA_WIDTH, FAUNA_HEIGHT)

fauna_sprites = pygame.sprite.Group()

for _ in range(Population):  # Creating 20 individuals in the fauna area
    ind = Individual()
    fauna_sprites.add(ind)

button1 = Button(FAUNA_WIDTH + 20, 100, 150, 50, "Restart", GREEN, GREEN)
button2 = Button(FAUNA_WIDTH + 20, 200, 150, 50, "Quit", GREEN, GREEN)
slow_down_button = SlowDownButton(FAUNA_WIDTH + 20, 400, 150, 50, "Slow Down", GREEN, GREEN)
normal_speed_button = NormalSpeedButton(FAUNA_WIDTH + 20, 500, 150, 50, "Normal Speed", GREEN, GREEN)
speed_up_button = SpeedUpButton(FAUNA_WIDTH + 20, 300, 150, 50, "Speed Up", GREEN, GREEN)
generation_text = update_generation(0)
corner_zones = [pygame.Rect(0, 0, 100, 100), pygame.Rect(FAUNA_WIDTH - 100, 0, 100, 100),
               pygame.Rect(0, FAUNA_HEIGHT - 100, 100, 100), pygame.Rect(FAUNA_WIDTH - 100, FAUNA_HEIGHT - 100, 100, 100)]
middle_zone = pygame.Rect(FAUNA_WIDTH // 2 - 50, FAUNA_HEIGHT // 2 - 50, 100, 100)

running = True
steps = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_pos = pygame.mouse.get_pos()
    if slow_down_button.check_hover(mouse_pos):
        slow_down_button.color = slow_down_button.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            slow_down_button.decrease_speed()
    else:
        SlowDownButton.color = LGREEN

    if speed_up_button.check_hover(mouse_pos):
        speed_up_button.color = speed_up_button.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            speed_up_button.increase_speed()
    else:
        SpeedUpButton.color = LGREEN

    if normal_speed_button.check_hover(mouse_pos):
        normal_speed_button.color = normal_speed_button.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            normal_speed_button.reset_speed()
    else:
        normal_speed_button.color = LGREEN

    if button1.check_hover(mouse_pos):
        button1.color = button1.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Restart simulation
            steps = 0
            generation_text = update_generation(steps)
            for sprite in fauna_sprites:
                sprite.rect.x = random.randint(0, FAUNA_WIDTH)
                sprite.rect.y = random.randint(0, FAUNA_HEIGHT)
    else:
        button1.color = LGREEN

    if button2.check_hover(mouse_pos):
        button2.color = button2.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            running = False  # Quit the application
    else:
        button2.color = LGREEN




    for ind in fauna_sprites:
        ind.update()

        collision_list = pygame.sprite.spritecollide(ind, fauna_sprites, False)
        for collided in collision_list:
            if collided != ind:
                ind.direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))

    screen.fill(WHITE)
    for zone in corner_zones:
        pygame.draw.rect(screen, RED, zone)

        # Draw green circular zone in the middle
    pygame.draw.ellipse(screen, GREEN, middle_zone)

    fauna_sprites.draw(screen)

    # Draw buttons and text in the dedicated area
    pygame.draw.rect(screen, GREY, pygame.Rect(FAUNA_WIDTH, 0, BUTTON_AREA_WIDTH, FAUNA_HEIGHT))

    button1.draw(screen)
    button2.draw(screen)
    speed_up_button.draw(screen)
    slow_down_button.draw(screen)
    normal_speed_button.draw(screen)

    font = pygame.font.Font(None, 36)
    text = font.render(generation_text, True, WHITE)
    screen.blit(text, (FAUNA_WIDTH + 20, 20))

    pygame.display.flip()
    clock.tick(FPS)
    steps += 1
    if steps*time_scale % (FPS * 10 ) == 0:
        generation_text = update_generation(steps)
pygame.quit()