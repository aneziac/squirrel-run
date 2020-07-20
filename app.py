import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import math
from random import random, randint
import colors
from levels import level1 as level1


# Classes
class World:
    def __init__(self):
        self.TILE_SIZE = 64
        self.TREE_HEIGHT = 600
        self.TREE_WIDTH = round(self.TREE_HEIGHT * (100 / 64))
        self.TREE_OVERLAP = self.TREE_WIDTH // 2

        self.SCREEN_TILE_WIDTH = math.ceil(SCREEN_WIDTH / self.TILE_SIZE) + 1
        self.SCREEN_TILE_HEIGHT = math.ceil(SCREEN_HEIGHT / self.TILE_SIZE) + 1
        self.BACKGROUND_WIDTH = math.ceil(SCREEN_WIDTH / (self.TREE_WIDTH - self.TREE_OVERLAP)) + 2

        self.WORLD_HEIGHT = self.SCREEN_TILE_HEIGHT
        self.WORLD_WIDTH = 100

        assert self.WORLD_HEIGHT >= self.SCREEN_TILE_HEIGHT
        assert self.WORLD_WIDTH >= self.SCREEN_TILE_WIDTH

        self.tiles = load_folder('tile', [self.TILE_SIZE] * 2)
        self.trees = load_folder('tree', [self.TREE_WIDTH, self.TREE_HEIGHT])
        self.create_map()

    def create_map(self):
        self.TREE_MAX = round(self.WORLD_WIDTH * (self.TILE_SIZE / (self.TREE_WIDTH - self.TREE_OVERLAP)))
        self.background = [-1] * self.TREE_MAX
        for x in range(self.TREE_MAX):
            self.background[x] = randint(0, len([f for f in os.listdir('./assets/image/tree') if not f.startswith('.')]) - 1)

        #self.world_map = [[-1] * self.WORLD_WIDTH for _ in range(self.WORLD_HEIGHT)]
        self.world_map = level1.world
        self.WORLD_WIDTH = len(level1.world[0])

        # add grass and water
        #for x in range(self.WORLD_WIDTH):
        #    self.world_map[x][-1] = 0
        #for x in range(randint(self.WORLD_WIDTH // 20, self.WORLD_WIDTH // 10)):
        #    self.world_map[]

    def render_trees(self):
        background_scroll_x = player.scroll_x * (world.SCREEN_TILE_WIDTH / world.TREE_WIDTH) * 4
        background_tile_offset = background_scroll_x - math.floor(background_scroll_x)

        for x in range(world.BACKGROUND_WIDTH):
            tree = world.background[x + (math.floor(background_scroll_x))]
            if tree != -1:
                screen.blit(world.trees[tree], q1_transform((x - background_tile_offset - 1) * world.TREE_OVERLAP, world.SCREEN_TILE_WIDTH + world.TREE_HEIGHT - 50))

    def render_tiles(self): 
        x_tile_offset = player.scroll_x - math.floor(player.scroll_x)
        y_tile_offset = player.scroll_y - math.floor(player.scroll_y)

        for x in range(self.SCREEN_TILE_WIDTH):
            for y in range(self.SCREEN_TILE_HEIGHT):
                tile = self.world_map[self.SCREEN_TILE_HEIGHT - 1 - (y + math.floor(player.scroll_y))][(x + math.floor(player.scroll_x))]
                if tile != -1:
                    screen.blit(self.tiles[tile], q1_transform((x - x_tile_offset) * self.TILE_SIZE, ((y + 1) - y_tile_offset) * self.TILE_SIZE))


class Player(pg.sprite.Sprite):
    def __init__(self):
        self.scroll_x = 5
        self.scroll_y = 0
        self.dims = [128, 64]

        self.walk = load_folder('sprite/walk', self.dims)
        self.jumpup = load_folder('sprite/jumpup', self.dims)
        self.jumpdown = load_folder('sprite/jumpdown', self.dims)
        self.glide = load_folder('sprite/glide', self.dims)
        self.costume = [self.walk, 12]

        self.YACC = -1
        self.yvel = 0
        self.RESTING_Y = world.TILE_SIZE * 2
        self.y = self.RESTING_Y

    def update(self, keys):
        if self.y >= self.RESTING_Y:
            if keys[pg.K_SPACE]:
                if self.costume != [[self.glide[2]], 1]:
                    self.costume = [self.glide, 3]
                self.y -= 1
                return
            else:
                self.yvel += self.YACC
                if self.yvel < 0 and self.y - 150 < self.RESTING_Y:
                    self.costume = [self.jumpdown, 6]
                elif self.costume != [[self.jumpup[6]], 1]:
                    self.costume = [self.jumpup, 7]
        elif keys[pg.K_w]:
            self.yvel = 20
        else:
            self.yvel = 0
            self.costume = [self.walk, 12]
        self.y += self.yvel

    def render(self):
        if self.costume == [self.glide, 3] and round(self.scroll_x * 10) % self.costume[1] == 2:
            self.costume = [[self.glide[2]], 1]
        elif self.costume == [self.jumpup, 7] and round(self.scroll_x * 10) % self.costume[1] == 6:
            self.costume = [[self.jumpup[6]], 1]
        screen.blit(self.costume[0][(frame // 2) % self.costume[1]], q1_transform(world.TILE_SIZE * 2, self.y))


# Global functions
def q1_transform(x, y):
    return [x, SCREEN_HEIGHT - y]


def load(file, extra_path="", scale=None):
    path = os.path.join('./assets/image/' + extra_path, file)
    image = pg.image.load(path)
    if scale is None:
        return image
    else:
        scale = [round(x) for x in scale]
        return pg.transform.scale(image, scale)

# add mirror image argument
def load_folder(folder_path, size):
    textures = []
    for name in sorted([f for f in os.listdir('./assets/image/' + folder_path) if not f.startswith('.')]):
        textures.append(load(name, folder_path, size))
    return textures


# Main code starts here
pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT]) #,flags=pg.FULLSCREEN)
pg.display.set_caption("Squirrel Run")
running = True
frame = 0

# Class instances
world = World()
player = Player()

while running:
    keys = pg.key.get_pressed()
    if pg.QUIT in [event.type for event in pg.event.get()] or keys[pg.K_ESCAPE]:
        running = False

    player.update(keys)

    screen.fill(colors.sky_blue)

    world.render_trees()
    world.render_tiles()
    player.render()

    player.scroll_x += 0.1
    frame += 1

    pg.mouse.set_visible(False)
    pg.display.update()
