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

            # Your actual filename is flashight.wav
            "flashlight": "flashight.wav",
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
    # BACKGROUND
    # ==========================================

    def start_background_music(self):

        path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "sounds",
            "background.wav"
        )

        try:

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

        # --------------------------------------
        # KEY
        # --------------------------------------

        if not self.mansion_map.key_collected:

            kx, ky = self.mansion_map.key_position

            distance = math.hypot(
                player.x - kx,
                player.y - ky
            )

            if distance < 1.15:

                self.mansion_map.collect_key()

                self.play("key")

                self.renderer.show_message(
                    "You found the key! Something heard you..."
                )

                enemy.activate()

                self.play("chase")

                return "key"

        # --------------------------------------
        # DOOR
        # --------------------------------------

        door = self.mansion_map.nearby_door(
            player.x,
            player.y,
            1.7
        )

        if door:

            x, y = door

            # Correct exit
            if self.mansion_map.is_exit_door(x, y):

                if self.mansion_map.key_collected:

                    self.mansion_map.open_door(
                        x,
                        y
                    )

                    self.play("door")

                    self.renderer.show_message(
                        "The key fits! Escape!"
                    )

                    return "exit_open"

                else:

                    self.play("locked")

                    self.renderer.show_message(
                        "LOCKED - You need a key."
                    )

                    return "locked"

            # Wrong door
            self.play("locked")

            self.renderer.show_message(
                "This door is locked."
            )

            return "locked"

        self.renderer.show_message(
            "Nothing to interact with here."
        )

        return None

    # ==========================================
    # FOOTSTEPS
    # ==========================================

    def footsteps(self):

        sound = self.sounds.get("footstep")

        if sound:

            if not pygame.mixer.get_busy():

                sound.play()

    # ==========================================
    # GAME OVER SOUND
    # ==========================================

    def game_over(self):

        pygame.mixer.music.stop()

        self.play("gameover")

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        pygame.mixer.music.stop()