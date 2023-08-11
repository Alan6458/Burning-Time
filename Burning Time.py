import pygame, random, math
pygame.init()

clock = pygame.time.Clock()
size = width, height = 600, 1000
running = True
px, py = 300, 960
vX, vY = 0, 0
grav = 0
aX, aY = 0, 0
vA = 0
pAngle = 0
timePos, fuelPos = [], []
time = pygame.transform.scale(pygame.image.load("data/time.png"), (36, 36))
gas = pygame.transform.scale(pygame.image.load("data/fuel.png"), (36, 36))
tMask, gMask = pygame.mask.from_surface(time), pygame.mask.from_surface(gas)
aDown, dDown, spaceDown = False, False, False
player = pygame.transform.scale(pygame.image.load("data/char.png"), (80, 80))
background = pygame.transform.scale(pygame.image.load("data/background.png"), (600, 1000))
flame = [pygame.transform.scale(pygame.image.load("data/" + str(i) + ".png"), (24, 72)) for i in range(1, 7)]
bar = pygame.transform.scale(pygame.image.load("data/bar.png"), (176, 32))
font = pygame.font.Font("data/prstart.ttf", 20)
fontBig = pygame.font.Font("data/prstart.ttf", 40)
pygame.display.set_icon(time)
pygame.display.set_caption("Burning Time")
dt = clock.tick_busy_loop()/1000
score = 0
fuel = 10
throttle = 0
timeLeft = 20
gameStarted = False
with open("data/Scores.txt") as file:
    scores = file.readlines()
    scores = [int(s.rstrip()) for s in scores]
while len(scores) < 1:
    scores.append(0)

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

screen = pygame.display.set_mode(size)

while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                aDown = True
            if event.key == pygame.K_d:
                dDown = True
            if event.key == pygame.K_SPACE:
                spaceDown = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                aDown = False
            if event.key == pygame.K_d:
                dDown = False
            if event.key == pygame.K_SPACE:
                spaceDown = False
    
    if gameStarted == False:
        if spaceDown == True:
            gameStarted = True
        screen.blit(player, (260, 920))
        screen.blit(time, (7, 918))
        screen.blit(gas, (7, 958))
        pygame.draw.rect(screen, (255-(timeLeft/20)*255, (timeLeft/20)*255, 0), (58, 928, 160*(timeLeft/20), 16))
        screen.blit(bar, (50, 920))
        pygame.draw.rect(screen, (255-(fuel/10)*255, (fuel/10)*255, 0), (58, 968, 160*(fuel/10), 16))
        screen.blit(bar, (50, 960))
        screen.blit(fontBig.render("Press SPACE", True, (0, 0, 0)), fontBig.render("Press SPACE", True, (0, 0, 0)).get_rect(center=(300, 400)))
        screen.blit(fontBig.render("To Start", True, (0, 0, 0)), fontBig.render("To Start", True, (0, 0, 0)).get_rect(center=(300, 450)))
        screen.blit(font.render("A and D To Turn", True, (0, 0, 0), None), font.render("A and D To Turn", True, (0, 0, 0), None).get_rect(center=(300, 500)))
        screen.blit(font.render("High Score: " + str(scores[0]), True, (0, 0, 0), None), (10, 10))
        pygame.display.flip()
        dt = clock.tick_busy_loop()/1000
        continue

    if timeLeft == 0:
        scores.append(math.floor(score*10))
        scores = sorted(scores, reverse=True)
        gameStarted = False
        px, py = 300, 960
        vX, vY = 0, 0
        grav = 0
        aX, aY = 0, 0
        vA = 0
        pAngle = 0
        timePos, fuelPos = [], []
        score = 0
        fuel = 10
        throttle = 0
        timeLeft = 20
        spaceDown = False
        pygame.mixer.music.load("data/gameEnd.wav")
        pygame.mixer.music.play()
        continue

    while len(timePos) < 1:
        timePos.append([random.randint(20, 562), random.randint(200, 782)])
    while len(fuelPos) < 5:
        fuelPos.append([random.randint(20, 562), random.randint(200, 782)])
    
    score += dt

    if fuel:
        if spaceDown:
            # 1 second to full throttle
            throttle = min(throttle+ dt/0.2, 1)
        else:
            throttle = max(throttle - dt/0.1, 0)
    else:
        throttle = 0
    
    vA = 0
    if aDown:
        vA -= 180
    if dDown:
        vA += 180
    pAngle += vA * dt
    pAngle %= 360

    grav = math.cos(score/5)*0.2

    if throttle and fuel >= throttle*dt:
        # Actually throttle x 1 second (30 seconds of fuel total) x dt
        fuel -= throttle*dt
    elif fuel < throttle*dt:
        throttle = 0
    
    # 40 pixels/meter
    aX = ((throttle*600) * math.sin(math.radians(pAngle)))/(1000+fuel*100)
    vX += aX * dt * 40
    px += vX
    aY = ((throttle*600) * math.cos(math.radians(pAngle)) - (1000+fuel*100)*grav)/(1000+fuel*100)
    vY += aY * dt * 40
    py -= vY

    if py >= 960:
        py = 960
        vX = 0
        if aY > 0:
            vY = 0
    elif py <= 40:
        vX = 0
        py = 40
        if aY < 0:
            vY = 0
    
    if px >= 560:
        px = 560
        if aX > 0:
            vX = 0
    elif px <= 40:
        px = 40
        if aX < 0:
            vX = 0

    pImage = rot_center(player, -pAngle, px, py)
    pMask = pygame.mask.from_surface(pImage[0])

    for i in timePos:
        if pMask.overlap(tMask, (i[0] - pImage[1].x, i[1] - pImage[1].y)):
            timePos.remove(i)
            timeLeft += 4
            pygame.mixer.music.load("data/pickup.wav")
            pygame.mixer.music.play(2)
        else:
            screen.blit(time, (i[0], i[1]))
    for i in fuelPos:
        if pMask.overlap(gMask, (i[0] - pImage[1].x, i[1] - pImage[1].y)):
            fuelPos.remove(i)
            fuel += 1
            pygame.mixer.music.load("data/pickup.wav")
            pygame.mixer.music.play()
        else:
            screen.blit(gas, (i[0], i[1]))
    
    timeLeft = min(max(timeLeft-dt, 0), 20)
    fuel = min(max(fuel, 0), 10)
    
    fImage = rot_center(random.choice(flame), -pAngle, px+throttle*72*math.sin(math.radians(-pAngle)), py+math.cos(math.radians(-pAngle))*72*throttle)
    screen.blit(fImage[0], fImage[1])
    screen.blit(pImage[0], pImage[1])
    screen.blit(time, (7, 918))
    screen.blit(gas, (7, 958))
    pygame.draw.rect(screen, (255-(timeLeft/20)*255, (timeLeft/20)*255, 0), (58, 928, 160*(timeLeft/20), 16))
    screen.blit(bar, (50, 920))
    pygame.draw.rect(screen, (255-(fuel/10)*255, (fuel/10)*255, 0), (58, 968, 160*(fuel/10), 16))
    screen.blit(bar, (50, 960))
    screen.blit(font.render("Score: " + str(math.floor(score*10)), True, (0, 0, 0), None), (10, 10))

    pygame.display.flip()

    dt = clock.tick_busy_loop()/1000
scores.append(math.floor(score*10))
scores = sorted(scores, reverse=True)
with open('data/Scores.txt', 'w') as sc:
    sc.write(str(max(scores)))
pygame.quit()