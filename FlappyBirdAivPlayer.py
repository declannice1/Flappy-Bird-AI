import pygame
from sys import exit
import random
import math
import json
import os

#game variables
HALL_OF_FAME = True #if true, will set best bird to json file, and use json file as starting bird.
#also sets first generation of birds as mutations of the best bird
MUTATION_RATE = 0 #is the +- percent that the birds change from the top_20 birds
GAME_WIDTH = 360
GAME_HEIGHT = 640

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
#screen setup

#bird class
birds = []
deadbirds = []
bird_x = GAME_WIDTH/8
bird_y = GAME_HEIGHT/2
bird_width = 34
bird_height = 24
score = 0

#scaled down size of bird img
class AiBird(pygame.Rect):
    def __init__(self, img, y, v, p1, p2, px, snd_p1, snd_p2, snd_px):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img
        self.velo = 0
        self.alive = True
        self.score = 0
        self.game_score = 0
        self.y_mut = y
        self.velo_mut = v
        self.pipe1_mut = p1
        self.pipe2_mut = p2
        self.pipex_mut = px
        self.snd_pipe1_mut = snd_p1
        self.snd_pipe2_mut = snd_p2
        self.snd_pipex_mut = snd_px
        #sets up all bird vars and also vars for ai

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img
        self.velo = 0
        self.alive = True
        #player bird vars

#pipe class
pipe_x = GAME_WIDTH #start off screen
pipe_y = 0
pipe_width = 64
pipe_height = 512

class Pipe(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.passed = False #has bird passed the pipe

#moving floor, using 2 floor objects
floor_x1 = 0
floor_x2 = 360

#game images
background_image = pygame.image.load("flappybirdbg1.png")
floor_image = pygame.image.load("flappybirdbg.png")
birdai_image = pygame.image.load("flappybirdai.png")
birdai_image = pygame.transform.scale(birdai_image, (bird_width, bird_height))

godbirdai_image = pygame.image.load("flappybird_god.png")
godbirdai_image = pygame.transform.scale(godbirdai_image, (bird_width, bird_height))
#god bird is a white bird, and is the best bird of the previous generation

#birdai_image.set_alpha(100)
#godbirdai_image.set_alpha(100)  # 0 = fully transparent, 255 = fully opaque
#optional transparency for ais

bird_image = pygame.image.load("flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
top_pipe_image = pygame.image.load("toppipe.png")
bottom_pipe_image = pygame.image.load("bottompipe.png")
top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))

#sets up the best_bird, which pulls from json file
seed_bird = None
best_score_ever = 0
best_game_score_ever = 0
if os.path.exists("best_bird.json"):
    with open("best_bird.json") as f:
        seed_bird = json.load(f)
if seed_bird is not None:
    best_score_ever = seed_bird["s"]
    best_game_score_ever = seed_bird["gs"]
best_bird_data = None

#game vars
player = None
gen_num = 0
death = False
pipes = []
top_20 = []
pipe_velo = -3 #speed of pipes moving to left

def draw():
    window.blit(background_image, (0, 0))

    for bird in birds:
        window.blit(bird.img, bird) #ai birds
    
    if len(birds) > 0:
        window.blit(birds[0].img, birds[0]) #draw god bird on top of ai birds

    if player != None:
        window.blit(player.img, player) # makes sure player is on top of all other birds

    for pipe in pipes:
        window.blit(pipe.img, pipe)

    window.blit(floor_image, (floor_x1, 95))
    window.blit(floor_image, (floor_x2, 95)) #floor goes over everything

    text_str = str(int(score)) #score is a float because + 0.5
    text_font = pygame.font.SysFont("Comic Sans MS", 40)
    text_render = text_font.render(text_str, True, "black")
    window.blit(text_render, (5, -5))

    text_font = pygame.font.SysFont("Comic Sans MS", 15)
    text_str = "AI highscore: " + str(int(best_game_score_ever))
    text_render = text_font.render(text_str, True, "black")
    window.blit(text_render, (5, 50))

    text_font = pygame.font.SysFont("Comic Sans MS", 25)
    text_str = "Generation: " + str(gen_num)
    text_render = text_font.render(text_str, True, "black")
    window.blit(text_render, (190, 0))

    text_str = "# Birds: " + str(len(birds))
    text_render = text_font.render(text_str, True, "black")
    window.blit(text_render, (190, 30))

