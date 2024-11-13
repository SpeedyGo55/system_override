import time
from json.encoder import INFINITY
from random import uniform, choice
from enum import Enum

import pygame
from pygame.math import Vector2
from pygame.sprite import Group

from config import WIDTH, HEIGHT

pygame.mixer.init()

SG_Shot = pygame.mixer.Sound("audio/Shotgun.mp3")
MG_Shot = pygame.mixer.Sound("audio/Machine_Gun.mp3")
HG_Shot = pygame.mixer.Sound("audio/Handgun.mp3")


class Weapon(Enum):
    PISTOL = 1
    MACHINE_GUN = 2
    SHOTGUN = 3


# noinspection PyTypeChecker
class Player(pygame.sprite.Sprite):
    def __init__(
        self, x: float, y: float, speed: int, high_score: int = 0, name: str = ""
    ):
        super().__init__()
        self.speed = speed
        self.health = 500
        self.max_health = 500
        self.weapon = Weapon.PISTOL
        self.og_image = pygame.image.load("img/MCHG.png")
        self.change_weapon(choice(list(Weapon)))
        self.image = self.og_image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.size = (self.rect.width + self.rect.height) / 4
        self.direction = Vector2(1, 1)
        self.last_shot = time.time()
        self.score = 0
        self.high_score = high_score
        self.name = name
        self.healthbar_red = pygame.image.load("img/HBR.png")
        self.healthbar_red = pygame.transform.scale(self.healthbar_red, (32 * 7, 7 * 7))
        self.healthbar_black = pygame.image.load("img/HBB.png")
        self.healthbar_black = pygame.transform.scale(
            self.healthbar_black, (32 * 7, 7 * 7)
        )

    def update(self, dt: float):
        direction_to_mouse = Vector2(
            pygame.mouse.get_pos()[0] - self.rect.centerx,
            pygame.mouse.get_pos()[1] - self.rect.centery,
        )
        if direction_to_mouse.length() != 0:
            direction_to_mouse = direction_to_mouse.normalize()
        self.direction = direction_to_mouse
        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.og_image, angle + 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.health <= 0:
            self.kill()
            return
        if self.border(WIDTH, HEIGHT, dt):
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 1
        if keys[pygame.K_d]:
            self.rect.x += 1
        if keys[pygame.K_w]:
            self.rect.y -= 1
        if keys[pygame.K_s]:
            self.rect.y += 1

    def border(self, width: int, height: int, dt: float):
        if self.rect.centerx < 0:
            self.rect.centerx += self.speed * dt
            return True
        if self.rect.centerx > width:
            self.rect.centerx -= self.speed * dt
            return True
        if self.rect.centery < 0:
            self.rect.centery += self.speed * dt
            return True
        if self.rect.centery > height:
            self.rect.centery -= self.speed * dt
            return True
        return False

    def change_weapon(self, weapon: Weapon):
        match weapon:
            case Weapon.PISTOL:
                self.og_image = pygame.image.load("img/MCHG.png")
            case Weapon.MACHINE_GUN:
                self.og_image = pygame.image.load("img/MCMG.png")
            case Weapon.SHOTGUN:
                self.og_image = pygame.image.load("img/MCSG.png")

        self.weapon = weapon

    def shoot(self, target: Group):
        offset = self.direction * 30
        offset = offset.rotate(12)
        hg_offset = self.direction * 25
        hg_offset = hg_offset.rotate(15)
        match self.weapon:
            case Weapon.PISTOL:
                if time.time() - self.last_shot < 0.2:
                    return
                HG_Shot.play()
                new_projectile = Projectile(
                    self.rect.centerx + hg_offset.x,
                    self.rect.centery + hg_offset.y,
                    200,
                    self.direction,
                    30,
                    1,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.MACHINE_GUN:
                if time.time() - self.last_shot < 0.1:
                    return
                MG_Shot.play()
                new_projectile = Projectile(
                    self.rect.centerx + offset.x,
                    self.rect.centery + offset.y,
                    100,
                    self.direction,
                    15,
                    3,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.SHOTGUN:
                if time.time() - self.last_shot < 1:
                    return
                SG_Shot.play()
                for i in range(10):
                    new_projectile = Projectile(
                        self.rect.centerx + offset.x,
                        self.rect.centery + offset.y,
                        100,
                        self.direction,
                        20,
                        20,
                        1,
                    )
                    target.add(new_projectile)
                self.last_shot = time.time()


# noinspection PyTypeChecker
class Enemy(pygame.sprite.Sprite):
    def __init__(
        self, x: float, y: float, speed: float, min_distance: int, health: int
    ):
        super().__init__()
        self.min_distance = min_distance
        self.speed = speed
        self.health = health
        self.weapon = choice([Weapon.PISTOL, Weapon.MACHINE_GUN, Weapon.SHOTGUN])
        match self.weapon:
            case Weapon.PISTOL:
                self.og_image = pygame.image.load("img/EHG.png")
            case Weapon.MACHINE_GUN:
                self.og_image = pygame.image.load("img/EMG.png")
            case Weapon.SHOTGUN:
                self.og_image = pygame.image.load("img/ESG.png")
        self.image = self.og_image.convert_alpha()
        self.direction = Vector2(1, 1)
        self.rect = self.image.get_rect()
        self.size = (self.rect.width + self.rect.height) / 5
        self.rect.center = (x, y)
        self.last_shot = time.time()

    def resolve_collision(self, groups: [pygame.sprite.Group]):
        # Check for collisions with other enemies in the group
        for group in groups:
            for other in group:
                if other != self:  # Don't check against itself
                    distance = (
                        (self.rect.centerx - other.rect.centerx) ** 2
                        + (self.rect.centery - other.rect.centery) ** 2
                    ) ** 0.5

                    # If there is overlap (distance < size of one enemy), resolve it
                    if distance < self.size:
                        direction = Vector2(
                            self.rect.centerx - other.rect.centerx,
                            self.rect.centery - other.rect.centery,
                        )
                        if direction.length() != 0:
                            direction = direction.normalize()
                        overlap_distance = self.size - distance
                        # Move this enemy out of the overlap by half the overlap distance
                        self.rect.centerx += direction.x * overlap_distance / 2
                        self.rect.centery += direction.y * overlap_distance / 2
                        # Move the other enemy out by the other half
                        other.rect.centerx -= direction.x * overlap_distance / 2
                        other.rect.centery -= direction.y * overlap_distance / 2

    def update(
        self,
        player: Player,
        enemies: pygame.sprite.Group,
        projectiles: Group,
        dt: float,
    ):
        # Existing movement logic
        if self.health <= 0:
            self.kill()
            player.score += 1
            return
        distance = (
            (self.rect.centerx - player.rect.centerx) ** 2
            + (self.rect.centery - player.rect.centery) ** 2
        ) ** 0.5
        direction: Vector2 = Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        )

        angle = direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.og_image, angle + 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if direction.length() != 0:
            direction = direction.normalize()

        if distance > self.min_distance:
            self.rect.centerx += direction.x * self.speed * dt
            self.rect.centery += direction.y * self.speed * dt

        if distance < 100:
            self.shoot(projectiles)

        self.direction = direction

        # Now resolve any overlap with other enemies
        self.resolve_collision([enemies, pygame.sprite.Group([player])])

    def shoot(self, target: Group):
        offset = self.direction * 30
        offset = offset.rotate(12)
        hg_offset = self.direction * 25
        hg_offset = hg_offset.rotate(15)
        match self.weapon:
            case Weapon.PISTOL:
                if time.time() - self.last_shot < 1:
                    return
                HG_Shot.play()
                new_projectile = Projectile(
                    self.rect.centerx + hg_offset.x,
                    self.rect.centery + hg_offset.y,
                    200,
                    self.direction,
                    5,
                    2,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.MACHINE_GUN:
                if time.time() - self.last_shot < 0.1:
                    return
                MG_Shot.play()
                new_projectile = Projectile(
                    self.rect.centerx + offset.x,
                    self.rect.centery + offset.y,
                    100,
                    self.direction,
                    2,
                    5,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.SHOTGUN:
                if time.time() - self.last_shot < 2:
                    return
                SG_Shot.play()
                for i in range(10):
                    new_projectile = Projectile(
                        self.rect.centerx + offset.x,
                        self.rect.centery + offset.y,
                        100,
                        self.direction,
                        2,
                        30,
                        1,
                    )
                    target.add(new_projectile)
                self.last_shot = time.time()


class Projectile(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        speed: int,
        direction: Vector2,
        damage: int,
        accuracy: float = 0,
        lifetime: float = INFINITY,
    ):
        super().__init__()
        if direction.length() == 0:
            direction = Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.image: pygame.image = pygame.image.load("img/Bullet.png")
        self.rect: pygame.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position: Vector2 = Vector2(x, y)
        self.direction = direction.normalize().rotate(uniform(-accuracy, accuracy))
        self.lifetime = lifetime

    def collision(self, target: Group):
        for enemy in target:
            distance = (
                (self.rect.centerx - enemy.rect.centerx) ** 2
                + (self.rect.centery - enemy.rect.centery) ** 2
            ) ** 0.5
            if distance < enemy.size:
                enemy.health -= self.damage
                self.kill()
                return
            if (
                self.rect.centerx < 0
                or self.rect.centerx > 800
                or self.rect.centery < 0
                or self.rect.centery > 600
            ):
                self.kill()

    def update(self, target: Group, dt: float):
        self.position += self.direction * self.speed * dt
        if self.lifetime > 0:
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.kill()
        self.rect.center = self.position
        self.collision(target)


class WeaponDrop(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, weapon: Weapon, ttl: float):
        super().__init__()
        self.weapon = weapon
        self.rot_angle = 0
        match weapon:
            case Weapon.PISTOL:
                self.og_image = pygame.image.load("img/Handgun.png")
                self.og_image = pygame.transform.scale(self.og_image, (100 / 3, 61 / 3))
                self.image = self.og_image.convert_alpha()
            case Weapon.MACHINE_GUN:
                self.og_image = pygame.image.load("img/Machine_Gun.png")
                self.og_image = pygame.transform.scale(self.og_image, (164 / 3, 86 / 3))
                self.image = self.og_image.convert_alpha()
            case Weapon.SHOTGUN:
                self.og_image = pygame.image.load("img/Shotgun.png")
                self.og_image = pygame.transform.scale(self.og_image, (157 / 3, 36 / 3))
                self.image = self.og_image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.center = self.rect.center
        self.ttl = ttl
        self.time_spawned = time.time()

    def collision(self, player: Player):
        if self.rect.colliderect(player.rect):
            player.change_weapon(self.weapon)
            self.kill()

    def update(self, player: Player, surface: pygame.Surface):
        self.image = pygame.transform.rotate(self.og_image, self.rot_angle)
        self.rect = self.image.get_rect(
            center=self.og_image.get_rect(center=self.center).center
        )
        if time.time() - self.time_spawned > self.ttl:
            self.kill()
        self.rot_angle += 0.5
        self.collision(player)


class MedPack(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, ttl: int):
        super().__init__()
        self.image = pygame.image.load("img/MedPack.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.ttl = ttl
        self.time_spawned = time.time()

    def collision(self, player: Player):
        if self.rect.colliderect(player.rect):
            player.health = min(
                player.max_health, round(player.health + (player.max_health / 2))
            )
            self.kill()

    def update(self, player: Player):
        if time.time() - self.time_spawned > self.ttl:
            self.kill()
        self.collision(player)
