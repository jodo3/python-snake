import math
import operator
from random import random

from pynput.keyboard import Key, Listener
from threading import Timer
import pygame
import pygame.freetype
import constants


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


# class Point:
#     def __init__(self, x=0, y=0):
#         self.x = x
#         self.y = y
#
#     def add(self, new_point):


class Board:
    snakeImg = pygame.image.load('snake-graphics.png')
    parts = {
        (1, 0, 3): (192, 0),
        (0, 1, 3): (192, 64),
        (-1, 0, 3): (256, 64),
        (0, -1, 3): (256, 0),
        (1, 0, 4): (192, 128),
        (0, 1, 4): (192, 192),
        (-1, 0, 4): (256, 192),
        (0, -1, 4): (256, 128),
        (1, 0, 1, 0): (128, 64),
        (-1, 0, -1, 0): (128, 64),
        (0, 1, 0, 1): (64, 0),
        (0, -1, 0, -1): (64, 0),
        (0, -1, 1, 0): (0, 0),
        (-1, 0, 0, 1): (0, 0),
        (0, -1, -1, 0): (0, 64),
        (1, 0, 0, 1): (0, 64),
        (0, 1, 1, 0): (128, 0),
        (-1, 0, 0, -1): (128, 0),
        (0, 1, -1, 0): (128, 128),
        (1, 0, 0, -1): (128, 128),
        2: (0, 192),
        0: (64, 64)
    }
    colours = {
        0: constants.WHITE,
        1: constants.RED,
        2: constants.BLUE,
        3: constants.ORANGE
    }

    def __init__(self, snake):
        self.screen = pygame.display.set_mode((constants.WIDTH + 50, constants.HEIGHT + 100))
        pygame.display.set_caption('Snake')
        pygame.freetype.init()
        self.GAME_FONT = pygame.freetype.SysFont('Verdana', 50)

        self.length = constants.ROWS
        self.width = constants.COLS
        self.grid = [[0]*self.width for i in range(self.length)]
        self.food = constants.FOOD
        self.snake = snake

        square = snake.head
        self.update_square(square, 1)
        for i in snake.body:
            square = tuple(map(operator.add, square, i))
            self.update_square(square, 1)
        self.new_food()
        self.grid[self.snake.head[0]][self.snake.head[1]] = 3
        self.grid[self.snake.tail[0]][self.snake.tail[1]] = 4
        self.print_board()
        self.rt = RepeatedTimer(1/constants.SPEED, self.update)
        # while True:
        #     self.update()

    def update(self):
        if self.snake.growth == 0:
            self.grid[self.snake.tail[0]][self.snake.tail[1]] = 0
        self.snake.update()
        x, y = self.snake.head[0], self.snake.head[1]
        if self.in_range(self.snake.head) and self.grid[x][y] != 1:
            if self.grid[x][y] == 2:
                self.snake.growth += constants.FOOD
                self.snake.score += constants.FOOD
                self.new_food()
            self.grid[x][y] = 3
            self.grid[self.snake.tail[0]][self.snake.tail[1]] = 4
            self.grid[self.snake.tail[0]][self.snake.tail[0]] = 4
            self.print_board()
            self.grid[x][y] = 1
        else:
            print("You Died!")
            self.GAME_FONT.render_to(self.screen, (300, 10), "You Died!", fgcolor=constants.YELLOW)
            pygame.display.update()
            self.rt.stop()
        return

    def in_range(self, square):
        if (square[0] in range(self.length)) and (square[1] in range(0, self.width)):
            return True
        return False

    def update_square(self, tup, value):
        if self.grid[tup[0]][tup[1]] == 1:
            return False
        self.grid[tup[0]][tup[1]] = value
        return True

    def add_part(self, target, coords):
        surface = pygame.Surface((64, 64))
        surface.blit(self.snakeImg, (0, 0), target + (64, 64))
        row, col = coords[1], coords[0]
        self.screen.blit(surface, (row * constants.SQUARE_SIZE + 25, col * constants.SQUARE_SIZE + 75))

    def print_board(self):
        self.screen.fill(constants.BLACK)
        self.add_part(self.parts[2], self.foodc)

        coords = self.snake.head
        target = self.parts[self.snake.direction + (3,)]
        self.add_part(target, coords)
        for i in range(len(self.snake.body)):
            dir = self.snake.body[i]
            coords = tuple(map(operator.add, coords, dir))
            if i == len(self.snake.body) - 1:
                target = self.parts[dir + (4,)]
            else:
                next_dir = self.snake.body[i+1]
                target = self.parts[dir + next_dir]
            self.add_part(target, coords)

        self.GAME_FONT.render_to(self.screen, (10, 10), f"Score: {self.snake.score}", fgcolor=constants.YELLOW)
        pygame.display.update()

    def new_food(self):
        index = math.floor(random()*(self.length*self.width-self.snake.score))
        for a in range(self.length):
            for b in range(self.width):
                if self.grid[a][b] == 0:
                    index -= 1
                    if index < 0:
                        self.foodc = (a, b)
                        self.grid[a][b] = 2
                        return


class Snake:

    directions = {
        'w': (1, 0),
        'up': (1, 0),
        'a': (0, 1),
        'left': (0, 1),
        's': (-1, 0),
        'down': (-1, 0),
        'd': (0, -1),
        'right': (0, -1),
        'a': (0, 1),
    }

    def __init__(self, score=3):
        self.score = score
        self.head = (5, 5)
        self.tail = (5, 3)
        self.body = [(0, -1) for i in range(score - 1)]
        self.direction = (0, -1)  # counted from head to tail
        self.growth = 0
        self.alive = True

    def new_press(self, key):
        if key in self.directions:
            new_dir = self.directions.get(key)
            if abs(new_dir[0] - self.direction[0]) == 1:
                self.direction = new_dir

    def update(self):
        self.head = tuple(map(operator.sub, self.head, self.direction))
        self.body.insert(0, self.direction)
        if self.growth == 0:
            self.tail = tuple(map(operator.sub, self.tail, self.body.pop(-1)))
        else:
            self.growth -= 1
        return


def on_press(key):
    try:
        snake.new_press(key.char)
    except AttributeError:
        snake.new_press(key.name)


def on_release(key):
    if key == Key.esc:
        listener.stop()
        board.rt.stop()
        return False


snake = Snake()
board = Board(snake)
run = True
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pass

pygame.quit()

