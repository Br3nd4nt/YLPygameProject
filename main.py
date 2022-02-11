from time import sleep
import pygame
import random
import os

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

class Star(pygame.sprite.Sprite):

    def __init__(self, pos, dx, dy, screen_rect, all_sprites):
        self.fire = [load_image("star.png")]
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))
        super().__init__(all_sprites)
        self.screen_rect = screen_rect
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 0.025

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen_rect):
            self.kill()

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, size, sprites):
        super().__init__(sprites)
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


class Board:
    def __init__(self, n, cell_size, bombs_total, font, screen):
        self.first = True
        self.running = True
        self.clock = pygame.time.Clock
        self.width = n
        self.height = n
        self.font = font
        self.screen = screen
        self.cell_size = cell_size
        self.board = [[-1] * n for _ in range(n)]
        self.bombs = [[0] * n for _ in range(n)]
        self.flags  = [[0] * n for _ in range(n)]
        self.bombs_count = 0
        self.bombs_total = bombs_total
        try:
            self.flag_image = pygame.transform.scale(load_image('flag.jpeg'), (self.cell_size, self.cell_size))
        except Exception:
            print(1)
            self.flag_image = None
        self.create_bombs()



    def create_bombs(self):
        self.bombs = [[0] * self.width for _ in range(self.width)]
        self.bombs_count = 0
        self.all_sprites = pygame.sprite.Group()
        while self.bombs_count != self.bombs_total:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.width - 1)
            if not self.bombs[y][x]:
                self.bombs[y][x] = 1
                self.bombs_count += 1
                AnimatedSprite(load_image("Explosion.png"), 12, 1, x * self.cell_size, y * self.cell_size, self.cell_size, self.all_sprites)

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(self.screen, pygame.Color("white"), (
                    x * self.cell_size, y * self.cell_size, self.cell_size,
                    self.cell_size), 1)  
                if self.board[y][x] >= 0:
                    pygame.draw.rect(self.screen, pygame.Color(128, 128, 128), (
                    x * self.cell_size, y * self.cell_size, self.cell_size,
                    self.cell_size))  
                if self.board[y][x] != -1 and self.board[y][x] != 0:
                    text = self.font.render(str(self.board[y][x]), False, pygame.Color('yellow'))
                    self.screen.blit(text, (x * self.cell_size + 9, y * self.cell_size + 4))
                if self.flags[y][x]:
                    if self.flag_image is not None:
                        pygame.draw.rect(self.screen, pygame.Color(0, 0, 0), (
                        x * self.cell_size, y * self.cell_size, self.cell_size,
                        self.cell_size)) 
                        self.screen.blit(self.flag_image, (
                        x * self.cell_size, y * self.cell_size, self.cell_size,
                        self.cell_size))
                    else:
                        pygame.draw.rect(self.screen, pygame.Color("red"), (
                        x * self.cell_size, y * self.cell_size, self.cell_size,
                        self.cell_size))  

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0]) // self.cell_size
        cell_y = (mouse_pos[1]) // self.cell_size    
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def lmb_click(self, cell):
        if self.board[cell[1]][cell[0]] == -1 and not self.flags[cell[1]][cell[0]]:
            self.make_move(cell, True)
            self.check_win()
    
    def rmb_click(self, cell):
        if self.board[cell[1]][cell[0]] == -1:
            self.flags[cell[1]][cell[0]] = (self.flags[cell[1]][cell[0]] + 1) % 2
            self.check_win()
            

    def make_move(self, pos, flag=True):
        ways = [(pos[0] - 1, pos[1] - 1), 
                (pos[0], pos[1] - 1),
                (pos[0] + 1, pos[1] - 1), 
                (pos[0] - 1, pos[1]),
                (pos[0] + 1, pos[1]),
                (pos[0] - 1, pos[1] + 1),
                (pos[0], pos[1] + 1),
                (pos[0] + 1, pos[1] + 1)]
        if flag:
            if self.bombs[pos[1]][pos[0]]:
                if not self.first:
                    self.game_lost()
                else:
                    self.first = True
                    self.create_bombs()
                    self.make_move(pos, flag)
                return 
            else:
                count = 0
                for i in ways:
                    if i[0] >= 0 and i[0] < self.width and i[1] >= 0 and  i[1] < self.height:
                        count += self.make_move(i, False)
                self.board[pos[1]][pos[0]] = count
                if count == 0:
                    for i in ways:
                        if i[0] >= 0 and i[0] < self.width and i[1] >= 0 and  i[1] < self.height and self.board[i[1]][i[0]] != 0:
                            self.make_move(i, True)
                else:
                    self.board[pos[1]][pos[0]] = count
                    self.first = False
                return count
        else:
            return self.bombs[pos[1]][pos[0]]

    def check_for_bomb(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.lmb_click(cell)

    def place_flag(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.rmb_click(cell)
    
    def game_lost(self):
        # self.running = False
        self.make_boom()
        pygame.quit()
        main()

    def game_won(self):
        self.make_stars()
        # self.running = False
        pygame.quit()
        main()

    def check_win(self):
        if self.running:
            # print(self.bombs == self.flags)
            if self.bombs == self.flags and not self.first and sum([x.count(-1) for x in self.board]) == self.bombs_count:
                # self.running = False
                self.game_won()

    def make_boom(self):
        for i in range(12):
            self.all_sprites.draw(self.screen)
            self.all_sprites.update()
            sleep(0.333)
            pygame.display.flip()

    def make_stars(self):
        all_sprites = pygame.sprite.Group()
        count = 0
        for i in range(30):
            particle_count = 20
            numbers = range(-5, 6)
            for _ in range(particle_count):
                Star((random.randrange(0, self.screen.get_width()), random.randrange(0, self.screen.get_height())), random.choice(numbers), random.choice(numbers), (0, 0, self.screen.get_width(), self.screen.get_height()), all_sprites)
        while count < 100:
            count += 1
            sleep(0.02)
            self.render()
            all_sprites.draw(self.screen)
            all_sprites.update()
            pygame.display.flip()

class StartWindow:
    def __init__(self, size, screen, font, running = True):
        self.running = True
        self.size = size
        self.screen = screen
        self.font = font
        self.screen.blit(self.font.render('Выберите уровень сложности:', False, pygame.Color(255, 255, 255)), (size[0] // 4, 5))

        pygame.draw.rect(screen, pygame.Color(128, 128, 128), (size[0] // 4 - 25, 50, size[0] // 2, size[1] // 10))
        self.screen.blit(self.font.render('Лёгкий (9 х 9)', False, pygame.Color(255, 255, 255)), (size[0] // 4 + 100, 60))
        
        pygame.draw.rect(screen, pygame.Color(128, 128, 128), (size[0] // 4 - 25, 150, size[0] // 2, size[1] // 10))
        self.screen.blit(self.font.render('Средний (16 х 16)', False, pygame.Color(255, 255, 255)), (size[0] // 4 + 80, 160))

        pygame.draw.rect(screen, pygame.Color(128, 128, 128), (size[0] // 4 - 25, 250, size[0] // 2, size[1] // 10))
        self.screen.blit(self.font.render('Сложный (25 х 25)', False, pygame.Color(255, 255, 255)), (size[0] // 4 + 80, 260))

    def click(self, pos):
        if self.size[0] * 0.22 <= pos[0] <= self.size[0] * 0.72:
            if self.size[1] * 0.088 <= pos[1] <= self.size[1] * 0.2:
                return 9
            elif self.size[1] * 0.25 <= pos[1] <= self.size[1] * 0.355:
                return 16
            elif self.size[1] * 0.42 <= pos[1] <= self.size[1] * 0.518:
                return 25
            else:
                return 0

def main():
    try:
    # if True:
        pygame.init()
        x = 100
        y = 45
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)        
        font = pygame.font.SysFont('Times New Roman', 28)
        pygame.display.set_caption('Сапёр')
        screen = pygame.display.set_mode((800, 600))

        start_window = StartWindow((800, 600), screen, font)
        pygame.display.flip()
        while start_window.running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    res = start_window.click(event.pos)
                    if res:
                        start_window.running = False
                        n = res
                if event.type == pygame.QUIT:
                    pygame.quit()
        cell_size = 40 + n // 5
        bombs_total = n ** 2 // 10

        size = n * cell_size, n * cell_size 
        screen = pygame.display.set_mode(size)
        
        
        board = Board(n, cell_size, bombs_total, font, screen)
        while board.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    board.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        board.check_for_bomb(event.pos)
                    elif event.button == 3:
                        board.place_flag(event.pos)
            if not board.running:
                break
            screen.fill((0, 0, 0))
            board.render()
            pygame.display.flip()
        
        pygame.quit()
    except Exception as e:
        if 'video system not initialized' in str(e):
            exit()
        print(str(e))

        pygame.quit()
        main()

if __name__ == '__main__':
    main()
