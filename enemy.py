
# ...existing code...
import math
import pygame


class Enemy:
    def __init__(
        self,
        x=0.0,
        y=0.0,
        image_path=None,
        speed=1.0,
        detection_range=8.0,
        health=100,
        damage=10,
    ):
        self.x = float(x)
        self.y = float(y)
        self.image_path = image_path
        self.speed = float(speed)
        self.detection_range = float(detection_range)
        self.health = health
        self.max_health = health
        self.damage = damage

        self.active = True
        self.attack_cooldown = 1.0  # seconds between attacks
        self._time_since_attack = 0.0

        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
            except Exception:
                # fallback placeholder
                self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (200, 200, 255), (16, 16), 16)

    def update(self, player, mansion_map, dt):
        if not self.active:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        # move toward player if within detection range
        if dist <= self.detection_range:
            nx = dx / dist
            ny = dy / dist
            move = self.speed * dt
            self.x += nx * move
            self.y += ny * move

        self._time_since_attack += dt

    def attack(self, player):
        if not self.active:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # simple melee range
        if dist <= 0.6 and self._time_since_attack >= self.attack_cooldown:
            if hasattr(player, "health"):
                player.health -= self.damage
            self._time_since_attack = 0.0

# ...existing code...
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    TITLE,
    MOUSE_SENSITIVITY,
    MENU,
    PLAYING,
    PAUSED,
    GAME_OVER,
    WIN,
)

from map import MansionMap
from player import Player
from enemy import Enemy
from key import Key
from raycasting import Raycaster
from renderer import Renderer
from interaction import InteractionSystem


