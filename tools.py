from random import uniform, choice

from classes import Enemy, WeaponDrop, Weapon, MedPack
from main import enemies, weapon_drops, med_packs


def map_val(value, fromLow, fromHigh, toLow, toHigh):
    """
    :param value:
    :param fromLow:
    :param fromHigh:
    :param toLow:
    :param toHigh:
    :return:
    """
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow


def spawn_random_enemy(width, height):
    new_enemy = Enemy(
        uniform(0, width), uniform(0, height), 50 + (5 * uniform(-3, 3)), 100, 100
    )
    enemies.add(new_enemy)


def spawn_random_weapon_drop(width, height):
    new_weapon_drop = WeaponDrop(
        uniform(0, width), uniform(0, height), choice(list(Weapon)), 10
    )
    weapon_drops.add(new_weapon_drop)


def spawn_random_med_pack(width, height):
    new_med_pack = MedPack(uniform(0, width), uniform(0, height), 10)
    med_packs.add(new_med_pack)