def move():
    global score, game_over, floor_x1, floor_x2

    for bird in birds:
        bird.velo += 0.4 #apply gravity to ai birds
        bird.y += bird.velo

    if player != None:
        if not player.alive:
            player.x += pipe_velo #this makes player bird slide with level when dead
        else:
            player.velo += 0.4
            player.y += player.velo # apply gravity to player
            if (player.y < 0):
                player.y = 0
                player.velo = 0 #player cannot go above screen
            if (player.y > 552):
                player.y = 552 # player cannot hit ground
                player.alive = False

    for i in range (len(birds) - 1, -1, - 1): #iterate backwards because removing from birds list
        if (birds[i].y < 0):
            birds[i].y = 0
            birds[i].velo = 0 #ai cannot go above screen
        if (birds[i].y > 552):
            birds[i].alive = False
            deadbirds.append(birds[i]) #ai cannot hit ground
            birds.pop(i)

    for pipe in pipes:
        pipe.x += pipe_velo # move pipes left

        for i in range (len(birds) - 1, -1, -1):
            if not pipe.passed and birds[i].x > pipe.x + pipe.width:
                pipe.passed = True
                score += 0.5 #since each set of pipes is 2
                birds[i].game_score += 0.5

            if birds[i].colliderect(pipe): #checking ai collision with pipes
                birds[i].alive = False
                deadbirds.append(birds[i])
                birds.pop(i)

        if len(birds) == 0 and player.alive:
            if not pipe.passed and player.x > pipe.x + pipe.width:
                pipe.passed = True
                score += 0.5 #since each set of pipes is 2
                
        if player != None:
            if player.colliderect(pipe): #checking player collision with pipes
                player.alive = False

    #move floor
    floor_x1 += pipe_velo
    floor_x2 += pipe_velo
    if floor_x1 <= -360:
        floor_x1 = floor_x2 + 360
    if floor_x2 <= -360:
        floor_x2 = floor_x1 + 360


    while (len(pipes) > 0 and pipes[0].x + pipe_width < 0):
        pipes.pop(0)
    #pipe cleanup, if pipe is offscreen pop it

