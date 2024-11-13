from random import uniform, choice

from classes import Enemy, WeaponDrop, Weapon, MedPack


def map_val(value, from_low, from_high, to_low, to_high):
    """
    :param value:
    :param from_low:
    :param from_high:
    :param to_low:
    :param to_high:
    :return:
    """
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


def spawn_random_enemy(width, height, enemies):
    new_enemy = Enemy(
        uniform(0, width), uniform(0, height), 50 + (5 * uniform(-3, 3)), 100, 100
    )
    enemies.add(new_enemy)


def spawn_random_weapon_drop(width, height, weapon_drops):
    new_weapon_drop = WeaponDrop(
        uniform(0, width), uniform(0, height), choice(list(Weapon)), 10
    )
    weapon_drops.add(new_weapon_drop)


def spawn_random_med_pack(width, height, med_packs):
    new_med_pack = MedPack(uniform(0, width), uniform(0, height), 10)
    med_packs.add(new_med_pack)
