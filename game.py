import os
import math
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    TITLE,
    MOUSE_SENSITIVITY,
    MENU,
    DOOR,
    PLAYING,
    PAUSED,
    GAME_OVER,
    WIN,
    HOW_TO_PLAY,
    OPTIONS,
)

from menu import MainMenu
from map import MansionMap
from player import Player
from enemy import Enemy
from key import Key
from raycasting import Raycaster
from renderer import Renderer
from interaction import InteractionSystem


class Game:

    def __init__(self):

        # ==========================================
        # DOOR
        # ==========================================

        self.door_open = False
        self.door_sound_played = False
        self.background_music_started = False

        # ==========================================
        # FOOTSTEPS
        # ==========================================

        self.footstep_timer = 0.0
        self.footstep_interval = 0.38

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.sound_dir = os.path.join(
            self.base_dir,
            "assets",
            "sounds"
        )

        pygame.init()
        
        # ==========================================
        # AUDIO INITIALIZATION
        # ==========================================

        self.audio_enabled = False

        try:

            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )

            self.audio_enabled = True

            print("AUDIO: mixer initialized")
            print(
                "AUDIO INFO:",
                pygame.mixer.get_init()
            )

        except pygame.error as error:

            print(
                "AUDIO INITIALIZATION ERROR:",
                error
            )

            print(
                "The game will continue without audio."
            )        
        # ==========================================
        # AUDIO
        # ==========================================

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.sound_dir = os.path.join(
            self.base_dir,
            "assets",
            "sounds"
        )

        print(
            "SOUND DIRECTORY:",
            self.sound_dir
        )

        # ------------------------------------------
        # Default values
        # ------------------------------------------

        self.door_sound = None
        self.footstep_sound = None
        self.footstep_channel = None

        self.door_sound_path = os.path.join(
            self.sound_dir,
            "door.wav"
        )

        self.footstep_sound_path = os.path.join(
            self.sound_dir,
            "footstep.wav"
        )

        self.background_music_path = os.path.join(
            self.sound_dir,
            "background.wav"
        )

        # ------------------------------------------
        # Load audio only if mixer works
        # ------------------------------------------

        if self.audio_enabled:

            try:

                if os.path.exists(
                    self.door_sound_path
                ):

                    self.door_sound = pygame.mixer.Sound(
                        self.door_sound_path
                    )

                    self.door_sound.set_volume(
                        0.8
                    )

                    print(
                        "AUDIO: door.wav loaded"
                    )

                else:

                    print(
                        "AUDIO ERROR: door.wav not found"
                    )

            except pygame.error as error:

                print(
                    "AUDIO ERROR loading door.wav:",
                    error
                )

            try:

                if os.path.exists(
                    self.footstep_sound_path
                ):

                    self.footstep_sound = pygame.mixer.Sound(
                        self.footstep_sound_path
                    )

                    self.footstep_sound.set_volume(
                        0.45
                    )

                    print(
                        "AUDIO: footstep.wav loaded"
                    )

                else:

                    print(
                        "AUDIO ERROR: footstep.wav not found"
                    )

            except pygame.error as error:

                print(
                    "AUDIO ERROR loading footstep.wav:",
                    error
                )

            # Footstep channel
            self.footstep_channel = pygame.mixer.Channel(
                2
            )

            # Background music
            if os.path.exists(
                self.background_music_path
            ):

                print(
                    "AUDIO: background.wav found"
                )

            else:

                print(
                    "AUDIO ERROR: background.wav not found"
                )

        else:

            print(
                "AUDIO DISABLED: mixer could not initialize"
            )
        
        # ==========================================
        # DISPLAY
        # ==========================================

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            TITLE
        )

        self.clock = pygame.time.Clock()

        # ==========================================
        # FONTS
        # ==========================================
        #
        # These are currently used by:
        # Pause / Game Over / Win screens.
        #
        # Main menu fonts are handled by menu.py.
        #

        self.menu_font = pygame.font.Font(
            None,
            48
        )

        self.font = pygame.font.Font(
            None,
            32
        )

        self.font_small = pygame.font.Font(
            None,
            22
        )

        self.big_font = pygame.font.Font(
            None,
            72
        )

        # ==========================================
        # WORLD / MANSION
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
        # INTERACTION SYSTEM
        # ==========================================

        self.interaction = InteractionSystem(
            self.mansion_map,
            self.renderer
        )

        # ==========================================
        # PLAYER
        # ==========================================

        self.player = Player(
            self.mansion_map
        )

        # ==========================================
        # HUD
        # ==========================================

        self.player_health = 100
        self.max_player_health = 100

        self.flashlight_battery = 100
        self.max_flashlight_battery = 100

        # Message shown at the bottom of the screen
        self.hud_message = ""
        self.hud_message_timer = 0.0

        # ==========================================
        # MINIMAP
        # ==========================================
        
        self.minimap_size = 220
        self.minimap_margin = 20
        self.minimap_scale = 10

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

        # Ghost starts asleep.
        # Later, collecting the Library Key
        # will activate it automatically.

        self.ghost.active = False

        # ==========================================
        # KEYS
        # ==========================================

        self.keys = [

            # ==========================================
            # LIBRARY KEY
            # ==========================================

            Key(
                x=3.5,
                y=3.5,
                image_path="assets/items/key.png",
                name="library_key"
            ),

            # ==========================================
            # BASEMENT KEY
            # ==========================================

            Key(
                x=13.5,
                y=4.5,
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
        self.renderer.game = self
        self.renderer.keys = self.keys

        # ==========================================
        # LIBRARY KEY IMAGE
        # ==========================================

        key_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "items",
            "key.png"
        )

        try:

            self.library_key_image = pygame.image.load(
                key_path
            ).convert_alpha()

            print("LIBRARY KEY IMAGE: loaded")

        except Exception as error:

            self.library_key_image = None

            print(
                "LIBRARY KEY IMAGE ERROR:",
                error
            )

        self.renderer.set_raycaster(
            self.raycaster
        )

        # ==========================================
        # INTERACTION SYSTEM
        # ==========================================

        self.interaction = InteractionSystem(
            self.mansion_map,
            self.renderer
        )

        # ==========================================
        # VAULT PUZZLE
        # ==========================================

        self.vault_puzzle_active = False
        self.vault_unlocked = False
        self.vault_code = "1947"
        self.vault_input = ""

        # ==========================================
        # BASEMENT / GENERATOR
        # ==========================================

        self.generator_puzzle_active = False
        self.generator_activated = False
        self.generator_input = ""

        # ==========================================
        # PLAYER LIVES / GHOST ATTACK
        # ==========================================

        self.player_lives = 3
        self.ghost_caught = False
        self.ghost_caught_time = 0.0
        self.escape_time_limit = 5.0
        self.ghost_attack_cooldown = 0.0

        # ==========================================
        # LIBRARY PUZZLE
        # ==========================================

        self.library_puzzle_active = False
        self.library_puzzle_solved = False
        self.library_books = []
        self.library_code = [3, 1, 4, 2]

        # ==========================================
        # GAME STATE
        # ==========================================

        self.state = MENU

        self.running = True

        self.mouse_sensitivity = (
            MOUSE_SENSITIVITY
        )

        # ==========================================
        # AUDIO SETTINGS
        # ==========================================

        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0

        # ==========================================
        # MAIN MENU
        # ==========================================

        self.menu = MainMenu(
            self
        )

        # ==========================================
        # MOUSE
        # ==========================================

        pygame.mouse.set_visible(
            True
        )

        pygame.event.set_grab(
            False
        )

    # ==========================================
    # MENU STATE PROPERTY
    # ==========================================
    #
    # menu.py uses:
    #
    #     self.game.game_state
    #
    # while this Game class uses:
    #
    #     self.state
    #
    # This property connects both.
    #

    @property
    def game_state(self):

        return self.state

    @game_state.setter
    def game_state(self, value):

        self.state = value

    # ==========================================
    # START GAME
    # ==========================================

    def start_game(self):

        self.state = DOOR
        self.footstep_timer = 0.0

        # ==========================================
        # RESET PLAYER LIVES
        # ==========================================

        self.player_lives = 3
        self.ghost_caught = False
        self.ghost_caught_time = 0.0
        self.ghost_attack_cooldown = 0.0
        self.ghost_phase = "dormant"

        # ==========================================
        # RESET PLAYER
        # ==========================================

        if hasattr(
            self.player,
            "health"
        ):

            if hasattr(
                self.player,
                "max_health"
            ):

                self.player.health = (
                    self.player.max_health
                )

            else:

                self.player.health = 100

        # Reset player inventory
        if hasattr(
            self.player,
            "inventory"
        ):

            self.player.inventory.clear()

        # ==========================================
        # RESET GHOST
        # ==========================================

        self.ghost.x = 5.5
        self.ghost.y = 1.5

        self.ghost.active = False

        if hasattr(
            self.ghost,
            "max_health"
        ):

            self.ghost.health = (
                self.ghost.max_health
            )

        # ==========================================
        # RESET KEYS
        # ==========================================

        for key in self.keys:

            key.collected = False

        # ==========================================
        # RESET VAULT
        # ==========================================

        self.vault_puzzle_active = False
        self.vault_unlocked = False
        self.vault_input = ""    

        # ==========================================
        # RESET LIBRARY PUZZLE
        # ==========================================

        self.library_puzzle_active = False
        self.library_puzzle_solved = False
        self.library_books = []

        self.generator_puzzle_active = False
        self.generator_activated = False
        self.generator_input = ""

        # ==========================================
        # CAPTURE MOUSE
        # ==========================================

        pygame.mouse.set_visible(
            False
        )

        pygame.event.set_grab(
            True
        )

        pygame.mouse.get_rel()

    # ==========================================
    # RETURN TO MENU
    # ==========================================

    def return_to_menu(self):

        self.state = MENU

        # Ghost goes back to sleep
        self.ghost.active = False

        #Stop background music
        pygame.mixer.music.stop()

        # Stop footsteps
        if hasattr(
            self,
            "footstep_channel"
        ):

            self.footstep_channel.stop()

        # Release mouse
        pygame.mouse.set_visible(
            True
        )

        pygame.event.set_grab(
            False
        )

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        while self.running:

            # Calculate delta time
            dt = (
                self.clock.tick(FPS)
                / 1000.0
            )

            # Prevent huge movement after lag
            dt = min(
                dt,
                0.05
            )

            # Events
            self.handle_events()

            # Gameplay update
            if self.state == PLAYING:

                self.update(
                    dt
                )

            # Draw
            self.draw()

        # ==========================================
        # CLEANUP
        # ==========================================

        self.interaction.stop()

        pygame.mouse.set_visible(
            True
        )

        pygame.event.set_grab(
            False
        )

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
            # Q = COMPLETELY QUIT
            # ======================================

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:

                    self.running = False

                    continue

            # ======================================
            # MENU EVENTS
            # ======================================
            #
            # MainMenu handles:
            #
            # PLAY
            # HOW TO PLAY
            # OPTIONS
            # QUIT
            # mouse
            # arrow keys
            # ENTER
            # ESC/back
            #

            if self.state in (
                MENU,
                HOW_TO_PLAY,
                OPTIONS,
            ):

                self.menu.handle_event(
                    event
                )

                continue

            # ======================================
            # DOOR SCREEN
            # ======================================

            if self.state == DOOR:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_e:

                        self.open_mansion_door()

                continue

            # ======================================
            # GAMEPLAY EVENTS
            # ======================================

            if event.type == pygame.KEYDOWN:

                # ==========================================
                # VAULT PUZZLE INPUT
                # ==========================================

                if self.vault_puzzle_active:

                    # Number keys
                    if event.unicode.isdigit():

                        if len(self.vault_input) < 4:
                            self.vault_input += event.unicode

                    # Backspace
                    elif event.key == pygame.K_BACKSPACE:

                        self.vault_input = self.vault_input[:-1]

                    # ENTER = CHECK CODE
                    elif event.key == pygame.K_RETURN:

                        if self.vault_input == self.vault_code:

                            self.vault_unlocked = True
                            self.vault_puzzle_active = False

                            self.show_hud_message(
                                "CORRECT! THE VAULT IS UNLOCKED!"
                            )

                            # Open the vault door
                            for door in self.mansion_map.doors:

                                if door.get("type") == "vault":

                                    door["locked"] = False
                                    door["open"] = True

                                    break

                        else:

                            self.vault_input = ""

                            self.show_hud_message(
                                "WRONG CODE!"
                            )

                    continue

                # ==========================================
                # LIBRARY PUZZLE INPUT
                # ==========================================

                if self.library_puzzle_active:

                    if event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                        pygame.K_4
                    ):

                        number = int(event.unicode)

                        if len(self.library_books) < 4:
                            self.library_books.append(number)

                        continue

                    elif event.key == pygame.K_BACKSPACE:

                        if self.library_books:
                            self.library_books.pop()

                        continue

                    elif event.key == pygame.K_RETURN:

                        if self.library_books == self.library_code:

                            # ==========================================
                            # LIBRARY PUZZLE SOLVED
                            # ==========================================

                            self.library_puzzle_solved = True
                            self.library_puzzle_active = False

                            # Find the basement key
                            for key in self.keys:

                                if key.name == "basement_key":

                                    # Make sure it can now be collected
                                    key.collected = False

                                    # Put the key inside the library
                                    key.x = 13.5
                                    key.y = 4.5

                                    break

                            self.show_hud_message(
                                "LIBRARY PUZZLE SOLVED! THE BASEMENT KEY HAS APPEARED!"
                            )

                            print(
                                "PUZZLE: Library solved. Basement key spawned."
                            )

                        else:

                            self.library_books = []

                            self.show_hud_message(
                                "WRONG BOOK ORDER!"
                            )

                        continue

                # ==========================================
                # E = INTERACT
                # ==========================================

                if event.key == pygame.K_e:

                    # ======================================
                    # FINAL EXIT
                    # ======================================

                    exit_x = self.mansion_map.exit_door["x"]
                    exit_y = self.mansion_map.exit_door["y"]

                    exit_distance = math.hypot(
                        self.player.x - exit_x,
                        self.player.y - exit_y
                    )

                    if exit_distance < 1.7:

                        if self.mansion_map.exit_door["locked"]:

                            self.show_hud_message(
                                "THE EXIT IS LOCKED. FIND THE BASEMENT KEY."
                            )

                        else:

                            self.mansion_map.exit_door["open"] = True

                            self.ghost.active = False

                            if self.interaction.sounds.get("chase"):
                                self.interaction.sounds["chase"].stop()

                            self.interaction.stop()

                            self.state = WIN

                            pygame.mouse.set_visible(True)
                            pygame.event.set_grab(False)

                        continue
    
                    # Check nearby door first
                    door = self.mansion_map.get_nearby_door(
                        self.player.x,
                        self.player.y,
                        2.0
                    )

                    # ==========================================
                    # BASEMENT DOOR
                    # ==========================================

                    basement_key_collected = any(
                        key.name == "basement_key" and key.collected
                        for key in self.keys
                    )

                    if door is not None and basement_key_collected:

                        door_type = str(
                            door.get("type", "")
                        ).lower()

                        # Detect basement door either by type
                        # or by its location
                        is_basement_door = (
                            door_type == "basement"
                            or
                            (
                                "x" in door
                                and "y" in door
                                and math.hypot(
                                    door["x"] - 15.5,
                                    door["y"] - 11.5
                                ) < 2.0
                            )
                        )

                        if is_basement_door:

                            # ==========================================
                            # BASEMENT IS THE FINAL EXIT
                            # ==========================================

                            door["locked"] = False
                            door["open"] = True

                            self.interaction.play("door")

                            self.show_hud_message(
                                "THE BASEMENT GATE OPENS... YOU ESCAPED!"
                            )

                            # Stop ghost
                            self.ghost_phase = "basement_safe"
                            self.ghost.active = False

                            if self.interaction.sounds.get("chase"):
                                self.interaction.sounds["chase"].stop()

                            # ==========================================
                            # WIN
                            # ==========================================

                            self.interaction.stop()

                            self.state = WIN

                            pygame.mouse.set_visible(True)
                            pygame.event.set_grab(False)

                            continue

                    # ======================================
                    # VAULT DOOR
                    # ======================================

                    if door is not None and door.get("type") == "vault":

                        if not self.vault_unlocked:

                            self.vault_puzzle_active = True
                            self.vault_input = ""

                            self.show_hud_message(
                                "VAULT LOCKED - ENTER 4-DIGIT CODE"
                            )

                        else:

                            door["open"] = True

                            self.show_hud_message(
                                "VAULT OPENED!"
                            )

                        continue

                    # ======================================
                    # LIBRARY DOOR
                    # ======================================

                    if (
                        door is not None
                        and door.get("type") == "library"
                    ):

                        if not any(
                            key.name == "library_key"
                            and key.collected
                            for key in self.keys
                        ):

                            self.show_hud_message(
                                "THE LIBRARY IS LOCKED. FIND THE LIBRARY KEY."
                            )

                        else:

                            door["open"] = True

                            self.ghost.active = False

                            if self.interaction.sounds.get("chase"):
                                self.interaction.sounds["chase"].stop()

                            self.show_hud_message(
                                "YOU ENTERED THE LIBRARY. THE GHOST CANNOT ENTER."
                            )

                        continue

                    # ==========================================
                    # LIBRARY DOOR
                    # ==========================================

                    if (
                        door is not None
                        and door.get("type") == "library"
                    ):

                        # Library door is opened after taking the key
                        library_key_taken = any(
                            key.name == "library_key"
                            and key.collected
                            for key in self.keys
                        )

                        if not library_key_taken:

                            self.interaction.play("locked")

                            self.show_hud_message(
                                "THE LIBRARY IS LOCKED."
                            )

                        else:

                            door["locked"] = False
                            door["open"] = True

                            self.interaction.play("door")

                            self.show_hud_message(
                                "THE LIBRARY DOOR OPENS..."
                            )

                        continue

                    # ==========================================
                    # LIBRARY SAFE ZONE
                    # ==========================================

                    library_x = 13.5
                    library_y = 4.5

                    library_distance = math.hypot(
                        self.player.x - library_x,
                        self.player.y - library_y
                    )

                    if (
                        self.ghost_phase == "library_chase"
                        and library_distance < 2.0
                    ):

                        self.ghost_phase = "library_safe"

                        self.ghost.active = False

                        if self.interaction.sounds.get("chase"):
                            self.interaction.sounds["chase"].stop()

                        self.show_hud_message(
                            "THE LIBRARY IS SAFE... FOR NOW."
                        )

                    # ==========================================
                    # GENERATOR PUZZLE
                    # ==========================================

                    if self.generator_puzzle_active:

                        if event.key == pygame.K_1:
                            self.generator_input += "1"

                        elif event.key == pygame.K_2:
                            self.generator_input += "2"

                        elif event.key == pygame.K_3:
                            self.generator_input += "3"

                        elif event.key == pygame.K_4:
                            self.generator_input += "4"

                        elif event.key == pygame.K_5:
                            self.generator_input += "5"

                        elif event.key == pygame.K_6:
                            self.generator_input += "6"

                        elif event.key == pygame.K_7:
                            self.generator_input += "7"

                        elif event.key == pygame.K_8:
                            self.generator_input += "8"

                        elif event.key == pygame.K_9:
                            self.generator_input += "9"

                        elif event.key == pygame.K_0:
                            self.generator_input += "0"

                        elif event.key == pygame.K_BACKSPACE:

                            self.generator_input = (
                                self.generator_input[:-1]
                            )

                        elif event.key == pygame.K_RETURN:

                            if self.generator_input == "428":

                                self.generator_puzzle_active = False

                                self.generator_activated = True

                                # ==================================
                                # GHOST RETURNS
                                # ==================================

                                self.ghost_phase = "final_chase"

                                self.ghost.active = True

                                self.interaction.play("chase")

                                self.show_hud_message(
                                    "GENERATOR ACTIVATED! THE GHOST HAS RETURNED!"
                                )

                            else:

                                self.generator_input = ""

                                self.show_hud_message(
                                    "WRONG SEQUENCE! TRY AGAIN."
                                )

                        continue

                    # # ==========================================
                    # # GENERATOR
                    # # ==========================================

                    # generator_x = 15.5
                    # generator_y = 11.5

                    # generator_distance = math.hypot(
                    #     self.player.x - generator_x,
                    #     self.player.y - generator_y
                    # )

                    # if (
                    #     generator_distance < 1.5
                    #     and not self.generator_activated
                    # ):

                    #     self.generator_puzzle_active = True
                    #     self.generator_input = ""

                    #     self.show_hud_message(
                    #         "GENERATOR OFF - ENTER THE START SEQUENCE"
                    #     )

                    #     continue

                    # ======================================
                    # NORMAL INTERACTION
                    # ======================================

                    result = self.interaction.interact(
                        self.player,
                        self.ghost
                    )

                    print(
                        "INTERACTION RESULT:",
                        result
                    )

                    continue
                # ==================================
                # ESC
                # ==================================

                if event.key == pygame.K_ESCAPE:

                    # Playing → Pause
                    if self.state == PLAYING:

                        self.state = PAUSED

                        pygame.mouse.set_visible(
                            True
                        )

                        pygame.event.set_grab(
                            False
                        )

                    # Pause → Playing
                    elif self.state == PAUSED:

                        self.state = PLAYING

                        pygame.mouse.set_visible(
                            False
                        )

                        pygame.event.set_grab(
                            True
                        )

                        pygame.mouse.get_rel()

                    # Game Over → Menu
                    elif self.state == GAME_OVER:

                        self.return_to_menu()

                    # Win → Menu
                    elif self.state == WIN:

                        self.return_to_menu()

                    continue

                # ==================================
                # ENTER / SPACE
                # ==================================

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):

                    # Game Over → Restart
                    if self.state == GAME_OVER:

                        self.start_game()

                    # Win → Restart
                    elif self.state == WIN:

                        self.start_game()

                    continue

    def open_mansion_door(self):

        if self.door_open:
            return

        print(
            "DOOR: Opening mansion door..."
        )

        self.door_open = True

        # ==========================================
        # DOOR SOUND
        # ==========================================

        if (self.audio_enabled
            and self.door_sound is not None):

            try:

                self.door_sound.play()

                print(
                    "AUDIO: door.wav playing"
                )

            except Exception as error:

                print(
                    "AUDIO ERROR playing door:",
                    error
                )

        # ==========================================
        # BACKGROUND MUSIC
        # ==========================================

        if self.audio_enabled:
            try:

                pygame.mixer.music.load(
                    self.background_music_path
                )

                pygame.mixer.music.set_volume(
                    0.5
                )

                pygame.mixer.music.play(
                    loops=-1
                )

                print(
                    "AUDIO: background.wav playing"
                )

            except Exception as error:

                print(
                    "AUDIO ERROR playing background:",
                    error
                )

        # ==========================================
        # ENTER MANSION
        # ==========================================

        self.state = PLAYING

        pygame.mouse.set_visible(
            False
        )

        pygame.event.set_grab(
            True
        )

        pygame.mouse.get_rel()

    def play_footsteps(self, dt):

        # ==========================================
        # SOUND AVAILABLE?
        # ==========================================

        if (
            not self.audio_enabled
            or self.footstep_sound is None
            or self.footstep_channel is None
        ):
            return

        # ==========================================
        # GHOST CAUGHT PLAYER
        # ==========================================

        if self.ghost_caught:

            self.footstep_timer = 0.0

            self.footstep_channel.stop()

            return

        # ==========================================
        # ONLY DURING GAMEPLAY
        # ==========================================

        if self.state != PLAYING:

            self.footstep_timer = 0.0

            return

        # ==========================================
        # KEYBOARD
        # ==========================================

        keys = pygame.key.get_pressed()

        moving = (
            keys[pygame.K_w]
            or keys[pygame.K_s]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
        )

        # ==========================================
        # PLAYER NOT MOVING
        # ==========================================

        if not moving:

            self.footstep_timer = 0.0

            return

        # ==========================================
        # TIMER
        # ==========================================

        if self.footstep_timer > 0:

            self.footstep_timer -= dt

            return

        # ==========================================
        # RUNNING?
        # ==========================================

        running = (
            keys[pygame.K_LSHIFT]
            or keys[pygame.K_RSHIFT]
        )

        # ==========================================
        # PLAY
        # ==========================================

        self.footstep_channel.play(
            self.footstep_sound
        )

        print(
            "AUDIO: footstep"
        )

        # ==========================================
        # SPEED
        # ==========================================

        if running:

            # 2x faster
            self.footstep_timer = 0.19

        else:

            # Normal
            self.footstep_timer = 0.38
    def show_hud_message(
        self,
        message,
        duration=3.0
    ):

        self.hud_message = message
        self.hud_message_timer = duration

    def draw_minimap(self):

        # ==========================================
        # MINIMAP SETTINGS
        # ==========================================

        minimap_width = 250
        minimap_height = 220

        margin = 20

        map_x = WIDTH - minimap_width - margin
        map_y = margin

        # Actual mansion map size
        map_width = self.mansion_map.width
        map_height = self.mansion_map.height

        # Leave space at top for title
        title_height = 30

        available_width = minimap_width - 20
        available_height = minimap_height - title_height - 10

        tile_size = min(
            available_width / map_width,
            available_height / map_height
        )

        # ==========================================
        # MINIMAP BACKGROUND
        # ==========================================

        minimap = pygame.Surface(
            (
                minimap_width,
                minimap_height
            ),
            pygame.SRCALPHA
        )

        minimap.fill(
            (5, 5, 8, 220)
        )

        # ==========================================
        # BORDER
        # ==========================================

        pygame.draw.rect(
            minimap,
            (180, 180, 180),
            (
                0,
                0,
                minimap_width,
                minimap_height
            ),
            2
        )

        # ==========================================
        # TITLE
        # ==========================================

        title = self.font_small.render(
            "MANSION MAP",
            True,
            (230, 230, 230)
        )

        minimap.blit(
            title,
            (
                10,
                5
            )
        )

        # ==========================================
        # MAP OFFSET
        # ==========================================

        map_offset_x = 10
        map_offset_y = title_height

        # ==========================================
        # DRAW ACTUAL MANSION GRID
        # ==========================================

        for row in range(map_height):

            for col in range(map_width):

                cell = self.mansion_map.grid[row][col]

                cell_x = int(
                    map_offset_x +
                    col * tile_size
                )

                cell_y = int(
                    map_offset_y +
                    row * tile_size
                )

                cell_width = max(
                    1,
                    int(tile_size) + 1
                )

                cell_height = max(
                    1,
                    int(tile_size) + 1
                )

                # ----------------------------------
                # WALL
                # ----------------------------------

                if cell == "#":

                    pygame.draw.rect(
                        minimap,
                        (55, 55, 60),
                        (
                            cell_x,
                            cell_y,
                            cell_width,
                            cell_height
                        )
                    )

                # ----------------------------------
                # FLOOR
                # ----------------------------------

                else:

                    pygame.draw.rect(
                        minimap,
                        (18, 18, 22),
                        (
                            cell_x,
                            cell_y,
                            cell_width,
                            cell_height
                        )
                    )

        # ==========================================
        # DOORS
        # ==========================================

        for door in self.mansion_map.doors:

            door_x = int(
                map_offset_x +
                door["x"] * tile_size
            )

            door_y = int(
                map_offset_y +
                door["y"] * tile_size
            )

            if door["locked"]:

                door_color = (
                    220,
                    60,
                    60
                )

            elif door["open"]:

                door_color = (
                    80,
                    200,
                    100
                )

            else:

                door_color = (
                    220,
                    180,
                    60
                )

            pygame.draw.circle(
                minimap,
                door_color,
                (
                    door_x,
                    door_y
                ),
                4
            )

        # ==========================================
        # LIBRARY KEY / KEY VAULT
        # ==========================================

        if not self.mansion_map.library_key["collected"]:

            key_x = int(
                map_offset_x +
                self.mansion_map.library_key["x"] *
                tile_size
            )

            key_y = int(
                map_offset_y +
                self.mansion_map.library_key["y"] *
                tile_size
            )

            # Key is hidden inside the vault
            if not self.mansion_map.key_vault["solved"]:

                pygame.draw.circle(
                    minimap,
                    (180, 120, 40),
                    (
                        key_x,
                        key_y
                    ),
                    5
                )

            # Vault solved -> show actual key
            else:

                pygame.draw.circle(
                    minimap,
                    (255, 215, 0),
                    (
                        key_x,
                        key_y
                    ),
                    4
                )

        # ==========================================
        # MEDKIT
        # ==========================================

        if not self.mansion_map.medkit["collected"]:

            medkit_x = int(
                map_offset_x +
                self.mansion_map.medkit["x"] *
                tile_size
            )

            medkit_y = int(
                map_offset_y +
                self.mansion_map.medkit["y"] *
                tile_size
            )

            pygame.draw.circle(
                minimap,
                (80, 220, 100),
                (
                    medkit_x,
                    medkit_y
                ),
                3
            )

        # ==========================================
        # EXIT DOOR
        # ==========================================

        exit_x = int(
            map_offset_x +
            self.mansion_map.exit_door["x"] *
            tile_size
        )

        exit_y = int(
            map_offset_y +
            self.mansion_map.exit_door["y"] *
            tile_size
        )

        # Locked exit = blue/red marker
        if self.mansion_map.exit_door["locked"]:

            exit_color = (
                80,
                120,
                255
            )

        else:

            # Unlocked exit = green
            exit_color = (
                80,
                255,
                120
            )

        pygame.draw.circle(
            minimap,
            exit_color,
            (
                exit_x,
                exit_y
            ),
            5
        )

        # ==========================================
        # GHOST
        # ==========================================

        if hasattr(self, "ghost"):

            if self.ghost.active:

                ghost_x = int(
                    map_offset_x +
                    self.ghost.x *
                    tile_size
                )

                ghost_y = int(
                    map_offset_y +
                    self.ghost.y *
                    tile_size
                )

                pygame.draw.circle(
                    minimap,
                    (190, 40, 220),
                    (
                        ghost_x,
                        ghost_y
                    ),
                    5
                )

        # ==========================================
        # PLAYER
        # ==========================================

        player_x = int(
            map_offset_x +
            self.player.x *
            tile_size
        )

        player_y = int(
            map_offset_y +
            self.player.y *
            tile_size
        )

        pygame.draw.circle(
            minimap,
            (50, 230, 80),
            (
                player_x,
                player_y
            ),
            5
        )

        # ==========================================
        # PLAYER DIRECTION
        # ==========================================

        direction_length = 8

        direction_x = int(
            player_x +
            math.cos(self.player.angle) *
            direction_length
        )

        direction_y = int(
            player_y +
            math.sin(self.player.angle) *
            direction_length
        )

        pygame.draw.line(
            minimap,
            (100, 255, 100),
            (
                player_x,
                player_y
            ),
            (
                direction_x,
                direction_y
            ),
            2
        )

        # ==========================================
        # SHOW MINIMAP
        # ==========================================

        self.screen.blit(
            minimap,
            (
                map_x,
                map_y
            )
        )

    # ==========================================
    # UPDATE
    # ==========================================

    def update(
        self,
        dt
    ):

        if self.state != PLAYING:

            return
        # ==========================================
        # HUD MESSAGE TIMER
        # ==========================================

        if self.hud_message_timer > 0:

            self.hud_message_timer -= dt

            if self.hud_message_timer <= 0:

                self.hud_message = ""
                self.hud_message_timer = 0
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

        self.player.update(
            dt
        )

        # ==========================================
        # LIBRARY SAFE ZONE
        # ==========================================

        library_x = 10.5
        library_y = 3.5

        library_distance = math.hypot(
            self.player.x - library_x,
            self.player.y - library_y
        )

        if (
            self.ghost_phase == "library_chase"
            and library_distance < 1.5
        ):

            self.ghost_phase = "library_safe"

            self.ghost.active = False

            if self.interaction.sounds.get("chase"):
                self.interaction.sounds["chase"].stop()

            self.show_hud_message(
                "THE LIBRARY IS SAFE... FOR NOW."
            )

        # ==========================================
        # LIBRARY KEY PICKUP
        # ==========================================

        # ==========================================
        # KEY PICKUP
        # ==========================================

        for key in self.keys:

            if key.collected:
                continue

            # Basement key is available only after
            # solving the library puzzle
            if (
                key.name == "basement_key"
                and not self.library_puzzle_solved
            ):
                continue

            distance = math.hypot(
                self.player.x - key.x,
                self.player.y - key.y
            )

            if distance < 1.0:

                key.collected = True

                # ==========================================
                # LIBRARY KEY
                # ==========================================

                if key.name == "library_key":

                    self.ghost_phase = "library_chase"
                    self.ghost.active = True

                    self.interaction.play("chase")

                    self.show_hud_message(
                        "LIBRARY KEY TAKEN! THE GHOST HAS AWAKENED!"
                    )

                # ==========================================
                # BASEMENT KEY
                # ==========================================

                elif key.name == "basement_key":

                    # Tell the map that the basement key was collected
                    self.mansion_map.basement_key_collected = True

                    self.ghost_phase = "basement_chase"
                    self.ghost.active = True

                    self.interaction.play("chase")

                    self.show_hud_message(
                        "BASEMENT KEY TAKEN! RUN TO THE BASEMENT!"
                    )

                    self.interaction.play("chase")

                    self.show_hud_message(
                        "BASEMENT KEY TAKEN! RUN TO THE BASEMENT!"
                    )

                break

        # ==========================================
        # BASEMENT AREA
        # ==========================================

        basement_x = 15.5
        basement_y = 11.5

        basement_distance = math.hypot(
            self.player.x - basement_x,
            self.player.y - basement_y
        )

        basement_key_collected = any(
            key.name == "basement_key"
            and key.collected
            for key in self.keys
        )

        if (
            basement_key_collected
            and basement_distance < 2.0
            and self.ghost_phase == "basement_chase"
        ):

            self.ghost_phase = "basement_safe"

            self.ghost.active = False

            if self.interaction.sounds.get("chase"):
                self.interaction.sounds["chase"].stop()

            # Unlock final exit
            self.mansion_map.exit_door["locked"] = False
            self.mansion_map.exit_door["open"] = True

            self.show_hud_message(
                "THE BASEMENT IS SAFE! THE EXIT IS NOW OPEN!"
            )
            
        # ==========================================
        # LIBRARY PUZZLE ACTIVATION
        # ==========================================

        library_x = 10.5
        library_y = 3.5

        library_distance = math.hypot(
            self.player.x - library_x,
            self.player.y - library_y
        )

        if (
            self.ghost_phase == "library_safe"
            and not self.library_puzzle_solved
            and not self.library_puzzle_active
            and library_distance < 2.0
        ):

            self.library_puzzle_active = True
            self.library_books = []

            self.show_hud_message(
                "LIBRARY PUZZLE: ARRANGE THE BOOKS!"
            )

        # ==========================================
        # PLAYER FOOTSTEPS
        # ==========================================

        self.play_footsteps(dt)

        # ==========================================
        # GHOST
        # ==========================================

        if self.ghost.active:

            self.ghost.update(
                self.player,
                self.mansion_map,
                dt
            )

            # ==========================================
            # GHOST ATTACK
            # ==========================================

            if self.ghost_attack_cooldown > 0:

                self.ghost_attack_cooldown -= dt

            ghost_distance = math.hypot(
                self.ghost.x - self.player.x,
                self.ghost.y - self.player.y
            )

            # Ghost catches player
            if (
                ghost_distance < 0.75
                and not self.ghost_caught
                and self.ghost_attack_cooldown <= 0
            ):

                self.ghost_caught = True
                self.ghost_caught_time = 0.0

                self.player_lives -= 1

                self.ghost_attack_cooldown = 2.0

                # Stop footsteps immediately
                if self.footstep_channel is not None:

                    self.footstep_channel.stop()

                self.show_hud_message(
                    "THE GHOST CAUGHT YOU! ESCAPE WITHIN 5 SECONDS!"
                )

                print(
                    f"GHOST CAUGHT PLAYER - LIVES LEFT: {self.player_lives}"
                )

                # ==========================================
                # GAME OVER
                # ==========================================

                if self.player_lives <= 0:

                    self.ghost.active = False

                    self.interaction.game_over()

                    self.state = GAME_OVER

                    pygame.mouse.set_visible(True)

                    pygame.event.set_grab(False)

                    return

            # ==========================================
            # ESCAPE TIMER
            # ==========================================

            if self.ghost_caught:

                self.ghost_caught_time += dt

                ghost_distance = math.hypot(
                    self.ghost.x - self.player.x,
                    self.ghost.y - self.player.y
                )

                # Player escaped
                if ghost_distance > 2.0:

                    self.ghost_caught = False
                    self.ghost_caught_time = 0.0

                    self.show_hud_message(
                        "YOU ESCAPED! RUN FASTER!"
                    )

                # ==========================================
                # 5 SECONDS FINISHED = GAME OVER
                # ==========================================

                elif self.ghost_caught_time >= self.escape_time_limit:

                    self.ghost_caught_time = 0.0
                    self.ghost_caught = False

                    self.ghost.active = False

                    self.interaction.game_over()

                    self.state = GAME_OVER

                    pygame.mouse.set_visible(True)

                    pygame.event.set_grab(False)

                    return

    def draw_library_key(self):

        # ==========================================
        # LIBRARY KEY VISIBILITY
        # ==========================================

        # Key is hidden until vault is unlocked
        if not self.vault_unlocked:
            return

        # Find the actual library key object
        library_key = None

        for key in self.keys:

            if key.name == "library_key":
                library_key = key
                break

        # Key object not found
        if library_key is None:
            return

        # Key already collected
        if library_key.collected:
            return

        # Image failed to load
        if self.library_key_image is None:
            return

        # ==========================================
        # KEY WORLD POSITION
        # ==========================================

        key_x = library_key.x
        key_y = library_key.y

        dx = key_x - self.player.x
        dy = key_y - self.player.y

        distance = math.hypot(
            dx,
            dy
        )

        # Too close / invalid
        if distance < 0.1:

            distance = 0.1

        # ==========================================
        # ANGLE TO KEY
        # ==========================================

        angle = math.atan2(
            dy,
            dx
        ) - self.player.angle

        # Normalize angle
        while angle > math.pi:

            angle -= 2 * math.pi

        while angle < -math.pi:

            angle += 2 * math.pi

        # ==========================================
        # FIELD OF VIEW
        # ==========================================

        fov = math.radians(60)

        if abs(angle) > fov / 2:

            return

        # ==========================================
        # SCREEN POSITION
        # ==========================================

        screen_x = (
            WIDTH // 2
            +
            int(
                (angle / fov)
                * WIDTH
            )
        )

        # ==========================================
        # SIZE
        # ==========================================

        size = int(
            160 / distance
        )

        size = max(
            35,
            min(
                180,
                size
            )
        )

        key_image = pygame.transform.smoothscale(
            self.library_key_image,
            (size, size)
        )

        rect = key_image.get_rect()

        rect.centerx = screen_x

        # Put key slightly below center
        rect.centery = HEIGHT // 2 + 40

        self.screen.blit(
            key_image,
            rect
        )

    def draw_basement_key(self):

        # ==========================================
        # BASEMENT KEY VISIBILITY
        # ==========================================

        # Basement key appears only after library puzzle
        if not self.library_puzzle_solved:
            return

        # Find basement key
        basement_key = None

        for key in self.keys:
            if key.name == "basement_key":
                basement_key = key
                break

        if basement_key is None:
            return

        # Already collected
        if basement_key.collected:
            return

        # Use same key image
        if self.library_key_image is None:
            return

        # ==========================================
        # KEY POSITION
        # ==========================================

        key_x = basement_key.x
        key_y = basement_key.y

        dx = key_x - self.player.x
        dy = key_y - self.player.y

        distance = math.hypot(dx, dy)

        if distance < 0.1:
            distance = 0.1

        # ==========================================
        # ANGLE
        # ==========================================

        angle = math.atan2(
            dy,
            dx
        ) - self.player.angle

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        # ==========================================
        # FIELD OF VIEW
        # ==========================================

        fov = math.radians(60)

        if abs(angle) > fov / 2:
            return

        # ==========================================
        # SCREEN POSITION
        # ==========================================

        screen_x = (
            WIDTH // 2
            +
            int(
                (angle / fov) * WIDTH
            )
        )

        # ==========================================
        # KEY SIZE
        # ==========================================

        size = int(160 / distance)

        size = max(
            35,
            min(
                180,
                size
            )
        )

        key_image = pygame.transform.smoothscale(
            self.library_key_image,
            (size, size)
        )

        rect = key_image.get_rect()

        rect.centerx = screen_x
        rect.centery = HEIGHT // 2 + 40

        self.screen.blit(
            key_image,
            rect
        )

    # ==========================================
    # DRAW
    # ==========================================

    def draw(self):

        # ==========================================
        # MAIN MENU / HOW TO PLAY / OPTIONS
        # ==========================================

        if self.state in (
            MENU,
            HOW_TO_PLAY,
            OPTIONS,
        ):

            self.menu.draw()

        elif self.state == DOOR:

            self.draw_door()

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

        # Renderer receives:
        #
        # screen
        # player
        # ghost
        #
        # Ghost rendering is handled by renderer.py.

        self.renderer.draw(
            self.screen,
            self.player,
            self.ghost
        )

        self.draw_library_key()
        self.draw_basement_key()
        # HUD
        self.draw_hud()

        # MINIMAP
        self.draw_minimap()

        # # ==========================================
        # # GENERATOR PUZZLE
        # # ==========================================

        # if self.generator_puzzle_active:

        #     overlay = pygame.Surface(
        #         (WIDTH, HEIGHT),
        #         pygame.SRCALPHA
        #     )

        #     overlay.fill(
        #         (0, 0, 0, 200)
        #     )

        #     self.screen.blit(
        #         overlay,
        #         (0, 0)
        #     )

        #     title = self.big_font.render(
        #         "BASEMENT GENERATOR",
        #         True,
        #         (220, 220, 220)
        #     )

        #     self.screen.blit(
        #         title,
        #         title.get_rect(
        #             center=(
        #                 WIDTH // 2,
        #                 170
        #             )
        #         )
        #     )

        #     instruction = self.font.render(
        #         "Enter the correct startup sequence",
        #         True,
        #         (230, 230, 230)
        #     )

        #     self.screen.blit(
        #         instruction,
        #         instruction.get_rect(
        #             center=(
        #                 WIDTH // 2,
        #                 250
        #             )
        #         )
        #     )

        #     sequence = self.generator_input

        #     if not sequence:
        #         sequence = "_ _ _"

        #     sequence_text = self.big_font.render(
        #         sequence,
        #         True,
        #         (255, 210, 80)
        #     )

        #     self.screen.blit(
        #         sequence_text,
        #         sequence_text.get_rect(
        #             center=(
        #                 WIDTH // 2,
        #                 350
        #             )
        #         )
        #     )

        #     help_text = self.font_small.render(
        #         "Enter 428    ENTER = Activate",
        #         True,
        #         (180, 180, 180)
        #     )

        #     self.screen.blit(
        #         help_text,
        #         help_text.get_rect(
        #             center=(
        #                 WIDTH // 2,
        #                 450
        #             )
        #         )
        #     )

        # ==========================================
        # VAULT PUZZLE
        # ==========================================

        if self.vault_puzzle_active:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 190)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            # Title
            title = self.big_font.render(
                "VAULT LOCKED",
                True,
                (220, 40, 40)
            )

            title_rect = title.get_rect(
                center=(
                    WIDTH // 2,
                    200
                )
            )

            self.screen.blit(
                title,
                title_rect
            )

            # Instruction
            instruction = self.font.render(
                "Enter the 4-digit code",
                True,
                (230, 230, 230)
            )

            instruction_rect = instruction.get_rect(
                center=(
                    WIDTH // 2,
                    280
                )
            )

            self.screen.blit(
                instruction,
                instruction_rect
            )

            # Code
            code_text = self.big_font.render(
                self.vault_input.ljust(4, "_"),
                True,
                (255, 210, 80)
            )

            code_rect = code_text.get_rect(
                center=(
                    WIDTH // 2,
                    370
                )
            )

            self.screen.blit(
                code_text,
                code_rect
            )

            # Help
            help_text = self.font_small.render(
                "ENTER = Unlock    BACKSPACE = Delete",
                True,
                (180, 180, 180)
            )

            help_rect = help_text.get_rect(
                center=(
                    WIDTH // 2,
                    450
                )
            )

            self.screen.blit(
                help_text,
                help_rect
            )

        # ==========================================
        # LIBRARY PUZZLE
        # ==========================================

        if self.library_puzzle_active:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 210)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            # TITLE
            title = self.big_font.render(
                "THE LIBRARY",
                True,
                (220, 220, 220)
            )

            self.screen.blit(
                title,
                title.get_rect(
                    center=(
                        WIDTH // 2,
                        150
                    )
                )
            )

            # PUZZLE INSTRUCTION
            instruction = self.font.render(
                "Arrange the books in the correct order",
                True,
                (230, 230, 230)
            )

            self.screen.blit(
                instruction,
                instruction.get_rect(
                    center=(
                        WIDTH // 2,
                        230
                    )
                )
            )

            # BOOKS
            books = self.big_font.render(
                "1    2    3    4",
                True,
                (180, 150, 80)
            )

            self.screen.blit(
                books,
                books.get_rect(
                    center=(
                        WIDTH // 2,
                        320
                    )
                )
            )

            # PLAYER INPUT
            if self.library_books:

                sequence = "  ".join(
                    str(number)
                    for number in self.library_books
                )

            else:

                sequence = "_  _  _  _"

            sequence_text = self.big_font.render(
                sequence,
                True,
                (255, 210, 80)
            )

            self.screen.blit(
                sequence_text,
                sequence_text.get_rect(
                    center=(
                        WIDTH // 2,
                        410
                    )
                )
            )

            # HELP
            help_text = self.font_small.render(
                "Press 1 2 3 4    ENTER = Confirm    BACKSPACE = Delete",
                True,
                (180, 180, 180)
            )

            self.screen.blit(
                help_text,
                help_text.get_rect(
                    center=(
                        WIDTH // 2,
                        510
                    )
                )
            )    

    def draw_door(self):

        # ==========================================
        # DARK BACKGROUND
        # ==========================================

        self.screen.fill(
            (5, 5, 8)
        )

        # ==========================================
        # LOAD DOOR IMAGE
        # ==========================================

        try:

            door_image = pygame.image.load(
                "assets/textures/door.png"
            ).convert()

            # Scale door to fit screen

            door_image = pygame.transform.scale(
                door_image,
                (
                    WIDTH,
                    HEIGHT
                )
            )

            self.screen.blit(
                door_image,
                (0, 0)
            )

        except Exception as error:

            print(
                "Door image error:",
                error
            )

            # Fallback door

            pygame.draw.rect(
                self.screen,
                (35, 25, 20),
                (
                    WIDTH // 2 - 180,
                    80,
                    360,
                    560
                )
            )

            pygame.draw.circle(
                self.screen,
                (180, 150, 70),
                (
                    WIDTH // 2 + 120,
                    HEIGHT // 2
                ),
                10
            )

        # ==========================================
        # TITLE
        # ==========================================

        title = self.big_font.render(
            "DARK HALL MANSION",
            True,
            (210, 210, 210)
        )

        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                60
            )
        )

        self.screen.blit(
            title,
            title_rect
        )

        # ==========================================
        # INSTRUCTION
        # ==========================================

        instruction = self.font.render(
            "Press E to open the mansion door",
            True,
            (220, 220, 220)
        )

        instruction_rect = instruction.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 70
            )
        )

        self.screen.blit(
            instruction,
            instruction_rect
        )

        # ==========================================
        # ATMOSPHERIC MESSAGE
        # ==========================================

        message = self.font.render(
            "Something waits inside...",
            True,
            (160, 60, 60)
        )

        message_rect = message.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT - 35
            )
        )

        self.screen.blit(
            message,
            message_rect
        )
    # ==========================================
    # PAUSE SCREEN
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

    def draw_hud(self):

        # ==========================================
        # HUD PANEL
        # ==========================================

        panel = pygame.Surface(
            (330, 105),
            pygame.SRCALPHA
        )

        panel.fill(
            (0, 0, 0, 150)
        )

        self.screen.blit(
            panel,
            (15, 15)
        )
        
        # ==========================================
        # HEALTH
        # ==========================================

        health_text = self.font.render(
            f"HEALTH: {self.player_health}%",
            True,
            (220, 70, 70)
        )

        self.screen.blit(
            health_text,
            (30, 30)
        )

        # ==========================================
        # HEALTH BAR
        # ==========================================

        bar_x = 30
        bar_y = 62
        bar_width = 280
        bar_height = 14

        pygame.draw.rect(
            self.screen,
            (60, 20, 20),
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            )
        )

        health_width = int(
            bar_width *
            max(
                0,
                min(
                    self.player_health /
                    self.max_player_health,
                    1
                )
            )
        )

        pygame.draw.rect(
            self.screen,
            (190, 40, 40),
            (
                bar_x,
                bar_y,
                health_width,
                bar_height
            )
        )

        # ==========================================
        # FLASHLIGHT
        # ==========================================

        flashlight_text = self.font.render(
            f"FLASHLIGHT: {self.flashlight_battery}%",
            True,
            (230, 220, 120)
        )

        self.screen.blit(
            flashlight_text,
            (30, 82)
        )

        # ==========================================
        # LIVES
        # ==========================================

        lives_text = self.font.render(
            f"LIVES: {self.player_lives}/3",
            True,
            (255, 80, 80)
        )

        self.screen.blit(
            lives_text,
            (30, 112)
        )

        # ==========================================
        # GHOST ESCAPE COUNTDOWN
        # ==========================================

        if self.ghost_caught:

            remaining = max(
                0,
                int(
                    self.escape_time_limit
                    - self.ghost_caught_time
                )
            )

            escape_text = self.font.render(
                f"ESCAPE! {remaining} SECONDS!",
                True,
                (255, 50, 50)
            )

            escape_rect = escape_text.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT - 60
                )
            )

            self.screen.blit(
                escape_text,
                escape_rect
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
            "You escaped the Dark Hall Mansion.",
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
