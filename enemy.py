import math
from collections import deque


class Enemy:

    def __init__(self, mansion_map):

        self.mansion_map = mansion_map

        # Start in the mansion
        self.x = 17.5
        self.y = 7.5

        self.speed = 1.35
        self.chase_speed = 2.15

        self.active = False
        self.searching = False
        self.chasing = False

        self.search_timer = 0

        self.catch_distance = 0.55

    # ==========================================
    # ACTIVATE
    # ==========================================

    def activate(self):

        if self.active:
            return

        self.active = True
        self.searching = True
        self.chasing = False

        self.search_timer = 3.0

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self, player, dt):

        if not self.active:
            return False

        self.search_timer -= dt

        if self.search_timer <= 0:

            self.searching = False
            self.chasing = True

        target = self.find_path_target(player)

        if target:

            tx, ty = target

            dx = tx - self.x
            dy = ty - self.y

            distance = math.hypot(dx, dy)

            if distance > 0.05:

                dx /= distance
                dy /= distance

                speed = (
                    self.speed
                    if self.searching
                    else self.chase_speed
                )

                self.move(
                    dx * speed * dt,
                    dy * speed * dt
                )

        distance_to_player = math.hypot(
            self.x - player.x,
            self.y - player.y
        )

        if distance_to_player <= self.catch_distance:

            return True

        return False

    # ==========================================
    # MOVEMENT
    # ==========================================

    def move(self, dx, dy):

        new_x = self.x + dx
        new_y = self.y + dy

        if self.can_move(new_x, self.y):

            self.x = new_x

        if self.can_move(self.x, new_y):

            self.y = new_y

    def can_move(self, x, y):

        return not self.mansion_map.is_wall(x, y)

    # ==========================================
    # PATHFINDING
    # ==========================================

    def find_path_target(self, player):

        start = (
            int(self.x),
            int(self.y)
        )

        target = (
            int(player.x),
            int(player.y)
        )

        if start == target:

            return player.x, player.y

        queue = deque([start])

        came_from = {
            start: None
        }

        while queue:

            current = queue.popleft()

            if current == target:
                break

            cx, cy = current

            neighbors = [
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1),
            ]

            for nx, ny in neighbors:

                if (
                    nx < 0
                    or ny < 0
                    or nx >= self.mansion_map.width
                    or ny >= self.mansion_map.height
                ):
                    continue

                if (nx, ny) in came_from:
                    continue

                # Enemy can move through open floor
                if self.mansion_map.is_wall(
                    nx + 0.5,
                    ny + 0.5
                ):
                    continue

                came_from[(nx, ny)] = current

                queue.append((nx, ny))

        if target not in came_from:

            return player.x, player.y

        current = target

        while (
            came_from[current] is not None
            and came_from[current] != start
        ):

            current = came_from[current]

        return (
            current[0] + 0.5,
            current[1] + 0.5
        )