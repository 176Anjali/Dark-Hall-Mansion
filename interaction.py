import os
import math
import pygame

from settings import (
    MASTER_VOLUME,
    SFX_VOLUME,
)


class InteractionSystem:

    def __init__(self, mansion_map, renderer):

        self.mansion_map = mansion_map
        self.renderer = renderer

        self.sounds = {}

        self.flashlight_on = False

        self.load_sounds()
        self.start_background_music()

    # ==========================================
    # SOUND LOADING
    # ==========================================

    def load_sounds(self):

        base = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "sounds"
        )

        sound_files = {

            "door": "door.wav",
            "key": "key.wav",
            "locked": "locked.wav",
            "footstep": "footstep.wav",
            "chase": "chase.wav",
            "gameover": "gameover.wav",
            "flashlight": "flashlight.wav",
        }

        for name, filename in sound_files.items():

            path = os.path.join(
                base,
                filename
            )

            try:

                if os.path.exists(path):

                    self.sounds[name] = pygame.mixer.Sound(
                        path
                    )

                    self.sounds[name].set_volume(
                        SFX_VOLUME * MASTER_VOLUME
                    )

                else:

                    print(
                        "Sound not found:",
                        path
                    )

            except Exception as error:

                print(
                    "Sound error:",
                    filename,
                    error
                )

    # ==========================================
    # BACKGROUND MUSIC
    # ==========================================

    def start_background_music(self):

        path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "sounds",
            "background.wav"
        )

        try:

            if os.path.exists(path):

                pygame.mixer.music.load(path)

                pygame.mixer.music.set_volume(
                    0.45 * MASTER_VOLUME
                )

                pygame.mixer.music.play(-1)

        except Exception as error:

            print(
                "Background music error:",
                error
            )

    # ==========================================
    # PLAY SOUND
    # ==========================================

    def play(self, name):

        sound = self.sounds.get(name)

        if sound:
            sound.play()

    # ==========================================
    # FLASHLIGHT
    # ==========================================

    def toggle_flashlight(self):

        self.flashlight_on = not self.flashlight_on

        self.play("flashlight")

        if self.flashlight_on:

            self.renderer.show_message(
                "Flashlight ON"
            )

        else:

            self.renderer.show_message(
                "Flashlight OFF"
            )

    # ==========================================
    # INTERACTION
    # ==========================================

    def interact(self, player, enemy):

        # ==========================================
        # FIND NEARBY DOOR
        # ==========================================

        door = self.mansion_map.get_nearby_door(
            player.x,
            player.y,
            2.0
        )

        if door:

            door_type = str(
                door.get("type", "")
            ).lower()

            # ======================================
            # VAULT
            # ======================================

            if door_type == "vault":

                if door["locked"]:

                    self.play("locked")

                    self.renderer.show_message(
                        "VAULT LOCKED - Solve the puzzle."
                    )

                    return "vault_locked"

                door["open"] = True

                self.play("door")

                self.renderer.show_message(
                    "VAULT OPENED!"
                )

                return "vault_open"

            # ======================================
            # LIBRARY
            # ======================================

            if door_type == "library":

                door["locked"] = False
                door["open"] = True

                self.play("door")

                self.renderer.show_message(
                    "LIBRARY DOOR OPENED!"
                )

                return "library_open"

            # ======================================
            # BASEMENT = FINAL EXIT
            # ======================================

            if door_type == "basement":

                if self.mansion_map.basement_key_collected:

                    door["locked"] = False
                    door["open"] = True

                    self.play("door")

                    self.renderer.show_message(
                        "THE BASEMENT GATE OPENS... YOU ESCAPED!"
                    )

                    return "game_complete"

                else:

                    self.play("locked")

                    self.renderer.show_message(
                        "BASEMENT LOCKED - You need the Basement Key."
                    )

                    return "basement_locked"

            # ======================================
            # NORMAL DOOR
            # ======================================

            if door["locked"]:

                self.play("locked")

                self.renderer.show_message(
                    "This door is locked."
                )

                return "locked"

            if not door["open"]:

                door["open"] = True

                self.play("door")

                self.renderer.show_message(
                    "Door opened."
                )

                return "door_open"

        # ==========================================
        # LIBRARY KEY
        # ==========================================

        library_key = getattr(
            self.mansion_map,
            "library_key",
            None
        )

        if library_key is not None:

            if (
                library_key["visible"]
                and not library_key["collected"]
            ):

                distance = math.hypot(
                    player.x - library_key["x"],
                    player.y - library_key["y"]
                )

                if distance < 1.15:

                    library_key["collected"] = True

                    self.play("key")

                    self.renderer.show_message(
                        "LIBRARY KEY COLLECTED!"
                    )

                    return "library_key"

        # ==========================================
        # NOTHING
        # ==========================================

        self.renderer.show_message(
            "Nothing to interact with here."
        )

        return None

    # ==========================================
    # FOOTSTEPS
    # ==========================================

    def footsteps(self):

        sound = self.sounds.get(
            "footstep"
        )

        if sound:

            if not pygame.mixer.get_busy():

                sound.play()

    # ==========================================
    # GAME OVER SOUND
    # ==========================================

    def game_over(self):

        pygame.mixer.music.stop()

        self.play(
            "gameover"
        )

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        pygame.mixer.music.stop()
