import json

import pygame
import time
from urllib import parse

import requests
from pygame import SurfaceType
from pygame.font import FontType
from pygame_textinput import TextInputVisualizer

from config import WIDTH, HEIGHT
from constants import GREEN
from classes import Player

game_font = pygame.font.Font("Fonts/game_over.ttf", 86)
score_font = pygame.font.Font("Fonts/game_over.ttf", 64)
CONFIG = json.load(open("config.json", "r"))
LB_SECRET = CONFIG["LEADERBOARD_SECRET"]
LB_PUBLIC = CONFIG["LEADERBOARD_PUBLIC"]
LB_URL = CONFIG["LEADERBOARD_URL"]


def leader_board_screen(screen: SurfaceType, last_response: float, leader_board: bool):
    back_text = game_font.render(
        "Back",
        True,
        (0, 0, 0),
    )
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 250))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return last_response, False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if back_rect.collidepoint(mouse_x, mouse_y):
                return last_response, False
    if time.time() - last_response <= 60 * 5:
        screen.blit(back_text, back_rect)
        pygame.display.flip()
        return last_response, leader_board

    top_users = get_top_users(5)["dreamlo"]["leaderboard"]["entry"]
    screen.fill(GREEN)
    y = 0
    for user in top_users:
        user_text = game_font.render(
            f"{parse.unquote_plus(user['name'])} - {user['score']}",
            True,
            (0, 0, 0),
        )
        user_rect = user_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + y))
        screen.blit(user_text, user_rect)
        pygame.display.flip()
        y += 50

    screen.blit(back_text, back_rect)
    last_response = time.time()
    pygame.display.flip()
    return last_response, leader_board


# noinspection DuplicatedCode
def start_screen(
    screen: SurfaceType,
    pixelify_sans: FontType,
    name_input: TextInputVisualizer,
    started: bool,
    leader_board: bool,
):
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
def death_screen(
    screen: SurfaceType, pixelify_sans: FontType, player: Player, running: bool
):
    screen.fill(GREEN)

    died_text = pixelify_sans.render("You Died", True, (255, 0, 0))
    died_rect = died_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))

    again_text = pixelify_sans.render("Try Again", True, (0, 0, 0))
    again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_text = pixelify_sans.render("Quit", True, (0, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    leader_board_text = pixelify_sans.render("Leader Board", True, (0, 0, 0))
    leader_board_rect = leader_board_text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 100)
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
                return player, True, False, True
            elif quit_rect.collidepoint(mouse_x, mouse_y):
                return player, False, False, False
            elif leader_board_rect.collidepoint(mouse_x, mouse_y):
                return player, True, True, False

    if player.score > player.high_score:
        player.high_score = player.score

    add_user(player.name, player.score)

    score_text = score_font.render(f"Score: {player.score}", True, (0, 0, 0))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    high_score_text = score_font.render(
        f"High Score: {player.high_score}", True, (0, 0, 0)
    )
    high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

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
