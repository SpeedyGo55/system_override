import json

import pygame
import time
from urllib import parse
import requests
from pygame import SurfaceType
from pygame_textinput import TextInputVisualizer

from config import WIDTH, HEIGHT
from classes import Player

# Define fonts and Leaderboard variables
game_font = pygame.font.Font("Fonts/game_over.ttf", 86)
title_font = pygame.font.Font("Fonts/game_over.ttf", 128)
credit_font = pygame.font.Font("Fonts/game_over.ttf", 32)
big_game_font = pygame.font.Font("Fonts/game_over.ttf", 96)
you_died_font = pygame.font.Font("Fonts/game_over.ttf", 128)
score_font = pygame.font.Font("Fonts/game_over.ttf", 64)
CONFIG = json.load(open("config.json", "r"))
LB_SECRET = CONFIG["LEADERBOARD_SECRET"]
LB_PUBLIC = CONFIG["LEADERBOARD_PUBLIC"]
LB_URL = CONFIG["LEADERBOARD_URL"]
# define variables, load images and resize them
added_user = False
menu_bg = pygame.image.load("img/Menu.png")
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
death_bg = pygame.image.load("img/DEATH.png")
death_bg = pygame.transform.scale(death_bg, (WIDTH, HEIGHT))
lb_bg = pygame.image.load("img/LB.png")
lb_bg = pygame.transform.scale(lb_bg, (WIDTH, HEIGHT))


def leader_board_screen(
    screen: SurfaceType, last_response: float, leader_board: bool
) -> tuple[float, bool]:
    """
    Display the leaderboard screen
    :param screen: The screen to display the leaderboard on
    :param last_response: When the last request to the leaderboard api was made
    :param leader_board: If the leaderboard screen should be displayed
    :return: A tuple containing the last_response and if the leaderboard screen should be displayed
    """
    # Render text and get rects
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
            return last_response, False  # Return to the start screen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if back_rect.collidepoint(
            mouse_x, mouse_y
        ):  # If the mouse is over the back button
            if (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # If the user clicks the back button
                return last_response, False  # Return to the start screen

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if back_rect.collidepoint(mouse_x, mouse_y):
        back_text = big_game_font.render("Back", True, (0, 255, 255))
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 190))

    if (
        time.time() - last_response <= 60 * 5
    ):  # If the last request was made less than 5 minutes ago
        screen.blit(
            lb_bg, back_rect.scale_by(1.1).topleft, back_rect.scale_by(1.1)
        )  # only draw the background where the back button is
        screen.blit(back_text, back_rect)
        pygame.display.flip()
        return (
            last_response,
            leader_board,
        )  # Return the last response and if the leaderboard screen should be displayed

    try:
        top_users = get_top_users(5)["dreamlo"]["leaderboard"]["entry"]
    except Exception as e:
        screen.blit(
            lb_bg, back_rect.scale_by(1.1).topleft, back_rect.scale_by(1.1)
        )  # only draw the background where the back button is
        screen.blit(back_text, back_rect)
        pygame.display.flip()
        return (
            last_response,
            leader_board,
        )  # Return the last response and if the leaderboard screen should be displayed
    screen.blit(lb_bg, (0, 0))
    y = 0
    for user in top_users:
        user_text = game_font.render(
            f"{parse.unquote_plus(user['name'])} - {user['score']}",  # Display the user's name and score
            True,
            (0, 255, 255),
        )
        user_rect = user_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100 + y))
        screen.blit(user_text, user_rect)
        pygame.display.flip()
        y += 53

    screen.blit(back_text, back_rect)
    last_response = time.time()  # Update the last response time
    pygame.display.flip()
    return (
        last_response,
        leader_board,
    )  # Return the last response and if the leaderboard screen should be displayed


# noinspection DuplicatedCode
def start_screen(
    screen: SurfaceType,
    name_input: TextInputVisualizer,
    started: bool,
    leader_board: bool,
) -> tuple[str, bool, bool, bool, int]:
    """
    Display the start screen
    :param screen: The screen to display the start screen on
    :param name_input: The text input object to get the name of the player
    :param started: If the game has started
    :param leader_board: If the leaderboard screen should be displayed
    :return: A tuple containing the name of the player, if the game has started, if the leaderboard screen should be displayed and if the start screen should be displayed
    """
    screen.blit(menu_bg, (0, 0))
    events = pygame.event.get()

    # Render text and get rects
    title_text = title_font.render(
        "System Override",
        True,
        (255, 0, 0),
    )
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))

    name_input_rect = name_input.surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    start_text = game_font.render("Start", True, (0, 0, 0))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    quit_text = game_font.render("Quit", True, (0, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    leader_board_text = game_font.render("Leader Board", True, (0, 0, 0))
    leader_board_rect = leader_board_text.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 100)
    )
    credits_text = credit_font.render(
        "Copyright Luca Buholzer & Niklas Schrader", True, (0, 0, 0)
    )
    credits_rect = credits_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))

    for event in events:
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return name_input.value, False, leader_board, False, 0  # Quit the game
        if (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # If the user clicks the left mouse button
            mouse_x, mouse_y = pygame.mouse.get_pos()  # Get the mouse position
            if start_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the start button
                return (
                    name_input.value,
                    True,
                    leader_board,
                    True,
                    get_user(name_input.value),
                )  # Start the game
            elif quit_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the quit button
                return name_input.value, False, leader_board, False, 0  # Quit the game
            elif leader_board_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the leaderboard button
                return (
                    name_input.value,
                    started,
                    True,
                    True,
                    0,
                )  # Display the leaderboard screen
    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get the mouse position
    if start_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the start button, change the text to big_game_font
        start_text = big_game_font.render("Start", True, (0, 0, 0))
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    if quit_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the quit button, change the text to big_game_font
        quit_text = big_game_font.render("Quit", True, (0, 0, 0))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    if leader_board_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the leaderboard button, change the text to big_game_font
        leader_board_text = big_game_font.render("Leader Board", True, (0, 0, 0))
        leader_board_rect = leader_board_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 100)
        )

    # noinspection PyTypeChecker
    name_input.update(events)

    # Draw everything to the screen
    screen.blit(title_text, title_rect)
    screen.blit(name_input.surface, name_input_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)
    screen.blit(credits_text, credits_rect)
    screen.blit(leader_board_text, leader_board_rect)

    pygame.display.flip()
    return name_input.value, started, leader_board, True, 0


