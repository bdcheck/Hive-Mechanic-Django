import pygame
from pygame.locals import *
from hive_client import HiveClient, VariableScope, GotoCommand
from HiveCache import HiveCache, PygameSoundCache, PygameImageCache
from requests import exceptions
import json
import configparser
from ast import literal_eval


net_timeout = 4
max_timeout = 10
check_time = 100
timeout = 120000
keys = [pygame.K_LEFT, pygame.K_RIGHT]
start_button = pygame.K_DOWN

config = configparser.ConfigParser()
config.read("./config.ini")
cd = config['Config']
DEBUG = cd.getboolean('debug')
PRELOAD_ON = cd.getboolean('preload_on')
FULLSCREEN = cd.getboolean('fullscreen')
error_screen_file = cd['error_screen_file']
token = cd['token']
url = cd['url']
start_sequence = cd['start_sequence']
intialize_sequence = cd["intial_sequence"]
IMAGE_RESOLUTION = literal_eval(cd['image_resolution'])


class MlkMural(object):

    def __init__(self):
        # pygame screen initialization
        pygame.init()
        pygame.mixer.init()
        flags = pygame.SCALED
        if FULLSCREEN:
            flags = pygame.FULLSCREEN | flags
        self.screen = pygame.display.set_mode(IMAGE_RESOLUTION, flags)
        self.error_screen = pygame.image.load(error_screen_file)

        # Hive client initialization
        self.client = HiveClient(api_url=url, token=token, max_timeout=max_timeout, timeout=net_timeout)

        # sound and image cache initialization
        self.sound_cache = PygameSoundCache.get_sound_cache()
        self.image_cache = PygameImageCache.get_image_cache()
        self.in_timeout = False
        self.net_requests = 0
        self.current_screen = ""
        self.initial_hive()

    def preload_cache(self):
        preload = self.fetch_variable("preload", scope=VariableScope.game)
        preload = json.loads(preload)
        # preload takes a variable on hive mechanic and downloads all the files
        if preload and PRELOAD_ON:
            for load in preload:
                url_type = HiveCache.get_type(load)
                if url_type == 'audio':
                    self.sound_cache.get_value(load)
                elif url_type == 'image':
                    self.image_cache.get_value(load)

    def goto_start_screen(self):
        self.issue_command(GotoCommand(start_sequence))
        self.current_screen = "start"

    def cleanup(self, cache: HiveCache):
        cache.clear()

    def initial_hive(self):
        self.issue_command(GotoCommand(intialize_sequence), player="game")
        self.preload_cache()

    def reset_system(self):
        self.cleanup(self.image_cache)
        self.cleanup(self.sound_cache)
        pygame.display.flip()
        pygame.display.update()
        self.initial_hive()

    def network_timeout(self):
        self.screen.blit(self.error_screen, (0, 0))
        pygame.display.flip()
        pygame.display.update()
        self.in_timeout = False
        self.net_requests = 0

    def issue_command(self, command, player="game"):
        waiting = True
        while waiting:
            try:
                self.client.issue_command(command, player=player)
                waiting = False
            except (TimeoutError, exceptions.ConnectionError):
                self.network_timeout()

    def fetch_variable(self, variable_name, player="game", scope=VariableScope.game):
        waiting = True
        while waiting:
            try:
                data = self.client.fetch_variable(variable_name, player=player, scope=scope)
                self.in_timeout = False
                waiting = False
                return data
            except (TimeoutError, exceptions.ConnectionError):
                self.network_timeout()

    def run(self):
        NEXT_SCREEN = USEREVENT + 1
        playing_sound = None
        choices = []
        # pause is there to flag when keypress need to be ignored, like during screen transitions
        pause = True
        last_press = 0
        timer = 0
        clock = pygame.time.Clock()
        reset = 0
        self.goto_start_screen()
        pygame.time.set_timer(NEXT_SCREEN, check_time, True)

        while True:
            tick = clock.tick()
            timer += tick
            for event in pygame.event.get():
                if event.type == NEXT_SCREEN:
                    if playing_sound:
                        self.sound_cache.stop(playing_sound)
                    sound = self.fetch_variable("sound", player="game", scope=VariableScope.game)
                    image = self.fetch_variable("image", player="game", scope=VariableScope.game)
                    if sound == '""':
                        sound = None
                    if image == '""':
                        image = None
                    c = self.fetch_variable("choices", player="game", scope=VariableScope.game)
                    if c:
                        choices = json.loads(c)
                    else:
                        choices = []
                        error = True
                    reset = self.fetch_variable("reset", player="game", scope=VariableScope.game)
                    # retrieve sound and play if there
                    if sound:
                        playing_sound = sound
                        self.sound_cache.play(sound)
                    # retrieve image and show on screen if there
                    if image:
                        current_image = self.image_cache.get_image(image)
                        if current_image:
                            self.screen.blit(current_image, (0, 0))
                            pygame.display.flip()
                            pygame.display.update()
                    else:
                        pygame.display.flip()
                        pygame.display.update()
                    pause = False

                if event.type == pygame.KEYUP:
                    last_press = timer
                    # quit game
                    if event.key == pygame.K_q and DEBUG:
                        self.cleanup(self.sound_cache)
                        self.cleanup(self.image_cache)
                        quit()
                    if event.key == start_button and self.current_screen != "start":
                        self.goto_start_screen()
                        pygame.time.set_timer(NEXT_SCREEN, check_time, True)
                    elif event.key == start_button:
                        # this starts with any keypress
                        choice = choices[0]
                        self.current_screen = choice
                        self.issue_command(GotoCommand(choice), player="game")
                        pygame.time.set_timer(NEXT_SCREEN, check_time, True)
                        pause = True
                        timer = 0
                        last_press = timer
                    # look to see if the button pressed was the first, second or third option
                    if event.key in keys and not pause:
                        index = keys.index(event.key)
                        choice = choices[index]
                        self.current_screen = choice
                        self.issue_command(GotoCommand(choice), player="game")
                        pygame.time.set_timer(NEXT_SCREEN, check_time, True)
                        pause = True
            # check for timeout and goto start screen
            diff = timer - last_press
            if diff > timeout and self.current_screen != "start":
                self.goto_start_screen()
                pygame.time.set_timer(NEXT_SCREEN, check_time, True)


if __name__ == "__main__":
    mlk_mural = MlkMural()
    mlk_mural.run()
