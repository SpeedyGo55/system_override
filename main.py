import time
from random import random
import pygame_textinput
import pygame


# Importing my own modules
from classes import Player, Weapon, player_death
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

pygame.init()  # Initialize Pygame

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), pygame.FULLSCREEN
)  # Set the screen size and mode (fullscreen)
pygame.display.set_caption("System Override")  # Set the window title
icon = pygame.image.load("img/SO.png")  # Load the icon image
pygame.display.set_icon(icon)
clock = pygame.time.Clock()  # Create a clock object to control the frame rate


# Variables
name = ""
started = False
name_input = pygame_textinput.TextInputVisualizer(font_object=game_font)
leader_board = False
last_response = 0
player = Player(WIDTH // 2, HEIGHT // 2, 100)
just_died = False
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

# Load Background Image
background = pygame.image.load("img/Background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load Background Music
pygame.mixer.music.load("audio/BackgroundMusic.wav")
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)


def play_screen():
    """
    This function is the main game loop. It handles all the game logic and rendering.
    :return:
    """
    global running, machine_gun, last_shot, just_pressed, started  # Global variables that are modified in this function

    for (
        event
    ) in (
        pygame.event.get()
    ):  # Get all the events that have occurred since the last frame
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            started = False  # If the user closes the window or presses the escape key, the game will return to the start screen
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and pygame.mouse.get_pressed(3)[0] == True
            and just_pressed
        ):  # If the user presses the left mouse button and the button was just pressed
            if (
                player.weapon == Weapon.MACHINE_GUN
            ):  # If the player has the machine gun weapon
                machine_gun = True  # The player will shoot continuously
            else:
                player.shoot(
                    player_projectiles
                )  # If the player does not have the machine gun weapon, the player will shoot once
            just_pressed = False
        if (
            event.type == pygame.MOUSEBUTTONUP
            and pygame.mouse.get_pressed(3)[0] == False
        ):  # If the user releases the left mouse button
            machine_gun = False  # The player will stop shooting
            just_pressed = True  # Reset the just_pressed variable

    # random enemy spawn. more likely to spawn if player has a higher score.
    if (
        random() < player.score / 10000 + 0.005
    ):  # The higher the player's score, the more likely an enemy will spawn
        spawn_random_enemy(WIDTH, HEIGHT, enemies)
    # random weapon drop spawn
    if random() < 0.001:
        spawn_random_weapon_drop(WIDTH, HEIGHT, weapon_drops)
    # random med pack spawn
    if random() < 0.0005:
        spawn_random_med_pack(WIDTH, HEIGHT, med_packs)
    # player shoot
    if machine_gun and time.time() - last_shot > 0.025:
        player.shoot(player_projectiles)
        last_shot = time.time()

    # Render Text
    score_text = score_font.render(f"Score: {player.score}", True, (0, 0, 0))
    score_rect = score_text.get_rect(topleft=(0, 0))
    high_score_text = score_font.render(
        f"High Score: {player.high_score}", True, (0, 0, 0)
    )
    high_score_rect = high_score_text.get_rect(topleft=(0, 24))

    # Calculate health bar length
    healthbar_len = int(map_val(player.health, 0, player.max_health, 0, 32 * 7))

    mapped_health = int(map_val(player.health, 0, player.max_health, 0, 100))

    # Render health text
    health_text = score_font.render(f"{mapped_health}", True, (0, 255, 0))
    health_rect = health_text.get_rect(topleft=(20 + (32 - 8) * 7 + 7, HEIGHT - 7 * 7))

    # Update
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
        player.healthbar_black,
        (20, HEIGHT - (20 + 7 * 7)),
        (0, 0, 32 * 8, 7 * 7),  # Draw the black part of the health bar
    )
    screen.blit(
        player.healthbar_red,
        (20, HEIGHT - (20 + 7 * 7)),
        (
            0,
            0,
            healthbar_len,
            7 * 7,
        ),  # Draw the red part of the health bar, over the black part, based on the player's health
    )
    screen.blit(health_text, health_rect)
    pygame.display.flip()


while running:
    # Main loop
    if (
        not started and not leader_board
    ):  # If the game is not started and the leader board is not being displayed
        player.name, started, leader_board, running = (
            start_screen(  # Display the start screen
                screen, name_input, started, leader_board
            )
        )
    elif leader_board:  # If the leader board is being displayed
        last_response, leader_board = leader_board_screen(  # Display the leader board
            screen, last_response, leader_board
        )
        if not leader_board:  # If the leader board is no longer being displayed
            last_response = 0  # Reset the last_response variable
    elif (
        player.health > 0 and started
    ):  # If the player's health is greater than 0 and the game has started
        if not just_died:  # If the player has not just died
            just_died = True  # Set the just_died variable to True
        play_screen()  # Play the game
    if (
        player.health <= 0 and not leader_board
    ):  # If the player's health is less than or equal to 0 and the leader board is not being displayed
        if just_died:  # If the player has just died
            player_death.play()  # Play the player death sound
            just_died = False  # Set the just_died variable to False
        # Reset all the game variables
        enemies.empty()
        player_projectiles.empty()
        enemy_projectiles.empty()
        weapon_drops.empty()
        med_packs.empty()
        player, running, leader_board, started = death_screen(
            screen, player, running
        )  # Display the death screen
    # Events

    dt = clock.tick(FPS) / 1000
