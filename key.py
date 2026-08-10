import math
import pygame


class Key:

    def __init__(
        self,
        x,
        y,
        image_path,
        name="Key"
    ):
        # ==========================================
        # WORLD POSITION
        # ==========================================

        self.x = x
        self.y = y

        # ==========================================
        # KEY INFORMATION
        # ==========================================

        self.name = name

        # False = key is still in the world
        # True = player has collected it
        self.collected = False

        # ==========================================
        # IMAGE
        # ==========================================

        self.image = pygame.image.load(
            image_path
        ).convert_alpha()

    # ==========================================
    # DISTANCE TO PLAYER
    # ==========================================

    def distance_to_player(self, player):

        dx = self.x - player.x
        dy = self.y - player.y

        return math.sqrt(
            dx * dx + dy * dy
        )

    # ==========================================
    # CHECK WHETHER PLAYER IS CLOSE
    # ==========================================

    def is_near_player(
        self,
        player,
        pickup_distance=0.7
    ):

        distance = self.distance_to_player(
            player
        )

        return distance <= pickup_distance

    # ==========================================
    # COLLECT KEY
    # ==========================================

    def collect(self, player):

        if self.collected:
            return False

        if self.is_near_player(player):

            self.collected = True

            return True

        return False

    # ==========================================
    # CHECK WHETHER KEY IS AVAILABLE
    # ==========================================

    def is_available(self):

        return not self.collected