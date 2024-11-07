import json
import time
from operator import contains
from random import uniform, choice, random
import requests
from urllib import parse
import pygame_textinput
import pygame

from classes import Player, Enemy, WeaponDrop, Weapon, MedPack
from config import WIDTH, HEIGHT, FPS
from constants import GREEN
from screens import (
    leader_board_screen,
    start_screen,
    death_screen,
    add_user,
    get_top_users,
    score_font,
    pixelify_sans,
)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("System Override")
clock = pygame.time.Clock()
name = ""
started = False
name_input = pygame_textinput.TextInputVisualizer()
leader_board = False
last_response = 0

player = Player(WIDTH // 2, HEIGHT // 2, 100)
enemies = pygame.sprite.Group()
player_projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()
weapon_drops = pygame.sprite.Group()
med_packs = pygame.sprite.Group()
machine_gun = False
running = True
dt = clock.tick(FPS) / 1000
last_shot = time.time()
just_pressed = False


def spawn_random_enemy():
    new_enemy = Enemy(
        uniform(0, WIDTH), uniform(0, HEIGHT), 50 + (5 * uniform(-3, 3)), 100, 100
    )
    enemies.add(new_enemy)


def spawn_random_weapon_drop():
    new_weapon_drop = WeaponDrop(
        uniform(0, WIDTH), uniform(0, HEIGHT), choice(list(Weapon)), 10
    )
    weapon_drops.add(new_weapon_drop)


def spawn_random_med_pack():
    new_med_pack = MedPack(uniform(0, WIDTH), uniform(0, HEIGHT), 10)
    med_packs.add(new_med_pack)


def play_screen():
    global running, machine_gun, last_shot, just_pressed

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and pygame.mouse.get_pressed(3)[0] == True
            and just_pressed
        ):
            if player.weapon == Weapon.MACHINE_GUN:
                machine_gun = True
            else:
                player.shoot(player_projectiles)
            just_pressed = False
        if (
            event.type == pygame.MOUSEBUTTONUP
            and pygame.mouse.get_pressed(3)[0] == False
        ):
            machine_gun = False
            just_pressed = True

    # random enemy spawn. more likely to spawn if player has a higher score. therefore more spawn if player has a higher score
    if random() < player.score / 1000 + 0.01:
        spawn_random_enemy()
    # random weapon drop spawn
    if random() < 0.001:
        spawn_random_weapon_drop()
    # random med pack spawn
    if random() < 0.0005:
        spawn_random_med_pack()
    # Update
    if machine_gun and time.time() - last_shot > 0.025:
        player.shoot(player_projectiles)
        last_shot = time.time()

    # score text
    score_text = score_font.render(f"Score: {player.score}", True, (0, 0, 0))
    score_rect = score_text.get_rect(topleft=(0, 0))
    high_score_text = score_font.render(
        f"High Score: {player.high_score}", True, (0, 0, 0)
    )
    high_score_rect = high_score_text.get_rect(topleft=(0, 24))

    player.update(dt)
    enemies.update(player, enemies, enemy_projectiles, dt)
    player_projectiles.update(enemies, dt)
    enemy_projectiles.update([player], dt)
    weapon_drops.update(player, screen)
    med_packs.update(player)
    # Draw
    screen.fill(GREEN)
    enemies.draw(screen)
    player_projectiles.draw(screen)
    enemy_projectiles.draw(screen)
    weapon_drops.draw(screen)
    med_packs.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    # Draw
    # Update


while running:
    if not started and not leader_board:
        player.name, started, leader_board, running = start_screen(
            screen, pixelify_sans, name_input, started, leader_board
        )
    elif leader_board:
        last_response, leader_board = leader_board_screen(
            screen, last_response, leader_board
        )
        if not leader_board:
            last_response = 0
    elif player.health > 0 and started:
        play_screen()
    if player.health <= 0 and not leader_board:
        player, running, leader_board, started = death_screen(
            screen, pixelify_sans, player, running
        )
    # Events

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
