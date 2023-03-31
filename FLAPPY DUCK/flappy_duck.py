# "FLAPPY DUCK" made with python 3.10.4

import pygame
import sys
import time
import schedule
from random import randint, choice
from itertools import groupby

# constants
WINDOW_WIDTH = 700 #custom
WINDOW_HEIGHT = 600 #custom
HS_FILE = "highscore.txt" # file with the highest score

#------------------------------------------------------------------------------------#
#-----------------------------------SPRITES------------------------------------------#
#------------------------------------------------------------------------------------#

class Background(pygame.sprite.Sprite): #creating background
    def __init__(self, group, scale_koef): #group = the group which it belongs to, scale_koef is needed to adjust the image size to the window size
        super().__init__(group) #for inheritance

        # image
        bg_image = pygame.image.load('images/background/background.png').convert_alpha()
        self.image = pygame.transform.scale(bg_image, pygame.math.Vector2(bg_image.get_size()) * scale_koef)

        # position
        self.rect = self.image.get_rect(topleft = (0, 0))
        self.position = pygame.math.Vector2(self.rect.topleft) #a vector for moving

    def update(self, dt): #moving
        self.position.x -= 200 * dt #moving to the left 
        if self.rect.centerx <= 0: #bringing the image back if it moves too far to the left
            self.position.x = 0
        self.rect.x = round(self.position.x)


class Grass(pygame.sprite.Sprite): # creating the ground
    def __init__(self, group, scale_koef):
        super().__init__(group)
        self.sprite_type = 'grass' # because the duck needs to be able to collide with it (and the duck can't collide with the background)

        # image
        grass_image = pygame.image.load('images/background/grass.png').convert_alpha()
        self.image = pygame.transform.scale(grass_image, pygame.math.Vector2(grass_image.get_size()) * scale_koef)

        # position
        self.rect = self.image.get_rect(bottomleft = (0, WINDOW_HEIGHT))
        self.position = pygame.math.Vector2(self.rect.topleft) #a vector for moving
    
    def update(self, dt): #moving
        self.position.x -= 250 * dt #moving to the left 
        if self.rect.centerx <= 0: #bringing the image back if it moves too far to the left
            self.position.x = 0
        self.rect.x = round(self.position.x)


class Trees(pygame.sprite.Sprite):
    def __init__(self, group, scale_koef):
        super().__init__(group)
        self.sprite_type = 'tree'

        # image
        self.distance = choice(('far', 'near')) # size depends on it
        
        if self.distance == 'near':
            tree_image = pygame.image.load(f'images/trees/tree1.png').convert_alpha()
            self.image = pygame.transform.scale(tree_image, pygame.math.Vector2(tree_image.get_size()) * scale_koef / 0.8)
            y = WINDOW_HEIGHT
        else:
            tree_image = pygame.image.load(f'images/trees/tree0.png').convert_alpha()
            self.image = pygame.transform.scale(tree_image, pygame.math.Vector2(tree_image.get_size()) * scale_koef * 1.5)
            y = WINDOW_HEIGHT - WINDOW_HEIGHT / 120

        x = WINDOW_WIDTH + randint(40, 100)
        self.rect = self.image.get_rect(bottomleft = (x, y))
        self.position = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        if self.distance == 'far':
            self.position.x -= 300 * dt
        else:
            self.position.x -=250 * dt
        self.rect.x = round(self.position.x)
        if self.rect.right <= -50:
            self.kill() # destroying the trees that left the window


class Rocks(pygame.sprite.Sprite): # adding obstacles (three types of rocks)
    def __init__(self, group, scale_koef):
        super().__init__(group)
        self.sprite_type = 'rock'

        orientation = choice(('upwards', 'downwards')) # two different randomly chosen orientations possible
        rock_type = pygame.image.load(f'images/rocks/rock{choice((0, 1, 2))}.png').convert_alpha() # randomly picking one type of rocks
        self.image = pygame.transform.scale(rock_type, pygame.math.Vector2(rock_type.get_size()) * scale_koef / 1.1) # adjusting the size of the rock
        
        # an upwards oriented rock and a downwards oriented one have to be located in different places on the screen #
        if orientation == 'downwards':
            x = WINDOW_WIDTH + randint(40, 100)
            y = randint(-50, -10)
            self.image = pygame.transform.flip(self.image, False, True) # flipping the image
            self.rect = self.image.get_rect(midtop = (x, y))
        else:
            x = WINDOW_WIDTH + randint(40, 110)
            y = WINDOW_HEIGHT + randint(10, 50)
            self.rect = self.image.get_rect(midbottom = (x, y))

        self.mask = pygame.mask.from_surface(self.image) # a mask that allows the duck to collide with a rock itself, not with the rectangle around it
        self.position = pygame.math.Vector2(self.rect.topleft) # a vector for moving

    def update(self, dt): # moving
        self.position.x -= 400 * dt
        self.rect.x = round(self.position.x)
        if self.rect.right <= -50:
            self.kill() # destroying the rocks that left the window


