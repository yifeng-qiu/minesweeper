import cv2
import os
import csv
import numpy as np

module_directory = os.path.dirname(os.path.abspath(__file__))
SCREEN_RESOLUTION = {
    'MBP-13 2020': [1600, 2560]
}


class GameGraphics:
    textureFile = os.path.join(module_directory, 'sprites', 'textures.png')
    textureMap = os.path.join(module_directory, 'sprites', 'texturemap.txt')

    def __init__(self, game, system='MBP-13 2020'):

        self.game = game
        self.system = system
        self.board_row, self.board_col = self.game.get_board_size()
        self.cellSize = 200
        self.boardImg = None
        self.text = [None, None]
        self.drawFocusBox = False
        self.focusBox = (0, 0)
        self.load_textures()
        self.game_board_init()
        self.draw_game_board()

    def load_textures(self):
        with open(self.textureMap, 'r', newline='') as fp:
            csvreader = csv.reader(fp, delimiter=',')
            try:
                textureMapping = {
                    row[0]: [int(row[1]), int(row[2])] for row in csvreader}
            except:
                print('Failed to load texture mapping.')
                exit(1)

        _textureImg = cv2.imread(self.textureFile, cv2.IMREAD_COLOR)
        _textures = {tName: _textureImg[coord[0]:coord[0]+self.cellSize,
                                        coord[1]:coord[1]+self.cellSize]
                     for tName, coord in textureMapping.items()}

        # determine texture size from screen resolution and board configuration
        screen_height, screen_width = SCREEN_RESOLUTION[self.system]
        self.screen_height = screen_height
        self.screen_width = screen_width
        cellSize = int(min(screen_height * 0.8 // (self.board_row),
                       screen_width * 0.9 // (self.board_col)))
        self.cellSize = cellSize
        self.textures = {tName: cv2.resize(
            img, [cellSize, cellSize]) for tName, img in _textures.items()}

    def game_board_init(self):
        self.boardImg = np.zeros((self.board_row * self.cellSize,
                                  self.board_col * self.cellSize,
                                  3),
                                 dtype=np.uint8)

    def draw_game_board(self):
        board = self.game.get_board()
        for r in range(self.board_row):
            for c in range(self.board_col):
                self.boardImg[r*self.cellSize:(r+1) * self.cellSize,
                              c*self.cellSize:(c+1) * self.cellSize, :] =\
                    self.textures[str(board[r][c])]

    def get_board(self):
        _img = self.boardImg.copy()
        if self.text is not None:
            for text in self.text:
                if text is not None:
                    cv2.putText(_img, text[0], text[1], cv2.FONT_HERSHEY_SIMPLEX,
                    1, text[2], 2, cv2.LINE_AA)
        
        if self.drawFocusBox:
            row, col = self.focusBox
            pt1 = (col * self.cellSize, row * self.cellSize)
            pt2 = (pt1[0] + self.cellSize, (pt1[1] + self.cellSize))
            cv2.rectangle(_img, pt1, pt2, (255, 0, 0), 5, cv2.LINE_AA)
        return _img


    def coord_to_cell(self, coord):
        row, col = coord[0] // self.cellSize, coord[1] // self.cellSize
        if row <0:
            row =0
        elif row > self.board_row - 1:
            row = self.board_row - 1
        
        if col <0:
            col = 0
        elif col > self.board_col - 1:
            col = self.board_col - 1
        return (row, col)

    def getWindowTopCornerCoordCenterAligned(self):
        screen_height, screen_width = SCREEN_RESOLUTION[self.system]
        board_height, board_width = self.boardImg.shape[:2]
        x = int((screen_width - board_width) // 3)
        y = int((screen_height - board_height) // 2)
        return (x, y)

    def add_text(self, text, coord, color, seq=0):
        self.text[seq] = [text, coord, color]
    
    def toggle_focus_box(self):
        self.drawFocusBox = not self.drawFocusBox
    
    def set_focus_box(self, cell):
        self.focusBox = cell
    
