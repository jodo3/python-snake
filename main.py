import math
import operator
from random import random

from pynput.keyboard import Key, Listener
from threading import Timer
import time


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

    def __init__(self, snake, length=10, width=10, food=1):
        self.length = length
        self.width = width
        self.grid = [[0]*width for i in range(length)]
        self.food = food
        self.score = 0
        self.snake = snake

        square = snake.head
        self.update_square(square, 1)
        for i in snake.body:
            square = tuple(map(operator.add, square, i))
            self.update_square(square, 1)
        self.new_food()

        self.print_board()
        self.rt = RepeatedTimer(0.5, self.update)
        # self.update()

    def update(self):
        if self.snake.growth == 0:
            self.grid[self.snake.tail[0]][self.snake.tail[1]] = 0
        self.snake.update()
        x, y = self.snake.head[0], self.snake.head[1]
        if self.in_range(self.snake.head) and self.grid[x][y] != 1:
            if self.grid[x][y] == 2:
                self.snake.growth += self.grid[x][y] * self.food / 2
                self.new_food()
            self.grid[x][y] = 1
            self.print_board()
        else:
            print("You Died!")
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

    def print_board(self):
        print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                         for row in self.grid]))
        print(f"Score: {self.snake.score}")

    def new_food(self):
        index = math.floor(random()*self.length*self.width-self.snake.score)
        for a in range(self.length):
            for b in range(self.width):
                if self.grid[a][b] == 0:
                    index -= 1
                    if index < 0:
                        self.grid[a][b] = 2
                        return


class Snake:

    directions = {
        'w': (1, 0),
        'a': (0, 1),
        's': (-1, 0),
        'd': (0, -1)
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
                print(self.direction)

    def update(self):
        self.head = tuple(map(operator.sub, self.head, self.direction))
        self.body.insert(0, self.direction)
        if self.growth == 0:
            self.tail = tuple(map(operator.sub, self.tail, self.body.pop(-1)))
        else:
            self.growth -= 1
            self.score += 1
        return


def on_press(key):
    snake.new_press(str(key)[1])


def on_release(key):
    if key == Key.esc:
        return False


snake = Snake()
board = Board(snake)
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

