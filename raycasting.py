import math


class Raycaster:

    def __init__(self, mansion_map):

        self.mansion_map = mansion_map

    def cast_ray(self, player, ray_angle):

        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        map_x = int(player.x)
        map_y = int(player.y)

        if ray_dir_x == 0:
            delta_dist_x = float("inf")
        else:
            delta_dist_x = abs(1 / ray_dir_x)

        if ray_dir_y == 0:
            delta_dist_y = float("inf")
        else:
            delta_dist_y = abs(1 / ray_dir_y)

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

        side = 0
        hit_tile = "#"

        for _ in range(100):

            if side_dist_x < side_dist_y:

                side_dist_x += delta_dist_x
                map_x += step_x

                side = 0

            else:

                side_dist_y += delta_dist_y
                map_y += step_y

                side = 1

            if (
                map_x < 0
                or map_x >= self.mansion_map.width
                or map_y < 0
                or map_y >= self.mansion_map.height
            ):

                return 20.0, side, "#"

            tile = self.mansion_map.grid[map_y][map_x]

            if tile in ("#", "D", "E"):

                # Open door behaves like empty space
                if (
                    tile in ("D", "E")
                    and (map_x, map_y)
                    in self.mansion_map.open_doors
                ):
                    continue

                hit_tile = tile

                break

        else:

            return 20.0, side, "#"

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

        return distance, side, hit_tile