class Game:

    def __init__(self):

        pygame.init()

        try:
            pygame.mixer.init()
        except Exception as error:
            print("Audio initialization error:", error)

        # ==========================================
        # DISPLAY
        # ==========================================

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()

        # ==========================================
        # FONTS
        # ==========================================

        self.menu_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 72)

        # ==========================================
        # WORLD
        # ==========================================

        self.mansion_map = MansionMap()

        # ==========================================
        # PLAYER
        # ==========================================

        self.player = Player(
            self.mansion_map
        )

        # ==========================================
        # GHOST / ENEMY
        # ==========================================

        self.ghost = Enemy(
            x=5.5,
            y=1.5,
            image_path="assets/enemies/ghost.png",
            speed=1.2,
            detection_range=10.0,
            health=100,
            damage=10
        )

        self.ghost.active = False

        # ==========================================
        # KEYS
        # ==========================================

        self.keys = [
            Key(
                x=5.5,
                y=3.5,
                image_path="assets/items/key.png",
                name="basement_key"
            )
        ]

        # ==========================================
        # RAYCASTER
        # ==========================================

        self.raycaster = Raycaster(
            self.mansion_map
        )

        # ==========================================
        # RENDERER
        # ==========================================

        self.renderer = Renderer(
            self.mansion_map
        )

        self.renderer.set_raycaster(
            self.raycaster
        )

        # ==========================================
        # INTERACTION
        # ==========================================

        self.interaction = InteractionSystem(
            self.mansion_map,
            self.renderer
        )

        # ==========================================
        # GAME STATE
        # ==========================================

        self.state = MENU
        self.running = True

        self.mouse_sensitivity = MOUSE_SENSITIVITY

        # ==========================================
        # MOUSE
        # ==========================================

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ==========================================
    # START GAME
    # ==========================================

    def start_game(self):

        self.state = PLAYING

        # Reset player if supported
        if hasattr(self.player, "health"):
            if hasattr(self.player, "max_health"):
                self.player.health = self.player.max_health

        # Reset ghost
        self.ghost.x = 5.5
        self.ghost.y = 1.5
        self.ghost.active = False

        if hasattr(self.ghost, "max_health"):
            self.ghost.health = self.ghost.max_health

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        pygame.mouse.get_rel()

    # ==========================================
    # RETURN TO MENU
    # ==========================================

    def return_to_menu(self):

        self.state = MENU

        self.ghost.active = False

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        while self.running:

            dt = self.clock.tick(FPS) / 1000.0

            dt = min(dt, 0.05)

            self.handle_events()

            if self.state == PLAYING:
                self.update(dt)

            self.draw()

        self.interaction.stop()

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        pygame.quit()

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self):

        for event in pygame.event.get():

            # ======================================
            # WINDOW CLOSE
            # ======================================

            if event.type == pygame.QUIT:

                self.running = False

                continue

            # ======================================
            # KEYBOARD
            # ======================================

            if event.type == pygame.KEYDOWN:

                # ----------------------------------
                # Q = QUIT
                # ----------------------------------

                if event.key == pygame.K_q:

                    self.running = False

                    continue

                # ----------------------------------
                # ESC
                # ----------------------------------

                if event.key == pygame.K_ESCAPE:

                    if self.state == PLAYING:

                        self.state = PAUSED

                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)

                    elif self.state == PAUSED:

                        self.state = PLAYING

                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)

                        pygame.mouse.get_rel()

                    elif self.state == GAME_OVER:
                        self.return_to_menu()

                    elif self.state == WIN:
                        self.return_to_menu()

                    elif self.state == MENU:

                        self.running = False

                    continue

                # ----------------------------------
                # ENTER / SPACE
                # ----------------------------------

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):

                    if self.state == MENU:

                        self.start_game()

                    elif self.state == GAME_OVER:

                        self.start_game()

                    elif self.state == WIN:

                        self.start_game()

                    continue

                # ----------------------------------
                # G = ACTIVATE GHOST
                # ----------------------------------

                if (
                    event.key == pygame.K_g
                    and self.state == PLAYING
                ):

                    self.ghost.active = True

                    if hasattr(
                        self.renderer,
                        "show_message"
                    ):

                        self.renderer.show_message(
                            "Something is following you..."
                        )

                    continue

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self, dt):

        if self.state != PLAYING:
            return

        # ==========================================
        # PLAYER CAMERA
        # ==========================================

        mouse_dx, _ = pygame.mouse.get_rel()

        self.player.rotate(
            mouse_dx,
            self.mouse_sensitivity
        )

        # ==========================================
        # PLAYER MOVEMENT
        # ==========================================

        self.player.update(dt)

        # ==========================================
        # GHOST MOVEMENT
        # ==========================================

        if self.ghost.active:

            self.ghost.update(
                self.player,
                self.mansion_map,
                dt
            )

            # ======================================
            # GHOST ATTACK
            # ======================================

            self.ghost.attack(
                self.player
            )

        # ==========================================
        # PLAYER DEATH
        # ==========================================

        if hasattr(self.player, "health"):

            if self.player.health <= 0:

                self.ghost.active = False

                self.state = GAME_OVER

                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self):

        # ==========================================
        # MENU
        # ==========================================

        if self.state == MENU:

            self.draw_menu()

        # ==========================================
        # PLAYING
        # ==========================================

        elif self.state == PLAYING:
            self.draw_game()

        # ==========================================
        # PAUSED
        # ==========================================

        elif self.state == PAUSED:
            self.draw_game()
            self.draw_pause()

        # ==========================================
        # GAME OVER
        # ==========================================

        elif self.state == GAME_OVER:
            self.draw_game_over()

        # ==========================================
        # WIN
        # ==========================================

        elif self.state == WIN:

            self.draw_win()

        pygame.display.flip()

    # ==========================================
    # DRAW GAME
    # ==========================================

    def draw_game(self):

        # The updated renderer receives the ghost
        # so it can render the enemy.

        self.renderer.draw(
            self.screen,
            self.player,
            self.ghost
        )

    # ==========================================
    # MENU
    # ==========================================

    def draw_menu(self):

        self.screen.fill(
            (5, 5, 8)
        )

        title = self.big_font.render(
            "DARK HALL MANSION",
            True,
            (210, 210, 220)
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 100
            )
        )

        self.screen.blit(
            title,
            title_rect
        )

        subtitle = self.font.render(
            "An abandoned mansion hides a terrible secret...",
            True,
            (130, 130, 140)
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 35
            )
        )

        self.screen.blit(
            subtitle,
            subtitle_rect
        )

        start = self.menu_font.render(
            "PRESS ENTER TO ENTER THE MANSION",
            True,
            (220, 220, 220)
        )

        start_rect = start.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 70
            )
        )

        self.screen.blit(
            start,
            start_rect
        )

        controls = self.font.render(
            "WASD = Move    Mouse = Look    G = Ghost",
            True,
            (120, 120, 120)
        )

        controls_rect = controls.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 60
            )
        )

        self.screen.blit(
            controls,
            controls_rect
        )

    # ==========================================
    # PAUSE
    # ==========================================

    def draw_pause(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        text = self.big_font.render(
            "PAUSED",
            True,
            (230, 230, 230)
        )

        rect = text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            text,
            rect
        )

        small = self.font.render(
            "ESC = Resume     Q = Quit",
            True,
            (180, 180, 180)
        )

        rect = small.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 30
            )
        )

        self.screen.blit(
            small,
            rect
        )

    # ==========================================
    # GAME OVER
    # ==========================================

    def draw_game_over(self):

        self.screen.fill(
            (8, 0, 0)
        )

        text = self.big_font.render(
            "YOU WERE CAUGHT",
            True,
            (210, 30, 30)
        )

        rect = text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 50
            )
        )

        self.screen.blit(
            text,
            rect
        )

        small = self.font.render(
            "The mansion was not empty...",
            True,
            (200, 200, 200)
        )

        rect = small.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 20
            )
        )

        self.screen.blit(
            small,
            rect
        )

        restart = self.font.render(
            "ENTER = Try Again     ESC = Menu",
            True,
            (150, 150, 150)
        )

        rect = restart.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 90
            )
        )

        self.screen.blit(
            restart,
            rect
        )

    # ==========================================
    # WIN
    # ==========================================

    def draw_win(self):

        self.screen.fill(
            (5, 15, 8)
        )

        text = self.big_font.render(
            "YOU ESCAPED!",
            True,
            (100, 230, 120)
        )

        rect = text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 50
            )
        )

        self.screen.blit(
            text,
            rect
        )

        small = self.font.render(
            "You found the correct door and escaped the mansion.",
            True,
            (210, 210, 210)
        )

        rect = small.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 20
            )
        )

        self.screen.blit(
            small,
            rect
        )

        restart = self.font.render(
            "ENTER = Play Again     ESC = Menu",
            True,
            (150, 150, 150)
        )

        rect = restart.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 90
            )
        )

        self.screen.blit(
            restart,
            rect
        )