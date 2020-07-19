import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import math
import colors


# Classes
class World:
    def __init__(self):
        self.TILE_SIZE = 64

        self.TILE_WIDTH = math.ceil(SCREEN_WIDTH / self.TILE_SIZE) + 1
        self.TILE_HEIGHT = math.ceil(SCREEN_HEIGHT / self.TILE_SIZE) + 1

        self.WORLD_HEIGHT = self.TILE_HEIGHT
        self.WORLD_WIDTH = 100

        assert self.WORLD_HEIGHT >= self.TILE_HEIGHT
        assert self.WORLD_WIDTH >= self.TILE_WIDTH

        self.tiles = [None]

        self.load_tiles()
        self.create_map()

    def load_tiles(self):
        for name in sorted([f for f in os.listdir('./assets/tiles') if not f.startswith('.')]):
            self.tiles.append(load(name, 'tiles', [self.TILE_SIZE] * 2))

    def create_map(self):
        self.world_map = [[0] * self.WORLD_HEIGHT for _ in range(self.WORLD_WIDTH)]
        for x in range(self.WORLD_WIDTH):
            self.world_map[x][-1] = 1


class Player(pg.sprite.Sprite):
    def __init__(self):
        self.scroll_x = 5
        self.scroll_y = 0


# Global functions
def q1_transform(x, y):
    return [x, SCREEN_HEIGHT - y]


def load(file, extra_path="", scale=None):
    path = os.path.join('./assets/' + extra_path, file)
    image = pg.image.load(path)
    if scale is None:
        return image
    else:
        scale = [round(x) for x in scale]
        return pg.transform.scale(image, scale)


# Main code starts here
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], flags=pg.FULLSCREEN)
pg.display.set_caption("The Hike")
running = True

# Class instances
player = Player()
world = World()

while running:
    keys = pg.key.get_pressed()
    if pg.QUIT in [event.type for event in pg.event.get()] or keys[pg.K_ESCAPE]:
        running = False

    screen.fill(colors.sky_blue)

    for x in range(world.TILE_WIDTH):
        for y in range(world.TILE_HEIGHT):
            x_offset = player.scroll_x - math.floor(player.scroll_x)
            y_offset = player.scroll_y - math.floor(player.scroll_y)
            tile = world.world_map[(x + math.floor(player.scroll_x))][world.TILE_HEIGHT - 1 - (y + math.floor(player.scroll_y))]
            if tile > 0:
                screen.blit(world.tiles[tile], q1_transform((x - x_offset) * world.TILE_SIZE, ((y + 1) - y_offset) * world.TILE_SIZE))

    player.scroll_x += 0.05

    pg.mouse.set_visible(False)
    pg.display.update()