class Flies(pygame.sprite.Sprite): # adding flies
    def __init__(self, group, scale_koef):
        super().__init__(group)
        self.sprite_type = 'fly'

        # image
        self.choose_image(scale_koef)
        self.image_index = 0
        self.image = self.images[self.image_index]

        # position
        self.rect = self.image.get_rect(midright = (WINDOW_WIDTH + randint(40, 100), WINDOW_HEIGHT / 2 + WINDOW_HEIGHT / 15))
        self.position = pygame.math.Vector2(self.rect.topleft) # a vector for moving
        self.mask = pygame.mask.from_surface(self.image)
    
    def choose_image(self, scale_koef):
        self.images = [] # a list of images
        for i in range(2):
            picture = pygame.image.load(f'images/flies/fly{i}.png').convert_alpha()
            self.images.append(pygame.transform.scale(picture, pygame.math.Vector2(picture.get_size()) * scale_koef / 2.5)) # adjusting the size and adding to the list
    
    def animate(self, dt): # changing images to create a motion effect
        self.image_index += 15 * dt # we want to change it gradually (dt is measured in milliseconds)
        if self.image_index >= len(self.images): # creating a loop
            self.image_index = 0
        self.image = self.images[int(self.image_index)]
    
    def update(self, dt): # moving
        self.position.x -= 490 * dt
        self.animate(dt)
        self.rect.x = round(self.position.x)
        if self.rect.right <= -50:
            self.kill() # destroying the flies that left the window


class Duck(pygame.sprite.Sprite): # creating the duck
    def __init__(self, group, scale_koef):
        super().__init__(group)

        # image
        self.choose_image(scale_koef)
        self.image_index = 0
        self.image = self.images[self.image_index]

        # position
        self.rect = self.image.get_rect(midleft = (WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2)) 
        self.position = pygame.math.Vector2(self.rect.topleft) # a vector for moving
        self.gravity = 600 # how fast the duck can go down
        self.direction = 0 # initial
        self.mask = pygame.mask.from_surface(self.image)

        # sounds
        self.jump_sound = pygame.mixer.Sound('sounds/quack.wav')
        self.jump_sound.set_volume(0.1)

    def choose_image(self, scale_koef):
        self.images = [] # a list of images
        for i in range(2):
            picture = pygame.image.load(f'images/bird/duck{i}.png').convert_alpha()
            self.images.append(pygame.transform.scale(picture, pygame.math.Vector2(picture.get_size()) * scale_koef)) # adjusting the size and adding to the list
    
    def animate(self, dt): # changing images to create a motion effect
        self.image_index += 15 * dt # we want to change it gradually (dt is measured in milliseconds)
        if self.image_index >= len(self.images): # creating a loop
            self.image_index = 0
        self.image = self.images[int(self.image_index)]
    
    def use_gravity(self, dt): # adding something like gravity; it is not a linear function
        self.direction += self.gravity * dt
        self.position.y += self.direction * dt
        self.rect.y = round(self.position.y)

    def jump(self):
        self.direction = -400
        self.jump_sound.play()
    
    def rotate(self): # making the duck turn slightly downwards while falling and slightly upwards while jumping
        duck_rotated = pygame.transform.rotozoom(self.image, -self.direction * 0.05, 1)
        self.image = duck_rotated
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt): # moving
        self.use_gravity(dt)
        self.animate(dt)
        self.rotate()


#------------------------------------------------------------------------------------#
#--------------------------------------MAIN------------------------------------------#
#------------------------------------------------------------------------------------#


