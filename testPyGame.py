import pygame

pygame.init()

screenWidth = 1000
screenHeight = 1000

win = pygame.display.set_mode((screenWidth,screenHeight))

pygame.display.set_caption('donuts')
x = 50
y = 50
height = 60
width = 40
vel = 5

run = True

while run:
    pygame.time.delay(10)

    for event in pygame.event.get():
        if event == pygame.QUIT:
            run = False

    key = pygame.key.get_pressed()

    if key[pygame.K_ESCAPE]:
        run = False
    if key[pygame.K_RIGHT] and x < screenWidth - width:
        x += vel
    if key[pygame.K_LEFT] and x > 0:
        x -= vel
    if key[pygame.K_UP] and y > 0:
        y -= vel
    if key[pygame.K_DOWN] and y < screenHeight - height:
        y += vel

    win.fill((0,0,0))

    pygame.draw.rect(win, (255, 0, 0), (x, y, width, height))
    pygame.display.update()

pygame.quit()

