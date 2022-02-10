import os
import pygame

pygame.init()

FPS = 10
WIDTH = 400
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()


def load_image(name, color_key=None):
    try:
        image = pygame.image.load(os.path.abspath(name)).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image



class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, size):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows, size)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows, size):
        scaled = pygame.transform.scale(sheet, (size * columns, size * rows))
        self.rect = pygame.Rect(0, 0, scaled.get_width() // columns, scaled.get_height() // rows)
        self.rect
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(scaled.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


dragon = AnimatedSprite(load_image("Explosion.png"), 12, 1, 0, 0, 50)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color("black"))
    # pygame.transform.scale(screen, (2, 2))
    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()