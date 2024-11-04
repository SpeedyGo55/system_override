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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("System Override")
pixelify_sans = pygame.font.Font("Fonts/PixelifySans.ttf", 32)
score_font = pygame.font.Font("Fonts/PixelifySans.ttf", 24)
clock = pygame.time.Clock()
name = ""
started = False
name_input = pygame_textinput.TextInputVisualizer()
leader_board = False
last_response = 0

CONFIG = json.load(open("config.json", "r"))
LB_SECRET = CONFIG["LEADERBOARD_SECRET"]
LB_PUBLIC = CONFIG["LEADERBOARD_PUBLIC"]
LB_URL = CONFIG["LEADERBOARD_URL"]


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


def add_user(name, score):
    global LB_SECRET, LB_URL
    url = f"{LB_URL}{LB_SECRET}/add/{parse.quote_plus(name)}/{score}"
    requests.get(url)


def get_top_users(top_n):
    global LB_PUBLIC, LB_URL
    url = f"{LB_URL}{LB_PUBLIC}/json/{top_n}"
    response = requests.get(url)
    print(response.text)
    result = json.loads(response.text)
    return result


def leader_board_screen():
    global screen, pixelify_sans, running, leader_board, last_response
    if time.time() - last_response <= 60 * 5:
        return
    screen.fill(GREEN)
    back_text = pixelify_sans.render(
        "Back",
        True,
        (0, 0, 0),
    )
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))

    top_users = get_top_users(10)["dreamlo"]["leaderboard"]["entry"]

    y = 0
    for user in top_users:
        user_text = pixelify_sans.render(
            f"{parse.unquote_plus(user['name'])} - {user['score']}",
            True,
            (0, 0, 0),
        )
        user_rect = user_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + y))
        screen.blit(user_text, user_rect)
        y += 50

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if back_rect.collidepoint(mouse_x, mouse_y):
                leader_board = False

    screen.blit(back_text, back_rect)
    last_response = time.time()
    pygame.display.flip()


def start_screen():
    global screen, pixelify_sans, running, name, started, name_input, leader_board
    screen.fill(GREEN)
    events = pygame.event.get()
    title_text = pixelify_sans.render(
        "System Override",
        True,
        (255, 0, 0),
    )
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    name_input_rect = name_input.surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    start_text = pixelify_sans.render("Start", True, (0, 0, 0))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_text = pixelify_sans.render("Quit", True, (0, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    leader_board_text = pixelify_sans.render("Leader Board", True, (0, 0, 0))
    leader_board_rect = leader_board_text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 100)
    )

    name_input.update(events)

    for event in events:
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if start_rect.collidepoint(mouse_x, mouse_y):
                started = True
                return name_input.value
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                running = False
                return name_input.value
            elif leader_board_rect.collidepoint(mouse_x, mouse_y):
                leader_board = True
                return name_input.value

    screen.blit(title_text, title_rect)
    screen.blit(name_input.surface, name_input_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)
    screen.blit(leader_board_text, leader_board_rect)

    pygame.display.flip()


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
            if player.weapon == Weapon.MACHINE_GUN:
                machine_gun = True
            else:
                player.shoot(player_projectiles)
        if (
            event.type == pygame.MOUSEBUTTONUP
            and pygame.mouse.get_pressed(3)[0] == False
        ):
            machine_gun = False

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
                player = Player(WIDTH // 2, HEIGHT // 2, 100, player.high_score)
                enemies.empty()
                enemy_projectiles.empty()
                player_projectiles.empty()
                weapon_drops.empty()
                med_packs.empty()
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                running = False

    if player.score > player.high_score:
        player.high_score = player.score

    add_user(name, player.score)

    screen.blit(quit_text, quit_rect)
    screen.blit(again_text, again_rect)


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

while running:
    if not started and not leader_board:
        name = start_screen()
    elif leader_board:
        leader_board_screen()
    elif player.health > 0 and started:
        play_screen()
    if player.health <= 0:
        death_screen()
    # Events

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000