# noinspection DuplicatedCode
def death_screen(
    screen: SurfaceType, player: Player, running: bool
) -> tuple[Player, bool, bool, bool]:
    """
    Display the death screen
    :param screen: The screen to display the death screen on
    :param player: The player object
    :param running: If the game is running
    :return: A tuple containing the player object, if the game is running, if the leaderboard screen should be displayed and if the death screen should be displayed
    """
    global added_user
    screen.blit(death_bg, (0, 0))

    # Render text and get rects
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
            return (
                Player(WIDTH // 2, HEIGHT // 2, 100),
                running,
                False,
                False,
            )  # Quit the game
        if (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # If the user clicks the left mouse button
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if again_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the try again button
                player = Player(
                    WIDTH // 2, HEIGHT // 2, 100, player.high_score, player.name
                )
                added_user = False
                return player, True, False, True  # Start the game
            elif quit_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the quit button
                return player, False, False, False  # Quit the game
            elif leader_board_rect.collidepoint(
                mouse_x, mouse_y
            ):  # If the user clicks the leaderboard button
                return player, True, True, False  # Display the leaderboard screen

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if again_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the try again button, change the text to big_game_font
        again_text = big_game_font.render("Try Again", True, (0, 255, 0))
        again_rect = again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    if quit_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the quit button, change the text to big_game_font
        quit_text = big_game_font.render("Quit", True, (0, 255, 0))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    if leader_board_rect.collidepoint(
        mouse_x, mouse_y
    ):  # If the mouse is over the leaderboard button, change the text to big_game_font
        leader_board_text = big_game_font.render("Leader Board", True, (0, 255, 0))
        leader_board_rect = leader_board_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 150)
        )

    if player.score > player.high_score:
        player.high_score = player.score
    if not added_user:  # If the user has not been added to the leaderboard
        add_user(player.name, player.score)  # Add the user to the leaderboard
        added_user = True

    score_text = score_font.render(f"Score: {player.score}", True, (0, 255, 0))
    score_rect = score_text.get_rect(center=(WIDTH // 2 - 210, HEIGHT // 2 - 50))
    high_score_text = score_font.render(
        f"High Score: {player.high_score}", True, (0, 255, 0)
    )  # Display the player's high score
    high_score_rect = high_score_text.get_rect(
        center=(WIDTH // 2 + 210, HEIGHT // 2 - 50)
    )

    # Draw everything to the screen
    screen.blit(died_text, died_rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text, high_score_rect)
    screen.blit(leader_board_text, leader_board_rect)
    screen.blit(quit_text, quit_rect)
    screen.blit(again_text, again_rect)

    pygame.display.flip()
    return player, running, False, True


def get_top_users(top_n: int) -> dict:
    """
    Get the top n users from the leaderboard
    :param top_n: The number of users to get
    :return: A dictionary containing the top n users
    """
    global LB_PUBLIC, LB_URL
    url = (
        f"{LB_URL}{LB_PUBLIC}/json/{top_n}"  # Get the top n users from the leaderboard
    )
    response = requests.get(url)  # Make a request to the leaderboard api
    result = json.loads(response.text)  # Parse the response as json
    return result


def add_user(name: str, score: int):
    """
    Add a user to the leaderboard
    :param name: Name of the user
    :param score: Score of the user
    :return:
    """
    global LB_SECRET, LB_URL
    url = f"{LB_URL}{LB_SECRET}/add/{parse.quote_plus(name)}/{score}"  # Add the user to the leaderboard
    requests.get(url)  # Make a request to the leaderboard api


def get_user(name: str) -> int:
    """
    Get the user from the leaderboard
    :param name: Name of the user
    :return: The score of the user or 0 if the user does not exist
    """
    global LB_PUBLIC, LB_URL
    if not name:
        return 0
    url = f"{LB_URL}{LB_PUBLIC}/pipe-get/{parse.quote_plus(name)}"  # Get the user from the leaderboard
    response = requests.get(url)  # Make a request to the leaderboard api
    try:
        _name, score, *_ = response.text.split("|")  # Parse the response
    except ValueError as e:
        print(e)
        return 0
    return int(score)  # Return the score of the user
