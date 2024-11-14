import json

import pygame
import time
from urllib import parse

import requests
from pygame import SurfaceType
from pygame_textinput import TextInputVisualizer

from config import WIDTH, HEIGHT
from classes import Player

game_font = pygame.font.Font("Fonts/game_over.ttf", 86)
big_game_font = pygame.font.Font("Fonts/game_over.ttf", 96)
you_died_font = pygame.font.Font("Fonts/game_over.ttf", 128)
score_font = pygame.font.Font("Fonts/game_over.ttf", 64)
CONFIG = json.load(open("config.json", "r"))
LB_SECRET = CONFIG["LEADERBOARD_SECRET"]
LB_PUBLIC = CONFIG["LEADERBOARD_PUBLIC"]
LB_URL = CONFIG["LEADERBOARD_URL"]

added_user = False
menu_bg = pygame.image.load("img/Menu.png")
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
death_bg = pygame.image.load("img/DEATH.png")
death_bg = pygame.transform.scale(death_bg, (WIDTH, HEIGHT))
lb_bg = pygame.image.load("img/LB.png")
lb_bg = pygame.transform.scale(lb_bg, (WIDTH, HEIGHT))


def leader_board_screen(screen: SurfaceType, last_response: float, leader_board: bool):
    back_text = game_font.render(
        "Back",
        True,
        (0, 255, 255),
    )
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 190))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return last_response, False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_x, mouse_y):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return last_response, False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if back_rect.collidepoint(mouse_x, mouse_y):
        back_text = big_game_font.render("Back", True, (0, 255, 255))
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 190))

    if time.time() - last_response <= 60 * 5:
        screen.blit(lb_bg, back_rect.scale_by(1.1).topleft, back_rect.scale_by(1.1))
        screen.blit(back_text, back_rect)
        pygame.display.flip()
        return last_response, leader_board

    top_users = get_top_users(5)["dreamlo"]["leaderboard"]["entry"]
    screen.blit(lb_bg, (0, 0))
    y = 0
    for user in top_users:
        user_text = game_font.render(
            f"{parse.unquote_plus(user['name'])} - {user['score']}",
            True,
            (0, 255, 255),
        )
        user_rect = user_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + y))
        screen.blit(user_text, user_rect)
        pygame.display.flip()
        y += 53

    screen.blit(back_text, back_rect)
    last_response = time.time()
    pygame.display.flip()
    return last_response, leader_board


# noinspection DuplicatedCode
def start_screen(
    screen: SurfaceType,
    name_input: TextInputVisualizer,
    started: bool,
    leader_board: bool,
):
    screen.blit(menu_bg, (0, 0))
    events = pygame.event.get()
    title_text = game_font.render(
        "System Override",
        True,
        (255, 0, 0),
    )
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    name_input_rect = name_input.surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    start_text = game_font.render("Start", True, (0, 0, 0))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_text = game_font.render("Quit", True, (0, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    leader_board_text = game_font.render("Leader Board", True, (0, 0, 0))
    leader_board_rect = leader_board_text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 100)
    )

    for event in events:
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return name_input.value, False, leader_board, False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if start_rect.collidepoint(mouse_x, mouse_y):
                return name_input.value, True, leader_board, True
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                return name_input.value, False, leader_board, False
            elif leader_board_rect.collidepoint(mouse_x, mouse_y):
                return name_input.value, started, True, True
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if start_rect.collidepoint(mouse_x, mouse_y):
        start_text = big_game_font.render("Start", True, (0, 0, 0))
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    if quit_rect.collidepoint(mouse_x, mouse_y):
        quit_text = big_game_font.render("Quit", True, (0, 0, 0))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    if leader_board_rect.collidepoint(mouse_x, mouse_y):
        leader_board_text = big_game_font.render("Leader Board", True, (0, 0, 0))
        leader_board_rect = leader_board_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 100)
        )

    # noinspection PyTypeChecker
    name_input.update(events)

    screen.blit(title_text, title_rect)
    screen.blit(name_input.surface, name_input_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)
    screen.blit(leader_board_text, leader_board_rect)

    pygame.display.flip()
    return name_input.value, started, leader_board, True


# noinspection DuplicatedCode
def death_screen(screen: SurfaceType, player: Player, running: bool):
    global added_user
    screen.blit(death_bg, (0, 0))

    died_text = you_died_font.render("You Died", True, (255, 0, 0))
    died_rect = died_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))

    again_text = game_font.render("Try Again", True, (0, 255, 0))
    again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    quit_text = game_font.render("Quit", True, (0, 255, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    leader_board_text = game_font.render("Leader Board", True, (0, 255, 0))
    leader_board_rect = leader_board_text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 150)
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return Player(WIDTH // 2, HEIGHT // 2, 100), running, False, False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if again_rect.collidepoint(mouse_x, mouse_y):
                player = Player(
                    WIDTH // 2, HEIGHT // 2, 100, player.high_score, player.name
                )
                added_user = False
                return player, True, False, True
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                return player, False, False, False
            elif leader_board_rect.collidepoint(mouse_x, mouse_y):
                return player, True, True, False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if again_rect.collidepoint(mouse_x, mouse_y):
        again_text = big_game_font.render("Try Again", True, (0, 255, 0))
        again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    if quit_rect.collidepoint(mouse_x, mouse_y):
        quit_text = big_game_font.render("Quit", True, (0, 255, 0))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    if leader_board_rect.collidepoint(mouse_x, mouse_y):
        leader_board_text = big_game_font.render("Leader Board", True, (0, 255, 0))
        leader_board_rect = leader_board_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 150)
        )

    if player.score > player.high_score:
        player.high_score = player.score
    if not added_user:
        add_user(player.name, player.score)
        added_user = True

    score_text = score_font.render(f"Score: {player.score}", True, (0, 255, 0))
    score_rect = score_text.get_rect(center=(WIDTH // 2 - 210, HEIGHT // 2 - 50))
    high_score_text = score_font.render(
        f"High Score: {player.high_score}", True, (0, 255, 0)
    )
    high_score_rect = high_score_text.get_rect(
        center=(WIDTH // 2 + 210, HEIGHT // 2 - 50)
    )

    screen.blit(died_text, died_rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    screen.blit(leader_board_text, leader_board_rect)
    screen.blit(quit_text, quit_rect)
    screen.blit(again_text, again_rect)

    pygame.display.flip()
    return player, running, False, True


def get_top_users(top_n: int):
    global LB_PUBLIC, LB_URL
    url = f"{LB_URL}{LB_PUBLIC}/json/{top_n}"
    response = requests.get(url)
    result = json.loads(response.text)
    return result


def add_user(name: str, score: int):
    global LB_SECRET, LB_URL
    url = f"{LB_URL}{LB_SECRET}/add/{parse.quote_plus(name)}/{score}"
    requests.get(url)
