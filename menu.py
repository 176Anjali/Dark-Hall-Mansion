import pygame
import os

from settings import (
    WIDTH,
    HEIGHT,
    MENU_BG,
    MENU_TEXT,
    MENU_SELECTED,
    MENU_DIM,
    MENU,
    HOW_TO_PLAY,
    OPTIONS,
)

def get_horror_font(size):
    """
    Try to load a horror-style font.
    Falls back safely if the font is not available.
    """

    horror_fonts = [
        "chiller",
        "oldenglishtextmt",
        "papyrus",
        "impact"
    ]

    for font_name in horror_fonts:

        font_path = pygame.font.match_font(
            font_name
        )

        if font_path:

            return pygame.font.Font(
                font_path,
                size
            )

    # Safe fallback
    return pygame.font.Font(
        None,
        size
    )
class MainMenu:

    def __init__(self, game):

        self.game = game

        # ==========================================
        # HORROR FONTS
        # ==========================================

        self.font_title = get_horror_font(90)
        self.font_button = get_horror_font(42)
        self.font_small = get_horror_font(28)
        self.font_text = get_horror_font(32)

        # Main menu
        self.options = [
            "PLAY",
            "HOW TO PLAY",
            "OPTIONS",
            "QUIT",
        ]

        self.selected = 0
        self.button_rects =[]
        self.back_rect = pygame.Rect(0,0,0,0)

        # Sub-menu selection
        self.sub_selected = 0

    # ==========================================
    # EVENT HANDLING
    # ==========================================

    def handle_event(self, event):

        # MAIN MENU
        if self.game.game_state == MENU:

            self.handle_main_menu(event)

        # HOW TO PLAY
        elif self.game.game_state == HOW_TO_PLAY:

            self.handle_how_to_play(event)

        # OPTIONS
        elif self.game.game_state == OPTIONS:

            self.handle_options(event)

    # ==========================================
    # MAIN MENU
    # ==========================================

    def handle_main_menu(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:

                self.selected -= 1

                if self.selected < 0:
                    self.selected = len(self.options) - 1

            elif event.key == pygame.K_DOWN:

                self.selected += 1

                if self.selected >= len(self.options):
                    self.selected = 0

            elif event.key == pygame.K_RETURN:

                self.select_option()

            elif event.key == pygame.K_ESCAPE:

                self.game.running = False

        elif event.type == pygame.MOUSEMOTION:

            mouse_pos = event.pos

            for index, rect in enumerate(self.button_rects):

                if rect.collidepoint(mouse_pos):
                    self.selected = index

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                self.select_option()

    def select_option(self):

        option = self.options[self.selected]

        if option == "PLAY":

            self.game.start_game()

        elif option == "HOW TO PLAY":

            self.game.game_state = HOW_TO_PLAY

        elif option == "OPTIONS":

            self.game.game_state = OPTIONS

        elif option == "QUIT":

            self.game.running = False

    # ==========================================
    # HOW TO PLAY
    # ==========================================

    def handle_how_to_play(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_BACKSPACE,
            ):

                self.game.game_state = MENU

            elif event.key == pygame.K_RETURN:

                self.game.game_state = MENU

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.back_rect.collidepoint(event.pos):

                    self.game.game_state = MENU

    # ==========================================
    # OPTIONS
    # ==========================================

    def handle_options(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                self.game.game_state = MENU

            elif event.key == pygame.K_UP:

                self.sub_selected -= 1

                if self.sub_selected < 0:
                    self.sub_selected = 2

            elif event.key == pygame.K_DOWN:

                self.sub_selected += 1

                if self.sub_selected > 2:
                    self.sub_selected = 0

            elif event.key == pygame.K_LEFT:

                self.change_option(-1)

            elif event.key == pygame.K_RIGHT:

                self.change_option(1)

            elif event.key == pygame.K_RETURN:

                if self.sub_selected == 2:
                    self.game.game_state = MENU

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.back_rect.collidepoint(event.pos):

                    self.game.game_state = MENU

    def change_option(self, direction):

        if self.sub_selected == 0:

            # Mouse sensitivity
            self.game.mouse_sensitivity += direction * 0.0005

            self.game.mouse_sensitivity = max(
                0.001,
                min(0.005, self.game.mouse_sensitivity)
            )

        elif self.sub_selected == 1:

            # Master volume
            self.game.master_volume += direction * 0.05

            self.game.master_volume = max(
                0.0,
                min(1.0, self.game.master_volume)
            )

    # ==========================================
    # DRAW MAIN MENU
    # ==========================================

    def draw(self):

        if self.game.game_state == MENU:

            self.draw_main_menu()

        elif self.game.game_state == HOW_TO_PLAY:

            self.draw_how_to_play()

        elif self.game.game_state == OPTIONS:

            self.draw_options()

    # ==========================================
    # MAIN MENU SCREEN
    # ==========================================

    def draw_main_menu(self):

        screen = self.game.screen

        screen.fill(MENU_BG)

        self.draw_dark_overlay()

        # Title
        title = self.font_title.render(
            "DARK HALL",
            True,
            MENU_TEXT
        )

        title2 = self.font_title.render(
            "MANSION",
            True,
            MENU_TEXT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 130)
            )
        )

        screen.blit(
            title2,
            title2.get_rect(
                center=(WIDTH // 2, 205)
            )
        )

        subtitle = self.font_small.render(
            "EXPLORE • SURVIVE • ESCAPE",
            True,
            MENU_TEXT
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, 260)
            )
        )

        # Buttons
        self.button_rects = []

        start_y = 350
        spacing = 65

        for index, option in enumerate(self.options):

            color = (
                MENU_SELECTED
                if index == self.selected
                else MENU_TEXT
            )

            text = self.font_button.render(
                option,
                True,
                color
            )

            rect = text.get_rect(
                center=(
                    WIDTH // 2,
                    start_y + index * spacing
                )
            )

            self.button_rects.append(rect)

            if index == self.selected:

                arrow = self.font_button.render(
                    ">",
                    True,
                    MENU_SELECTED
                )

                arrow_rect = arrow.get_rect(
                    midright=(
                        rect.left - 20,
                        rect.centery
                    )
                )

                screen.blit(
                    arrow,
                    arrow_rect
                )

            screen.blit(text, rect)

        hint = self.font_small.render(
            "UP / DOWN   SELECT     ENTER   CONFIRM",
            True,
            MENU_DIM
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(WIDTH // 2, HEIGHT - 45)
            )
        )

    # ==========================================
    # HOW TO PLAY SCREEN
    # ==========================================

    def draw_how_to_play(self):

        screen = self.game.screen

        screen.fill(MENU_BG)
        self.draw_dark_overlay()

        # ==========================================
        # TITLE
        # ==========================================

        title = self.font_title.render(
            "HOW TO PLAY",
            True,
            MENU_TEXT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 75)
            )
        )

        # ==========================================
        # CONTROLS
        # ==========================================

        controls = [
            ("W A S D", "Move around the mansion"),
            ("MOUSE", "Look around"),
            ("SHIFT", "Run faster"),
            ("E", "Interact / collect / open"),
            ("F", "Toggle flashlight"),
            ("ESC", "Pause the game"),
        ]

        start_y = 170
        spacing = 55

        for index, (key, description) in enumerate(controls):

            y = start_y + index * spacing

            key_text = self.font_button.render(
                key,
                True,
                MENU_SELECTED
            )

            description_text = self.font_text.render(
                description,
                True,
                MENU_TEXT
            )

            screen.blit(
                key_text,
                key_text.get_rect(
                    midright=(WIDTH // 2 - 25, y)
                )
            )

            screen.blit(
                description_text,
                description_text.get_rect(
                    midleft=(WIDTH // 2 + 25, y)
                )
            )

        # ==========================================
        # OBJECTIVE
        # ==========================================

        objective_title = self.font_button.render(
            "OBJECTIVE",
            True,
            MENU_SELECTED
        )

        screen.blit(
            objective_title,
            objective_title.get_rect(
                center=(WIDTH // 2, 535)
            )
        )

        objectives = [
            "Find the Library Key and awaken the ghost.",
            "Escape the ghost and reach the Library.",
            "Solve the Library puzzle to obtain the Basement Key.",
            "Use the Basement Key to enter the Basement.",
            "Reach the exit and escape the mansion.",
        ]

        y = 580

        for text in objectives:

            objective_text = self.font_small.render(
                text,
                True,
                MENU_TEXT
            )

            screen.blit(
                objective_text,
                objective_text.get_rect(
                    center=(WIDTH // 2, y)
                )
            )

            y += 30

        # ==========================================
        # BACK
        # ==========================================

        back = self.font_small.render(
            "ESC / ENTER    BACK",
            True,
            MENU_DIM
        )

        screen.blit(
            back,
            back.get_rect(
                center=(WIDTH // 2, HEIGHT - 25)
            )
        )
    

    # ==========================================
    # OPTIONS SCREEN
    # ==========================================

    def draw_options(self):

        screen = self.game.screen

        screen.fill(MENU_BG)

        self.draw_dark_overlay()

        title = self.font_title.render(
            "OPTIONS",
            True,
            MENU_TEXT
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 100)
            )
        )

        sensitivity = int(
            (
                self.game.mouse_sensitivity
                / 0.005
            ) * 100
        )

        volume = int(
            self.game.master_volume * 100
        )

        options = [
            f"MOUSE SENSITIVITY     {sensitivity}%",
            f"MASTER VOLUME         {volume}%",
            "BACK",
        ]

        start_y = 260

        for index, option in enumerate(options):

            color = (
                MENU_SELECTED
                if index == self.sub_selected
                else MENU_TEXT
            )

            text = self.font_button.render(
                option,
                True,
                color
            )

            rect = text.get_rect(
                center=(
                    WIDTH // 2,
                    start_y + index * 80
                )
            )

            screen.blit(text, rect)

            if index == self.sub_selected:

                arrow = self.font_button.render(
                    ">",
                    True,
                    MENU_SELECTED
                )

                screen.blit(
                    arrow,
                    arrow.get_rect(
                        midright=(
                            rect.left - 20,
                            rect.centery
                        )
                    )
                )

        hint = self.font_small.render(
            "UP / DOWN   SELECT     LEFT / RIGHT   CHANGE",
            True,
            MENU_DIM
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(WIDTH // 2, HEIGHT - 45)
            )
        )

        self.back_rect = pygame.Rect(
            WIDTH // 2 - 100,
            start_y + 2 * 80 - 25,
            200,
            50
        )

    # ==========================================
    # COMMON FUNCTIONS
    # ==========================================

    def draw_back_button(self):

        text = self.font_button.render(
            "BACK",
            True,
            MENU_SELECTED
        )

        self.back_rect = text.get_rect(
            center=(WIDTH // 2, HEIGHT - 80)
        )

        self.game.screen.blit(
            text,
            self.back_rect
        )

    def draw_dark_overlay(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(100)

        overlay.fill((0, 0, 0))

        self.game.screen.blit(
            overlay,
            (0, 0)
        )
