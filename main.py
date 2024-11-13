import time
from random import random
import pygame_textinput
import pygame

from classes import Player, Weapon
from config import WIDTH, HEIGHT, FPS
from screens import (
    leader_board_screen,
    start_screen,
    death_screen,
    score_font,
    game_font,
)
from tools import (
    map_val,
    spawn_random_enemy,
    spawn_random_weapon_drop,
    spawn_random_med_pack,
)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("System Override")
clock = pygame.time.Clock()
name = ""
started = False
name_input = pygame_textinput.TextInputVisualizer(font_object=game_font)
leader_board = False
last_response = 0
background = pygame.image.load("img/Background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

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
        spawn_random_enemy(WIDTH, HEIGHT)
    # random weapon drop spawn
    if random() < 0.001:
        spawn_random_weapon_drop(WIDTH, HEIGHT)
    # random med pack spawn
    if random() < 0.0005:
        spawn_random_med_pack(WIDTH, HEIGHT)
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

    healthbar_len = int(map_val(player.health, 0, player.max_health, 0, 32 * 7))

    mapped_health = int(map_val(player.health, 0, player.max_health, 0, 100))

    health_text = score_font.render(f"{mapped_health}", True, (0, 255, 0))
    health_rect = health_text.get_rect(topleft=(20 + (32 - 8) * 7 + 7, HEIGHT - 7 * 7))

    player.update(dt)
    enemies.update(player, enemies, enemy_projectiles, dt)
    player_projectiles.update(enemies, dt)
    enemy_projectiles.update([player], dt)
    weapon_drops.update(player, screen)
    med_packs.update(player)
    # Draw
    screen.blit(background, (0, 0))
    enemies.draw(screen)
    player_projectiles.draw(screen)
    enemy_projectiles.draw(screen)
    weapon_drops.draw(screen)
    med_packs.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    screen.blit(
        player.healthbar_black, (20, HEIGHT - (20 + 7 * 7)), (0, 0, 32 * 8, 7 * 7)
    )
    screen.blit(
        player.healthbar_red, (20, HEIGHT - (20 + 7 * 7)), (0, 0, healthbar_len, 7 * 7)
    )
    screen.blit(health_text, health_rect)
    # Draw
    # Update


while running:
    if not started and not leader_board:
        player.name, started, leader_board, running = start_screen(
            screen, game_font, name_input, started, leader_board
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
        enemies.empty()
        player_projectiles.empty()
        enemy_projectiles.empty()
        weapon_drops.empty()
        med_packs.empty()
        player, running, leader_board, started = death_screen(
            screen, game_font, player, running
        )
    # Events

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
