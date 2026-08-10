import math
import pygame


class Enemy:

    def __init__(
        self,
        x,
        y,
        image_path,
        speed=1.2,
        detection_range=8.0,
        health=100,
        damage=20
    ):
        # ==============================
        # POSITION
        # ==============================

        self.x = x
        self.y = y

        # ==============================
        # MOVEMENT
        # ==============================

        self.speed = speed

        # Maximum distance at which
        # enemy can detect the player
        self.detection_range = detection_range

        # ==============================
        # HEALTH / DAMAGE
        # ==============================

        self.health = health
        self.max_health = health

        self.damage = damage

        # ==============================
        # IMAGE
        # ==============================

        self.image = pygame.image.load(
            image_path
        ).convert_alpha()

        # ==============================
        # STATE
        # ==============================

        self.detected_player = False

    # ==========================================
    # DISTANCE TO PLAYER
    # ==========================================

    def distance_to_player(self, player):

        dx = player.x - self.x
        dy = player.y - self.y

        return math.sqrt(
            dx * dx + dy * dy
        )

    # ==========================================
    # DETECT PLAYER
    # ==========================================

    def can_detect_player(self, player):

        distance = self.distance_to_player(player)

        if distance <= self.detection_range:
            self.detected_player = True
            return True

        self.detected_player = False
        return False

    # ==========================================
    # UPDATE ENEMY POSITION
    # ==========================================

    def update(self, player, mansion_map, dt):

        if not self.active:
            return

        # Check whether player is within range
        if not self.can_detect_player(player):
            return

        # Direction from enemy to player
        dx = player.x - self.x
        dy = player.y - self.y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        # Prevent division by zero
        if distance == 0:
            return

        # Normalize direction
        dx /= distance
        dy /= distance

        # Calculate movement
        movement = self.speed * dt

        new_x = self.x + dx * movement
        new_y = self.y + dy * movement

        # ==========================================
        # COLLISION WITH WALLS
        # ==========================================

        if mansion_map.is_walkable(
            new_x,
            self.y
        ):
            self.x = new_x

        if mansion_map.is_walkable(
            self.x,
            new_y
        ):
            self.y = new_y

    # ==========================================
    # ATTACK PLAYER
    # ==========================================

    def can_attack(self, player, attack_range=0.7):

        distance = self.distance_to_player(player)

        return distance <= attack_range

    def attack(self, player):

        if self.can_attack(player):

            if hasattr(player, "health"):

                player.health -= self.damage

                # Prevent negative health
                player.health = max(
                    0,
                    player.health
                )

                return True

        return False

    # ==========================================
    # TAKE DAMAGE
    # ==========================================

    def take_damage(self, amount):

        if amount <= 0:
            return

        self.health -= amount

        # Prevent negative health
        self.health = max(
            0,
            self.health
        )

    # ==========================================
    # CHECK WHETHER ENEMY IS ALIVE
    # ==========================================

    def is_alive(self):

        return self.health > 0