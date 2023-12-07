import pygame
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('TkAgg')
# Pygame setup
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ENTITY_RADIUS = 10
ENTITY_COLOR = (255, 0, 0)
FOOD_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (255, 255, 255)
FOOD_RADIUS = 5

# Matplotlib setup
fig, axs = plt.subplots(3, 1, figsize=(8, 6))
generation_counter = 0

class Entity:
    def __init__(self):
        self.speed = random.uniform(1.0, 5.0)
        self.size = random.uniform(10.0, 30.0)
        self.position = [random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT)]
        self.cloning_probability = random.uniform(0.1, 1.0)  # Added cloning_probability attribute

    def move(self):
        self.position[0] += self.speed * random.uniform(-1, 1)
        self.position[1] += self.speed * random.uniform(-1, 1)

        # Keep entities within bounds
        self.position[0] = max(0, min(SCREEN_WIDTH, self.position[0]))
        self.position[1] = max(0, min(SCREEN_HEIGHT, self.position[1]))

    def draw(self, screen):
        pygame.draw.circle(screen, ENTITY_COLOR, (int(self.position[0]), int(self.position[1])), int(self.size))

    def is_collision(self, food_position):
        distance = ((self.position[0] - food_position[0]) ** 2 + (self.position[1] - food_position[1]) ** 2) ** 0.5
        return distance < (self.size + FOOD_RADIUS)

    def consume_food(self):
        self.size += random.uniform(1, 5)  # Adjust the growth factor as needed

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Entity Simulation')

# Main simulation loop
entities = [Entity() for _ in range(10)]
food_positions = [(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT)) for _ in range(5)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    # Draw and move entities
    for entity in entities:
        entity.move()
        entity.draw(screen)

    # Draw food
    for food_position in food_positions:
        pygame.draw.circle(screen, FOOD_COLOR, (int(food_position[0]), int(food_position[1])), FOOD_RADIUS)

    # Check for collisions with food
    for entity in entities:
        for food_position in food_positions:
            if entity.is_collision(food_position):
                entity.consume_food()

    pygame.display.flip()

# Matplotlib plots
def plot_population_stats(frame):
    global generation_counter
    generation_counter += 1

    speeds = [entity.speed for entity in entities]
    sizes = [entity.size for entity in entities]
    cloning_probs = [entity.cloning_probability for entity in entities]

    axs[0].hist(speeds, bins=20, alpha=0.7, color='blue')
    axs[0].set_title(f'Generation {generation_counter} - Speed Distribution')

    axs[1].hist(sizes, bins=20, alpha=0.7, color='green')
    axs[1].set_title(f'Generation {generation_counter} - Size Distribution')

    axs[2].hist(cloning_probs, bins=20, alpha=0.7, color='red')
    axs[2].set_title(f'Generation {generation_counter} - Cloning Probability Distribution')

    plt.tight_layout()

# Run Matplotlib animation
animation = FuncAnimation(fig, plot_population_stats, frames=50, repeat=False)
plt.show()

pygame.quit()
