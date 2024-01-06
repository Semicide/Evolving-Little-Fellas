import pygame
import random

# individual.genes=[move1,move2,speed,size,MoveBias1,MoveBias2] veya biaslar ayrı bir arrayde de tutulabilir [MoveBias1,MoveBias2]
# sensory olcuak 4 yanını [0,0,0,0] tarzı bir arrayle görücek 0 ise boş 1 ise dolu demek olucak o grid
# Crossover moveler çapra#mutasyonda movement genleri değişecek speed size a belirli bir aralıkta verilen random sayılar eklenip çıkacak ayrıca biaslarda değişebiliecek mutasyonla

# Constants,

FAUNA_WIDTH, FAUNA_HEIGHT = 640, 640
BUTTON_AREA_WIDTH = 400
FPS = 30
YELLOW = (255, 236, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (109, 206, 70)
LGREEN = (95, 191, 56)
GREY = (194, 194, 194)
BLUE = (0, 0, 255)
LIFE_TIME = 300
Population = 100
time_scale = 1
min_time_scale = 0.1  # Set a minimum time scale to prevent stopping
r = [0, 1]
l = [0, -1]
u = [1, 0]
d = [-1, 0]
directions = [r,l,u,d]


class Individual(pygame.sprite.Sprite):
    def __init__(self, genes=None):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, FAUNA_WIDTH)
        self.rect.y = random.randint(0, FAUNA_HEIGHT)
        self.loop_direction = False
        self.loop_counter = 0
        self.loop_duration = 50  # You can adjust this value based on your desired loop duration

        # Initialize genes
        # Inside the __init__ method of the Individual class
        if genes is None:
            direction1 = random.choice(directions)
            direction2 = random.choice(directions)
            dominance1 = random.uniform(0, 1)
            dominance2 = 1 - dominance1
            size = random.randint(0, 2)
            speed = random.randint(0, 3)
            self.genes = [direction1, direction2, dominance1, dominance2, size, speed]

            # Ensure that self.direction is consistently a list containing a tuple
            self.direction = [(direction1[0], direction1[1])]
        else:
            self.genes = genes
            self.direction = [(self.genes[0], self.genes[1])]

        # Extract biases from genes
        self.dominance = self.genes[2:4]  # Ensure that self.dominance has two elements
        self.size = self.genes[4]
        self.speed = self.genes[5]
        self.direction1 = self.genes[1]
        self.direction2= self.genes[0]
        self.fitness = 0.0
    # Inside the Individual class
    def update(self):
        movement_x, movement_y = self.move()
        print(movement_x,movement_y,type(movement_x))
        self.rect.x += int(movement_x * time_scale)  # Ensure the result is an integer
        self.rect.y += int(movement_y * time_scale)  # Ensure the result is an integer
        self.fitness = fitness(self)
        # Collision barrier for the fauna area
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, FAUNA_WIDTH)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, FAUNA_HEIGHT)
    # Inside the Individual class
    def move(self):
        # Update direction based on dominance
        if self.dominance[1] > self.dominance[0]:
            preferred_x, preferred_y = self.direction1[0], self.direction1[1]
            secondary_x, secondary_y = self.direction2[0], self.direction2[1]
            primary_speed = self.speed
        else:
            preferred_x, preferred_y = self.direction2[0], self.direction2[1]
            secondary_x, secondary_y = self.direction1[0], self.direction1[1]
            primary_speed = self.speed

        # Handle speed 0 and looping
        if self.speed == 0:
            if self.loop_direction:
                preferred_x, preferred_y, secondary_x, secondary_y = secondary_x, secondary_y, preferred_x, preferred_y
                self.loop_counter += 1
                if self.loop_counter >= self.loop_duration:
                    self.loop_direction = False
                    self.loop_counter = 0
            else:
                preferred_x, preferred_y = secondary_x, secondary_y

        # Apply preferred direction to movement
        movement_x = preferred_x * primary_speed
        movement_y = preferred_y * primary_speed

        return movement_x, movement_y

    def crossover(self, partner):
        # Ebeveynlerin None olup olmadığını kontrol et
        if partner is None:
            return self  # Eğer partner None ise, kendini döndür

        # Crossover genes
        crossover_point = random.randint(1, len(self.genes) - 2)
        child_genes = self.genes[:crossover_point] + partner.genes[crossover_point:]

        # Crossover move biases
        crossover_bias_point = random.randint(1, len(self.move_biases) - 1)
        child_genes[4:6] = self.move_biases[:crossover_bias_point] + partner.move_biases[crossover_bias_point:]

        # Mutate size and speed
        mutation_range = 2
        child_genes[2] = (self.genes[2] + partner.genes[2]) / 2 + random.uniform(-mutation_range, mutation_range)
        child_genes[3] = (self.genes[3] + partner.genes[3]) / 2 + random.uniform(-mutation_range, mutation_range)

        return Individual(child_genes)

    def mutate(self, mutation_range=0.2):
        mutation_rate = 0.1
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] += random.uniform(-mutation_range, mutation_range)

        # Update move biases after mutation
        self.move_biases = self.genes[4:6]




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
    generation_time = steps * time_scale // (FPS * 10)  # Calculate generation time based on FPS (game speed)
    return f"Generation: {int(generation_time)}   " \
           f"Speed: {int(time_scale)}"


class SpeedUpButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def increase_speed(self):
        # This function increases the simulation speed when the button is clicked
        global time_scale
        time_scale = time_scale + 0.1  # Increase the time scale factor within the limit of 1.0


class SlowDownButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def decrease_speed(self):
        # This function decreases the simulation speed when the button is clicked
        global time_scale
        if time_scale > 0.1:
            time_scale = max(min_time_scale,
                             time_scale - 0.1)  # Decrease the time scale factor but not below the minimum


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
left_zone = pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, FAUNA_HEIGHT)
right_zone = pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, FAUNA_HEIGHT)
middle_zone = pygame.Rect(FAUNA_WIDTH // 2 - 50, FAUNA_HEIGHT // 2 - 50, 100, 100)
top_left=pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
top_right=pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_left= pygame.Rect(0, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_right = pygame.Rect(0.9 * FAUNA_WIDTH, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)

# Fitness Fonksiyonu
def fitness(ind):
    x, y = ind.rect.x, ind.rect.y

    if left_zone.collidepoint(x, y) or right_zone.collidepoint(x, y):
        return 1.0  # Mavi bölgede ise 1 puan
    elif top_left.collidepoint(x, y) or top_right.collidepoint(x, y) or bottom_left.collidepoint(x, y) or bottom_right.collidepoint(x, y):
        return 0.5  # Yeşil bölgede ise 0.5 puan
    else:
        return 0.0  # Diğer durumlarda 0 puan

# Oyun döngüsünde fitness değerlerini topla ve ölü yaratıkları çıkar
def update_fitness_and_remove_dead():
    total_fitness = 0
    dead_individuals = []

    for ind in fauna_sprites:
        ind.update()

        collision_list = pygame.sprite.spritecollide(ind, fauna_sprites, False)
        for collided in collision_list:
            if collided != ind:
                ind.direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))

        ind_fitness = fitness(ind)
        total_fitness += ind_fitness

        if steps >= LIFE_TIME:  # Yaşam süresi sona erdiğinde
            dead_individuals.append(ind)

    for dead_ind in dead_individuals:
        fauna_sprites.remove(dead_ind)

    return total_fitness
def tournament_selection(population, tournament_size):
    # Popülasyon sayısından küçük bir turnuva boyutu belirleyelim
    tournament_size = min(tournament_size, len(population.sprites()))

    # Popülasyon büyüklüğü turnuva boyutundan küçükse, turnuva boyutunu popülasyon büyüklüğüne ayarla
    if tournament_size > len(population.sprites()):
        tournament_size = len(population.sprites())

    # Turnuva seçimi ile örnek seçme
    participants = random.sample(population.sprites(), k=tournament_size)

    # Eğer populasyon boşsa veya seçilen bireylerden herhangi birisi None ise, hata almamak için None döndür
    if not participants or None in participants:
        return None

    return max(participants, key=lambda ind: fitness(ind))


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
        slow_down_button.color = LGREEN

    if speed_up_button.check_hover(mouse_pos):
        speed_up_button.color = speed_up_button.hover_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            speed_up_button.increase_speed()
    else:
        speed_up_button.color = LGREEN

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
    pygame.draw.rect(screen, GREEN, left_zone)
    pygame.draw.rect(screen, GREEN, right_zone)
    pygame.draw.rect(screen, BLUE, top_right)
    pygame.draw.rect(screen, BLUE,top_left)
    pygame.draw.rect(screen, BLUE,bottom_left)
    pygame.draw.rect(screen, BLUE,bottom_right)

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
    total_fitness = update_fitness_and_remove_dead()

    if steps * time_scale % (FPS * 10) == 0:
        generation_text = update_generation(steps)

        # Yeni nesli başlat
        new_generation = pygame.sprite.Group()
        for _ in range(Population):
            # Turnuva seçimi ile ebeveynleri seç
            parents = [tournament_selection(fauna_sprites, tournament_size=3) for _ in range(2)]

            # Ebeveynler arasında çaprazlama ve mutasyon
            child = parents[0].crossover(parents[1])
            child.mutate()
            new_generation.add(child)

        fauna_sprites = new_generation  # Eski nesnenin yerine yeni nesneyi ata
        steps = 0

pygame.quit()
