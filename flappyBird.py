import pygame
import neat
import time
import os
import random
pygame.font.init()

windowWidth = 500
windowHeight = 800

generation = 0

birdImages = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
pipeImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
groundImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
backgroundImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

statFont = pygame.font.SysFont("comicsans", 50)


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

    def draw(self, window):
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
        window.blit(rotatedImage, newRectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    gap = 200
    velocity = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeImage, False, True)
        self.pipeBottom = pipeImage

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipeTop.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.velocity

    def draw(self, window):
        window.blit(self.pipeTop, (self.x, self.top))
        window.blit(self.pipeBottom, (self.x, self.bottom))

    def collid(self, bird):
        birdMask = bird.get_mask()
        topMask = pygame.mask.from_surface(self.pipeTop)
        bottomMask = pygame.mask.from_surface(self.pipeBottom)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        bottomPoint = birdMask.overlap(bottomMask, bottomOffset)
        topPoint = birdMask.overlap(topMask, topOffset)

        if bottomPoint or topPoint:
            return True
        return False


class Ground:
    velocity = 5
    width = groundImage.get_width()
    image = groundImage

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.velocity
        self.x2 -= self.velocity

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, window):
        window.blit(self.image, (self.x1, self.y))
        window.blit(self.image, (self.x2, self.y))



def draw_window(window, birds, pipes, ground, score, generation, numberOfBirds):
    window.blit(backgroundImage, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = statFont.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (windowWidth - 10 - text.get_width(), 10))

    text = statFont.render("Generation: " + str(generation), 1, (255, 255, 255))
    window.blit(text, (10, 10))

    text = statFont.render("Number of Birds: " + str(numberOfBirds), 1, (255, 255, 255))
    window.blit(text, (10, 50))

    ground.draw(window)

    for bird in birds:
        bird.draw(window)

    pygame.display.update()


def main(genomes, config):
    global generation
    generation += 1
    numberOfBirds = 15

    nets = []
    ge = []
    birds = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    ground = Ground(730)
    pipes = [Pipe(600)]
    window = pygame.display.set_mode((windowWidth, windowHeight))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].bottom)))

            if output[0] > 0.5:
                bird.jump()

        addPipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collid(bird):
                    ge[x].fitness -= 1
                    birds.pop()
                    nets.pop()
                    ge.pop()
                    numberOfBirds -= 1

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.pipeTop.get_width() < 0:
                remove.append(pipe)

            pipe.move()

        if addPipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(600))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                numberOfBirds -= 1

        ground.move()
        draw_window(window, birds, pipes, ground, score, generation, numberOfBirds)


def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    configPath = os.path.join(local_dir, 'config-feedforward.txt')
    run(configPath)

