
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
        # Depth buffer used for enemy rendering
        self.depth_buffer = [float("inf")] * WIDTH

        # ==================================================
        # TEXTURES
        # ==================================================

        base_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "textures"
        )

        self.wall_texture = self.load_texture(
            os.path.join(base_path, "wall.png")
        )

        self.door_texture = self.load_texture(
            os.path.join(base_path, "door.png")
        )

        self.floor_texture = self.load_texture(
            os.path.join(base_path, "floor.png")
        )

        self.ceiling_texture = self.load_texture(
            os.path.join(base_path, "ceiling.png")
        )

        # ==================================================
        # MESSAGE
        # ==================================================

        self.message = ""
        self.message_timer = 0.0

        self.font = pygame.font.SysFont(
            "Arial",
            26,
            bold=True
        )

    # ======================================================
    # LOAD TEXTURE
    # ======================================================

    def load_texture(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return image
        except Exception as error:
            print("Texture error:", path)
            print(error)
            return None

    # ======================================================
    # RAYCASTER
    # ======================================================

    def set_raycaster(self, raycaster):
        self.raycaster = raycaster

    # ======================================================
    # MESSAGE
    # ======================================================

    def show_message(self, text):
        self.message = text
        self.message_timer = 1.5

    # ======================================================
    # DRAW FLOOR + CEILING
    # ======================================================

    def draw_floor_and_ceiling(
        self,
        screen,
        player
    ):

        horizon = HEIGHT // 2

        # --------------------------------------------------
        # FALLBACK COLORS
        # --------------------------------------------------

        screen.fill((8, 7, 7))

        pygame.draw.rect(
            screen,
            (25, 19, 16),
            (0, horizon, WIDTH, HEIGHT - horizon)
        )

        pygame.draw.rect(
            screen,
            (7, 7, 10),
            (0, 0, WIDTH, horizon)
        )

        # Textured floor
        if self.floor_texture:

            texture = self.floor_texture
            tex_w = texture.get_width()
            tex_h = texture.get_height()

            ray_left_angle = player.angle - math.radians(FOV / 2)
            ray_right_angle = player.angle + math.radians(FOV / 2)

            left_x = math.cos(ray_left_angle)
            left_y = math.sin(ray_left_angle)
            right_x = math.cos(ray_right_angle)
            right_y = math.sin(ray_right_angle)

            # Sample every 3 pixels for performance
            for y in range(horizon + 1, HEIGHT, 3):
                distance = (HEIGHT * 0.45) / max(1, y - horizon)

                for x in range(0, WIDTH, 3):
                    camera_x = x / WIDTH

                    world_dir_x = left_x + (right_x - left_x) * camera_x
                    world_dir_y = left_y + (right_y - left_y) * camera_x

                    world_x = player.x + world_dir_x * distance
                    world_y = player.y + world_dir_y * distance

                    tex_x = int(world_x * tex_w) % tex_w
                    tex_y = int(world_y * tex_h) % tex_h

                    color = texture.get_at((tex_x, tex_y))

                    shade = max(
                        0.25,
                        min(
                            0.85,
                            1.0 / (1 + distance * 0.08)
                        )
                    )

                    color = (
                        int(color.r * shade),
                        int(color.g * shade),
                        int(color.b * shade)
                    )

                    pygame.draw.rect(screen, color, (x, y, 3, 3))

        # Textured ceiling
        if self.ceiling_texture:

            texture = self.ceiling_texture
            tex_w = texture.get_width()
            tex_h = texture.get_height()

            ray_left_angle = player.angle - math.radians(FOV / 2)
            ray_right_angle = player.angle + math.radians(FOV / 2)

            left_x = math.cos(ray_left_angle)
            left_y = math.sin(ray_left_angle)
            right_x = math.cos(ray_right_angle)
            right_y = math.sin(ray_right_angle)

            for y in range(0, horizon, 3):
                distance = (HEIGHT * 0.45) / max(1, horizon - y)

                for x in range(0, WIDTH, 3):
                    camera_x = x / WIDTH

                    world_dir_x = left_x + (right_x - left_x) * camera_x
                    world_dir_y = left_y + (right_y - left_y) * camera_x

                    world_x = player.x + world_dir_x * distance
                    world_y = player.y + world_dir_y * distance

                    tex_x = int(world_x * tex_w) % tex_w
                    tex_y = int(world_y * tex_h) % tex_h

                    color = texture.get_at((tex_x, tex_y))

                    shade = max(
                        0.18,
                        min(
                            0.65,
                            1.0 / (1 + distance * 0.10)
                        )
                    )

                    color = (
                        int(color.r * shade),
                        int(color.g * shade),
                        int(color.b * shade)
                    )

                    pygame.draw.rect(screen, color, (x, y, 3, 3))

    # ======================================================
    # DRAW WALLS
    # ======================================================

    def draw_walls(
        self,
        screen,
        player
    ):

        half_fov = math.radians(FOV / 2)

        # Projection distance
        projection_distance = (WIDTH / 2) / math.tan(half_fov)

        # Reset depth buffer
        self.depth_buffer = [float("inf")] * WIDTH

        for column in range(0, WIDTH, 2):

            camera_x = 2 * column / WIDTH - 1

            ray_angle = player.angle + camera_x * half_fov

            distance, side, tile = self.raycaster.cast_ray(player, ray_angle)

            # ------------------------------------------------
            # FISH-EYE CORRECTION
            # ------------------------------------------------

            angle_difference = ray_angle - player.angle

            corrected_distance = distance * math.cos(angle_difference)
            corrected_distance = max(corrected_distance, 0.05)

            # Store wall distance for this screen column
            self.depth_buffer[column] = corrected_distance
            if column + 1 < WIDTH:
                self.depth_buffer[column + 1] = corrected_distance

            # ------------------------------------------------
            # WALL HEIGHT
            # ------------------------------------------------
            wall_height = int(projection_distance / corrected_distance)
            wall_height = min(wall_height, HEIGHT * 2)

            wall_top = HEIGHT // 2 - wall_height // 2

            # ------------------------------------------------
            # SELECT TEXTURE
            # ------------------------------------------------
            texture = self.wall_texture
            if tile == "D":
                texture = self.door_texture

            # ------------------------------------------------
            # TEXTURED WALL
            # ------------------------------------------------
            if texture:

                tex_w = texture.get_width()
                tex_h = texture.get_height()

                # Exact wall hit position
                if side == 0:
                    wall_hit = player.y + distance * math.sin(ray_angle)
                else:
                    wall_hit = player.x + distance * math.cos(ray_angle)

                wall_hit -= math.floor(wall_hit)

                texture_x = int(wall_hit * tex_w)
                texture_x = max(0, min(tex_w - 1, texture_x))

                # Extract vertical strip
                strip = texture.subsurface(texture_x, 0, 1, tex_h)
                strip = pygame.transform.scale(strip, (2, wall_height))

                # ------------------------------------------------
                # LIGHTING
                # ------------------------------------------------
                brightness = 1.0 / (1 + corrected_distance * 0.08)
                brightness = max(0.25, min(1.0, brightness))

                # Side walls darker
                if side == 1:
                    brightness *= 0.72

                lighting = pygame.Surface(strip.get_size())
                lighting.fill((
                    int(255 * brightness),
                    int(255 * brightness),
                    int(255 * brightness)
                ))

                strip.blit(lighting, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                screen.blit(strip, (column, wall_top))

            else:
                # Fallback
                brightness = int(120 / (1 + corrected_distance * 0.1))
                brightness = max(20, min(120, brightness))

                pygame.draw.rect(
                    screen,
                    (
                        brightness,
                        int(brightness * 0.7),
                        int(brightness * 0.5)
                    ),
                    (column, wall_top, 2, wall_height)
                )

    # ======================================================
    # DRAW ENEMY
    # ======================================================

    def draw_enemy(
        self,
        screen,
        player,
        enemy
    ):

        # Enemy not provided or inactive
        if enemy is None or not getattr(enemy, "active", False):
            return

        # Enemy dead check
        if hasattr(enemy, "health") and enemy.health <= 0:
            return

        dx = enemy.x - player.x
        dy = enemy.y - player.y

        distance = math.hypot(dx, dy)
        if distance < 0.1:
            return

        enemy_angle = math.atan2(dy, dx)
        angle_difference = enemy_angle - player.angle

        while angle_difference > math.pi:
            angle_difference -= 2 * math.pi
        while angle_difference < -math.pi:
            angle_difference += 2 * math.pi

        half_fov = math.radians(FOV / 2)
        if abs(angle_difference) > half_fov:
            return

        projection_distance = (WIDTH / 2) / math.tan(half_fov)

        screen_x = WIDTH / 2 + math.tan(angle_difference) * projection_distance

        sprite_height = int(projection_distance / distance)
        sprite_height = int(sprite_height * 1.5)
        sprite_height = max(20, min(sprite_height, HEIGHT * 2))

        sprite_width = int(sprite_height * enemy.image.get_width() / enemy.image.get_height())

        sprite = pygame.transform.scale(enemy.image, (sprite_width, sprite_height))

        sprite_x = int(screen_x - sprite_width / 2)
        sprite_y = int(HEIGHT / 2 - sprite_height / 2)

        # Render in small vertical strips so walls can occlude
        for x in range(sprite_width):
            screen_x_position = sprite_x + x
            if screen_x_position < 0 or screen_x_position >= WIDTH:
                continue

            wall_distance = self.depth_buffer[screen_x_position]
            if distance < wall_distance:
                source_x = int(x * enemy.image.get_width() / sprite_width)
                source_x = max(0, min(enemy.image.get_width() - 1, source_x))

                column = sprite.subsurface((x, 0, 1, sprite_height))
                screen.blit(column, (screen_x_position, sprite_y))

    # ======================================================
    # CROSSHAIR
    # ======================================================

    def draw_crosshair(self, screen):

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (center_x - 6, center_y),
            (center_x + 6, center_y),
            2
        )

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (center_x, center_y - 6),
            (center_x, center_y + 6),
            2
        )

    # ======================================================
    # MESSAGE
    # ======================================================

    def draw_message(self, screen):
        if self.message_timer <= 0:
            return

        # decrement based on frame (approx 60fps)
        self.message_timer -= (1 / 60)

        text = self.font.render(self.message, True, (240, 240, 240))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))

        background_rect = rect.inflate(35, 18)
        background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))

        screen.blit(background, background_rect)
        screen.blit(text, rect)

    # ======================================================
    # MAIN DRAW
    # ======================================================

    def draw(
        self,
        screen,
        player,
        enemy=None
    ):

        if self.raycaster is None:
            return

        # Floor + ceiling move with player
        self.draw_floor_and_ceiling(screen, player)

        # Walls
        self.draw_walls(screen, player)

        # Enemy / ghost
        if enemy is not None:
            self.draw_enemy(screen, player, enemy)

        # Crosshair
        self.draw_crosshair(screen)

        # Messages
        self.draw_message(screen)

        # --------------------------------------------------
        # VIGNETTE
        # --------------------------------------------------

        darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for i in range(60):
            alpha = int(1.3 * (60 - i))
            pygame.draw.rect(
                darkness,
                (0, 0, 0, alpha),
                (i, i, WIDTH - 2 * i, HEIGHT - 2 * i),
                2
            )

        screen.blit(darkness, (0, 0))
