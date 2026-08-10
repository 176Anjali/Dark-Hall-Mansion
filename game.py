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
from enemy import Enemy
from key import Key
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

        # ==========================================
        # PLAYER
        # ==========================================

        self.player = Player(
            self.mansion_map
        )

        # ==========================================
        # ENEMY / GHOST
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

        # Ghost starts inactive.
        # Press G to activate it for testing.
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
            ),

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
    # START GAME
    # ==========================================

    def start_game(self):

        self.game_state = PLAYING

        # Reset player position
        self.player.x = 2.5
        self.player.y = 1.5
        self.player.angle = 0.0

        # Reset ghost
        self.ghost.x = 5.5
        self.ghost.y = 1.5
        self.ghost.active = False
        self.ghost.health = self.ghost.max_health

        # Capture mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # Clear previous mouse movement
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

            # ======================================
            # WINDOW CLOSE BUTTON
            # ======================================

            if event.type == pygame.QUIT:

                self.running = False

                continue

            # ======================================
            # KEYBOARD EVENTS
            # ======================================

            if event.type == pygame.KEYDOWN:

                # ----------------------------------
                # Q = QUIT GAME
                # ----------------------------------

                if event.key == pygame.K_q:

                    self.running = False

                    continue

                # ----------------------------------
                # ESC = BACK / MENU / QUIT
                # ----------------------------------

                if event.key == pygame.K_ESCAPE:

                    if self.game_state == PLAYING:

                        self.return_to_menu()

                    elif self.game_state in (
                        HOW_TO_PLAY,
                        OPTIONS,
                    ):

                        self.game_state = MENU

                    elif self.game_state == MENU:

                        self.running = False

                    continue

                # ----------------------------------
                # G = ACTIVATE GHOST
                # ----------------------------------

                if (
                    event.key == pygame.K_g
                    and self.game_state == PLAYING
                ):

                    self.ghost.active = True

                    # Display message if renderer
                    # supports show_message()
                    if hasattr(
                        self.renderer,
                        "show_message"
                    ):

                        self.renderer.show_message(
                            "Something is following you..."
                        )

                    continue

            # ======================================
            # MENU EVENTS
            # ======================================

            if self.game_state in (
                MENU,
                HOW_TO_PLAY,
                OPTIONS,
            ):

                self.menu.handle_event(event)

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self):

        if self.game_state != PLAYING:

            return

        # Time since previous frame
        dt = (
            self.clock.get_time()
            / 1000.0
        )

        # Prevent huge movement after lag
        dt = min(
            dt,
            0.05
        )

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

        self.ghost.update(
            self.player,
            self.mansion_map,
            dt
        )

        # ==========================================
        # GHOST ATTACK
        # ==========================================

        self.ghost.attack(
            self.player
        )

        # ==========================================
        # GAME OVER
        # ==========================================

        if hasattr(
            self.player,
            "health"
        ):

            if self.player.health <= 0:

                self.ghost.active = False

                self.return_to_menu()
    
    # ==========================================
    # DRAW
    # ==========================================

    def draw(self):

        # ==========================================
        # MENU
        # ==========================================

        if self.game_state in (
            MENU,
            HOW_TO_PLAY,
            OPTIONS,
        ):

            self.menu.draw()

        # ==========================================
        # GAMEPLAY
        # ==========================================

        elif self.game_state == PLAYING:

            # Pass the ghost to the renderer
            self.renderer.draw(
                self.screen,
                self.player,
                self.ghost
            )

        # ==========================================
        # DISPLAY
        # ==========================================

        pygame.display.flip()

    # ==========================================
    # MAIN LOOP
    # ==========================================

    def run(self):

        while self.running:

            # Handle keyboard / mouse / window events
            self.handle_events()

            # Update game objects
            self.update()

            # Draw everything
            self.draw()

            # Maintain FPS
            self.clock.tick(FPS)

        # ==========================================
        # CLEANUP
        # ==========================================

        pygame.mouse.set_visible(True)

        pygame.event.set_grab(False)

        pygame.quit()