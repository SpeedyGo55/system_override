import requests
import pygame
from classes import Player, Enemy

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



# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

# Main Loop

player = Player(WIDTH // 2, HEIGHT // 2, 100)
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
            new_enemy = Enemy(mouse_x, mouse_y, 75, 100, 30)
            enemies.add(new_enemy)

    # Update
    player.update(dt)
    enemies.update(player, enemies, dt)

    # Draw
    screen.fill(GREEN)
    enemies.draw(screen)
    screen.blit(player.image, player.rect)

    # Draw

    # Update
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
