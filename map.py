import math


class MansionMap:

    def __init__(self):

        # ==========================================================
        # MANSION MAP
        #
        # # = wall
        # . = floor
        # D = locked door
        #
        # The player must find the key and unlock the final door.
        # ==========================================================

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

        # ==========================================================
        # DOORS
        # ==========================================================

        self.doors = [
            {
                "x": 8.5,
                "y": 10.5,
                "locked": True,
                "open": False,
            },
            {
                "x": 18.5,
                "y": 10.5,
                "locked": True,
                "open": False,
            },
        ]

        # ==========================================================
        # KEY
        # ==========================================================

        self.key = {
            "x": 3.5,
            "y": 3.5,
            "collected": False,
        }

        # ==========================================================
        # MEDKIT
        # ==========================================================

        self.medkit = {
            "x": 5.5,
            "y": 9.5,
            "collected": False,
        }

        # ==========================================================
        # CANDLES
        # ==========================================================

        self.candles = [
            {
                "x": 2.5,
                "y": 1.5,
            },
            {
                "x": 10.5,
                "y": 3.5,
            },
            {
                "x": 16.5,
                "y": 5.5,
            },
            {
                "x": 14.5,
                "y": 11.5,
            },
        ]

        # ==========================================================
        # ESCAPE LOCATION
        # ==========================================================

        self.escape_x = 17.5
        self.escape_y = 13.5

    # ==============================================================
    # WALL CHECK
    # ==============================================================

    def is_wall(self, x, y):

        map_x = int(x)
        map_y = int(y)

        if (
            map_x < 0
            or map_x >= self.width
            or map_y < 0
            or map_y >= self.height
        ):
            return True

        # Check doors
        for door in self.doors:

            if (
                int(door["x"]) == map_x
                and int(door["y"]) == map_y
            ):

                if door["open"]:
                    return False

                return True

        return self.grid[map_y][map_x] == "#"

    # ==============================================================
    # WALKABLE
    # ==============================================================

    def is_walkable(self, x, y):

        return not self.is_wall(x, y)

    # ==============================================================
    # GET NEARBY DOOR
    # ==============================================================

    def get_nearby_door(
        self,
        player_x,
        player_y,
        max_distance=1.5
    ):

        closest = None
        closest_distance = max_distance

        for door in self.doors:

            distance = math.hypot(
                door["x"] - player_x,
                door["y"] - player_y
            )

            if distance <= closest_distance:

                closest = door
                closest_distance = distance

        return closest

    # ==============================================================
    # OPEN DOOR
    # ==============================================================

    def open_door(self, door):

        if door is None:
            return False

        if door["locked"]:
            return False

        door["open"] = True

        return True

    # ==============================================================
    # UNLOCK DOOR
    # ==============================================================

    def unlock_door(self, door):

        if door is None:
            return False

        door["locked"] = False
        door["open"] = True

        return True

    # ==============================================================
    # GET NEARBY KEY
    # ==============================================================

    def get_nearby_key(
        self,
        player_x,
        player_y,
        max_distance=1.0
    ):

        if self.key["collected"]:
            return None

        distance = math.hypot(
            self.key["x"] - player_x,
            self.key["y"] - player_y
        )

        if distance <= max_distance:
            return self.key

        return None

    # ==============================================================
    # GET NEARBY MEDKIT
    # ==============================================================

    def get_nearby_medkit(
        self,
        player_x,
        player_y,
        max_distance=1.0
    ):

        if self.medkit["collected"]:
            return None

        distance = math.hypot(
            self.medkit["x"] - player_x,
            self.medkit["y"] - player_y
        )

        if distance <= max_distance:
            return self.medkit

        return None

    # ==============================================================
    # ESCAPE CHECK
    # ==============================================================

    def is_escape_reached(
        self,
        player_x,
        player_y
    ):

        distance = math.hypot(
            self.escape_x - player_x,
            self.escape_y - player_y
        )

        return distance < 1.0