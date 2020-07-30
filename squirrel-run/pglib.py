import pygame as pg
import os
import sys


# Colors
sky_blue = (0, 204, 255)
black = (0, 0, 0)


# Classes
class Screen:
    def __init__(self, dims, title, version="", alpha=False):
        pg.init()
        pg.font.init()
        pg.mixer.init()

        flags = pg.DOUBLEBUF
        if len(sys.argv) == 1 or "w" not in sys.argv[1]:
            flags = flags | pg.FULLSCREEN | pg.HWSURFACE
        elif len(sys.argv) > 1:
            if "n" in sys.argv[1]:
                flags = flags | pg.NOFRAME
            if "r" in sys.argv[1]:
                flags = flags | pg.RESIZABLE

        self.WIDTH, self.HEIGHT = dims
        self.canvas = pg.display.set_mode(dims, flags)
        if not alpha:
            self.canvas.set_alpha(None)
        if version != "":
            version = " v. " + version

        pg.display.set_caption(title + version)
        pg.mouse.set_visible(False)
        self.frame = 0
        self.clock = pg.time.Clock()

    def q1_transform(self, location):
        def q1_transform_coordinate(location):
            return [location[0], self.HEIGHT - location[1]]

        if isinstance(location[0], list):
            transformed_coordinates = []
            for x in location:
                transformed_coordinates.append(q1_transform_coordinate(x))
            return transformed_coordinates
        else:
            return q1_transform_coordinate(location) 

    def q1_transform_rect(self, location, dims):  # transform rectangle (4 inputs)
        return [location[0] + a, self.HEIGHT - location[1], -dims[0], -dims[1]]

    def text(self, text, color, font, location):
        rendered_text = font.render(text, True, color)
        location = [location[x] + (font.size(text)[x] // 2) for x in range(len(self.q1_transform(location)))]
        self.canvas.blit(rendered_text, location)

    def raw_text(self, text, color, font, location):
        self.canvas.blit(font.render(text, True, color), location)

    def center_text(self, text, color, font):
        self.text(text, color, font, [self.WIDTH // 2, self.HEIGHT // 2])

    def hcenter_text(self, text, color, font, height):
        self.text(text, color, font, [self.WIDTH // 2, height])

    def polygon(self, vertices, color):
        vertices = q1_transform(vertices)
        for v in vertices:
            if self.is_onscreen(q1_transform(v)):
                pg.gfxdraw.aapolygon(self.canvas, vertices, color)
                pg.gfxdraw.filled_polygon(self.canvas, vertices, color)
                return

    def circle(self, location, radius, color):
        if self.is_onscreen(location, radius):
            pg.gfxdraw.aacircle(self.canvas, location[0], location[1], radius, color)
            pg.gfxdraw.filled_circle(self.canvas, location[0], location[1], radius, color)

    def rect(self, location, dims, color):
        pg.draw.rect(self.canvas, color, location + dims)

    def blit(self, image, location):
        x, y = self.q1_transform(location)
        y -= image.get_size()[1]
        self.canvas.blit(image, [x, y])

    def is_onscreen(self, location, radius=0):
        in_width = location[0] - radius > 0 and location[0] + radius < self.WIDTH
        in_height = location[1] - radius > 0 and location[1] + radius < self.HEIGHT
        return in_width and in_height

    def update(self):
        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return False

        self.frame += 1
        self.clock.tick()
        pg.display.update()
        return True


# Load functions
def load(file, extra_path="", scale=None):
    path = os.path.join("./assets/image/" + extra_path, file)
    image = pg.image.load(path)
    if scale is None:
        return image
    else:
        scale = [round(x) for x in scale]
        return pg.transform.scale(image, scale)

# add mirror image argument
def load_folder(folder_path, scale=None):
    textures = []
    for name in sorted([f for f in os.listdir("./assets/image/" + folder_path) if not f.startswith('.')]):
        textures.append(load(name, folder_path, scale))
    return textures


def play_music(file_path):
    pg.mixer.music.load(file_path)
    pg.mixer.music.play()


def num_files(directory):
    return len([name for name in os.listdir(directory) if name != ".DS_Store"])
