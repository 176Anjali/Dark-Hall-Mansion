import math


class MansionMap:

    def __init__(self):

        # ==========================================================
        # MANSION MAP
        #
        # # = wall
        # . = floor
        #
        # Final objective:
        # Library Puzzle
        #       ↓
        # Basement Key
        #       ↓
        # Basement Door
        #       ↓
        # WIN
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
            "#.#....#.#.#...#.#.#",
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

            # ==========================================
            # VAULT
            # ==========================================

            {
                "x": 8.5,
                "y": 10.5,
                "locked": True,
                "open": False,
                "type": "vault",
            },

            # ==========================================
            # LIBRARY
            # ==========================================

            {
                "x": 9.5,
                "y": 3.5,
                "locked": True,
                "open": False,
                "type": "library",
            },

            # ==========================================
            # BASEMENT / FINAL EXIT
            # ==========================================

            {
                "x": 15.5,
                "y": 11.5,
                "locked": True,
                "open": False,
                "type": "basement",
            },
        ]

        # ==========================================================
        # BASEMENT KEY STATE
        # ==========================================================

        self.basement_key_collected = False

        # ==========================================================
        # LIBRARY KEY
        # ==========================================================

        self.library_key = {
            "x": 3.5,
            "y": 3.5,
            "collected": False,
            "visible": False,
        }

        # ==========================================================
        # KEY VAULT
        # ==========================================================

        self.key_vault = {
            "x": 3.5,
            "y": 3.5,
            "locked": True,
            "solved": False,
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
        # FINAL ESCAPE LOCATION
        #
        # The basement door itself is the final exit.
        # ==========================================================

        self.escape_x = 15.5
        self.escape_y = 11.5

        # Kept for compatibility with old game code.
        self.exit_door = {
            "x": self.escape_x,
            "y": self.escape_y,
            "locked": True,
            "open": False,
        }

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
        max_distance=2.0
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
    # GET NEARBY LIBRARY KEY
    # ==============================================================

    def get_nearby_key(
        self,
        player_x,
        player_y,
        max_distance=1.0
    ):

        if self.library_key["collected"]:
            return None

        if not self.library_key["visible"]:
            return None

        distance = math.hypot(
            self.library_key["x"] - player_x,
            self.library_key["y"] - player_y
        )

        if distance <= max_distance:
            return self.library_key

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
