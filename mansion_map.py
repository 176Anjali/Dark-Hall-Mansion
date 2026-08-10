class MansionMap:

    def __init__(self):

        # ==========================================
        # DARK HALL MANSION
        #
        # # = wall
        # . = floor
        # D = locked door
        # E = entrance door
        # K = key location
        # ==========================================

        self.grid = [
            "#####E#################",
            "#.........#...........#",
            "#.........#...........#",
            "D....K....#...........#",
            "#.........D...........#",
            "#.........#...........#",
            "#.....................#",
            "#.........#...........#",
            "#.........#...........#",
            "#.........#...........#",
            "#.........#...........#",
            "#.........#...........#",
            "#.........#...........#",
            "#.....................#",
            "########D##############",
        ]

        self.height = len(self.grid)
        self.width = len(self.grid[0])

        self.key_position = (5.5, 3.5)

        # Correct escape door
        self.exit_door = (8, 14)

        # Entrance
        self.entrance_door = (5, 0)

        # Other locked doors
        self.locked_doors = {
            (0, 3),
            (10, 4),
        }

        self.open_doors = set()

        self.key_collected = False

    # ==========================================
    # TILE
    # ==========================================

    def get_tile(self, x, y):

        if x < 0 or x >= self.width:
            return "#"

        if y < 0 or y >= self.height:
            return "#"

        return self.grid[y][x]

    # ==========================================
    # WALL CHECK
    # ==========================================

    def is_wall(self, x, y):

        tile_x = int(x)
        tile_y = int(y)

        if (
            tile_x < 0
            or tile_x >= self.width
            or tile_y < 0
            or tile_y >= self.height
        ):
            return True

        tile = self.grid[tile_y][tile_x]

        if tile == "#":
            return True

        if tile == "E":
            return True

        if tile == "D":

            if (tile_x, tile_y) in self.open_doors:
                return False

            return True

        return False

    # ==========================================
    # DOOR
    # ==========================================

    def is_door(self, x, y):

        tile = self.get_tile(x, y)

        return tile == "D" or tile == "E"

    def is_open(self, x, y):

        return (x, y) in self.open_doors

    def open_door(self, x, y):

        if self.is_door(x, y):

            self.open_doors.add((x, y))

            return True

        return False

    # ==========================================
    # CORRECT EXIT
    # ==========================================

    def is_exit_door(self, x, y):

        return (x, y) == self.exit_door

    # ==========================================
    # FIND NEAREST DOOR
    # ==========================================

    def nearby_door(self, px, py, radius=1.5):

        closest = None
        closest_distance = radius

        for y in range(self.height):

            for x in range(self.width):

                if not self.is_door(x, y):
                    continue

                if (x, y) in self.open_doors:
                    continue

                dx = (x + 0.5) - px
                dy = (y + 0.5) - py

                distance = (dx * dx + dy * dy) ** 0.5

                if distance < closest_distance:

                    closest_distance = distance
                    closest = (x, y)

        return closest

    # ==========================================
    # KEY
    # ==========================================

    def collect_key(self):

        self.key_collected = True

    # ==========================================
    # ITEMS
    # ==========================================

    def get_item_positions(self):

        return {
            "key": self.key_position,
            "candle": (3.5, 5.5),
            "medkit": (7.5, 8.5),
        }