import time
from random import uniform, random

import requests
import pygame
from classes import *

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
projectiles = pygame.sprite.Group()
weapon_drops = pygame.sprite.Group()
machine_gun = False
running = True
dt = clock.tick(FPS) / 1000
last_shot = time.time()
while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[0] == True:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_enemy = Enemy(mouse_x, mouse_y, 75, 100, 100)
            enemies.add(new_enemy)
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[1] == True:
            new_drop = WeaponDrop(uniform(0, WIDTH), uniform(0, HEIGHT), Weapon.MACHINE_GUN)
            weapon_drops.add(new_drop)
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[2] == True:
            if player.weapon == Weapon.MACHINE_GUN:
                machine_gun = True
            player.shoot(projectiles)
        if event.type == pygame.MOUSEBUTTONUP and pygame.mouse.get_pressed(3)[2] == False:
            machine_gun = False

    # Update
    if machine_gun and time.time() - last_shot > 0.025:
        player.shoot(projectiles)
        last_shot = time.time()
    player.update(dt)
    enemies.update(player, enemies, dt)
    projectiles.update(enemies, dt)

    # Draw
    screen.fill(GREEN)
    enemies.draw(screen)
    projectiles.draw(screen)
    screen.blit(player.image, player.rect)

    # Draw

    # Update
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
