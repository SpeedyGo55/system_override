from json.encoder import INFINITY
from random import uniform
from enum import Enum

import pygame
from pygame.math import Vector2

BLUE = (0, 0, 255)

class Weapon(Enum):
    PISTOL = 1
    MACHINE_GUN = 2
    SHOTGUN = 3

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.speed = speed
        self.health = 100
        self.og_image = pygame.image.load("img/player.png")
        self.image = self.og_image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.weapon = Weapon.SHOTGUN
        self.direction = Vector2(1, 1)

    def update(self, dt):
        direction_to_mouse = Vector2(pygame.mouse.get_pos()[0] - self.rect.centerx, pygame.mouse.get_pos()[1] - self.rect.centery)
        if direction_to_mouse.length() != 0:
            direction_to_mouse = direction_to_mouse.normalize()
        angle = direction_to_mouse.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(self.og_image, angle-90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.health <= 0:
            self.kill()
            return
        if self.border(self.rect.x, self.rect.y, dt):
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 1
        if keys[pygame.K_RIGHT]:
            self.rect.x += 1
        if keys[pygame.K_UP]:
            self.rect.y -= 1
        if keys[pygame.K_DOWN]:
            self.rect.y += 1

    def border(self, width, height, dt):
        if self.rect.x < 0:
            self.rect.x += self.speed * dt
            return True
        if self.rect.x > width:
            self.rect.x -= self.speed * dt
            return True
        if self.rect.y < 0:
            self.rect.y += self.speed * dt
            return True
        if self.rect.y > height:
            self.rect.y -= self.speed * dt
            return True
        return False

    def change_weapon(self, weapon: Weapon):
        self.weapon = weapon

    def shoot(self, target):
        match self.weapon:
            case Weapon.PISTOL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_projectile = Projectile(self.rect.centerx, self.rect.centery, 200,
                                            Vector2(mouse_x - self.rect.centerx, mouse_y - self.rect.centery),
                                            20,
                                            1)
                target.add(new_projectile)
            case Weapon.MACHINE_GUN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_projectile = Projectile(self.rect.centerx, self.rect.centery, 200,
                                            Vector2(mouse_x - self.rect.centerx, mouse_y - self.rect.centery),
                                            10,
                                            3)
                target.add(new_projectile)
            case Weapon.SHOTGUN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i in range(10):
                    new_projectile = Projectile(self.rect.centerx, self.rect.centery, 200,
                                                Vector2(mouse_x - self.rect.centerx, mouse_y - self.rect.centery),
                                                10,
                                                20,
                                                1)
                    target.add(new_projectile)



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, min_distance, health):
        super().__init__()
        self.min_distance = min_distance
        self.speed = speed
        self.health = health
        self.image = pygame.image.load("img/enemy.png")
        self.direction = Vector2(1, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def resolve_collision(self, groups: [pygame.sprite.Group]):
        # Check for collisions with other enemies in the group
        for group in groups:
            for other in group:
                if other != self:  # Don't check against itself
                    distance = ((self.rect.x - other.rect.x) ** 2 + (self.rect.y - other.rect.y) ** 2) ** 0.5

                    # If there is overlap (distance < size of one enemy), resolve it
                    if distance < self.rect.width:
                        direction = Vector2(self.rect.x - other.rect.x, self.rect.y - other.rect.y)
                        if direction.length() != 0:
                            direction = direction.normalize()
                        overlap_distance = self.rect.width - distance
                        # Move this enemy out of the overlap by half the overlap distance
                        self.rect.x += direction.x * overlap_distance / 2
                        self.rect.y += direction.y * overlap_distance / 2
                        # Move the other enemy out by the other half
                        other.rect.x -= direction.x * overlap_distance / 2
                        other.rect.y -= direction.y * overlap_distance / 2

    def update(self, player: Player, enemies: pygame.sprite.Group, dt):
        # Existing movement logic
        if self.health <= 0:
            self.kill()
            return
        distance = ((self.rect.x - player.rect.x) ** 2 + (self.rect.y - player.rect.y) ** 2) ** 0.5
        direction: Vector2 = Vector2(player.rect.x - self.rect.x, player.rect.y - self.rect.y)

        if direction.length() != 0:
            direction = direction.normalize()

        if distance > self.min_distance:
            self.rect.x += direction.x * self.speed * dt
            self.rect.y += direction.y * self.speed * dt


        self.direction = direction

        # Now resolve any overlap with other enemies
        self.resolve_collision([enemies, pygame.sprite.Group([player])])

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed, direction: Vector2, damage, accuracy: float = 0, lifetime: float = INFINITY):
        super().__init__()
        if direction.length() == 0:
            direction = Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.image: pygame.image = pygame.image.load("img/projectile.png")
        self.rect: pygame.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position: Vector2 = Vector2(x, y)
        self.direction = direction.normalize().rotate(uniform(-accuracy, accuracy))
        self.lifetime = lifetime

    def collision(self, target):
        for enemy in target:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.damage
                self.kill()
                return
            if self.rect.x < 0 or self.rect.x > 800 or self.rect.y < 0 or self.rect.y > 600:
                self.kill()

    def update(self, target, dt):
        self.position += self.direction * self.speed * dt
        if self.lifetime > 0:
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.kill()
        self.rect.center = self.position
        self.collision(target)

class WeaponDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon: Weapon):
        super().__init__()
        self.weapon = weapon
        self.rot_angle = 0
        match weapon:
            case Weapon.PISTOL:
                self.og_image = pygame.image.load("img/pistol.png")
            case Weapon.MACHINE_GUN:
                self.og_image = pygame.image.load("img/machine_gun.png")
                self.og_image = pygame.transform.scale(self.og_image, (164/3, 86/3))
                self.image = self.og_image.convert_alpha()
            case Weapon.SHOTGUN:
                self.og_image = pygame.image.load("img/shotgun.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.center = self.rect.center

    def collision(self, player: Player):
        if self.rect.colliderect(player.rect):
            player.change_weapon(self.weapon)
            self.kill()

    def update(self, player: Player, surface: pygame.Surface):
        self.image = pygame.transform.rotate(self.og_image, self.rot_angle)
        self.rect = self.image.get_rect(center=self.og_image.get_rect(center = self.center).center)
        self.rot_angle += 0.5
        self.collision(player)