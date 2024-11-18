import json
from random import uniform, choice

from classes import Enemy, WeaponDrop, Weapon, MedPack


def map_val(value, from_low, from_high, to_low, to_high) -> float:
    """
    Maps a value from one range to another.
    :param value: The value to map
    :param from_low: The low end of the range the value is currently in
    :param from_high: The high end of the range the value is currently in
    :param to_low: The low end of the range to map the value to
    :param to_high: The high end of the range to map the value to
    :return: The value mapped to the new range
    """
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


def spawn_random_enemy(width, height, enemies):
    """
    Spawns a random enemy at a random location on the screen.
    :param width: Width of the screen
    :param height: Height of the screen
    :param enemies: The group of enemies to add the new enemy to
    :return:
    """
    new_enemy = Enemy(
        uniform(0, width), uniform(0, height), 50 + (5 * uniform(-3, 3)), 100, 100
    )
    enemies.add(new_enemy)


def spawn_random_weapon_drop(width, height, weapon_drops):
    """
    Spawns a random weapon drop at a random location on the screen.
    :param width: Width of the screen
    :param height: Height of the screen
    :param weapon_drops: The group of weapon drops to add the new weapon drop to
    :return:
    """
    new_weapon_drop = WeaponDrop(
        uniform(0, width), uniform(0, height), choice(list(Weapon)), 10
    )
    weapon_drops.add(new_weapon_drop)


def spawn_random_med_pack(width, height, med_packs):
    """
    Spawns a random med pack at a random location on the screen.
    :param width: Width of the screen
    :param height: Height of the screen
    :param med_packs: The group of med packs to add the new med pack to
    :return:
    """
    new_med_pack = MedPack(uniform(0, width), uniform(0, height), 10)
    med_packs.add(new_med_pack)
