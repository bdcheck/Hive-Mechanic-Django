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


IMAGE_RESOLUTION = (600,600)
#pygame initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(IMAGE_RESOLUTION)

#cache imitialization
sound_cache = PygameSoundCache.get_sound_cache()
image_cache = PygameImageCache.get_image_cache()
NEXT_SCREEN =  USEREVENT + 1
#define the keys for picks
picks = [pygame.K_a, pygame.K_l, pygame.K_SPACE]
#token that is set in hivemechanic that links to correct activity
token = "soundhello" # nosec
url = 'http://localhost:8000/http/'
client = HiveClient(api_url=url,token=token)
playing_sound = None
preload = client.fetch_variable("preload",VariableScope.game)

#preload takes a variable on hive mechanic and downloads all the files
if preload:
    for l in preload:
        url_type = HiveCache.get_type(l)
        if url_type == 'audio':
            #val = sound_cache.get_value(l)
            pass
        elif url_type == 'image':
            #val = image_cache.get_value(l)
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
            image = client.fetch_variable("image", player="game",scope=VariableScope.game)
            c = client.fetch_variable("choices", player="game", scope=VariableScope.game)
            if c:
                choices = json.loads(c)
            else:
                choices = []
                error = True
            sound = None
            reset = client.fetch_variable("reset", player="game", scope=VariableScope.game)
            #retrieve sound and play if there
            if sound:
                if playing_sound:
                    sound_cache.stop(playing_sound)
                playing_sound = sound
                sound_cache.play(sound)
            #retrieve image and show on screen if there
            if image:
                current_image = image_cache.get_image(image)
                if current_image:
                    screen.blit(current_image,(0,0))
                    pygame.display.flip()
                    pygame.display.update()


            else:
                error = True

        if event.type == pygame.KEYUP:
            # quit game
            if event.key == "q":
                reset()
                cleanup(sound_cache)
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




