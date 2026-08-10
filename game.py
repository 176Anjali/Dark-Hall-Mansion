import pygame

from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    TITLE,
    MENU,
    PLAYING,
    HOW_TO_PLAY,
    OPTIONS,
    MOUSE_SENSITIVITY,
    MASTER_VOLUME,
)

from menu import MainMenu
from map import MansionMap
from player import Player
from raycasting import Raycaster
from renderer import Renderer


class Game:

    def __init__(self):

        pygame.init()

        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.running = True

        # ==========================================
        # GAME STATE
        # ==========================================

        self.game_state = MENU

        # ==========================================
        # SETTINGS
        # ==========================================

        self.mouse_sensitivity = MOUSE_SENSITIVITY
        self.master_volume = MASTER_VOLUME

        # ==========================================
        # MENU
        # ==========================================

        self.menu = MainMenu(self)

        # ==========================================
        # MANSION
        # ==========================================

        self.mansion_map = MansionMap()

        self.player = Player(
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

    # ==========================================
    # START GAME
    # ==========================================

    def start_game(self):

        self.game_state = PLAYING

        # Reset player position
        self.player.x = 2.5
        self.player.y = 1.5
        self.player.angle = 0.0

        # Capture mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        pygame.mouse.get_rel()

    # ==========================================
    # RETURN TO MENU
    # ==========================================

    def return_to_menu(self):

        self.game_state = MENU

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ==========================================
    # EVENTS
    # ==========================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            # --------------------------------------
            # MENU / MENU SCREENS
            # --------------------------------------

            elif self.game_state in (
                MENU,
                HOW_TO_PLAY,
                OPTIONS,
            ):

                self.menu.handle_event(event)

            # --------------------------------------
            # GAMEPLAY
            # --------------------------------------

            elif self.game_state == PLAYING:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.return_to_menu()

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self):

        if self.game_state == PLAYING:

            dt = self.clock.get_time() / 1000.0

            # Prevent huge movement after lag
            dt = min(dt, 0.05)

            # Mouse camera
            mouse_dx, _ = pygame.mouse.get_rel()

            self.player.rotate(
                mouse_dx,
                self.mouse_sensitivity
            )

            # Player movement
            self.player.update(dt)

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self):

        if self.game_state in (
            MENU,
            HOW_TO_PLAY,
            OPTIONS,
        ):

            self.menu.draw()

        elif self.game_state == PLAYING:

            self.renderer.draw(
                self.screen,
                self.player
            )

        pygame.display.flip()

    # ==========================================
    # MAIN LOOP
    # ==========================================

    def run(self):

        while self.running:

            self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        pygame.quit()