class Game:
    def __init__(self):
        
        # settings
        pygame.init()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #the game window
        pygame.display.set_caption('Flappy Duck') #the name
        pygame.display.set_icon(pygame.image.load('images/bird/icon.bmp')) # the icon
        self.clock = pygame.time.Clock() #implementing time
        self.is_active = True #shows if the game is active or not

        # text
        self.font = pygame.font.Font('font/custom_font.ttf', 30)

        # scale koefficient
        self.scale_koef = WINDOW_HEIGHT / (pygame.image.load('images/background/background.png').get_height())

        # sprite settings
        self.all_sprites = pygame.sprite.Group() # all sprites
        self.collision_sprites = pygame.sprite.Group() # only the ones that collide
        Background(self.all_sprites, self.scale_koef)
        schedule.every(4).seconds.do(self.tree_spawn)
        Grass([self.all_sprites, self.collision_sprites], self.scale_koef / 1.3) # belongs to both sprite types
        self.duck = Duck(self.all_sprites, self.scale_koef / 1.7)

        # intro screen (menu)
        menu_image = pygame.image.load('images/bird/duck_stand.png').convert_alpha()
        self.menu_surf = pygame.transform.scale(menu_image, pygame.math.Vector2(menu_image.get_size()) * self.scale_koef / 4)
        self.menu_rect = self.menu_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # score -- just shows for how many seconds a user managed to keep playing
        self.score = 0
        self.start_time = 0
        self.load_data()

        # timer for rocks
        self.timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer, 1200) # how often rocks appear - now it's once per 1200 milliseconds

        # timer for flies
        self.timer_flies = pygame.USEREVENT + 2
        pygame.time.set_timer(self.timer_flies, 5000) # how often flies appear - now it's once per 5000 milliseconds


    def load_data(self):
        #load high score 
        with open(HS_FILE, 'r') as f:
            try:
                self.highscore = int(f.readline())
                self.secondbest = int(f.readline())
                self.thirdbest = int(f.readline())
            except:
                self.highscore = 0
                self.secondbest = 0
                self.thirdbest = 0

    def tree_spawn(self):
        Trees(self.all_sprites, self.scale_koef)

    def collision(self):
        if self.duck.rect.top <= 0 or pygame.sprite.spritecollide(self.duck, self.collision_sprites, False, pygame.sprite.collide_mask):
            for sprite in self.collision_sprites.sprites():
                if sprite.sprite_type == 'rock' or sprite.sprite_type == 'fly': # we need to delete rocks and flies if there is a collision, but we don't need to delete the ground or trees
                    sprite.kill()
                self.is_active = False # game stops
                self.duck.kill() # duck gets deleted

    def display_score(self):
        if self.is_active:
            self.score = (pygame.time.get_ticks() - self.start_time) // 1000
            y = WINDOW_HEIGHT / 10
            score_surf = self.font.render(str(self.score), True, 'black')
        else:
            if int(self.score) > int(self.highscore):
                self.thirdbest = self.secondbest
                self.secondbest = self.highscore
                self.highscore = self.score
                with open(HS_FILE, 'w') as f:
                    f.write(f'{self.score}\n')
                    f.write(f'{self.secondbest}\n')
                    f.write(f'{self.thirdbest}')
            if int(self.score) > int(self.secondbest) and int(self.score) < int(self.highscore):
                self.thirdbest = self.secondbest
                self.secondbest = self.score
                with open(HS_FILE, 'w') as f:
                    f.write(f'{self.highscore}\n')
                    f.write(f'{self.score}\n')
                    f.write(f'{self.thirdbest}')
            if int(self.score) > int(self.thirdbest) and int(self.score) < int(self.secondbest):
                self.thirdbest = self.score
                with open(HS_FILE, 'w') as f:
                    f.write(f'{self.highscore}\n')
                    f.write(f'{self.secondbest}\n')
                    f.write(f'{self.score}')
            y = WINDOW_HEIGHT / 2 + (self.menu_rect.height / 1.5)
            score_surf = self.font.render(f'Your score: {self.score}', True, 'black')

        score_rect = score_surf.get_rect(midtop = (WINDOW_WIDTH / 2, y))
        self.display_surf.blit(score_surf, score_rect)

    def display_message(self):
        message_surf = self.font.render('Press SPACE to jump', True, 'black')
        message_rect = message_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - WINDOW_HEIGHT / 50))
        self.display_surf.blit(message_surf, message_rect)
    
    def new_score(self):
        new_score_surf = self.font.render('HIGH SCORE!', True, 'black')
        new_score_rect = new_score_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
        self.display_surf.blit(new_score_surf, new_score_rect)
    
    def high_score(self):
        high_score_surf = self.font.render(f'High score: {self.highscore}', True, 'black')
        high_score_rect = high_score_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - WINDOW_HEIGHT / 8))
        self.display_surf.blit(high_score_surf, high_score_rect)

    def run(self): # running the game
        prev_time = time.time()
        while True:
            dt = time.time() - prev_time # deltaTime -- the difference between the last and the current frames. It makes things happen at a constant rate regardless of the framerate 
            prev_time = time.time()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # if 'space' is pressed
                    if self.is_active:
                        self.duck.jump()
                    else: # restarting the game
                        self.duck = Duck(self.all_sprites, self.scale_koef / 1.7)
                        self.is_active = True
                        self.start_time = pygame.time.get_ticks()
                if event.type == self.timer and self.is_active: # spawning rocks
                    Rocks([self.all_sprites, self.collision_sprites], self.scale_koef)
                if event.type == self.timer_flies and self.is_active: # spawning flies
                    Flies([self.all_sprites, self.collision_sprites], self.scale_koef)
                schedule.run_pending() # spawning trees
                 
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surf)
            self.display_score()
            self.display_message()

            if self.is_active: self.collision()
            else: 
                self.display_surf.blit(self.menu_surf, self.menu_rect)
                if self.score >= self.highscore:
                    self.new_score()
                self.high_score()

            pygame.display.update()
            
            
game = Game()
game.run()



# resources:
# environment - https://opengameart.org/content/tappy-plane
# duck - https://opengameart.org/content/duck