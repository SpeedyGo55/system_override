import time
from random import uniform, choice

import pygame

from classes import Player, Enemy, WeaponDrop, Weapon
from config import WIDTH, HEIGHT, FPS
from constants import GREEN

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pygame Template")
pixelify_sans = pygame.font.Font("Fonts/PixelifySans.ttf", 32)
clock = pygame.time.Clock()


# Main Loop
def play_screen():
    global running, machine_gun, last_shot
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and pygame.mouse.get_pressed(3)[0] == True
        ):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_enemy = Enemy(mouse_x, mouse_y, 75, 100, 100)
            enemies.add(new_enemy)
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and pygame.mouse.get_pressed(3)[1] == True
        ):
            new_drop = WeaponDrop(
                uniform(0, WIDTH), uniform(0, HEIGHT), choice(list(Weapon))
            )
            weapon_drops.add(new_drop)
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and pygame.mouse.get_pressed(3)[2] == True
        ):
            if player.weapon == Weapon.MACHINE_GUN:
                machine_gun = True
            else:
                player.shoot(player_projectiles)
        if (
            event.type == pygame.MOUSEBUTTONUP
            and pygame.mouse.get_pressed(3)[2] == False
        ):
            machine_gun = False
    # Update
    if machine_gun and time.time() - last_shot > 0.025:
        player.shoot(player_projectiles)
        last_shot = time.time()
    player.update(dt)
    enemies.update(player, enemies, enemy_projectiles, dt)
    player_projectiles.update(enemies, dt)
    enemy_projectiles.update([player], dt)
    weapon_drops.update(player, screen)
    # Draw
    screen.fill(GREEN)
    enemies.draw(screen)
    player_projectiles.draw(screen)
    enemy_projectiles.draw(screen)
    weapon_drops.draw(screen)
    screen.blit(player.image, player.rect)
    # Draw
    # Update


def death_screen():
    global screen, pixelify_sans, player, running
    screen.fill(GREEN)
    again_text = pixelify_sans.render(
        "Try Again",
        True,
        (0, 0, 0),
    )
    again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_text = pixelify_sans.render("Quit", True, (0, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if again_rect.collidepoint(mouse_x, mouse_y):
                player = Player(WIDTH // 2, HEIGHT // 2, 100)
                enemies.empty()
                enemy_projectiles.empty()
                player_projectiles.empty()
                weapon_drops.empty()
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                running = False

    screen.blit(quit_text, quit_rect)
    screen.blit(again_text, again_rect)


player = Player(WIDTH // 2, HEIGHT // 2, 100)
enemies = pygame.sprite.Group()
player_projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()
weapon_drops = pygame.sprite.Group()
machine_gun = False
running = True
dt = clock.tick(FPS) / 1000
last_shot = time.time()

while running:
    if player.health <= 0:
        death_screen()
    # Events
    if player.health > 0:
        play_screen()

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
