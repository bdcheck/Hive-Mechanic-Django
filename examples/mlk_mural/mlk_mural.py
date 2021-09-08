import pygame
from pygame.locals import *
from hive_client import HiveClient, VariableScope, GotoCommand
from HiveCache import HiveCache, PygameSoundCache, PygameImageCache
import json


def cleanup(cache: HiveCache):
    cache.clear()


def reset():
    issue_command(GotoCommand("initial"), player="game")


def network_timeout():
    global in_timeout
    if not in_timeout:
        screen.blit(error_screen,(0,0))
        pygame.display.flip()
        pygame.display.update()
        in_timeout = True


def fetch_variable(variable_name, player="game", scope=VariableScope.game):
    try:
        data = client.fetch_variable(variable_name,player=player, scope=scope)
        in_timeout = False
        return data
    except TimeoutError:
        network_timeout()


def issue_command(command, player="game"):
    try:
        client.issue_command(command, player=player)
    except TimeoutError:
        network_timeout()


IMAGE_RESOLUTION = (600, 600)
# pygame initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(IMAGE_RESOLUTION)
error_screen = pygame.image.load("images/contacting-server.gif")
# cache initialization
sound_cache = PygameSoundCache.get_sound_cache()
image_cache = PygameImageCache.get_image_cache()
NEXT_SCREEN = USEREVENT + 1
# define the keys for picks
picks = [pygame.K_LEFT, pygame.K_RIGHT]
# token that is set in hivemechanic that links to correct activity
token = "soundhello"
url = 'https://dev.hivemechanic.org/http/'
net_timeout = 4
in_timeout = False
client = HiveClient(api_url=url, token=token, timeout=net_timeout)
reset()
start_screen = "start"
current_screen = "start"
playing_sound = None
preload = fetch_variable("preload", scope=VariableScope.game)
timeout = 3600000
# preload takes a variable on hive mechanic and downloads all the files
if preload:
    for load in preload:
        url_type = HiveCache.get_type(load)
        if url_type == 'audio':
            # val = sound_cache.get_value(load)
            pass
        elif url_type == 'image':
            # val = image_cache.get_value(load)
            pass


choices = []
pygame.time.set_timer(NEXT_SCREEN, 1000, True)
# pause is there to flag when keypress need to be ignored, like during screen transitions
pause = True
last_press = 0
timer = 0
clock = pygame.time.Clock()
while True:

    # reset from server
    if reset == "1":
        reset()
    tick = clock.tick()
    timer += tick
    for event in pygame.event.get():
        if event.type == NEXT_SCREEN:
            sound = fetch_variable("sound", player="game", scope=VariableScope.game)
            image = fetch_variable("image", player="game", scope=VariableScope.game)
            if sound == '""':
                sound = None
            if image == '""':
                image = None
            c = fetch_variable("choices", player="game", scope=VariableScope.game)
            if c:
                choices = json.loads(c)
            else:
                choices = []
                error = True
            reset = client.fetch_variable("reset", player="game", scope=VariableScope.game)
            # retrieve sound and play if there
            if sound:
                if playing_sound:
                    sound_cache.stop(playing_sound)
                playing_sound = sound
                sound_cache.play(sound)
            # retrieve image and show on screen if there
            if image:
                current_image = image_cache.get_image(image)
                if current_image:
                    screen.blit(current_image, (0, 0))
                    pygame.display.flip()
                    pygame.display.update()
            else:
                pygame.display.flip()
                pygame.display.update()
            pause = False

        if event.type == pygame.KEYUP:
            last_press = timer
            # quit game
            if event.key == "q":
                reset()
                cleanup(sound_cache)
                break
            if event.key == pygame.K_d:
                issue_command(GotoCommand("start"), player="game")
                current_screen = "start"
                pygame.time.set_timer(NEXT_SCREEN, 500, True)
            # look to see if the button pressed was the first, second or third option
            if event.key in picks and not pause:
                index = picks.index(event.key)
                choice = choices[index]
                current_screen = choice
                issue_command(GotoCommand(choice), player="game")
                pygame.time.set_timer(NEXT_SCREEN, 500, True)
                pause = True

        diff = timer - last_press
        if diff > timeout:
            issue_command(GotoCommand("timeout_start"))
            pygame.time.set_timer(NEXT_SCREEN, 500, True)

