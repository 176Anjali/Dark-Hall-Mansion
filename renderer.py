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

        base_path = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        texture_path = os.path.join(
            base_path,
            "textures"
        )

        item_path = os.path.join(
            base_path,
            "items"
        )

        enemy_path = os.path.join(
            base_path,
            "enemy"
        )

        self.wall_texture = self.load_texture(
            os.path.join(texture_path, "wall.png")
        )

        self.door_texture = self.load_texture(
            os.path.join(texture_path, "door.png")
        )

        self.floor_texture = self.load_texture(
            os.path.join(texture_path, "floor.png")
        )

        self.ceiling_texture = self.load_texture(
            os.path.join(texture_path, "ceiling.png")
        )

        self.key_image = self.load_texture(
            os.path.join(item_path, "key.png")
        )

        self.candle_image = self.load_texture(
            os.path.join(item_path, "candle.png")
        )

        self.lock_image = self.load_texture(
            os.path.join(item_path, "lock.png")
        )

        self.medkit_image = self.load_texture(
            os.path.join(item_path, "medkit.png")
        )

        self.enemy_image = self.load_texture(
            os.path.join(enemy_path, "enemy.png")
        )

        self.message = ""
        self.message_timer = 0

        self.font = pygame.font.SysFont(
            "Arial",
            26,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            20,
            bold=True
        )

        self.depth_buffer = [
            20.0
        ] * WIDTH

    # ==========================================
    # TEXTURE
    # ==========================================

    def load_texture(self, path):

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            return image

        except Exception as error:

            print(
                "Asset error:",
                path
            )

            print(error)

            return None

    # ==========================================
    # RAYCASTER
    # ==========================================

    def set_raycaster(self, raycaster):

        self.raycaster = raycaster

    # ==========================================
    # MESSAGE
    # ==========================================

    def show_message(self, text):

        self.message = text
        self.message_timer = 2.5

    # ==========================================
    # FLOOR / CEILING
    # ==========================================

    def draw_floor_and_ceiling(
        self,
        screen,
        player
    ):

        horizon = HEIGHT // 2

        screen.fill(
            (7, 7, 10)
        )

        pygame.draw.rect(
            screen,
            (22, 18, 15),
            (
                0,
                horizon,
                WIDTH,
                HEIGHT - horizon
            )
        )

        # Ceiling
        pygame.draw.rect(
            screen,
            (7, 7, 10),
            (
                0,
                0,
                WIDTH,
                horizon
            )
        )

        # Textured floor
        if self.floor_texture:

            texture = self.floor_texture

            tex_w = texture.get_width()
            tex_h = texture.get_height()

            for y in range(
                horizon + 4,
                HEIGHT,
                4
            ):

                distance = (
                    HEIGHT * 0.45
                ) / max(
                    1,
                    y - horizon
                )

                shade = max(
                    0.2,
                    min(
                        0.75,
                        1.0 /
                        (1 + distance * 0.08)
                    )
                )

                for x in range(
                    0,
                    WIDTH,
                    4
                ):

                    angle_offset = (
                        (x / WIDTH) - 0.5
                    ) * math.radians(FOV)

                    world_x = (
                        player.x
                        + math.cos(
                            player.angle
                            + angle_offset
                        ) * distance
                    )

                    world_y = (
                        player.y
                        + math.sin(
                            player.angle
                            + angle_offset
                        ) * distance
                    )

                    tx = int(
                        world_x * tex_w
                    ) % tex_w

                    ty = int(
                        world_y * tex_h
                    ) % tex_h

                    color = texture.get_at(
                        (tx, ty)
                    )

                    color = (
                        int(color.r * shade),
                        int(color.g * shade),
                        int(color.b * shade)
                    )

                    pygame.draw.rect(
                        screen,
                        color,
                        (x, y, 4, 4)
                    )

    # ==========================================
    # WALLS
    # ==========================================

    def draw_walls(
        self,
        screen,
        player
    ):

        half_fov = math.radians(
            FOV / 2
        )

        projection_distance = (
            (WIDTH / 2)
            / math.tan(half_fov)
        )

        self.depth_buffer = [
            20.0
        ] * WIDTH

        for column in range(
            0,
            WIDTH,
            2
        ):

            camera_x = (
                2 * column / WIDTH - 1
            )

            ray_angle = (
                player.angle
                + camera_x * half_fov
            )

            distance, side, tile = (
                self.raycaster.cast_ray(
                    player,
                    ray_angle
                )
            )

            corrected_distance = (
                distance
                * math.cos(
                    ray_angle - player.angle
                )
            )

            corrected_distance = max(
                corrected_distance,
                0.05
            )

            self.depth_buffer[column] = (
                corrected_distance
            )

            if column + 1 < WIDTH:

                self.depth_buffer[
                    column + 1
                ] = corrected_distance

            wall_height = int(
                projection_distance
                / corrected_distance
            )

            wall_height = min(
                wall_height,
                HEIGHT * 2
            )

            wall_top = (
                HEIGHT // 2
                - wall_height // 2
            )

            if tile in ("D", "E"):

                texture = self.door_texture

            else:

                texture = self.wall_texture

            if texture:

                tex_w = texture.get_width()
                tex_h = texture.get_height()

                if side == 0:

                    wall_hit = (
                        player.y
                        + distance
                        * math.sin(ray_angle)
                    )

                else:

                    wall_hit = (
                        player.x
                        + distance
                        * math.cos(ray_angle)
                    )

                wall_hit -= math.floor(
                    wall_hit
                )

                texture_x = int(
                    wall_hit * tex_w
                )

                texture_x = max(
                    0,
                    min(
                        tex_w - 1,
                        texture_x
                    )
                )

                strip = texture.subsurface(
                    texture_x,
                    0,
                    1,
                    tex_h
                )

                strip = pygame.transform.scale(
                    strip,
                    (
                        2,
                        wall_height
                    )
                )

                brightness = (
                    1.0 /
                    (
                        1
                        + corrected_distance
                        * 0.08
                    )
                )

                brightness = max(
                    0.18,
                    min(
                        1.0,
                        brightness
                    )
                )

                if side == 1:

                    brightness *= 0.7

                lighting = pygame.Surface(
                    strip.get_size()
                )

                lighting.fill(
                    (
                        int(
                            255 * brightness
                        ),
                        int(
                            255 * brightness
                        ),
                        int(
                            255 * brightness
                        )
                    )
                )

                strip.blit(
                    lighting,
                    (0, 0),
                    special_flags=pygame.BLEND_RGB_MULT
                )

                screen.blit(
                    strip,
                    (
                        column,
                        wall_top
                    )
                )

            else:

                brightness = max(
                    20,
                    int(
                        120 /
                        (
                            1
                            + corrected_distance
                            * 0.1
                        )
                    )
                )

                pygame.draw.rect(
                    screen,
                    (
                        brightness,
                        int(brightness * 0.7),
                        int(brightness * 0.5)
                    ),
                    (
                        column,
                        wall_top,
                        2,
                        wall_height
                    )
                )

    # ==========================================
    # SPRITE
    # ==========================================

    def draw_sprite(
        self,
        screen,
        player,
        image,
        x,
        y,
        scale=1.0
    ):

        if image is None:
            return

        dx = x - player.x
        dy = y - player.y

        distance = math.hypot(
            dx,
            dy
        )

        if distance <= 0.1:
            return

        angle = math.atan2(
            dy,
            dx
        )

        angle_difference = (
            angle - player.angle
        )

        while angle_difference > math.pi:

            angle_difference -= (
                2 * math.pi
            )

        while angle_difference < -math.pi:

            angle_difference += (
                2 * math.pi
            )

        half_fov = math.radians(
            FOV / 2
        )

        if abs(angle_difference) > (
            half_fov + 0.5
        ):
            return

        projection_distance = (
            WIDTH / 2
        ) / math.tan(half_fov)

        screen_x = (
            WIDTH / 2
            + math.tan(
                angle_difference
            ) * projection_distance
        )

        sprite_height = int(
            projection_distance
            / distance
            * scale
        )

        sprite_height = max(
            10,
            min(
                900,
                sprite_height
            )
        )

        ratio = (
            image.get_width()
            / image.get_height()
        )

        sprite_width = int(
            sprite_height * ratio
        )

        sprite = pygame.transform.smoothscale(
            image,
            (
                sprite_width,
                sprite_height
            )
        )

        top = (
            HEIGHT // 2
            - sprite_height // 2
        )

        left = int(
            screen_x
            - sprite_width / 2
        )

        # Draw in small horizontal sections
        for sx in range(
            max(0, left),
            min(WIDTH, left + sprite_width)
        ):

            relative_x = sx - left

            depth_index = (
                sx
                if sx < WIDTH
                else WIDTH - 1
            )

            if distance < (
                self.depth_buffer[
                    depth_index
                ] + 0.15
            ):

                source_x = int(
                    relative_x
                    * image.get_width()
                    / sprite_width
                )

                if (
                    source_x < 0
                    or source_x >= image.get_width()
                ):
                    continue

                column_surface = sprite.subsurface(
                    relative_x,
                    0,
                    1,
                    sprite_height
                )

                screen.blit(
                    column_surface,
                    (
                        sx,
                        top
                    )
                )

    # ==========================================
    # ITEMS + ENEMY
    # ==========================================

    def draw_objects(
        self,
        screen,
        player,
        enemy
    ):

        # Key
        if not self.mansion_map.key_collected:

            x, y = self.mansion_map.key_position

            self.draw_sprite(
                screen,
                player,
                self.key_image,
                x,
                y,
                0.75
            )

        # Candle
        candle_x, candle_y = (
            self.mansion_map
            .get_item_positions()["candle"]
        )

        self.draw_sprite(
            screen,
            player,
            self.candle_image,
            candle_x,
            candle_y,
            0.55
        )

        # Medkit
        medkit_x, medkit_y = (
            self.mansion_map
            .get_item_positions()["medkit"]
        )

        self.draw_sprite(
            screen,
            player,
            self.medkit_image,
            medkit_x,
            medkit_y,
            0.55
        )

        # Enemy
        if enemy.active:

            self.draw_sprite(
                screen,
                player,
                self.enemy_image,
                enemy.x,
                enemy.y,
                1.4
            )

    # ==========================================
    # CROSSHAIR
    # ==========================================

    def draw_crosshair(self, screen):

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (
                center_x - 6,
                center_y
            ),
            (
                center_x + 6,
                center_y
            ),
            2
        )

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (
                center_x,
                center_y - 6
            ),
            (
                center_x,
                center_y + 6
            ),
            2
        )

    # ==========================================
    # MESSAGE
    # ==========================================

    def draw_message(self, screen, dt):

        if self.message_timer <= 0:
            return

        self.message_timer -= dt

        text = self.font.render(
            self.message,
            True,
            (240, 240, 240)
        )

        rect = text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 75
            )
        )

        background_rect = rect.inflate(
            40,
            20
        )

        background = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA
        )

        background.fill(
            (0, 0, 0, 190)
        )

        screen.blit(
            background,
            background_rect
        )

        screen.blit(
            text,
            rect
        )

    # ==========================================
    # HUD
    # ==========================================

    def draw_hud(
        self,
        screen,
        key_collected,
        enemy_active,
        flashlight
    ):

        key_text = (
            "KEY: FOUND"
            if key_collected
            else "KEY: SEARCH"
        )

        key_color = (
            (100, 255, 100)
            if key_collected
            else (220, 220, 220)
        )

        text = self.small_font.render(
            key_text,
            True,
            key_color
        )

        screen.blit(
            text,
            (25, 25)
        )

        if enemy_active:

            enemy_text = self.small_font.render(
                "!!! THE ENEMY IS SEARCHING !!!",
                True,
                (220, 50, 50)
            )

            screen.blit(
                enemy_text,
                (
                    WIDTH // 2
                    - enemy_text.get_width() // 2,
                    25
                )
            )

        flashlight_text = (
            "FLASHLIGHT: ON"
            if flashlight
            else "FLASHLIGHT: OFF"
        )

        flash_text = self.small_font.render(
            flashlight_text,
            True,
            (220, 220, 220)
        )

        screen.blit(
            flash_text,
            (
                WIDTH - flash_text.get_width() - 25,
                25
            )
        )

    # ==========================================
    # VIGNETTE
    # ==========================================

    def draw_vignette(self, screen):

        darkness = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        for i in range(70):

            alpha = int(
                1.4 * (70 - i)
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

    # ==========================================
    # MAIN DRAW
    # ==========================================

    def draw(
        self,
        screen,
        player,
        enemy,
        key_collected,
        flashlight,
        dt
    ):

        if self.raycaster is None:
            return

        self.draw_floor_and_ceiling(
            screen,
            player
        )

        self.draw_walls(
            screen,
            player
        )

        self.draw_objects(
            screen,
            player,
            enemy
        )

        self.draw_crosshair(
            screen
        )

        self.draw_hud(
            screen,
            key_collected,
            enemy.active,
            flashlight
        )

        self.draw_message(
            screen,
            dt
        )

        self.draw_vignette(
            screen
        )