import math
import pygame

from settings import (
    PLAYER_X,
    PLAYER_Y,
    PLAYER_ANGLE,
    MOVE_SPEED,
    RUN_SPEED,
    PLAYER_RADIUS,
)


class Player:

    def __init__(self, mansion_map):

        self.x = PLAYER_X
        self.y = PLAYER_Y

        self.angle = PLAYER_ANGLE

        self.mansion_map = mansion_map

        self.radius = PLAYER_RADIUS

        #Player's health
        self.health = 100
        # Items collected by the player
        self.inventory = []

    # ==========================================
    # MOVEMENT
    # ==========================================

    def update(self, dt):

        keys = pygame.key.get_pressed()

        speed = MOVE_SPEED

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed = RUN_SPEED

        movement_speed = speed * dt

        dx = 0
        dy = 0

        if keys[pygame.K_w]:

            dx += math.cos(self.angle)
            dy += math.sin(self.angle)

        if keys[pygame.K_s]:

            dx -= math.cos(self.angle)
            dy -= math.sin(self.angle)

        if keys[pygame.K_a]:

            dx += math.cos(self.angle - math.pi / 2)
            dy += math.sin(self.angle - math.pi / 2)

        if keys[pygame.K_d]:

            dx += math.cos(self.angle + math.pi / 2)
            dy += math.sin(self.angle + math.pi / 2)

        length = math.hypot(dx, dy)

        if length > 0:

            dx /= length
            dy /= length

            dx *= movement_speed
            dy *= movement_speed

        self.move_with_collision(dx, dy)

    # ==========================================
    # COLLISION
    # ==========================================

    def move_with_collision(self, dx, dy):

        new_x = self.x + dx
        new_y = self.y + dy

        if self.can_move_to(new_x, self.y):

            self.x = new_x

        if self.can_move_to(self.x, new_y):

            self.y = new_y

    def can_move_to(self, x, y):

        r = self.radius

        return (
            not self.mansion_map.is_wall(x - r, y - r)
            and not self.mansion_map.is_wall(x + r, y - r)
            and not self.mansion_map.is_wall(x - r, y + r)
            and not self.mansion_map.is_wall(x + r, y + r)
        )

    # ==========================================
    # CAMERA
    # ==========================================

    def rotate(self, mouse_dx, sensitivity):

        self.angle += mouse_dx * sensitivity

        # Keep angle between 0 and 2π
        self.angle %= (2 * math.pi)

        # ==========================================
        # INVENTORY
        # ==========================================

        def add_item(self, item):

            if item not in self.inventory:

                self.inventory.append(item)


        def has_item(self, item):

            return item in self.inventory


        def remove_item(self, item):

            if item in self.inventory:

                self.inventory.remove(item)
