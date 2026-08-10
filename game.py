import math
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

from mansion_map import MansionMap
from raycasting import Raycaster
from renderer import Renderer
from player import Player
from enemy import Enemy
from interaction import InteractionSystem


class Game:

    def __init__(self):

        pygame.init()

        try:
            pygame.mixer.init()
        except Exception as error:
            print("Audio initialization error:", error)

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            TITLE
        )

        self.clock = pygame.time.Clock()

        # ==========================================
        # WORLD
        # ==========================================

        self.mansion_map = MansionMap()

        self.player = Player(
            self.mansion_map
        )

        self.enemy = Enemy(
            self.mansion_map
        )

        self.raycaster = Raycaster(
            self.mansion_map
        )

        self.renderer = Renderer(
            self.mansion_map
        )

        self.renderer.set_raycaster(
            self.raycaster
        )

        self.interaction = InteractionSystem(
            self.mansion_map,
            self.renderer
        )

        # ==========================================
        # STATE
        # ==========================================

        self.state = MENU

        self.running = True

        self.mouse_locked = False

        self.big_font = pygame.font.SysFont(
            "Arial",
            52,
            bold=True
        )

        self.font = pygame.font.SysFont(
            "Arial",
            25,
            bold=True
        )

        self.menu_font = pygame.font.SysFont(
            "Arial",
            32,
            bold=True
        )

        self.message_timer = 0

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        pygame.mouse.set_visible(True)

        while self.running:

            dt = self.clock.tick(FPS) / 1000.0

            dt = min(
                dt,
                0.05
            )

            self.handle_events()

            if self.state == PLAYING:

                self.update(
                    dt
                )

            self.draw()

        self.interaction.stop()

        pygame.quit()

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            # --------------------------------------
            # MENU
            # --------------------------------------

            if self.state == MENU:

                if (
                    event.type
                    == pygame.KEYDOWN
                ):

                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE
                    ):

                        self.start_game()

                    elif event.key == pygame.K_ESCAPE:

                        self.running = False

                continue

            # --------------------------------------
            # PLAYING
            # --------------------------------------

            if self.state == PLAYING:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.state = PAUSED

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                    elif event.key == pygame.K_e:

                        self.interaction.interact(
                            self.player,
                            self.enemy
                        )

                    elif event.key == pygame.K_f:

                        self.interaction.toggle_flashlight()

                elif event.type == pygame.MOUSEMOTION:

                    if self.mouse_locked:

                        self.player.rotate(
                            event.rel[0],
                            MOUSE_SENSITIVITY
                        )

                continue

            # --------------------------------------
            # PAUSED
            # --------------------------------------

            if self.state == PAUSED:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.resume_game()

                    elif event.key == pygame.K_q:

                        self.running = False

                continue

            # --------------------------------------
            # GAME OVER
            # --------------------------------------

            if self.state == GAME_OVER:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:

                        self.restart()

                    elif event.key == pygame.K_ESCAPE:

                        self.running = False

                continue

            # --------------------------------------
            # WIN
            # --------------------------------------

            if self.state == WIN:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:

                        self.restart()

                    elif event.key == pygame.K_ESCAPE:

                        self.running = False

    # ==========================================
    # START
    # ==========================================

    def start_game(self):

        self.state = PLAYING

        self.mouse_locked = True

        pygame.mouse.set_visible(
            False
        )

        pygame.event.set_grab(
            True
        )

        self.renderer.show_message(
            "Find the key. Then find the correct door."
        )

    # ==========================================
    # RESUME
    # ==========================================

    def resume_game(self):

        self.state = PLAYING

        self.mouse_locked = True

        pygame.mouse.set_visible(
            False
        )

        pygame.event.set_grab(
            True
        )

    # ==========================================
    # RESTART
    # ==========================================

    def restart(self):

        self.mansion_map = MansionMap()

        self.player = Player(
            self.mansion_map
        )

        self.enemy = Enemy(
            self.mansion_map
        )

        self.raycaster = Raycaster(
            self.mansion_map
        )

        self.renderer = Renderer(
            self.mansion_map
        )

        self.renderer.set_raycaster(
            self.raycaster
        )

        self.interaction = InteractionSystem(
            self.mansion_map,
            self.renderer
        )

        self.start_game()

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self, dt):

        old_x = self.player.x
        old_y = self.player.y

        self.player.update(
            dt
        )

        # ======================================
        # FOOTSTEPS
        # ======================================

        distance_moved = math.hypot(
            self.player.x - old_x,
            self.player.y - old_y
        )

        if distance_moved > 0.001:

            # Occasional footstep
            if pygame.time.get_ticks() % 450 < 20:

                self.interaction.play(
                    "footstep"
                )

        # ======================================
        # ENEMY
        # ======================================

        caught = self.enemy.update(
            self.player,
            dt
        )

        if caught:

            self.state = GAME_OVER

            pygame.mouse.set_visible(
                True
            )

            pygame.event.set_grab(
                False
            )

            self.interaction.game_over()

            return

        # ======================================
        # ESCAPE
        # ======================================

        exit_x, exit_y = (
            self.mansion_map.exit_door
        )

        distance_to_exit = math.hypot(
            self.player.x - (exit_x + 0.5),
            self.player.y - (exit_y + 0.5)
        )

        if (
            self.mansion_map.is_open(
                exit_x,
                exit_y
            )
            and distance_to_exit < 1.1
        ):

            self.state = WIN

            pygame.mouse.set_visible(
                True
            )

            pygame.event.set_grab(
                False
            )

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self):

        if self.state == MENU:

            self.draw_menu()

        elif self.state == PLAYING:

            self.renderer.draw(
                self.screen,
                self.player,
                self.enemy,
                self.mansion_map.key_collected,
                self.interaction.flashlight_on,
                1 / FPS
            )

        elif self.state == PAUSED:

            self.renderer.draw(
                self.screen,
                self.player,
                self.enemy,
                self.mansion_map.key_collected,
                self.interaction.flashlight_on,
                1 / FPS
            )

            self.draw_pause()

        elif self.state == GAME_OVER:

            self.draw_game_over()

        elif self.state == WIN:

            self.draw_win()

        pygame.display.flip()

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
            (180, 25, 25)
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 3
            )
        )

        self.screen.blit(
            title,
            title_rect
        )

        subtitle = self.font.render(
            "A dark mansion. A hidden key. Something is waiting.",
            True,
            (190, 190, 190)
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 3 + 70
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
                HEIGHT // 2 + 80
            )
        )

        self.screen.blit(
            start,
            start_rect
        )

        controls = self.font.render(
            "WASD = Move    Mouse = Look    E = Interact    F = Flashlight",
            True,
            (120, 120, 120)
        )

        controls_rect = controls.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 80
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
            "ENTER = Try Again     ESC = Quit",
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
            "ENTER = Play Again     ESC = Quit",
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