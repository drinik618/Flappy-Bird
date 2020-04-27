import pygame
import neat
import time
import os
import random

windowWidth = 500
windowHeight = 800

birdImages = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
pipeImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
groundImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
backgroundImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    images = birdImages
    maxRotation = 25
    roationVelocity = 20
    animationTime = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.velocity = 0
        self.height = self.y
        self.imageCount = 0
        self.image = self.images[0]

    def jump(self):
        self.velocity = -10.5
        self.tickCount = 0
        self.height = self.y

    def move(self):
        self.tickCount += 1

        displacment = self.velocity * self.tickCount + 1.5 * self.tickCount ** 2

        if displacment >= 16:
            displacment = 16

        if displacment < 0:
            displacment -= 2

        self.y = self.y + displacment

        if displacment < 0 or self.y < self.height + 50:
            if self.tilt < self.maxRotation:
                self.tilt = self.maxRotation
        else:
            if self.tilt > -90:
                self.tilt -= self.roationVelocity

    def draw(self, win):
        self.imageCount += 1

        if self.imageCount < self.animationTime:
            self.image = self.images[0]
        elif self.imageCount < self.animationTime * 2:
            self.image = self.images[1]
        elif self.imageCount < self.animationTime * 3:
            self.image = self.images[2]
        elif self.imageCount < self.animationTime * 4:
            self.image = self.images[1]
        elif self.imageCount < self.animationTime * 4 + 1:
            self.image = self.images[0]
            self.imageCount = 0

        if self.tilt <= -80:
            self.image = self.images[1]
            self.imageCount = self.animationTime * 2

        rotatedImage = pygame.transform.rotate(self.image, self.tilt)
        newRectangle = rotatedImage.get_rect(center=self.image.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotatedImage, newRectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

def draw_window(window, bird):
    window.blit(backgroundImage, (0, 0))
    bird.draw(window)
    pygame.display.update()

def main():
    bird = Bird(200, 200)
    window = pygame.display.set_mode((windowWidth, windowHeight))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()
        draw_window(window, bird)

    pygame.quit()
    quit()

main()