def create_pipes():
    global top_20, death, player, best_score_ever, best_bird_data, best_game_score_ever

    if death:
        pipes.clear()

    random_pipe_y = random.randint(-450, -150)
    pipe_gap = GAME_HEIGHT/5

    top_pipe = Pipe(top_pipe_image)
    top_pipe.y = random_pipe_y
    bottom_pipe = Pipe(bottom_pipe_image)

    bottom_pipe.y = top_pipe.y + top_pipe.height + pipe_gap

    pipes.append(top_pipe)
    pipes.append(bottom_pipe)

    if death:
        # elitism: carry forward the top performer completely unchanged
        for i in range(min(1, len(top_20))):
            elite = top_20[i]
            birds.append(AiBird(godbirdai_image, elite.y_mut, elite.velo_mut,
                                elite.pipe1_mut, elite.pipe2_mut, elite.pipex_mut,
                                elite.snd_pipe1_mut, elite.snd_pipe2_mut, elite.snd_pipex_mut))

        #if the best bird made it furthest, rewrite it as new best bird in json file
        if len(top_20) > 0 and top_20[0].score > best_score_ever:
            best_score_ever = top_20[0].score
            best_game_score_ever = top_20[0].game_score
            b = top_20[0]
            best_bird_data = {"gs": int(b.game_score), "s": b.score, "y": b.y_mut, "v": b.velo_mut,
                               "p1": b.pipe1_mut, "p2": b.pipe2_mut, "px": b.pipex_mut,
                               "sndp1": b.snd_pipe1_mut, "sndp2": b.snd_pipe2_mut, "sndpx": b.snd_pipex_mut}
            with open("best_bird.json", "w") as f:
                json.dump(best_bird_data, f, indent=2)
            print(f"New best! Score {best_score_ever} saved.")

        for _ in range(1):
            if HALL_OF_FAME:
                if len(top_20) != 0:
                    rand_bird1 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird2 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird3 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird4 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird5 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_y = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_v = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    #picks random birds, and random percentages using the mutation rate %, and adds a bird using stats from 5 random birds
                    birds.append(AiBird(birdai_image,
                                        rand_bird1.y_mut + rand_bird1.y_mut*rand_y,
                                        rand_bird2.velo_mut + rand_bird2.velo_mut*rand_v,
                                        rand_bird3.pipe1_mut + rand_bird3.pipe1_mut*rand_p1,
                                        rand_bird4.pipe2_mut + rand_bird4.pipe2_mut*rand_p2,
                                        rand_bird5.pipex_mut + rand_bird5.pipex_mut*rand_px,
                                        rand_bird5.snd_pipe1_mut + rand_bird5.snd_pipe1_mut*rand_snd_p1,
                                        rand_bird5.snd_pipe2_mut + rand_bird5.snd_pipe2_mut*rand_snd_p2,
                                        rand_bird5.snd_pipex_mut + rand_bird5.snd_pipex_mut*rand_snd_px))
                    
                else: #this would be if it is first generation, we will make all birds variants of the json bird
                    seed_bird = None
                    if os.path.exists("best_bird.json"):
                        with open("best_bird.json") as f:
                            seed_bird = json.load(f)
                        print(f"Loaded seed bird: {seed_bird}")
                    if seed_bird is not None:
                        rand_y = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_v = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_snd_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_snd_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        rand_snd_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                        #picks random percentages using the mutation rate % from the seed bird and adds a new bird
                        birds.append(AiBird(birdai_image,
                                            seed_bird["y"] + seed_bird["y"]*rand_y,
                                            seed_bird["v"] + seed_bird["v"]*rand_v,
                                            seed_bird["p1"] + seed_bird["p1"]*rand_p1,
                                            seed_bird["p2"] + seed_bird["p2"]*rand_p2,
                                            seed_bird["px"] + seed_bird["px"]*rand_px,
                                            seed_bird["sndp1"] + seed_bird["sndp1"]*rand_snd_p1,
                                            seed_bird["sndp2"] + seed_bird["sndp2"]*rand_snd_p2,
                                            seed_bird["sndpx"] + seed_bird["sndpx"]*rand_snd_px))
                    else: #if there is no seed bird, just use random vals for first generation
                        birds.append(AiBird(birdai_image, random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                                            random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                                            random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)))
            else:
                if len(top_20) != 0:
                    rand_bird1 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird2 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird3 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird4 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_bird5 = top_20[random.randint(0, len(top_20) - 1)]
                    rand_y = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_v = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_p1 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_p2 = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    rand_snd_px = (random.random() * (2*MUTATION_RATE) - MUTATION_RATE)/100.0
                    #picks random birds, and random percentages using the mutation rate %, and adds a bird using stats from 5 random birds
                    birds.append(AiBird(birdai_image,
                                        rand_bird1.y_mut + rand_bird1.y_mut*rand_y,
                                        rand_bird2.velo_mut + rand_bird2.velo_mut*rand_v,
                                        rand_bird3.pipe1_mut + rand_bird3.pipe1_mut*rand_p1,
                                        rand_bird4.pipe2_mut + rand_bird4.pipe2_mut*rand_p2,
                                        rand_bird5.pipex_mut + rand_bird5.pipex_mut*rand_px,
                                        rand_bird5.snd_pipe1_mut + rand_bird5.snd_pipe1_mut*rand_snd_p1,
                                        rand_bird5.snd_pipe2_mut + rand_bird5.snd_pipe2_mut*rand_snd_p2,
                                        rand_bird5.snd_pipex_mut + rand_bird5.snd_pipex_mut*rand_snd_px))
                else: #if first generation, use random values
                    birds.append(AiBird(birdai_image, random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                                        random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                                        random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)))
        player = Bird(bird_image)
        death = False
        #automatically resets if everything is dead

