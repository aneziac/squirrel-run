import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import math
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
        self.TREES_OFFSET = ((self.TREE_WIDTH - self.TREE_DIST) * 0.5)

        self.ACORN_NUMBER = 3

        self.SCREEN_TILE_WIDTH = (screen.WIDTH // self.TILE_SIZE) + 2
        self.SCREEN_TILE_HEIGHT = (screen.HEIGHT // self.TILE_SIZE) + 2

        if generated: # make level image reader
            self.HEIGHT = self.SCREEN_TILE_HEIGHT
            self.WIDTH = 400
            self.create_world_map()
        else:
            self.HEIGHT = len(level1.world)
            self.WIDTH = len(level1.world[0])
            self.MAP = level1.world[::-1]

        self.create_tree_map()

        assert self.HEIGHT >= self.SCREEN_TILE_HEIGHT
        assert self.WIDTH >= self.SCREEN_TILE_WIDTH

        self.TILE_TEXTURES = pglib.load_folder("tile", [self.TILE_SIZE] * 2)
        self.TREE_TEXTURES = pglib.load_folder("tree", [self.TREE_WIDTH, self.TREE_HEIGHT])

        self.BACKGROUND_SCALAR = (self.TREE_MAX / self.WIDTH) / self.RELATIVE_TREE_SPEED

    def create_world_map(self):
        self.MAP = [[0] * self.WIDTH for _ in range(self.HEIGHT)]

        # add grass and water
        for x in range(self.WIDTH):
            if random() < 0.2:
                self.MAP[0][x] = 5
            else:
                self.MAP[0][x] = 1

            if random() < 0.05:
                self.MAP[randint(1, 4)][x] = 3

    def create_tree_map(self):
        self.TREE_MAX = (self.WIDTH * self.TILE_SIZE) // self.TREE_DIST
        self.TREES = []
        for x in range(self.TREE_MAX):
            self.TREES.append(randint(0, pglib.num_files("./assets/image/tree") - 1))

    def render_trees(self):
        background_scroll_x = player.scroll_x * self.BACKGROUND_SCALAR
        background_tile_offset = background_scroll_x - math.floor(background_scroll_x)

        for x in range(self.BACKGROUND_WIDTH):
            tree = self.TREES[x + (math.floor(background_scroll_x))]
            xpos = (x - background_tile_offset) * self.TREE_DIST - self.TREES_OFFSET
            screen.blit(self.TREE_TEXTURES[tree], [xpos, self.TILE_SIZE - 100])

    def render_tiles(self):
        x_tile_offset = round(player.scroll_x - math.floor(player.scroll_x), 3)
        y_tile_offset = round(player.scroll_y - math.floor(player.scroll_y), 3)

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

        self.actions = {}
        for action in ["walk", "jump", "land", "glide"]:
            if action == "walk":
                self.load_action(action, True)
            else:
                self.load_action(action)

        self.YACC = -1
        self.yvel = 0
        self.RESTING_Y = world.TILE_SIZE
        self.y = self.RESTING_Y

        self.X = world.TILE_SIZE * 2
        self.X_OFFSET = ((self.X + self.dims[0]) / world.TILE_SIZE) - 1
        self.SPEED = 0.05

        self.old_action = "walk"
        self.anim_frame = 0

    def load_action(self, name, loop=False):
        folder = "player/" + name
        self.actions[name] = [pglib.load_folder(folder, self.dims), pglib.num_files("assets/image/" + folder), loop]

    def update(self, keys):
        self.tile_x, self.tile_y = math.floor(self.scroll_x + self.X_OFFSET), self.y // world.TILE_SIZE
        on_tile = world.MAP[self.tile_y + 1][self.tile_x]
        below_tile = world.MAP[self.tile_y][self.tile_x]

        if on_tile == 3:
            self.score += 1
            world.MAP[self.tile_y + 1][self.tile_x] = 0

        # if on a solid platform
        if below_tile == 1 or below_tile == 2:

            # jumping
            if keys[pg.K_w] and not keys[pg.K_SPACE]:
                self.yvel = 20

            # walking
            else:
                self.y += world.TILE_SIZE - (self.y % world.TILE_SIZE) - 1  # prevent clipping into tile underneath
                self.yvel = 0
                self.action = "walk"

        else:
            # drowning
            if below_tile == 4 or below_tile == 5 or below_tile == 6:
                self.die()

            # gliding
            elif keys[pg.K_SPACE]:
                self.yvel = 0
                self.y -= 2
                self.action = "glide"

            else:
                # landing
                if False:  # self.tile_y >= 3 and world.MAP[self.tile_y - 3][self.tile_x] == 1 and not keys[pg.K_SPACE]:
                    self.action = "land"

                # midair
                else:
                    self.action = "jump"

                self.yvel += self.YACC

        self.y += self.yvel
        self.anim_frame += 1
        self.scroll_x += self.SPEED

    def die(self):
        print("You died")
        self.scroll_x, self.scroll_y = 0, 0
        self.y = self.RESTING_Y

    def render(self):
        blit_loc = [self.X, self.y]
        action = self.actions[self.action]

        if self.old_action != self.action:
            self.anim_frame = 0
            self.old_action = self.action

        if not action[2] and self.anim_frame == action[1]:
            screen.blit(action[0][self.anim_frame - 1], blit_loc)
            self.anim_frame -= 1
        else:
            screen.blit(action[0][(self.anim_frame // 2) % action[1]], blit_loc)


class Acorn:
    instances = []

    def __init__(self):
        self.TEXTURE = pglib.load('acorn.png', 'entity', [world.TILE_SIZE] * 2)
        Acorn.instances.append(self)
        self.fade = -2

    def spawn(self):
        self.y = randint(screen.HEIGHT - 200, screen.HEIGHT)
        self.yacc = -0.1
        self.yvel = 0
        self.x = randint(round(player.scroll_x + 200), round(player.scroll_x) + screen.WIDTH - 100)
        self.fade = -1

    def update(self):
        if self.fade == 0:
            self.fade = -2
            return
        elif self.fade > 0:
            self.fade -= 1
            self.x -= player.SPEED * world.TILE_SIZE
            return

        self.tile_x, self.tile_y = round(self.x) // world.TILE_SIZE, round(self.y) // world.TILE_SIZE

        if self.tile_x == player.tile_x and self.tile_y == player.tile_y:
            player.die()
        elif not world.MAP[self.tile_y][self.tile_x] == 0 and not world.MAP[self.tile_y][self.tile_x] == 3:
            self.fade = 30
        else:
            self.yvel += self.yacc
            self.y += self.yvel

    def render(self):
        screen.blit(self.TEXTURE, [self.x - player.scroll_x, self.y])


# Main code starts here
screen = pglib.Screen([900, 600], "Squirrel Run")
running = True
font = pg.font.Font('assets/font/retro.ttf', 40)

# Class instances
world = World()
player = Player()

for x in range(world.ACORN_NUMBER):
    Acorn()

while screen.update():
    # update
    keys = pg.key.get_pressed()
    player.update(keys)

    for acorn in Acorn.instances:
        if random() < 0.01 and acorn.fade == -2:
            acorn.spawn()
        if acorn.fade >= -1:
            acorn.update()

    # render
    screen.canvas.fill(pglib.sky_blue)

    world.render_trees()
    world.render_tiles()

    for acorn in Acorn.instances:
        if acorn.fade >= -1:
            acorn.render()

    player.render()

    screen.raw_text("Score: " + str(player.score), pglib.black, font, [0, 0])
