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
        # LOAD WALL TEXTURE
        # ==========================================

        texture_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "textures",
            "wall.png"
        )

        self.wall_texture = pygame.image.load(
            texture_path
        ).convert()

        # Texture dimensions
        self.texture_width = self.wall_texture.get_width()
        self.texture_height = self.wall_texture.get_height()

    # ==========================================
    # SET RAYCASTER
    # ==========================================

    def set_raycaster(self, raycaster):

        self.raycaster = raycaster

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self, screen, player):

        # ==========================================
        # DARK CEILING
        # ==========================================

        screen.fill((5, 5, 6))

        pygame.draw.rect(
            screen,
            (7, 6, 7),
            (
                0,
                0,
                WIDTH,
                HEIGHT // 2
            )
        )

        # ==========================================
        # DARK FLOOR
        # ==========================================

        pygame.draw.rect(
            screen,
            (18, 14, 12),
            (
                0,
                HEIGHT // 2,
                WIDTH,
                HEIGHT // 2
            )
        )

        # ==========================================
        # RAYCASTING
        # ==========================================

        half_fov = math.radians(FOV / 2)

        # Render every 2nd column for performance
        for column in range(0, WIDTH, 2):

            camera_x = (
                2 * column / WIDTH - 1
            )

            ray_angle = (
                player.angle
                + camera_x * half_fov
            )

            distance, side, wall_hit = (
                self.raycaster.cast_ray(
                    player,
                    ray_angle
                )
            )

            # ======================================
            # FISH-EYE CORRECTION
            # ======================================

            angle_difference = (
                ray_angle - player.angle
            )

            corrected_distance = (
                distance *
                math.cos(angle_difference)
            )

            corrected_distance = max(
                corrected_distance,
                0.001
            )

            # ======================================
            # WALL HEIGHT
            # ======================================

            wall_height = int(
                HEIGHT / corrected_distance
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
            # FIND TEXTURE COLUMN
            # ======================================

            texture_x = int(
                wall_hit *
                self.texture_width
            )

            texture_x = max(
                0,
                min(
                    self.texture_width - 1,
                    texture_x
                )
            )

            # ======================================
            # GET ONE VERTICAL STRIP
            # ======================================

            texture_column = self.wall_texture.subsurface(
                (
                    texture_x,
                    0,
                    1,
                    self.texture_height
                )
            )

            # ======================================
            # SCALE TEXTURE COLUMN
            # ======================================

            texture_column = pygame.transform.scale(
                texture_column,
                (
                    2,
                    max(1, wall_height)
                )
            )
            texture_column = texture_column.convert()

            # ======================================
            # DISTANCE LIGHTING
            # ======================================

            brightness = (
                255 /
                (1 + corrected_distance * 0.18)
            )

            brightness = max(
                25,
                min(180, int(brightness))
            )

            # Side walls are darker
            if side == 1:

                brightness = int(
                    brightness * 0.65
                )

            # ======================================
            # DARKEN TEXTURE
            # ======================================

            shade = pygame.Surface(
                texture_column.get_size(),
                pygame.SRCALPHA
            )

            darkness = 255 - brightness

            shade.fill(
                (
                    0,
                    0,
                    0,
                    darkness
                )
            )

            texture_column.blit(
                shade,
                (0, 0),
                special_flags=pygame.BLEND_RGBA_SUB
            )

            # ======================================
            # DRAW TEXTURED WALL
            # ======================================

            screen.blit(
                texture_column,
                (
                    column,
                    wall_top
                )
            )

    # ==========================================
    # DARK VIGNETTE
    # ==========================================

        darkness = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        for i in range(70):

            alpha = int(
                1.2 * (70 - i)
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