# filepath: c:\Users\Lenovo\Documents\Dark-Hall-Mansion\renderer.py
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
        # Depth buffer used for enemy rendering
        self.depth_buffer = [float("inf")] * WIDTH

        # ==================================================
        # TEXTURES
        # ==================================================

        base_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "textures"
        )

        self.wall_texture = self.load_texture(
            os.path.join(base_path, "wall.png")
        )

        self.door_texture = self.load_texture(
            os.path.join(base_path, "door.png")
        )

        self.floor_texture = self.load_texture(
            os.path.join(base_path, "floor.png")
        )

        self.ceiling_texture = self.load_texture(
            os.path.join(base_path, "ceiling.png")
        )

        # ==================================================
        # MESSAGE
        # ==================================================

        self.message = ""
        self.message_timer = 0.0

        self.font = pygame.font.SysFont(
            "Arial",
            26,
            bold=True
        )

    # ======================================================
    # LOAD TEXTURE
    # ======================================================

    def load_texture(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return image
        except Exception as error:
            print("Texture error:", path)
            print(error)
            return None

    # ======================================================
    # RAYCASTER
    # ======================================================

    def set_raycaster(self, raycaster):
        self.raycaster = raycaster

    # ======================================================
    # MESSAGE
    # ======================================================

    def show_message(self, text):
        self.message = text
        self.message_timer = 1.5

    # ======================================================
    # DRAW FLOOR + CEILING
    # ======================================================

    def draw_floor_and_ceiling(
        self,
        screen,
        player
    ):

        horizon = HEIGHT // 2

        # --------------------------------------------------
        # FALLBACK COLORS
        # --------------------------------------------------

        screen.fill((8, 7, 7))

        pygame.draw.rect(
            screen,
            (25, 19, 16),
            (0, horizon, WIDTH, HEIGHT - horizon)
        )

        pygame.draw.rect(
            screen,
            (7, 7, 10),
            (0, 0, WIDTH, horizon)
        )

        # Textured floor
        if self.floor_texture:

            texture = self.floor_texture
            tex_w = texture.get_width()
            tex_h = texture.get_height()

            ray_left_angle = player.angle - math.radians(FOV / 2)
            ray_right_angle = player.angle + math.radians(FOV / 2)

            left_x = math.cos(ray_left_angle)
            left_y = math.sin(ray_left_angle)
            right_x = math.cos(ray_right_angle)
            right_y = math.sin(ray_right_angle)

            # Sample every 3 pixels for performance
            for y in range(horizon + 1, HEIGHT, 3):
                distance = (HEIGHT * 0.45) / max(1, y - horizon)

                for x in range(0, WIDTH, 3):
                    camera_x = x / WIDTH

                    world_dir_x = left_x + (right_x - left_x) * camera_x
                    world_dir_y = left_y + (right_y - left_y) * camera_x

                    world_x = player.x + world_dir_x * distance
                    world_y = player.y + world_dir_y * distance

                    tex_x = int(world_x * tex_w) % tex_w
                    tex_y = int(world_y * tex_h) % tex_h

                    color = texture.get_at((tex_x, tex_y))

                    shade = max(
                        0.25,
                        min(
                            0.85,
                            1.0 / (1 + distance * 0.08)
                        )
                    )

                    color = (
                        int(color.r * shade),
                        int(color.g * shade),
                        int(color.b * shade)
                    )

                    pygame.draw.rect(screen, color, (x, y, 3, 3))

        # Textured ceiling
        if self.ceiling_texture:

            texture = self.ceiling_texture
            tex_w = texture.get_width()
            tex_h = texture.get_height()

            ray_left_angle = player.angle - math.radians(FOV / 2)
            ray_right_angle = player.angle + math.radians(FOV / 2)

            left_x = math.cos(ray_left_angle)
            left_y = math.sin(ray_left_angle)
            right_x = math.cos(ray_right_angle)
            right_y = math.sin(ray_right_angle)

            for y in range(0, horizon, 3):
                distance = (HEIGHT * 0.45) / max(1, horizon - y)

                for x in range(0, WIDTH, 3):
                    camera_x = x / WIDTH

                    world_dir_x = left_x + (right_x - left_x) * camera_x
                    world_dir_y = left_y + (right_y - left_y) * camera_x

                    world_x = player.x + world_dir_x * distance
                    world_y = player.y + world_dir_y * distance

                    tex_x = int(world_x * tex_w) % tex_w
                    tex_y = int(world_y * tex_h) % tex_h

                    color = texture.get_at((tex_x, tex_y))

                    shade = max(
                        0.18,
                        min(
                            0.65,
                            1.0 / (1 + distance * 0.10)
                        )
                    )

                    color = (
                        int(color.r * shade),
                        int(color.g * shade),
                        int(color.b * shade)
                    )

                    pygame.draw.rect(screen, color, (x, y, 3, 3))

    # ======================================================
    # DRAW WALLS
    # ======================================================

    def draw_walls(
        self,
        screen,
        player
    ):

        half_fov = math.radians(FOV / 2)

        # Projection distance
        projection_distance = (WIDTH / 2) / math.tan(half_fov)

        # Reset depth buffer
        self.depth_buffer = [float("inf")] * WIDTH

        for column in range(0, WIDTH, 2):

            camera_x = 2 * column / WIDTH - 1

            ray_angle = player.angle + camera_x * half_fov

            distance, side, tile = self.raycaster.cast_ray(player, ray_angle)

            # ------------------------------------------------
            # FISH-EYE CORRECTION
            # ------------------------------------------------

            angle_difference = ray_angle - player.angle

            corrected_distance = distance * math.cos(angle_difference)
            corrected_distance = max(corrected_distance, 0.05)

            # Store wall distance for this screen column
            self.depth_buffer[column] = corrected_distance
            if column + 1 < WIDTH:
                self.depth_buffer[column + 1] = corrected_distance

            # ------------------------------------------------
            # WALL HEIGHT
            # ------------------------------------------------
            wall_height = int(projection_distance / corrected_distance)
            wall_height = min(wall_height, HEIGHT * 2)

            wall_top = HEIGHT // 2 - wall_height // 2

            # ------------------------------------------------
            # SELECT TEXTURE
            # ------------------------------------------------
            texture = self.wall_texture
            if tile == "D":
                texture = self.door_texture

            # ------------------------------------------------
            # TEXTURED WALL
            # ------------------------------------------------
            if texture:

                tex_w = texture.get_width()
                tex_h = texture.get_height()

                # Exact wall hit position
                if side == 0:
                    wall_hit = player.y + distance * math.sin(ray_angle)
                else:
                    wall_hit = player.x + distance * math.cos(ray_angle)

                wall_hit -= math.floor(wall_hit)

                texture_x = int(wall_hit * tex_w)
                texture_x = max(0, min(tex_w - 1, texture_x))

                # Extract vertical strip
                strip = texture.subsurface(texture_x, 0, 1, tex_h)
                strip = pygame.transform.scale(strip, (2, wall_height))

                # ------------------------------------------------
                # LIGHTING
                # ------------------------------------------------
                brightness = 1.0 / (1 + corrected_distance * 0.08)
                brightness = max(0.25, min(1.0, brightness))

                # Side walls darker
                if side == 1:
                    brightness *= 0.72

                lighting = pygame.Surface(strip.get_size())
                lighting.fill((
                    int(255 * brightness),
                    int(255 * brightness),
                    int(255 * brightness)
                ))

                strip.blit(lighting, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                screen.blit(strip, (column, wall_top))

            else:
                # Fallback
                brightness = int(120 / (1 + corrected_distance * 0.1))
                brightness = max(20, min(120, brightness))

                pygame.draw.rect(
                    screen,
                    (
                        brightness,
                        int(brightness * 0.7),
                        int(brightness * 0.5)
                    ),
                    (column, wall_top, 2, wall_height)
                )

    # ======================================================
    # DRAW ENEMY
    # ======================================================

    def draw_enemy(
        self,
        screen,
        player,
        enemy
    ):

        # Enemy not provided or inactive
        if enemy is None or not getattr(enemy, "active", False):
            return

        # Enemy dead check
        if hasattr(enemy, "health") and enemy.health <= 0:
            return

        dx = enemy.x - player.x
        dy = enemy.y - player.y

        distance = math.hypot(dx, dy)
        if distance < 0.1:
            return

        enemy_angle = math.atan2(dy, dx)
        angle_difference = enemy_angle - player.angle

        while angle_difference > math.pi:
            angle_difference -= 2 * math.pi
        while angle_difference < -math.pi:
            angle_difference += 2 * math.pi

        half_fov = math.radians(FOV / 2)
        if abs(angle_difference) > half_fov:
            return

        projection_distance = (WIDTH / 2) / math.tan(half_fov)

        screen_x = WIDTH / 2 + math.tan(angle_difference) * projection_distance

        sprite_height = int(projection_distance / distance)
        sprite_height = int(sprite_height * 1.5)
        sprite_height = max(20, min(sprite_height, HEIGHT * 2))

        sprite_width = int(sprite_height * enemy.image.get_width() / enemy.image.get_height())

        sprite = pygame.transform.scale(enemy.image, (sprite_width, sprite_height))

        sprite_x = int(screen_x - sprite_width / 2)
        sprite_y = int(HEIGHT / 2 - sprite_height / 2)

        # Render in small vertical strips so walls can occlude
        for x in range(sprite_width):
            screen_x_position = sprite_x + x
            if screen_x_position < 0 or screen_x_position >= WIDTH:
                continue

            wall_distance = self.depth_buffer[screen_x_position]
            if distance < wall_distance:
                source_x = int(x * enemy.image.get_width() / sprite_width)
                source_x = max(0, min(enemy.image.get_width() - 1, source_x))

                column = sprite.subsurface((x, 0, 1, sprite_height))
                screen.blit(column, (screen_x_position, sprite_y))

    # ======================================================
    # CROSSHAIR
    # ======================================================

    def draw_crosshair(self, screen):

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (center_x - 6, center_y),
            (center_x + 6, center_y),
            2
        )

        pygame.draw.line(
            screen,
            (220, 220, 220),
            (center_x, center_y - 6),
            (center_x, center_y + 6),
            2
        )

    # ======================================================
    # MESSAGE
    # ======================================================

    def draw_message(self, screen):
        if self.message_timer <= 0:
            return

        # decrement based on frame (approx 60fps)
        self.message_timer -= (1 / 60)

        text = self.font.render(self.message, True, (240, 240, 240))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 80))

        background_rect = rect.inflate(35, 18)
        background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))

        screen.blit(background, background_rect)
        screen.blit(text, rect)

    # ======================================================
    # MAIN DRAW
    # ======================================================

    def draw(
        self,
        screen,
        player,
        enemy=None
    ):

        if self.raycaster is None:
            return

        # Floor + ceiling move with player
        self.draw_floor_and_ceiling(screen, player)

        # Walls
        self.draw_walls(screen, player)

        # Enemy / ghost
        if enemy is not None:
            self.draw_enemy(screen, player, enemy)

        # Crosshair
        self.draw_crosshair(screen)

        # Messages
        self.draw_message(screen)

        # --------------------------------------------------
        # VIGNETTE
        # --------------------------------------------------

        darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for i in range(60):
            alpha = int(1.3 * (60 - i))
            pygame.draw.rect(
                darkness,
                (0, 0, 0, alpha),
                (i, i, WIDTH - 2 * i, HEIGHT - 2 * i),
                2
            )

        screen.blit(darkness, (0, 0))
