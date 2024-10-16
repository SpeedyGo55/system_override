import requests
import pygame
from random import randint

# Global Variables
global dt

# Constants

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen
WIDTH, HEIGHT = 800, 600
FPS = 60

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=500):
        super().__init__()
        self.speed = speed
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed * dt

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=500, min_distance=50):
        super().__init__()
        self.min_distance = min_distance
        self.speed = speed
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, player: Player):
        distance = ((self.rect.x - player.rect.x) ** 2 + (self.rect.y - player.rect.y) ** 2) ** 0.5
        if self.rect.x < player.rect.x and distance > self.min_distance:
            self.rect.x += self.speed * dt
        if self.rect.x > player.rect.x and distance > self.min_distance:
            self.rect.x -= self.speed * dt
        if self.rect.y < player.rect.y and distance > self.min_distance:
            self.rect.y += self.speed * dt
        if self.rect.y > player.rect.y and distance > self.min_distance:
            self.rect.y -= self.speed * dt


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

# Main Loop

player = Player(WIDTH // 2, HEIGHT // 2, 1000)
enemies = [None] * 5
for i in range(5):
    enemies[i] = Enemy(randint(0, WIDTH), randint(0, HEIGHT), min_distance=100)
running = True
dt = clock.tick(FPS) / 1000

while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Update
    player.update()
    for enemy in enemies:
        enemy.update(player)

    # Draw
    screen.fill(GREEN)
    screen.blit(player.image, player.rect)
    screen.blit(enemy.image, enemy.rect)

    # Draw

    # Update
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
