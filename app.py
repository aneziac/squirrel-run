import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import math
import time
from random import random, randint
import pglib
from levels import level1 as level1


# Classes
class World:
    def __init__(self, generated=True):
        self.TILE_SIZE = 64
        self.TREE_HEIGHT = 600
        self.TREE_WIDTH = round(self.TREE_HEIGHT * (100 / 64))
        self.TREE_OVERLAP = self.TREE_WIDTH // 2
        self.TREE_DIST = self.TREE_WIDTH - self.TREE_OVERLAP # effective width of trees
        self.BACKGROUND_WIDTH = (screen.WIDTH // self.TREE_DIST) + 2
        self.RELATIVE_TREE_SPEED = 3

        self.SCREEN_TILE_WIDTH = (screen.WIDTH // self.TILE_SIZE) + 1
        self.SCREEN_TILE_HEIGHT = (screen.HEIGHT // self.TILE_SIZE) + 1

        if generated:
            self.HEIGHT = self.SCREEN_TILE_HEIGHT
            self.WIDTH = 100
            self.create_map()
        else:
            self.HEIGHT = len(level1.world)
            self.WIDTH = len(level1.world[0])
            self.MAP = level1.world[::-1]

        assert self.HEIGHT >= self.SCREEN_TILE_HEIGHT
        assert self.WIDTH >= self.SCREEN_TILE_WIDTH

        self.TILE_TEXTURES = pglib.load_folder("tile", [self.TILE_SIZE] * 2)
        self.TREE_TEXTURES = pglib.load_folder("tree", [self.TREE_WIDTH, self.TREE_HEIGHT])

        self.BACKGROUND_SCALAR = (self.TREE_MAX / self.WIDTH) / self.RELATIVE_TREE_SPEED

    def create_map(self):
        self.TREE_MAX = (self.WIDTH * self.TILE_SIZE) // self.TREE_DIST
        self.TREES = []
        for x in range(self.TREE_MAX):
            self.TREES.append(randint(1, pglib.num_files("./assets/image/tree")) - 1)

        self.MAP = [[0] * self.WIDTH for _ in range(self.HEIGHT)]

        # add grass and water
        for x in range(self.WIDTH):
            self.MAP[0][x] = 1

    def render_trees(self):
        background_scroll_x = player.scroll_x * self.BACKGROUND_SCALAR
        background_tile_offset = background_scroll_x - math.floor(background_scroll_x)

        for x in range(self.BACKGROUND_WIDTH):
            tree = self.TREES[x + (math.floor(background_scroll_x))]
            if tree != 0:
                screen.blit(self.TREE_TEXTURES[tree - 1], [(x - background_tile_offset) * self.TREE_DIST, self.TILE_SIZE - 100])

    def render_tiles(self):
        x_tile_offset = player.scroll_x - math.floor(player.scroll_x)
        y_tile_offset = player.scroll_y - math.floor(player.scroll_y)

        for x in range(self.SCREEN_TILE_WIDTH):
            for y in range(self.SCREEN_TILE_HEIGHT):
                tile = self.MAP[y + math.floor(player.scroll_y)][x + math.floor(player.scroll_x)]
                if tile != 0:
                    screen.blit(self.TILE_TEXTURES[tile - 1], [(x - x_tile_offset) * self.TILE_SIZE, (y - y_tile_offset) * self.TILE_SIZE])


class Player(pg.sprite.Sprite):
    def __init__(self):
        self.scroll_x = 0
        self.scroll_y = 0
        self.dims = [128, 64]
        self.score = 0

        self.walk = pglib.load_folder("player/walk", self.dims)
        self.jumpup = pglib.load_folder("player/jumpup", self.dims)
        self.jumpdown = pglib.load_folder("player/jumpdown", self.dims)
        self.glide = pglib.load_folder("player/glide", self.dims)
        self.costume = [self.walk, 12]

        self.YACC = -1
        self.yvel = 0
        self.RESTING_Y = world.TILE_SIZE
        self.y = self.RESTING_Y

        self.X = world.TILE_SIZE * 2

    def update(self, keys):
        self.tile_x, self.tile_y = math.floor(self.scroll_x), self.y // world.TILE_SIZE
        on_tile = world.MAP[self.tile_y][self.tile_x]

        if on_tile == 2:
            self.score += 1
            world.MAP[self.tile_y][self.tile_x] = 0

        if not (on_tile == 6 or on_tile == 1):
            if keys[pg.K_SPACE]:
                if self.costume != [[self.glide[2]], 1]:
                    self.costume = [self.glide, 3]
                self.yvel = 0
                self.y -= 2
                return True
            else:
                self.yvel += self.YACC
                if self.costume != [[self.jumpup[6]], 1]:
                    self.costume = [self.jumpup, 7]
        elif keys[pg.K_w] and not keys[pg.K_SPACE]:
            self.yvel = 20
        else:
            if on_tile == 7 or on_tile == 4 or on_tile == 5:
                return False

            self.yvel = 0

            # prevent clipping into tile underneath
            self.y += world.TILE_SIZE - (self.y % world.TILE_SIZE) - 1
            self.costume = [self.walk, 12]
        self.y += self.yvel

    def render(self):
        if self.costume == [self.glide, 3] and round(self.scroll_x * 10) % self.costume[1] == 2:
            self.costume = [[self.glide[2]], 1]
        elif self.costume == [self.jumpup, 7] and round(self.scroll_x * 10) % self.costume[1] == 6:
            self.costume = [[self.jumpup[6]], 1]
        screen.blit(self.costume[0][(screen.frame // 2) % self.costume[1]], [self.X, self.y])


class Acorn:
    instances = []

    def __init__(self, x):
        self.TEXTURE = pglib.load('2_acorn.png', 'tile', [world.TILE_SIZE] * 2)
        self.y = randint(screen.HEIGHT - 200, screen.HEIGHT)
        self.yacc = -0.2
        self.yvel = 0
        self.x = x
        Acorn.instances.append(self)

    def update(self):
        if self.y > world.TILE_SIZE * 2:
            self.yvel += self.yacc
            self.y += self.yvel
        else:
            Acorn.instances.remove(self)

    def render(self):
        screen.blit(self.TEXTURE, [self.x - player.scroll_x, self.y])


# Main code starts here

screen = pglib.Screen([900, 600], "Squirrel Run")
running = True
font = pg.font.Font('assets/font/retro.ttf', 40)

# Class instances
world = World()
player = Player()

while screen.update():
    keys = pg.key.get_pressed()

    if player.update(keys) == False:
        screen.text("GAME OVER!", pglib.black, font)
        pg.display.flip()
        time.sleep(3)
        quit()

    #for instance in Acorn.instances:
    #    instance.update()

    screen.canvas.fill(pglib.sky_blue)

    world.render_trees()
    world.render_tiles()
    for instance in Acorn.instances:
        instance.render()
    player.render()

    screen.raw_text("Score: " + str(player.score), pglib.black, font, [0, 0])

    # if screen.frame % 5 == 0 and random() < 0.03:
    #    Acorn(randint(round(player.scroll_x + 200), round(player.scroll_x) + screen.WIDTH - 100))

    player.scroll_x += 0.05
