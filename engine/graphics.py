import cv2
import os
import csv
import numpy as np
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
ImgSize = namedtuple('Size', ['width', 'height'])
GameSize = namedtuple('Size', ['row', 'col'])

module_directory = os.path.dirname(os.path.abspath(__file__))
SCREEN_RESOLUTION = {
    'MBP-13 2020': [2560, 1600]
}


class GameGraphics:
    textureFile = os.path.join(module_directory, 'sprites', 'textures.png')
    textureMap = os.path.join(module_directory, 'sprites', 'texturemap.txt')

    def __init__(self, gameSize, system='MBP-13 2020'):
        self.system = system
        self.gameSize = gameSize
        self.cellSize = 200
        self.boardImg = None
        self.boardSize = None
        self.screenSize = ImgSize(*SCREEN_RESOLUTION[self.system])
        self.drawFocusBox = False
        self.focusBox = (0, 0)
        self.windowTopLeftCorner = None
        self.lastCommand = None
        self.gameStatusText = ''
        self.debugInfo = True
        self.loadTextures()
        self.gameBoardInit()

    def loadTextures(self):
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
        cellSize = int(min(self.screenSize.height * 0.8 // (self.gameSize.row),
                       self.screenSize.width * 0.9 // (self.gameSize.col)))
        self.cellSize = cellSize
        self.textures = {tName: cv2.resize(
            img, [cellSize, cellSize]) for tName, img in _textures.items()}

    def gameBoardInit(self):
        self.boardImg = np.zeros((self.gameSize.row * self.cellSize,
                                  self.gameSize.col * self.cellSize,
                                  3),
                                 dtype=np.uint8)
        self.boardSize = ImgSize(self.boardImg.shape[1], self.boardImg.shape[0])

    def drawGameBoard(self, board=None):
        if board:
            for r in range(self.gameSize.row):
                for c in range(self.gameSize.col):
                    self.boardImg[r*self.cellSize:(r+1) * self.cellSize,
                                c*self.cellSize:(c+1) * self.cellSize, :] =\
                        self.textures[str(board[r][c])]
        
        _img = self.boardImg.copy()

        if self.gameStatusText != '':
            cv2.putText(_img, self.gameStatusText, 
            (self.boardSize.width // 2 - 200, self.boardSize.height //2),
            cv2.FONT_HERSHEY_PLAIN, 10, (250, 114, 112), 10, cv2.LINE_AA)
        
        if self.drawFocusBox:
            row, col = self.focusBox
            pt1 = (col * self.cellSize, row * self.cellSize)
            pt2 = (pt1[0] + self.cellSize, (pt1[1] + self.cellSize))
            cv2.rectangle(_img, pt1, pt2, (255, 0, 0), 5, cv2.LINE_AA)
        
        if self.debugInfo and self.windowTopLeftCorner:
            # show window lower-left corner coordinate in the screen image
            # windowLocText = f'Game window lower-left corner x: {self.windowTopLeftCorner.x} y: {self.windowTopLeftCorner.y}'
            # cv2.putText(_img, windowLocText, (5, self.boardSize.height - 10), cv2.FONT_HERSHEY_SIMPLEX,
            #         1, (250, 114, 112), 2, cv2.LINE_AA)
            # show last executed command
            lastCmdText = f'Last recognized command {self.lastCommand}'
            cv2.putText(_img, lastCmdText, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 114, 112), 2, cv2.LINE_AA)            

        return _img       

    def coordToCell(self, coord):
        row, col = coord[0] // self.cellSize, coord[1] // self.cellSize
        row = max(0, min(row, self.gameSize.row - 1))
        col = max(0, min(col, self.gameSize.col - 1))
        return (row, col)

    def cellToCoord(self, cell):
        row, col = int((cell[0] + 0.5) * self.cellSize), int((cell[1] + 0.5) * self.cellSize)
        return (row, col)        
    
    def enableFocusBox(self):
        self.drawFocusBox = True
    
    def disableFocusBox(self):
        self.drawFocusBox = False

    def setFocusBox(self, cell):
        self.focusBox = cell

    def gameStatusText(self, text):
        self.gameStatusText = text

    def setGameWindowTopLeftCoord(self, x, y):
        y = self.screenSize.height - self.boardSize.height - y
        self.windowTopLeftCorner = Point(x, y)
    
    def setLastExecutedCommand(self, cmd):
        self.lastCommand = cmd

    def fingerInsideGameWindow(self, x, y):
        return (self.windowTopLeftCorner.x <= x <= self.windowTopLeftCorner.x + self.boardSize.width) and \
            (self.windowTopLeftCorner.y <= y <= self.windowTopLeftCorner.y + self.boardSize.height)
    
    def getRelativeBoardCoord(self, x, y):
        return (y - self.windowTopLeftCorner.y, x - self.windowTopLeftCorner.x)
