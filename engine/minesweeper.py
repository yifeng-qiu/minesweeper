"""
Module implementing the MineSweeper game logic.

Author:  Yifeng Qiu
Date: 2022-09-06
"""
import random
from collections import deque
from collections import namedtuple

GameSize = namedtuple('Size', ['row', 'col'])

GAME_DIFFICULTY_SETTING = {
    # board size (row, col), number of mines
    'Easy': [(9, 9), 10],
    'Intermediate': [(16, 16), 40],
    'Hard': [(16, 30), 99]
}


class MineSweeper():
    WON = 0b11
    LOST = 0b10
    PLAYING = 0b01
    INIT = 0b00

    FLAGGED = 2
    MASKED = 1
    UNMASKED = 0

    def __init__(self, difficulty='Easy') -> None:
        """
        Initialize a new Minesweeper game
        :param size: the width and the length of the game map
        :param mines: the number of mines for the game 
        :return: None
        """
        self.boardSize = GameSize(*GAME_DIFFICULTY_SETTING[difficulty][0])
        self.mineCount = GAME_DIFFICULTY_SETTING[difficulty][1]
        self.difficulty = difficulty
        self.reset()

    @property
    def status(self):
        if self._status == self.LOST:
            return 'lost'
        elif self._status == self.WON:
            return 'won'
        else:
            return 'playing'

    def reset(self):
        self._mask = [[self.MASKED] * self.boardSize.col
                      for _ in range(self.boardSize.row)]
        self._field = [[0] * self.boardSize.col
                       for _ in range(self.boardSize.row)]
        self._display = [['?'] * self.boardSize.col
                         for _ in range(self.boardSize.row)]
        self._mines = None
        self._numbers = set()
        self._status = self.INIT

    def getPlayerBoard(self):
        return self._display

    def getBoardSize(self):
        return self.boardSize

    def generateMineField(self, coord):
        """
        Randomly generate locations for the mines and populate the cells around mines with numbers
        indicating the number of mines in their 3x3 vicinity 
        This function is called at the first user input. The mines are generated at least two cells
        away from the user input coordinate.
        """
        _mines = set()
        r, c = coord
        # set the distance to the nearest mine based on difficulty
        distance_to_mine = 1 if self.difficulty == 'Hard' else 2
        # repeatedly generate mines until enough qualified ones have been generated.
        while len(_mines) < self.mineCount:
            row, col = random.randrange(
                0, self.boardSize.row), random.randrange(0, self.boardSize.col)
            if abs(row - r) >= distance_to_mine and abs(col - c) >= distance_to_mine:
                _mines.add((row, col))

        # place the mines on the board
        for mine in _mines:
            r, c = mine
            self._field[r][c] = '*'
        # All mines must be placed first before calculating the numbers.
        for mine in _mines:
            r, c = mine
            for (row, col) in self._neighbors(r, c):
                if 0 <= row < self.boardSize.row and 0 <= col < self.boardSize.col and \
                        self._field[row][col] != '*':
                    self._field[row][col] += 1
                    self._numbers.add((row, col))

        self._mines = _mines  # store coordinates of the mines

    def generatePlayerBoard(self):
        for r in range(self.boardSize.row):
            for c in range(self.boardSize.col):
                if self._mask[r][c] == self.MASKED:
                    self._display[r][c] = '?'
                elif self._mask[r][c] == self.FLAGGED:
                    self._display[r][c] = 'F'
                else:
                    self._display[r][c] = self._field[r][c]

    def showBoard(self, masked=True):
        self.generatePlayerBoard()
        format_string = '{}|' + '\t{}' * self.boardSize.col
        _map = self._display if masked else self._field
        print(format_string.format('R\C', *range(self.boardSize.col)))
        print(format_string.format('___', *['_']*self.boardSize.col))
        for row_id, row in enumerate(_map):
            print(format_string.format(row_id, *row))

    def judge(self, coord):
        if self._status in [self.WON, self.LOST]:
            return False
        if self._status == self.INIT:
            self._status = self.PLAYING
            self.generateMineField(coord)
        r, c = coord
        if self._mask[r][c] in [self.UNMASKED, self.FLAGGED]:
            # Clicking on an unmasked or flagged cell is not allowed
            return False
        elif self._field[r][c] == '*':
            # Clicking on a mine leads to immediate gameover
           
            self.unmaskAll()  # Show the entire board to the user, unmasked
            self._status = self.LOST # Mark the game status lost
            self._field[r][c] = '**'  # Set the clicked bomb as exploding bomb

        else:
            self.clearmask((r, c))
            if len(self._numbers) == 0:
                self._status = self.WON
                self.unmaskAll()
        self.generatePlayerBoard()
        return True

    def unmaskAll(self):
        self._mask = [[self.UNMASKED]*self.boardSize.col
                      for _ in range(self.boardSize.row)]

    def flagCell(self, coord):
        if self._status in [self.WON, self.LOST, self.INIT]:
            # flag action is only allowed while the game is in progress
            return False
        r, c = coord
        if not (self._mask[r][c] == self.MASKED or 
                self._mask[r][c] == self.FLAGGED):
            return False
        if self._mask[r][c] == self.MASKED:
            self._mask[r][c] = self.FLAGGED
        elif self._mask[r][c] == self.FLAGGED:
            self._mask[r][c] = self.MASKED
        self.generatePlayerBoard()
        return True

    def clearmask(self, coord):
        r, c = coord
        queue = deque()
        queue.append((r, c))
        while len(queue) > 0:
            r, c = queue.popleft()
            self._mask[r][c] = self.UNMASKED
            if self._field[r][c] == 0:
                # propagate around cells with 0
                for (nr, nc) in self._neighbors(r, c):
                    if (0 <= nr < self.boardSize.row and 0 <= nc < self.boardSize.col) and\
                        self._mask[nr][nc] == self.MASKED and self._field[nr][nc] != '*':
                        if self._field[nr][nc] == 0:
                            queue.append((nr, nc))
                        else:
                            self._mask[nr][nc] = self.UNMASKED
                            self._numbers.remove((nr, nc))
            else:
                self._numbers.remove((r, c))

    def _neighbors(self, r, c):
        return [(r-1, c-1), (r-1, c), (r-1, c+1), (r, c-1),
                (r, c+1), (r+1, c-1), (r+1, c), (r+1, c+1)]
