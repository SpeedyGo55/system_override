import pygame
from pygame.math import Vector2

BLUE = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.speed = speed
        self.health = 100
        self.image = pygame.image.load("img/player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed * dt


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

