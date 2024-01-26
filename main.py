import pygame
import random

# Constants,

generation_text = ""
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
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

LIFE_TIME = 5
Population = 100
time_scale = 1
generation_count = 0
percentage_count=0

middle_zone = pygame.Rect(FAUNA_WIDTH // 2 - 50, FAUNA_HEIGHT // 2 - 50, 100, 100)
top_left=pygame.Rect(0, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
top_right=pygame.Rect(0.9 * FAUNA_WIDTH, 0, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_left= pygame.Rect(0, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)
bottom_right = pygame.Rect(0.9 * FAUNA_WIDTH, 0.9 * FAUNA_HEIGHT, 0.1 * FAUNA_WIDTH, 0.1 * FAUNA_HEIGHT)


wall1 = pygame.Rect(80, 110, 10, 390)
wall2 = pygame.Rect(100, 500,400 ,10)
wall3 = pygame.Rect(503, 110, 10, 394)
wall4 = pygame.Rect(100,100,400,10)
min_time_scale = 0.5

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
        if genes is None:
            direction1 = directions[random.randint(0, len(directions) - 1)]
            direction2 = directions[random.randint(0, len(directions) - 1)]

            dominance1 = random.uniform(0, 1)
            dominance2 = 1 - dominance1
            size = random.randint(1, 5)
            speed = random.randint(0, 5)
            self.genes = [direction1, direction2, dominance1, dominance2, size, speed]

            self.direction = [(direction1[0], direction1[1])]
        else:
            self.genes = genes
            self.direction = [(self.genes[0], self.genes[1])]

        self.loop_direction = True
        self.dominance = self.genes[2:4]
        self.size = self.genes[4]
        self.speed = self.genes[5]
        self.direction1 = self.genes[1]
        self.direction2= self.genes[0]
        self.fitness = 0.0
        direction_color_mapping = {
            (0, 1): BLUE,
            (0, -1): RED,
            (1, 0): GREEN,
            (-1, 0): YELLOW,
            (1, -1):    CYAN,
            (-1, -1): MAGENTA,
            (1, 1):ORANGE,
            (-1, 1):PURPLE
        }

        # Choose the color based on the given directions
        color1 = direction_color_mapping.get((self.direction1[0], self.direction1[1]), WHITE)
        color2 = direction_color_mapping.get((self.direction2[0], self.direction2[1]), WHITE)

        # Blend the colors to create a visual representation
        blended_color = (
            (color1[0] + color2[0]) // 2,
            (color1[1] + color2[1]) // 2,
            (color1[2] + color2[2]) // 2
        )
        self.initialized = False
        self.image = pygame.Surface((self.size * 8, self.size * 8))
        self.image.fill(blended_color)



        self.rect = self.image.get_rect()
        self.rect.x = random.randint(FAUNA_WIDTH // 3, 3 * FAUNA_WIDTH // 6)
        self.rect.y = random.randint(FAUNA_HEIGHT // 3, 3 * FAUNA_HEIGHT // 6)
        self.loop_counter = 0
        self.loop_duration = 10

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

        # Check for collisions with walls and adjust position
        if wall1.colliderect(self.rect):
            self.rect.left = max(self.rect.left, wall1.right)
        elif wall3.colliderect(self.rect):
            self.rect.right = min(self.rect.right, wall3.left)
        elif wall2.colliderect(self.rect):
            self.rect.bottom = max(self.rect.top, wall2.top)  # Adjusted this line
            self.direction1, self.direction2 = self.direction2, self.direction1  # Switch directions
        elif wall4.colliderect(self.rect):
            self.rect.top = max(self.rect.top, wall4.bottom)

        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= FAUNA_WIDTH:
            self.rect.right = FAUNA_WIDTH

        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= FAUNA_HEIGHT:
            self.rect.bottom = FAUNA_HEIGHT

        if self.speed == 0:
            self.loop_counter += 1
            if self.loop_counter >= self.loop_duration:
                self.loop_direction = not self.loop_direction  # Switch directions
                self.loop_counter = 0

        self.check_collision_zones()

    def check_collision_zones(self):
        if top_left.colliderect(self.rect) or top_right.colliderect(self.rect) \
                or bottom_left.colliderect(self.rect) or bottom_right.colliderect(self.rect):
            self.fitness = 1.0
        else:
            self.fitness = 0.0  # Make sure to set it to 0 if not in the desired zones

        if wall4.colliderect(self.rect)  or wall2.colliderect(self.rect)  or wall1.colliderect(self.rect)  or wall3.colliderect(self.rect) or self.rect.left <= 0 or self.rect.right >= FAUNA_WIDTH or self.rect.top <= 0 or self.rect.bottom >= FAUNA_HEIGHT:
            self.handle_collision()
        for other_individual in fauna_sprites:
            if other_individual != self and pygame.sprite.collide_rect(self, other_individual):
                self.handle_collision_with_individual(other_individual)

    def handle_collision(self):
        # Switch between direction1 and direction2 when a collision occurs or when the individual hits a wall
        self.direction1, self.direction2 = self.direction2, self.direction1

        active_direction = self.direction1

        # Update the direction based on collisions
        for collided in collision_list:
            if collided != self:
                # Switch to the other direction when a collision occurs
                active_direction = self.direction2 if active_direction == self.direction1 else self.direction1

        # Ensure that self.direction is consistently a list containing a tuple
        self.direction = [(active_direction[0], active_direction[1])]

    def handle_collision_with_individual(self, other_individual):
        # Switch between direction1 and direction2 when a collision occurs with another individual
        self.direction1, self.direction2 = self.direction2, self.direction1

        active_direction = self.direction1

        # Ensure that self.direction is consistently a list containing a tuple
        self.direction = [(active_direction[0], active_direction[1])]

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
            else:
                preferred_x, preferred_y = secondary_x, secondary_y

            self.loop_counter += 1
            if self.loop_counter >= self.loop_duration:
                self.loop_direction = not self.loop_direction  # Switch directions
                self.loop_counter = 0

        # Apply preferred direction to movement
        movement_x = preferred_x * primary_speed
        movement_y = preferred_y * primary_speed

        return movement_x, movement_y

    def crossover(self, partner):
        if partner is None:
            return self
        print("Parent 1 genes:", self.genes, "Parent 1 fitness:", self.fitness)
        print("Parent 2 genes:", partner.genes, "Parent 2 fitness:", self.fitness)
        crossover_point = random.randint(1, len(self.genes) - 2)

        # Create a new list for child_genes to avoid referencing the existing lists
        child_genes = self.genes[:crossover_point] + partner.genes[crossover_point:].copy()

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

    def mutate(self, mutation_rate=0.05, mutation_range=0.2):
        mutated_genes = self.genes.copy()

        for i in range(len(mutated_genes)):
            if isinstance(mutated_genes[i], (int, float)):
                if random.random() < mutation_rate:
                    mutation_amount = random.uniform(-mutation_range, mutation_range)

                    if i == 0:
                        mutated_genes[i] = random.choice(directions)
                    elif i == 1:
                        mutated_genes[i] = random.choice(directions)
                    elif i == 4:  # Handling size gene
                        # Ensure size stays within [0, 2]
                        mutated_genes[i] = max(2, min(6, mutated_genes[i] + mutation_amount))
                    elif i == 5:  # Handling speed gene
                        # Ensure speed stays within [0, 6]
                        mutated_genes[i] = max(0, min(5, mutated_genes[i] + mutation_amount))

        # Update move biases after mutation
        mutated_genes[4:6] = [max(0, min(5, val)) for val in mutated_genes[4:6]]
        print("mutated")
        return Individual(mutated_genes)


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
    global generation_count, percentage_count, Population
    perc = (percentage_count * 100) // (Population * (generation_count + 1))

    generation_text = f"Generation: {generation_count-2}   " \
                      f"Speed: {int(time_scale)}" \
                      f" P: {int(perc)}%"

    generation_count += 1  # Increment generation_count here
    percentage_count = 0  # Reset percentage_count for the next generation

    return generation_text





class SpeedUpButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def increase_speed(self):
        global time_scale
        time_scale = min(2.0, time_scale + 0.1)


class SlowDownButton(Button):
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        super().__init__(x, y, width, height, text, color, hover_color, action)

    def decrease_speed(self):
        global time_scale
        min_time_scale = 0.1  # Set your desired minimum time scale here
        percentage_threshold = 0.2  # Set your desired percentage threshold here

        new_time_scale = max(min_time_scale, time_scale - 0.1)

        if new_time_scale / time_scale < percentage_threshold:
            # Avoid slowing down too much, keep it moving by a certain percentage
            time_scale = time_scale * (1 - percentage_threshold)
        else:
            time_scale = new_time_scale



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
    global percentage_count
    total_fitness = 0.0
    dead_individuals = []

    for ind in fauna_sprites:
        if steps > 0:  # Add this check to skip updating fitness in the first generation
            ind.update()

        ind_fitness = fitness(ind)
        total_fitness += ind_fitness

        if steps >= LIFE_TIME * FPS:
            dead_individuals.append(ind)

    # Calculate the percentage of surviving individuals
    percentage_count = int(len(fauna_sprites) / Population * 100)

    for dead_ind in dead_individuals:
        fauna_sprites.remove(dead_ind)

    if steps % (LIFE_TIME * FPS // time_scale) == 0 and steps > 0:
        global generation_count
        generation_text = update_generation(steps)  # Update generation_text here

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

        total_individuals = len(fauna_sprites)
        print(f"Percentage of surviving individuals: {percentage_count:.2f}%")

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
steps = 0
update_generation(steps)
generation_text = update_generation(steps)
generation_count += 1

running = True
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

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, top_right)
    pygame.draw.rect(screen, BLUE, top_left)
    pygame.draw.rect(screen, BLUE, bottom_left)
    pygame.draw.rect(screen, BLUE, bottom_right)
    pygame.draw.rect(screen, BLACK, wall1)
    pygame.draw.rect(screen, BLACK, wall2)
    pygame.draw.rect(screen, BLACK, wall3)
    pygame.draw.rect(screen, BLACK, wall4)

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

    # Update the percentage text
    percentage_text = f"Percentage: {percentage_count:.2f}%"
    text = font.render(percentage_text, True, WHITE)
    screen.blit(text, (FAUNA_WIDTH + 20, 60))

    pygame.display.flip()
    clock.tick(FPS)

    total_fitness = update_fitness_and_remove_dead(steps)
    steps += 1

    if steps % (LIFE_TIME * FPS // time_scale) == 0:
        print("works")
        new_generation = pygame.sprite.Group()
        for _ in range(Population):
            parents = tournament_selection(fauna_sprites, tournament_size=3)
            if parents is not None:
                parent1, parent2 = parents
                child = parent1.crossover(parent2)
                child.mutate()
                new_generation.add(child)

        generation_text = update_generation(steps) # Update generation_text here
        fauna_sprites.empty()
        fauna_sprites.add(new_generation.sprites())
        steps = 0

pygame.quit()