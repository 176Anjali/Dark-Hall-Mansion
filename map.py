import math


class MansionMap:

    def __init__(self):

        # # = wall
        # . = floor
        #
        # This is our first mansion layout.
        # We will expand it later.

        self.grid = [
            "####################",
            "#..................#",
            "#.######.#########.#",
            "#.#....#.#.......#.#",
            "#.#....#.#.......#.#",
            "#.#....#.#.......#.#",
            "#.#....#.#.#####.#.#",
            "#.#....#.#.#...#.#.#",
            "#.######.#.#...#.#.#",
            "#........#.#...#...#",
            "########.#.#####.###",
            "#........#.........#",
            "#.################.#",
            "#..................#",
            "####################",
        ]

        self.height = len(self.grid)
        self.width = len(self.grid[0])

    def is_wall(self, x, y):

        map_x = int(x)
        map_y = int(y)

        # Outside the map = wall
        if (
            map_x < 0
            or map_x >= self.width
            or map_y < 0
            or map_y >= self.height
        ):
            return True

        return self.grid[map_y][map_x] == "#"

    def is_walkable(self, x, y):

        return not self.is_wall(x, y)