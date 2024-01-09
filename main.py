import pygame
import random

# individual.genes=[move1,move2,speed,size,MoveBias1,MoveBias2] veya biaslar ayrı bir arrayde de tutulabilir [MoveBias1,MoveBias2]
# sensory olcuak 4 yanını [0,0,0,0] tarzı bir arrayle görücek 0 ise boş 1 ise dolu demek olucak o grid
# Crossover moveler çapra#mutasyonda movement genleri değişecek speed size a belirli bir aralıkta verilen random sayılar eklenip çıkacak ayrıca biaslarda değişebiliecek mutasyonla

# Constants,

FAUNA_WIDTH, FAUNA_HEIGHT = 640, 640
BUTTON_AREA_WIDTH = 400
FPS = 60
YELLOW = (255, 236, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (109, 206, 70)
LGREEN = (95, 191, 56)
GREY = (194, 194, 194)
BLUE = (0, 0, 255)
LIFE_TIME = 600
Population = 100
time_scale = 1
left_zone = pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, FAUNA_HEIGHT)
right_zone = pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, FAUNA_HEIGHT)
middle_zone = pygame.Rect(FAUNA_WIDTH // 2 - 50, FAUNA_HEIGHT // 2 - 50, 100, 100)
top_left=pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
top_right=pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_left= pygame.Rect(0, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_right = pygame.Rect(0.9 * FAUNA_WIDTH, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
min_time_scale = 0.1
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
            direction1 = directions[random.randint(0, len(directions) - 1)]
            direction2 = directions[random.randint(0, len(directions) - 1)]

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

    def check_collision_zones(self):
        if left_zone.colliderect(self.rect) or right_zone.colliderect(self.rect):
            if top_left.colliderect(self.rect) or top_right.colliderect(self.rect) \
                    or bottom_left.colliderect(self.rect) or bottom_right.colliderect(self.rect):
                self.fitness = 1.0
            else:
                self.fitness = 0.5
        else:
            self.fitness = 0
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
        if partner is None:
            return self
        print("Parent 1 genes:", self.genes)
        print("Parent 2 genes:", partner.genes)

        crossover_point = random.randint(1, len(self.genes) - 2)
        child_genes = self.genes[:crossover_point] + partner.genes[crossover_point:]

        crossover_bias_point = random.randint(1, len(self.genes) - 1)
        child_genes[4:6] = (
                self.genes[4:6][:crossover_bias_point] + partner.genes[4:6][crossover_bias_point:]
        )

        mutation_rate = 0.1
        mutation_range = 0.2
        for i in range(len(child_genes)):
            if isinstance(child_genes[i], (int, float)):  # Check if the gene is an int or float
                if random.random() < mutation_rate:
                    child_genes[i] += random.uniform(-mutation_range, mutation_range)
                    # Ensure that the mutated value stays within bounds
                    if i == 4:  # Handling size gene
                        child_genes[i] = max(0, min(2, child_genes[i]))
                    elif i == 5:  # Handling speed gene
                        child_genes[i] = max(0, min(3, child_genes[i]))

        print("Child genes after mutation:", child_genes)
        return Individual(child_genes)

    def mutate(self, mutation_range=0.2):
        mutation_rate = 0.1
        for i in range(len(self.genes)):
            if isinstance(self.genes[i], (int, float)):  # Check if the gene is an int or float
                if random.random() < mutation_rate:
                    self.genes[i] += random.uniform(-mutation_range, mutation_range)
                    # Ensure that the mutated value stays within bounds
                    if i == 4:  # Handling size gene
                        self.genes[i] = max(0, min(2, self.genes[i]))
                    elif i == 5:  # Handling speed gene
                        self.genes[i] = max(0, min(3, self.genes[i]))

        # Update move biases after mutation
        self.genes[4:6] = [max(0, min(1, val)) for val in self.genes[4:6]]


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


generation_text = "Generation: 0   Speed: 1"

def update_generation(steps):
    global generation_text
    generation_time = steps * time_scale // (FPS * 10)
    generation_text = f"Generation: {int(generation_time)}   " \
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

# Fitness Fonksiyonu
def fitness(ind):
    x, y = ind.rect.x, ind.rect.y

    if left_zone.collidepoint(x, y) or right_zone.collidepoint(x, y):
        return 1.0  # Mavi bölgede ise 1 puan
    elif top_left.collidepoint(x, y) or top_right.collidepoint(x, y) or bottom_left.collidepoint(x, y) or bottom_right.collidepoint(x, y):
        return 0.5  # Yeşil bölgede ise 0.5 puan
    else:
        return 0.0  # Diğer durumlarda 0 puan

def update_fitness_and_remove_dead(steps):
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

    if steps * time_scale % (FPS * 10) == 0:
        update_generation(steps)  # Update the generation text

        new_generation = pygame.sprite.Group()
        for _ in range(Population):
            parents = tournament_selection(fauna_sprites, tournament_size=3)
            if parents is not None:
                parent1, parent2 = parents
                child = parent1.crossover(parent2)
                child.mutate()
                new_generation.add(child)

        fauna_sprites.empty()
        fauna_sprites.add(*new_generation.sprites())

    return total_fitness

def tournament_selection(population, tournament_size):
    selected_parents = []
    for _ in range(2):  # Select two parents for crossover
        if len(population) < tournament_size:
            return None  # Handle the case where the population is smaller than the tournament size
        participants = random.sample(population.sprites(), k=tournament_size)
        selected_parent = max(participants, key=lambda ind: fitness(ind))
        selected_parents.append(selected_parent)

    print("Selected parents genes:")
    for parent in selected_parents:
        print(parent.genes)

    return selected_parents




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
    total_fitness = update_fitness_and_remove_dead(steps)
    steps += 1

    if steps * time_scale % (FPS * 10) == 0:
        generation_text = update_generation(steps)

        new_generation = pygame.sprite.Group()
        for _ in range(Population):
            parents = tournament_selection(fauna_sprites, tournament_size=3)
            if parents is not None:
                parent1, parent2 = parents
                child = parent1.crossover(parent2)
                child.mutate()
                new_generation.add(child)

        fauna_sprites.empty()  # Clear the old generation
        fauna_sprites.add(new_generation.sprites())  # Add the new generation to the existing sprite group

        steps = 0


pygame.quit()
