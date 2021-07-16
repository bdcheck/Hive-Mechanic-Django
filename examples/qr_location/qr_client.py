import qrcode
import pygame
from pygame.locals import *
from hive_client import HiveClient,VariableScope

#qrcode generates an array this turns it into a png
#https://stackoverflow.com/questions/25202092/pil-and-pygame-image
def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

#retrieves the variables next_lat and next_lng from the server  and generates the qrcode
def get_new_image():
    lat = client.fetch_variable("next_lat", VariableScope.game)
    lng = client.fetch_variable("next_lng", VariableScope.game)
    geo = "geo:" + str(lat) + "," + str(lng)
    qr = qrcode.QRCode()
    qr.add_data(geo)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    pg_image = pilImageToSurface(img.convert("RGB"))
    return pg_image

token = "yelphello"
url = 'https://dev.hivemechanic.org/http/'
client = HiveClient(api_url=url,token=token)
#event tag
GET_IMAGE = USEREVENT + 1

pygame.init()
screen = pygame.display.set_mode((360,360))
pg_image = get_new_image()

#converts generated image to pygame surface
#have to convert qr code which is 1 bit to rgb since pygame doesnt understand 1 bit images
quit_g = False
pygame.time.set_timer(GET_IMAGE, 10000)

#pygame loop
while not quit_g:
    #quit
    for event in pygame.event.get():
        if event.type == QUIT or event.type == KEYUP and event.key == pygame.K_q:
            pygame.quit()
            quit_g = True
            break
        #getimage
        elif event.type == GET_IMAGE:
            pg_image = get_new_image()

    screen.blit(pg_image, (0,0))
    pygame.display.flip()
    pygame.display.update()


