import pygame
import random

# Constants,
steps =0
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
LIFE_TIME = 10
Population = 100
time_scale = 1
generation_count = 1
percentage_count=0
middle_zone = pygame.Rect(FAUNA_WIDTH // 2 - 50, FAUNA_HEIGHT // 2 - 50, 100, 100)
top_left=pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
top_right=pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_left= pygame.Rect(0, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_right = pygame.Rect(0.9 * FAUNA_WIDTH, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
# Add wall rectangles
wall1 = pygame.Rect(100, 200, 20, 200)

wall3 = pygame.Rect(500, 200, 20, 200)

min_time_scale = 0.1
r = [0, 1]
l = [0, -1]
u = [1, 0]
d = [-1, 0]
ur = [1, -1]
ul = [-1, -1]
dr = [1, 1]
dl = [-1, 1]
directions = [r,l,u,d,ur,ul,dr,dl]


class Individual(pygame.sprite.Sprite):
    def __init__(self, genes=None):
        super().__init__()
        self.image = pygame.Surface((8,8))
        self.image.fill(YELLOW)
        # Update the initialization of rect for a spawn area in the middle
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(FAUNA_WIDTH // 3, 3 * FAUNA_WIDTH // 6)
        self.rect.y = random.randint(FAUNA_HEIGHT // 3, 3 * FAUNA_HEIGHT // 6)
        self.loop_direction = False
        self.loop_counter = 0
        self.loop_duration = 10  # You can adjust this value based on your desired loop duration

        # Initialize genes
        # Inside the __init__ method of the Individual class
        if genes is None:
            direction1 = directions[random.randint(0, len(directions) - 1)]
            direction2 = directions[random.randint(0, len(directions) - 1)]

            dominance1 = random.uniform(0, 1)
            dominance2 = 1 - dominance1
            size = random.randint(0, 2)
            speed = random.randint(0, 5)
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
        # Flag to prevent automatic crossover at the start
        self.initialized = False
    # Inside the Individual class

    # Remove one of the duplicate update methods
    def update(self):
        movement_x, movement_y = self.move()
        self.rect.x += int(movement_x * time_scale)
        self.rect.y += int(movement_y * time_scale)
        self.fitness = fitness(self)

        # Collision barrier for the fauna area
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, FAUNA_WIDTH)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, FAUNA_HEIGHT)

        # Check for collisions with walls
        if wall1.colliderect(self.rect)  or wall3.colliderect(self.rect):
            self.handle_collision()
        if not self.initialized:
            self.initialized = True
            return  # Skip the update for the first frame to avoid automatic crossover

        if self.speed == 0:
            if self.loop_direction:
                self.loop_counter += 1
                if self.loop_counter >= self.loop_duration:
                    self.loop_direction = False
                    self.loop_counter = 0
            else:
                self.loop_direction = True
                self.direction1, self.direction2 = self.direction2, self.direction1  # Switch directions

        self.check_collision_zones()

    def check_collision_zones(self):
        if top_left.colliderect(self.rect) or top_right.colliderect(self.rect) \
                or bottom_left.colliderect(self.rect) or bottom_right.colliderect(self.rect):
            self.fitness = 1.0
        else:
            self.fitness = 0.0  # Make sure to set it to 0 if not in the desired zones

        if self.rect.left <= 0 or self.rect.right >= FAUNA_WIDTH or self.rect.top <= 0 or self.rect.bottom >= FAUNA_HEIGHT:
            self.handle_collision()

    def handle_collision(self):
        # Switch between direction1 and direction2 when a collision occurs or when the individual hits a wall
        self.direction1, self.direction2 = self.direction2, self.direction1

        # Initially, set the direction1 as active
        active_direction = self.direction1

        # Update the direction based on collisions
        for collided in collision_list:
            if collided != self:
                # Switch to the other direction when a collision occurs
                active_direction = self.direction2 if active_direction == self.direction1 else self.direction1

        # Ensure that self.direction is consistently a list containing a tuple
        self.direction = [(active_direction[0], active_direction[1])]

    # Inside the Individual class

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
        print("Parent 1 genes:", self.genes,"Parent 1 fitness:",self.fitness)
        print("Parent 2 genes:", partner.genes,"Parent 2 fitness:",self.fitness)
        crossover_point = random.randint(1, len(self.genes) - 2)
        # Crossover for gene0 and gene1 (directions)
        child_genes = self.genes[:crossover_point] + partner.genes[crossover_point:]
        # Crossover for gene2 and gene3 (dominance values)
        crossover_bias_point = random.randint(1, len(self.genes) - 1)
        child_genes[2:4] = (
                self.genes[2:4][:crossover_bias_point] + partner.genes[2:4][crossover_bias_point:]
        )
        # Crossover for gene4 and gene5 (size and speed values)
        crossover_bias_point = random.randint(1, len(self.genes) - 1)
        child_genes[4] = random.choice([self.genes[4], partner.genes[4]])
        child_genes[5] = random.choice([self.genes[5], partner.genes[5]])

        # Mutation code remains the same...
        print("Child genes after mutation:", child_genes)
        return Individual(child_genes)

    def mutate(self, mutation_range=0.2):
        mutation_rate = 0.05
        for i in range(len(self.genes)):
            if isinstance(self.genes[i], (int, float)):  # Check if the gene is an int or float
                if random.random() < mutation_rate:
                    self.genes[i] += random.uniform(-mutation_range, mutation_range)
                    # Ensure that the mutated value stays within bounds
                    if i==0:
                        self.genes[i]=random.selection(directions)
                    elif i==1:
                        self.genes[i]=random.selection(directions)
                    elif i == 4:  # Handling size gene
                        self.genes[i] = max(0, min(2, self.genes[i]))
                    elif i == 5:  # Handling speed gene
                        self.genes[i] = max(0, min(20, self.genes[i]))

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



def update_generation(steps):
    global generation_text, generation_count, percentage_count, Population
    perc = (percentage_count * 100) // (Population * (generation_count + 1))

    generation_text = f"Generation: {generation_count}   " \
                      f"Speed: {int(time_scale)}" \
                      f" P: {int(perc)}%"

    generation_count =+ 1  # Move this line here to increment after updating generation_text








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
update_generation(steps)  # Ensure this line is present


def restart_simulation():
    global steps, generation_count, time_scale

    generation_text = update_generation(steps)

# Fitness Fonksiyonu
def fitness(ind):
    x, y = ind.rect.x, ind.rect.y
    if top_left.collidepoint(x, y) or top_right.collidepoint(x, y) or bottom_left.collidepoint(x, y) or bottom_right.collidepoint(x, y):
        return 1.0  # Yeşil bölgede ise 0.5 puan
    else:
        return 0.0  # Diğer durumlarda 0 puan
def update_fitness_and_remove_dead(steps):
    total_fitness = 0.0
    dead_individuals = []

    for ind in fauna_sprites:
        if steps > 0:  # Add this check to skip updating fitness in the first generation
            ind.update()

        collision_list = pygame.sprite.spritecollide(ind, fauna_sprites, False)

        ind_fitness = fitness(ind)
        total_fitness += ind_fitness

        if steps >= LIFE_TIME * FPS:
            dead_individuals.append(ind)

    for dead_ind in dead_individuals:
        fauna_sprites.remove(dead_ind)

    if steps % (LIFE_TIME * FPS // time_scale) == 0 and steps > 0:
        global percentage_count
        generation_text = update_generation(steps)

        print("works")
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

        accuracy = total_fitness / Population

        for ind in fauna_sprites:
            if ind.fitness > 0:
                percentage_count += 1

        print(f"Generation {generation_count}: Accuracy = {accuracy * 100:.2f}%")

    return total_fitness


def tournament_selection(population, tournament_size):
    selected_parents = []

    if len(population) < tournament_size:
        return None  # Handle the case where the population is smaller than the tournament size

    # Select the top 50% of the population based on fitness
    sorted_population = sorted(population.sprites(), key=lambda ind: fitness(ind), reverse=True)
    top_half = sorted_population[:len(sorted_population)//2]

    # Select two parents for crossover from the top 50%
    for _ in range(2):
        participants = random.sample(top_half, k=tournament_size)
        selected_parent = max(participants, key=lambda ind: fitness(ind))
        selected_parents.append(selected_parent)

    return selected_parents






# Add this block of code to initialize and update generation_count before entering the main loop
update_generation(steps)
generation_count += 1

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
    pygame.draw.rect(screen, BLUE, top_right)
    pygame.draw.rect(screen, BLUE,top_left)
    pygame.draw.rect(screen, BLUE,bottom_left)
    pygame.draw.rect(screen, BLUE,bottom_right)
    pygame.draw.rect(screen, BLACK, wall1)
    pygame.draw.rect(screen, BLACK, wall3)

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
    print(steps)

    if steps % (LIFE_TIME * FPS  // time_scale) == 0:
        print ("works")
        new_generation = pygame.sprite.Group()
        for _ in range(Population):
            parents = tournament_selection(fauna_sprites, tournament_size=3)
            if parents is not None:
                parent1, parent2 = parents
                child = parent1.crossover(parent2)
                child.mutate()
                new_generation.add(child)

        generation_count += 1
        fauna_sprites.empty()  # Clear the old generation
        fauna_sprites.add(new_generation.sprites())  # Add the new generation to the existing sprite group

        steps = 0


pygame.quit()