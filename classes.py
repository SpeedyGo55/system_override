import time
from json.encoder import INFINITY
from random import uniform, choice
from enum import Enum

# Import pygame
import pygame
from pygame.math import Vector2
from pygame.sprite import Group

# Import the WIDTH and HEIGHT from the config file
from config import WIDTH, HEIGHT

# Initialize the mixer
pygame.mixer.pre_init(44100, -16, 16, 64)
pygame.mixer.init()

# Load the sounds
enemy_hit = pygame.mixer.Sound("audio/Hitmarker.mp3")
enemy_hit.set_volume(0.1)
player_death = pygame.mixer.Sound("audio/Player_Death.mp3")


class Weapon(Enum):
    """
    Enum for the different weapons in the game.
    """

    PISTOL = 1
    MACHINE_GUN = 2
    SHOTGUN = 3


# noinspection PyTypeChecker
class Player(pygame.sprite.Sprite):
    """
    Player class
    """

    def __init__(
        self, x: float, y: float, speed: int, high_score: int = 0, name: str = ""
    ):
        """
        Constructor
        :param x: x position
        :param y: y position
        :param speed: Speed of the player
        :param high_score: High score of the player, defaults to 0
        :param name: Name of the player, defaults to ""
        """
        super().__init__()  # Initialize the sprite
        self.speed = speed
        self.health = 500
        self.max_health = 500
        self.weapon = Weapon.PISTOL  # Default weapon
        self.og_image = pygame.image.load("img/MCHG.png")  # Load the image
        self.change_weapon(choice(list(Weapon)))  # Change the weapon to a random weapon
        self.image = self.og_image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.size = (
            self.rect.width + self.rect.height
        ) / 4  # Player size for better collision
        self.direction = Vector2(1, 1)
        self.last_shot = time.time()  # Last time the player shot
        self.score = 0
        self.high_score = high_score
        self.name = name
        self.healthbar_red = pygame.image.load("img/HBR.png")
        self.healthbar_red = pygame.transform.scale(
            self.healthbar_red, (32 * 7, 7 * 7)
        )  # Health bar resizing
        self.healthbar_black = pygame.image.load("img/HBB.png")
        self.healthbar_black = pygame.transform.scale(
            self.healthbar_black, (32 * 7, 7 * 7)
        )

    def update(self, dt: float):
        """
        Update function
        :param dt: Delta time
        :return:
        """
        direction_to_mouse = Vector2(  # Direction to mouse as a vector
            pygame.mouse.get_pos()[0] - self.rect.centerx,
            pygame.mouse.get_pos()[1] - self.rect.centery,
        )
        if direction_to_mouse.length() != 0:  # Normalize the direction
            direction_to_mouse = direction_to_mouse.normalize()

        self.direction = direction_to_mouse
        angle = self.direction.angle_to(
            Vector2(1, 0)
        )  # Convert the direction to an angle

        self.image = pygame.transform.rotate(
            self.og_image, angle + 90
        )  # Rotate the image
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.health <= 0:
            self.kill()  # Kill the player if health is less than 0
            return
        if self.border(WIDTH, HEIGHT, dt):  # Check if the player is out of bounds
            return
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 1
        if keys[pygame.K_d]:
            self.rect.x += 1
        if keys[pygame.K_w]:
            self.rect.y -= 1
        if keys[pygame.K_s]:
            self.rect.y += 1

    def border(self, width: int, height: int, dt: float) -> bool:
        """
        Check if the player is out of bounds
        :param width: Width of the screen
        :param height: Height of the screen
        :param dt: Delta time
        :return: True if the player is out of bounds, False otherwise
        """
        # Check if the player is out of bounds next frame
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
        """
        Change the weapon of the player
        :param weapon: Weapon to change to
        :return:
        """
        # Match the weapon
        match weapon:
            case Weapon.PISTOL:
                self.og_image = pygame.image.load("img/MCHG.png")
            case Weapon.MACHINE_GUN:
                self.og_image = pygame.image.load("img/MCMG.png")
            case Weapon.SHOTGUN:
                self.og_image = pygame.image.load("img/MCSG.png")

        self.weapon = weapon

    def shoot(self, target: Group):
        """
        Shoot function
        :param target: With which group the bullet should collide
        :return:
        """
        offset = self.direction * 30  # Offset for the bullet so it spawns at the muzzle
        offset = offset.rotate(12)
        hg_offset = self.direction * 25  # Offset for the handgun
        hg_offset = hg_offset.rotate(15)
        # Match the weapon and shoot with the corresponding parameters and cooldown
        match self.weapon:
            case Weapon.PISTOL:
                if time.time() - self.last_shot < 0.2:
                    return
                new_projectile = Projectile(
                    self.rect.centerx + hg_offset.x,
                    self.rect.centery + hg_offset.y,
                    200,
                    self.direction,
                    30,
                    enemy_hit,
                    1,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.MACHINE_GUN:
                if time.time() - self.last_shot < 0.1:
                    return
                new_projectile = Projectile(
                    self.rect.centerx + offset.x,
                    self.rect.centery + offset.y,
                    100,
                    self.direction,
                    15,
                    enemy_hit,
                    3,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.SHOTGUN:
                if time.time() - self.last_shot < 1:
                    return
                for i in range(10):  # Shoot 10 bullets in random directions in a cone
                    new_projectile = Projectile(
                        self.rect.centerx + offset.x,
                        self.rect.centery + offset.y,
                        100,
                        self.direction,
                        20,
                        enemy_hit,
                        20,
                        1,
                    )
                    target.add(new_projectile)
                self.last_shot = time.time()


# noinspection PyTypeChecker
class Enemy(pygame.sprite.Sprite):
    """
    Enemy class
    """

    def __init__(
        self, x: float, y: float, speed: float, min_distance: int, health: int
    ):
        """
        Constructor
        :param x: x position
        :param y: y position
        :param speed: Speed of the enemy
        :param min_distance: Distance to the player until the enemy stops moving
        :param health: Health of the enemy
        """
        super().__init__()  # Initialize the sprite
        self.min_distance = min_distance
        self.speed = speed
        self.health = health
        self.weapon = choice(
            [Weapon.PISTOL, Weapon.MACHINE_GUN, Weapon.SHOTGUN]
        )  # Random weapon
        match self.weapon:  # Match the weapon
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
        """
        Resolve collision with other enemies
        :param groups: A list of groups to check for collision
        :return:
        """
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
        """
        Update function
        :param player: The player
        :param enemies: The group of enemies
        :param projectiles: The group of projectiles
        :param dt: Delta time
        :return:
        """
        # Check if the enemy is dead
        if self.health <= 0:
            self.kill()
            player.score += 1
            return
        distance = (
            (self.rect.centerx - player.rect.centerx) ** 2
            + (self.rect.centery - player.rect.centery) ** 2
        ) ** 0.5  # Distance to the player
        direction: Vector2 = Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        )  # Direction to the player

        angle = direction.angle_to(Vector2(1, 0))  # Convert the direction to an angle
        self.image = pygame.transform.rotate(
            self.og_image, angle + 90
        )  # Rotate the image
        self.rect = self.image.get_rect(center=self.rect.center)  # Get the new rect

        if (
            direction.length() != 0
        ):  # Normalize the direction, only if the length is not 0
            direction = direction.normalize()

        if (
            distance > self.min_distance
        ):  # Move towards the player if the distance is greater than the minimum distance
            self.rect.centerx += direction.x * self.speed * dt
            self.rect.centery += direction.y * self.speed * dt

        if distance < 100:  # Shoot if the distance is less than 100
            self.shoot(projectiles)

        self.direction = direction  # Update the direction

        # Now resolve any overlap with other enemies
        self.resolve_collision([enemies, pygame.sprite.Group([player])])

    def shoot(self, target: Group):
        """
        Shoot function
        :param target: With which group the bullet should collide with
        :return:
        """
        offset = self.direction * 30  # Offset for the bullet so it spawns at the muzzle
        offset = offset.rotate(12)
        hg_offset = self.direction * 25  # Offset for the handgun
        hg_offset = hg_offset.rotate(15)
        match self.weapon:  # Match the weapon and shoot with the corresponding parameters and cooldown
            case Weapon.PISTOL:
                if time.time() - self.last_shot < 1:
                    return
                new_projectile = Projectile(
                    self.rect.centerx + hg_offset.x,
                    self.rect.centery + hg_offset.y,
                    200,
                    self.direction,
                    5,
                    None,
                    2,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.MACHINE_GUN:
                if time.time() - self.last_shot < 0.1:
                    return
                new_projectile = Projectile(
                    self.rect.centerx + offset.x,
                    self.rect.centery + offset.y,
                    100,
                    self.direction,
                    2,
                    None,
                    5,
                )
                target.add(new_projectile)
                self.last_shot = time.time()
            case Weapon.SHOTGUN:
                if time.time() - self.last_shot < 2:
                    return
                for i in range(10):  # Shoot 10 bullets in random directions in a cone
                    new_projectile = Projectile(
                        self.rect.centerx + offset.x,
                        self.rect.centery + offset.y,
                        100,
                        self.direction,
                        2,
                        None,
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
        hit_sound: pygame.mixer.Sound,
        accuracy: float = 0,
        ttl: float = INFINITY,
    ):
        """
        Constructor
        :param x: x position
        :param y: y position
        :param speed: Speed of the projectile
        :param direction: Direction of the projectile
        :param damage: Damage the projectile does
        :param hit_sound: Sound to play when the projectile hits
        :param accuracy: Accuracy of the projectile, defaults to 0. The higher the value, the more inaccurate the projectile
        :param ttl: Lifetime of the projectile, defaults to INFINITY. The projectile will be removed after the lifetime is over, it hits something or goes out of bounds
        """
        super().__init__()  # Initialize the sprite
        if direction.length() == 0:
            direction = Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.hit_sound = hit_sound
        self.image: pygame.image = pygame.image.load("img/Bullet.png")  # Load the image
        self.rect: pygame.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position: Vector2 = Vector2(x, y)
        self.direction = direction.normalize().rotate(
            uniform(-accuracy, accuracy)
        )  # Rotate the direction by a random value between -accuracy and accuracy
        self.lifetime = ttl

    def collision(self, target: Group):
        """
        Check for collision with the target group
        :param target: The group to check for collision
        :return:
        """
        for enemy in target:
            distance = (
                (self.rect.centerx - enemy.rect.centerx) ** 2
                + (self.rect.centery - enemy.rect.centery) ** 2
            ) ** 0.5  # Distance to the enemy
            if distance < enemy.size:
                enemy.health -= self.damage  # Deal damage to the enemy
                if self.hit_sound is not None:  # Play the hit sound
                    self.hit_sound.play()
                self.kill()
                return
            if (
                self.rect.centerx < 0
                or self.rect.centerx > WIDTH
                or self.rect.centery < 0
                or self.rect.centery > HEIGHT
            ):  # Check if the projectile is out of bounds
                self.kill()

    def update(self, target: Group, dt: float):
        """
        Update function
        :param target: The group to check for collision
        :param dt: Delta time
        :return:
        """
        self.position += self.direction * self.speed * dt
        if self.lifetime > 0:  # Check if the lifetime is over
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.kill()
        self.rect.center = self.position  # Update the rect
        self.collision(target)  # Check for collision


class WeaponDrop(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, weapon: Weapon, ttl: float):
        """
        Constructor
        :param x: x position
        :param y: y position
        :param weapon: Weapon to drop
        :param ttl: Time to live
        """
        super().__init__()  # Initialize the sprite
        self.weapon = weapon
        self.rot_angle = 0
        match weapon:  # Match the weapon and load the corresponding image. Scale the image down
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
        self.time_spawned = time.time()  # Time the weapon drop was spawned

    def collision(self, player: Player):
        """
        Check for collision with the player
        :param player: The player
        :return:
        """
        if self.rect.colliderect(player.rect):  # Check for collision
            player.change_weapon(self.weapon)
            self.kill()

    def update(self, player: Player, surface: pygame.Surface):
        """
        Update function
        :param player: The player
        :param surface: The surface to draw on
        :return:
        """
        self.image = pygame.transform.rotate(
            self.og_image, self.rot_angle
        )  # Rotate the image
        self.rect = self.image.get_rect(
            center=self.og_image.get_rect(center=self.center).center
        )
        if (
            time.time() - self.time_spawned > self.ttl
        ):  # Check if the time to live is over
            self.kill()
        self.rot_angle += 0.5  # Rotate the angle
        self.collision(player)  # Check for collision


class MedPack(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, ttl: int):
        """
        Constructor
        :param x: x position
        :param y: y position
        :param ttl: Time to live
        """
        super().__init__()  # Initialize the sprite
        self.image = pygame.image.load("img/MedPack.png")  # Load the image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.ttl = ttl
        self.time_spawned = time.time()  # Time the med pack was spawned

    def collision(self, player: Player):
        """
        Check for collision with the player
        :param player: The player
        :return:
        """
        if self.rect.colliderect(player.rect):  # Check for collision
            player.health = min(
                player.max_health, round(player.health + (player.max_health / 2))
            )  # Heal the player by half of the max health or to the max health. Whichever is lower
            self.kill()

    def update(self, player: Player):
        """
        Update function
        :param player: The player
        :return:
        """
        if (
            time.time() - self.time_spawned > self.ttl
        ):  # Check if the time to live is over
            self.kill()
        self.collision(player)
