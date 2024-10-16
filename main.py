import requests
import pygame
from random import uniform

from pygame import Vector2
from pygame.sprite import AbstractGroup

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

# Functions


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

    def resolve_collision(self, group: pygame.sprite.Group):
        # Check for collisions with other enemies in the group
        for other in group:
            if other != self:  # Don't check against itself
                distance = ((self.rect.x - other.rect.x) ** 2 + (self.rect.y - other.rect.y) ** 2) ** 0.5

                # If there is overlap (distance < size of one enemy), resolve it
                if distance < self.rect.width:
                    direction = Vector2(self.rect.x - other.rect.x, self.rect.y - other.rect.y).normalize()
                    overlap_distance = self.rect.width - distance
                    # Move this enemy out of the overlap by half the overlap distance
                    self.rect.x += direction.x * overlap_distance / 2
                    self.rect.y += direction.y * overlap_distance / 2
                    # Move the other enemy out by the other half
                    other.rect.x -= direction.x * overlap_distance / 2
                    other.rect.y -= direction.y * overlap_distance / 2

    def update(self, player: Player, enemies: pygame.sprite.Group):
        # Existing movement logic
        distance = ((self.rect.x - player.rect.x) ** 2 + (self.rect.y - player.rect.y) ** 2) ** 0.5
        direction: Vector2 = Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y).normalize()

        if distance > self.min_distance:
            self.rect.x += direction.x * self.speed * dt
            self.rect.y += direction.y * self.speed * dt
        else:
            self.rect.x -= direction.x * self.speed * dt * 0.01
            self.rect.y -= direction.y * self.speed * dt * 0.01

        # Now resolve any overlap with other enemies
        self.resolve_collision(enemies)


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

# Main Loop

player = Player(WIDTH // 2, HEIGHT // 2, 1000)
enemies = pygame.sprite.Group()
running = True
dt = clock.tick(FPS) / 1000

while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[0] == True:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_enemy = Enemy(mouse_x, mouse_y, 100, 100)
            enemies.add(new_enemy)

    # Update
    player.update()
    for enemy in enemies:
        enemy.update(player, enemies)

    # Draw
    screen.fill(GREEN)
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)
    screen.blit(player.image, player.rect)

    # Draw

    # Update
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
