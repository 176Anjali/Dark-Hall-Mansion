import math


class Raycaster:

    def __init__(self, mansion_map):
        self.mansion_map = mansion_map

    def cast_ray(self, player, ray_angle):

        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        map_x = int(player.x)
        map_y = int(player.y)

        # Distance required to travel one map square
        if ray_dir_x == 0:
            delta_dist_x = float("inf")
        else:
            delta_dist_x = abs(1 / ray_dir_x)

        if ray_dir_y == 0:
            delta_dist_y = float("inf")
        else:
            delta_dist_y = abs(1 / ray_dir_y)

        # Determine direction
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (
                player.x - map_x
            ) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (
                map_x + 1.0 - player.x
            ) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (
                player.y - map_y
            ) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (
                map_y + 1.0 - player.y
            ) * delta_dist_y

        hit = False
        side = 0

        # DDA algorithm
        for _ in range(100):

            if side_dist_x < side_dist_y:

                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0

            else:

                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if self.mansion_map.is_wall(map_x, map_y):

                hit = True
                break

        if not hit:
            return 20.0, side, 0.0

        # Calculate distance
        if side == 0:

            distance = (
                map_x
                - player.x
                + (1 - step_x) / 2
            ) / ray_dir_x

        else:

            distance = (
                map_y
                - player.y
                + (1 - step_y) / 2
            ) / ray_dir_y

        distance = max(distance, 0.001)

        # ------------------------------------------
        # FIND EXACT POSITION ON THE WALL
        # ------------------------------------------

        if side == 0:

            wall_hit = (
                player.y
                + distance * ray_dir_y
            )

        else:

            wall_hit = (
                player.x
                + distance * ray_dir_x
            )

        # Keep only fractional part
        wall_hit -= math.floor(wall_hit)

        return distance, side, wall_hit