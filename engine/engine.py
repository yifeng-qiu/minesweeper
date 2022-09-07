"""
Module implementing the MineSweeper game logic.

Author:  Yifeng Qiu
Date: 2022-09-06
"""
import random
from collections import deque

GAME_DIFFICULTY_SETTING = {
    # board size, number of mines
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
        self.boardsize = GAME_DIFFICULTY_SETTING[difficulty][0]
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
        self._mask = [[self.MASKED] * self.boardsize[1]
                      for _ in range(self.boardsize[0])]
        self._field = [[0] * self.boardsize[1]
                       for _ in range(self.boardsize[0])]
        self._display = [['?'] * self.boardsize[1]
                         for _ in range(self.boardsize[0])]
        self._mines = None
        self._numbers = set()
        self._status = self.INIT

    def get_board(self):
        return self._display

    def get_board_size(self):
        return self.boardsize

    def generate_minefield(self, coord):
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
                0, self.boardsize[0]), random.randrange(0, self.boardsize[1])
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
                if 0 <= row < self.boardsize[0] and 0 <= col < self.boardsize[1] and \
                        self._field[row][col] != '*':
                    self._field[row][col] += 1
                    self._numbers.add((row, col))

        self._mines = _mines  # store coordinates of the mines

    def generate_displaymap(self):
        for r in range(self.boardsize[0]):
            for c in range(self.boardsize[1]):
                if self._mask[r][c] == self.MASKED:
                    self._display[r][c] = '?'
                elif self._mask[r][c] == self.FLAGGED:
                    self._display[r][c] = 'F'
                else:
                    self._display[r][c] = self._field[r][c]

    def show_board(self, masked=True):
        self.generate_displaymap()
        format_string = '{}|' + '\t{}' * self.boardsize[1]
        _map = self._display if masked else self._field
        print(format_string.format('R\C', *range(self.boardsize[1])))
        print(format_string.format('___', *['_']*self.boardsize[1]))
        for row_id, row in enumerate(_map):
            print(format_string.format(row_id, *row))

    def judge(self, coord):
        if self._status in [self.WON, self.LOST]:
            return False
        if self._status == self.INIT:
            self._status = self.PLAYING
            self.generate_minefield(coord)
        r, c = coord
        if self._mask[r][c] in [self.UNMASKED, self.FLAGGED]:
            # Clicking on an unmasked or flagged cell is not allowed
            return False
        elif self._field[r][c] == '*':
            # Clicking on a mine leads to immediate gameover
           
            self.unmask_all()  # Show the entire board to the user, unmasked
            self._status = self.LOST # Mark the game status lost
            self._field[r][c] = '**'  # Set the clicked bomb as exploding bomb

        else:
            self.clearmask((r, c))
            if len(self._numbers) == 0:
                self._status = self.WON
                self.unmask_all()
        self.generate_displaymap()
        return True

    def unmask_all(self):
        self._mask = [[self.UNMASKED]*self.boardsize[1]
                      for _ in range(self.boardsize[0])]

    def flag_cell(self, coord):
        if self._status in [self.WON, self.LOST]:
            return False
        r, c = coord
        if not (self._mask[r][c] == self.MASKED or 
                self._mask[r][c] == self.FLAGGED):
            return False
        if self._mask[r][c] == self.MASKED:
            self._mask[r][c] = self.FLAGGED
        elif self._mask[r][c] == self.FLAGGED:
            self._mask[r][c] = self.MASKED
        self.generate_displaymap()
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
                    if (0 <= nr < self.boardsize[0] and 0 <= nc < self.boardsize[1]) and\
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