def activation(bird, y, velo, i, i2, sndi, sndi2):
    #all variables are normalized, as to try to get between -1 and 1.
    #this makes var generation easier
    norm_y = (y / GAME_HEIGHT) * 2 - 1 
    norm_velo = velo / 10                        
    norm_pipe1 = (i.y / GAME_HEIGHT) * 2 - 1
    norm_pipe2 = (i2.y / GAME_HEIGHT) * 2 - 1
    norm_pipex = (i.x / GAME_WIDTH) * 2 - 1
    norm_snd_pipe1 = 0
    norm_snd_pipe2 = 0
    norm_snd_pipex = 0
    if sndi != None: #if there is a second pipe, we can set this. sometimes there is only 1 pipe on screen, so otherwise vars are 0
        norm_snd_pipe1 = (sndi.y / GAME_HEIGHT) * 2 - 1
        norm_snd_pipe2 = (sndi2.y / GAME_HEIGHT) * 2 - 1
        norm_snd_pipex = (sndi.x / GAME_WIDTH) * 2 - 1

    x = (bird.y_mut * norm_y + bird.velo_mut * norm_velo +
         bird.pipe1_mut * norm_pipe1 + bird.pipe2_mut * norm_pipe2 + bird.pipex_mut * norm_pipex +
         bird.snd_pipe1_mut * norm_snd_pipe1 + bird.snd_pipe2_mut * norm_snd_pipe2 + bird.snd_pipex_mut * norm_snd_pipex)
    #uses normalized values to prevent large values inflating the equation
    return (2*math.atan(x))/math.pi
    #this will always return between -1 and 1

clock = pygame.time.Clock()
create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, 1170)
#will create pipe ever ~1.17 second

while True: #main game loop

    closest_x = 1000
    closest_i = 0
    closest_i2 = 0
    snd_closest_i = None
    snd_closest_i2 = None
    #these statements will find the closest pipe, and second closest pipe if there is a second pipe
    if (len(birds) != 0 and len(pipes) != 0):
        for i in range (0, len(pipes)):
            if pipes[i].x + pipe_width >= birds[0].x:  # only pipes not yet passed
                if abs(pipes[i].x - birds[0].x) < closest_x:
                    closest_x = pipes[i].x
                    closest_i = i

    if closest_i % 2 == 0: #makes sure we dont have out of bounds error
        closest_i2 = closest_i + 1
    else:
        closest_i2 = closest_i - 1

    if (len(pipes) > max(closest_i, closest_i2) + 1): #if second pipe exists
        snd_closest_i = closest_i + 2
        snd_closest_i2 = closest_i2 + 2

    for bird in birds:
        bird.score += 1
        x = 0
        if len(pipes) != 0:
            if snd_closest_i == None:
                x = activation(bird, bird.y, bird.velo, pipes[closest_i], pipes[closest_i2], None, None)
            else:
                x = activation(bird, bird.y, bird.velo, pipes[closest_i], pipes[closest_i2], pipes[snd_closest_i], pipes[snd_closest_i2])
        else:
            x = 0
        if x >= 0.5: #makes sure ai is confident jumping is correct to actually jump
            bird.velo = -7
        
    for event in pygame.event.get(): #allows us to quit program
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer:
            create_pipes()

        if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if player != None:
                        player.velo = -7 #player jump

                if event.key == pygame.K_p: #kills all birds.
                    if len(birds) != 0:
                        deadbirds.extend(birds)
                        birds.clear()
                        deadbirds.sort(key=lambda b: b.score, reverse=True)
                        top_20 = deadbirds[:20]
                        deadbirds.clear()
                        score = 0
                        gen_num += 1
                        death = True
                        if player != None:
                            player.alive = False
                        #manually force a generation change without closing the program

    if player == None:
        if (len(birds) == 0 and not death):
            deadbirds.sort(key=lambda b: b.score, reverse = True)
            top_20 = deadbirds[:20]
            deadbirds.clear()
            score = 0
            gen_num += 1
            death = True
    else:
        if (len(birds) == 0 and not death and not player.alive):
            deadbirds.sort(key=lambda b: b.score, reverse=True)
            top_20 = deadbirds[:20]
            deadbirds.clear()
            score = 0
            gen_num += 1
            death = True
    #if all birds(ai and player) are dead, create top 20 birds, and start a new generation

    move()
    draw()
    pygame.display.update()
    clock.tick(60)