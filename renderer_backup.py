import math
import os
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    FOV,
)


class Renderer:

    def __init__(self, mansion_map):

        self.mansion_map = mansion_map
        self.raycaster = None

        # ==========================================
        # ASSET PATHS
        # ==========================================

        self.assets_path = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        self.textures_path = os.path.join(
            self.assets_path,
            "textures"
        )

        self.enemies_path = os.path.join(
            self.assets_path,
            "enemies"
        )

        self.items_path = os.path.join(
            self.assets_path,
            "items"
        )

        # ==========================================
        # LOAD ASSETS
        # ==========================================

        self.textures = {}
        self.enemies = {}
        self.items = {}

        self.load_all_assets(
            self.textures_path,
            self.textures
        )

        self.load_all_assets(
            self.enemies_path,
            self.enemies
        )

        self.load_all_assets(
            self.items_path,
            self.items
        )

        # ==========================================
        # IMPORTANT TEXTURES
        # ==========================================

        self.wall_texture = self.find_texture(
            self.textures,
            ["wall.png", "wood_wall.png"]
        )

        self.floor_texture = self.find_texture(
            self.textures,
            ["floor.png"]
        )

        self.ceiling_texture = self.find_texture(
            self.textures,
            ["ceiling.png"]
        )

        self.door_texture = self.find_texture(
            self.textures,
            ["door.png"]
        )

    # ==========================================
    # ASSET LOADING
    # ==========================================

    def load_all_assets(self, folder, storage):

        if not os.path.exists(folder):
            return

        for root, dirs, files in os.walk(folder):

            for filename in files:

                if filename.lower().endswith(
                    (".png", ".jpg", ".jpeg")
                ):

                    path = os.path.join(
                        root,
                        filename
                    )

                    try:

                        image = pygame.image.load(
                            path
                        ).convert_alpha()

                        storage[
                            filename.lower()
                        ] = image

                        print(
                            "Loaded asset:",
                            path
                        )

                    except pygame.error:

                        print(
                            "Could not load:",
                            path
                        )

    # ==========================================
    # FIND TEXTURE
    # ==========================================

    def find_texture(self, storage, names):

        for name in names:

            if name.lower() in storage:
                return storage[name.lower()]

        return None

    # ==========================================
    # RAYCASTER
    # ==========================================

    def set_raycaster(self, raycaster):

        self.raycaster = raycaster

    # ==========================================
    # MAIN DRAW
    # ==========================================

    def draw(self, screen, player):

        # Ceiling and floor first
        self.draw_floor_and_ceiling(
            screen,
            player
        )

        # Walls over them
        self.draw_walls(
            screen,
            player
        )

        # Atmosphere
        self.draw_vignette(
            screen
        )

    # ==========================================
    # PROPER FLOOR + CEILING CASTING
    # ==========================================

    def draw_floor_and_ceiling(
        self,
        screen,
        player
    ):

        horizon = HEIGHT // 2

        # ==========================================
        # FALLBACK BACKGROUND
        # ==========================================

        screen.fill(
            (7, 6, 7)
        )

        pygame.draw.rect(
            screen,
            (20, 15, 12),
            (
                0,
                horizon,
                WIDTH,
                HEIGHT - horizon
            )
        )

        # If neither texture exists,
        # keep the colored background.
        if (
            self.floor_texture is None
            and self.ceiling_texture is None
        ):
            return

        # ==========================================
        # CAMERA DIRECTION
        # ==========================================

        dir_x = math.cos(
            player.angle
        )

        dir_y = math.sin(
            player.angle
        )

        # ==========================================
        # CAMERA PLANE
        # ==========================================

        half_fov = math.radians(
            FOV / 2
        )

        plane_length = math.tan(
            half_fov
        )

        plane_x = -dir_y * plane_length
        plane_y = dir_x * plane_length

        # ==========================================
        # LEFT / RIGHT RAY DIRECTIONS
        # ==========================================

        ray_left_x = (
            dir_x - plane_x
        )

        ray_left_y = (
            dir_y - plane_y
        )

        ray_right_x = (
            dir_x + plane_x
        )

        ray_right_y = (
            dir_y + plane_y
        )

        # ==========================================
        # TEXTURE DIMENSIONS
        # ==========================================

        floor_w = 1
        floor_h = 1

        ceiling_w = 1
        ceiling_h = 1

        if self.floor_texture:

            floor_w = (
                self.floor_texture.get_width()
            )

            floor_h = (
                self.floor_texture.get_height()
            )

        if self.ceiling_texture:

            ceiling_w = (
                self.ceiling_texture.get_width()
            )

            ceiling_h = (
                self.ceiling_texture.get_height()
            )

        # ==========================================
        # DRAW FLOOR
        # ==========================================

        # Use small vertical steps for performance.
        # Each block represents several pixels.

        step_y = 3
        step_x = 4

        for screen_y in range(
            horizon + 1,
            HEIGHT,
            step_y
        ):

            # Distance from camera to floor plane.
            row_distance = (
                HEIGHT /
                (
                    2.0 *
                    (screen_y - horizon)
                )
            )

            row_distance = max(
                row_distance,
                0.01
            )

            # ======================================
            # WORLD POSITION AT LEFT EDGE
            # ======================================

            floor_left_x = (
                player.x
                + ray_left_x *
                row_distance
            )

            floor_left_y = (
                player.y
                + ray_left_y *
                row_distance
            )

            # ======================================
            # WORLD POSITION AT RIGHT EDGE
            # ======================================

            floor_right_x = (
                player.x
                + ray_right_x *
                row_distance
            )

            floor_right_y = (
                player.y
                + ray_right_y *
                row_distance
            )

            # ======================================
            # WORLD STEP ACROSS SCREEN
            # ======================================

            step_world_x = (
                floor_right_x -
                floor_left_x
            ) / WIDTH

            step_world_y = (
                floor_right_y -
                floor_left_y
            ) / WIDTH

            current_x = floor_left_x
            current_y = floor_left_y

            for screen_x in range(
                0,
                WIDTH,
                step_x
            ):

                # ==================================
                # FLOOR TEXTURE
                # ==================================

                if self.floor_texture:

                    texture_x = int(
                        current_x *
                        floor_w *
                        1.5
                    ) % floor_w

                    texture_y = int(
                        current_y *
                        floor_h *
                        1.5
                    ) % floor_h

                    color = (
                        self.floor_texture.get_at(
                            (
                                texture_x,
                                texture_y
                            )
                        )
                    )

                    # Distance lighting
                    brightness = (
                        185 /
                        (
                            1.0 +
                            row_distance *
                            0.10
                        )
                    )

                    brightness = max(
                        35,
                        min(
                            185,
                            brightness
                        )
                    )

                    factor = (
                        brightness / 255.0
                    )

                    color = (
                        int(color.r * factor),
                        int(color.g * factor),
                        int(color.b * factor)
                    )

                else:

                    color = (
                        20,
                        15,
                        12
                    )

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        screen_x,
                        screen_y,
                        step_x,
                        step_y
                    )
                )

                current_x += (
                    step_world_x *
                    step_x
                )

                current_y += (
                    step_world_y *
                    step_x
                )

        # ==========================================
        # DRAW CEILING
        # ==========================================

        for screen_y in range(
            0,
            horizon,
            step_y
        ):

            # Distance to ceiling plane
            row_distance = (
                HEIGHT /
                (
                    2.0 *
                    (
                        horizon -
                        screen_y
                    )
                )
            )

            row_distance = max(
                row_distance,
                0.01
            )

            # ======================================
            # WORLD POSITION LEFT
            # ======================================

            ceiling_left_x = (
                player.x
                + ray_left_x *
                row_distance
            )

            ceiling_left_y = (
                player.y
                + ray_left_y *
                row_distance
            )

            # ======================================
            # WORLD POSITION RIGHT
            # ======================================

            ceiling_right_x = (
                player.x
                + ray_right_x *
                row_distance
            )

            ceiling_right_y = (
                player.y
                + ray_right_y *
                row_distance
            )

            # ======================================
            # WORLD STEP
            # ======================================

            step_world_x = (
                ceiling_right_x -
                ceiling_left_x
            ) / WIDTH

            step_world_y = (
                ceiling_right_y -
                ceiling_left_y
            ) / WIDTH

            current_x = ceiling_left_x
            current_y = ceiling_left_y

            for screen_x in range(
                0,
                WIDTH,
                step_x
            ):

                # ==================================
                # CEILING TEXTURE
                # ==================================

                if self.ceiling_texture:

                    texture_x = int(
                        current_x *
                        ceiling_w *
                        1.5
                    ) % ceiling_w

                    texture_y = int(
                        current_y *
                        ceiling_h *
                        1.5
                    ) % ceiling_h

                    color = (
                        self.ceiling_texture.get_at(
                            (
                                texture_x,
                                texture_y
                            )
                        )
                    )

                    # Ceiling darker than floor
                    brightness = (
                        115 /
                        (
                            1.0 +
                            row_distance *
                            0.12
                        )
                    )

                    brightness = max(
                        20,
                        min(
                            115,
                            brightness
                        )
                    )

                    factor = (
                        brightness / 255.0
                    )

                    color = (
                        int(color.r * factor),
                        int(color.g * factor),
                        int(color.b * factor)
                    )

                else:

                    color = (
                        7,
                        6,
                        7
                    )

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        screen_x,
                        screen_y,
                        step_x,
                        step_y
                    )
                )

                current_x += (
                    step_world_x *
                    step_x
                )

                current_y += (
                    step_world_y *
                    step_x
                )

    # ==========================================
    # WALLS
    # ==========================================

    def draw_walls(
        self,
        screen,
        player
    ):

        if self.raycaster is None:
            return

        half_fov = math.radians(
            FOV / 2
        )

        for column in range(
            0,
            WIDTH,
            2
        ):

            camera_x = (
                2 * column / WIDTH
                - 1
            )

            ray_angle = (
                player.angle
                + camera_x *
                half_fov
            )

            result = (
                self.raycaster.cast_ray(
                    player,
                    ray_angle
                )
            )

            # Supports either:
            # (distance, side)
            # or
            # (distance, side, wall_hit)

            distance = result[0]
            side = result[1]

            # ======================================
            # FISH-EYE CORRECTION
            # ======================================

            angle_difference = (
                ray_angle -
                player.angle
            )

            corrected_distance = (
                distance *
                math.cos(
                    angle_difference
                )
            )

            corrected_distance = max(
                corrected_distance,
                0.001
            )

            # ======================================
            # WALL HEIGHT
            # ======================================

            wall_height = int(
                HEIGHT /
                corrected_distance
            )

            wall_height = min(
                wall_height,
                HEIGHT * 2
            )

            wall_top = (
                HEIGHT // 2
                - wall_height // 2
            )

            wall_bottom = (
                HEIGHT // 2
                + wall_height // 2
            )

            # ======================================
            # TEXTURED WALL
            # ======================================

            if self.wall_texture:

                texture_width = (
                    self.wall_texture.get_width()
                )

                texture_height = (
                    self.wall_texture.get_height()
                )

                # Exact wall hit position
                if side == 0:

                    wall_hit = (
                        player.y
                        + distance *
                        math.sin(
                            ray_angle
                        )
                    )

                else:

                    wall_hit = (
                        player.x
                        + distance *
                        math.cos(
                            ray_angle
                        )
                    )

                wall_hit -= math.floor(
                    wall_hit
                )

                texture_x = int(
                    wall_hit *
                    texture_width
                )

                texture_x = max(
                    0,
                    min(
                        texture_width - 1,
                        texture_x
                    )
                )

                wall_slice = (
                    self.wall_texture.subsurface(
                        (
                            texture_x,
                            0,
                            1,
                            texture_height
                        )
                    )
                )

                wall_slice = pygame.transform.scale(
                    wall_slice,
                    (
                        2,
                        max(
                            1,
                            wall_bottom -
                            wall_top
                        )
                    )
                )

                # ==================================
                # LIGHTING
                # ==================================

                brightness = int(
                    255 /
                    (
                        1.0 +
                        corrected_distance *
                        0.14
                    )
                )

                brightness = max(
                    30,
                    min(
                        255,
                        brightness
                    )
                )

                if side == 1:

                    brightness = int(
                        brightness *
                        0.62
                    )

                dark_overlay = pygame.Surface(
                    wall_slice.get_size(),
                    pygame.SRCALPHA
                )

                dark_overlay.fill(
                    (
                        0,
                        0,
                        0,
                        255 - brightness
                    )
                )

                wall_slice.blit(
                    dark_overlay,
                    (0, 0)
                )

                screen.blit(
                    wall_slice,
                    (
                        column,
                        wall_top
                    )
                )

            else:

                # Fallback wall
                brightness = int(
                    150 /
                    (
                        1 +
                        corrected_distance *
                        0.15
                    )
                )

                brightness = max(
                    25,
                    min(
                        150,
                        brightness
                    )
                )

                if side == 1:

                    brightness = int(
                        brightness *
                        0.65
                    )

                pygame.draw.rect(
                    screen,
                    (
                        int(
                            brightness * 0.78
                        ),
                        int(
                            brightness * 0.52
                        ),
                        int(
                            brightness * 0.34
                        )
                    ),
                    (
                        column,
                        wall_top,
                        2,
                        wall_bottom -
                        wall_top
                    )
                )

    # ==========================================
    # VIGNETTE
    # ==========================================

    def draw_vignette(
        self,
        screen
    ):

        darkness = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        for i in range(
            70
        ):

            alpha = int(
                0.8 *
                (70 - i)
            )

            pygame.draw.rect(
                darkness,
                (
                    0,
                    0,
                    0,
                    alpha
                ),
                (
                    i,
                    i,
                    WIDTH - 2 * i,
                    HEIGHT - 2 * i
                ),
                2
            )

        screen.blit(
            darkness,
            (0, 0)
        )