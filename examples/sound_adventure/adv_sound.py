import pygame
from pygame.locals import *
from hive_client import HiveClient,VariableScope, GotoCommand, TriggerInterruptCommand
from HiveCache import HiveCache, PygameSoundCache, PygameImageCache
import json

def cleanup(cache:HiveCache):
    cache.clear()

def reset():
    global client
    client.issue_command(GotoCommand("beginning"),player="game")


pygame.init()
pygame.mixer.init()

soundcache = PygameSoundCache.get_sound_cache()
imagecache = PygameImageCache.get_image_cache()
NEXT_SCREEN =  USEREVENT + 1
picks = [pygame.K_a, pygame.K_l, pygame.K_SPACE]
token = "soundhello"
url = 'http://localhost:8000/http/'
client = HiveClient(api_url=url,token=token)
playing_sound = None
preload = client.fetch_variable("preload",VariableScope.game)

if preload:
    for l in preload:
        #val = soundcache.get_value(l)
        pass

choices = []
client.issue_command(GotoCommand("v1"),player="game")
pygame.time.set_timer(NEXT_SCREEN,1000,True)

while True:
    # reset from server
    if reset == "1":
        reset()

    for event in pygame.event.get():
        if event.type == NEXT_SCREEN:
            #sound = client.fetch_variable("play_sound", player="game", scope=VariableScope.game)
            c = client.fetch_variable("choices", player="game", scope=VariableScope.game)
            if c:
                choices = json.loads(c)
            else:
                choices = []
                error = True
            sound = None
            reset = client.fetch_variable("reset", player="game", scope=VariableScope.game)
            if sound:
                if playing_sound:
                    soundcache.stop(playing_sound)
                playing_sound = sound
                soundcache.play(sound)

            else:
                error = True

        if event.type == pygame.KEYUP:
            # quit game
            if event.key == "q":
                reset()
                cleanup(soundcache)
                break
            if event.key == pygame.K_d:
                client.issue_command(GotoCommand("v1"), player="game")
                pygame.time.set_timer(NEXT_SCREEN, 1000, True)
            # look to see if the button pressed was the first, second or third option
            for i,k in enumerate(picks):
                if event.key == k:
                    choice = choices[i]
                    client.issue_command(GotoCommand(choice),player="game")
                    pygame.time.set_timer(NEXT_SCREEN,100,True)




