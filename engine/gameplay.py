'''
Module implementing the game play logic. 
'''
import cv2
from engine import MineSweeper, GameGraphics, GestureController
import time

class CoolDown:
    def __init__(self, cmd, coolDownDuration):
        self.cmd = cmd
        self.coolDownDuration = coolDownDuration
        self.t0 = time.time()

    def expired(self):
        return (time.time() - self.t0) >= self.coolDownDuration

class GamePlay:
    def __init__(self, difficulty='Easy'):
        self.game = MineSweeper(difficulty=difficulty)
        self.gamegui = GameGraphics(self.game.getBoardSize())
        self.mouseEvent = None
        self.boardSize = self.gamegui.boardImg.shape
        self.windowName = 'MineSweeper'
        self.gestureController = GestureController()

    def startGame(self):
        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName, self.mouse_callback)
        self.gamegui.drawGameBoard(self.game.getPlayerBoard())
        self.gestureController.startController()
        self.gamegui.enableFocusBox()
        lastCell = (0, 0)
        self.lastExecutedCommand = None
        paused = False
        while True:
            x, y, _, _ = cv2.getWindowImageRect(self.windowName)
            """
            For whatever reason, imshow displays image at an arbitrary resolution.
            Also the function getWindowImageRect does not return the correct coordinate or window size
            even when the window gets resized. The dimension of the window stays the same as the display
            image. Therefore I can get y+h > screen height. This seems to be a problem with MacOS.
            """
            self.gamegui.setGameWindowTopLeftCoord(x, y) # get the top-left corner y-axis coordinate value
            # print(self.gestureController.currentCommand())
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                self.gestureController.close()
                break
            elif key == ord('R') or key == ord('r'):
                self.game.reset()
                self.gamegui.drawGameBoard(self.game.getPlayerBoard())
                self.lastExecutedCommand = None
                self.gamegui.gameStatusText = ''
            elif key == ord('f') or key == ord('F'):
                self.gamegui.enableFocusBox()
            elif key == ord('p'):
                paused = not paused
                if paused:
                    self.gamegui.gameStatusText = 'Paused'
                    cv2.imshow(self.windowName, self.gamegui.drawGameBoard())
                else:
                    self.gamegui.gameStatusText = ''
                

            if paused or self.game.status in ['win', 'lost']:
                continue
            
            updateBoard = False
            if self.gestureController.getCurrentCommand() == 'move':
                fingerPos = self.gestureController.lastPointerLocation
                fingerX = int(self.gamegui.screenSize.width * fingerPos[0])
                fingerY = int(self.gamegui.screenSize.height * fingerPos[1])
                if self.gamegui.fingerInsideGameWindow(fingerX, fingerY):
                    lastCell = self.gamegui.coordToCell(self.gamegui.getRelativeBoardCoord(fingerX, fingerY))
                    self.gamegui.setFocusBox(lastCell)
                    self.lastExecutedCommand = 'move'
                    self.gamegui.setLastExecutedCommand(f'x:{fingerX} y:{fingerY}')
            elif self.gestureController.getCurrentCommand() == 'click' and self.lastExecutedCommand != 'click':
                self.lastExecutedCommand = 'click'
                self.gamegui.setLastExecutedCommand('click')
                if self.game.judge(lastCell):
                    updateBoard = True
            elif self.gestureController.getCurrentCommand() == 'flag' and self.lastExecutedCommand != 'flag':
                self.lastExecutedCommand = 'flag'
                self.gamegui.setLastExecutedCommand('flag')
                if self.game.flagCell(lastCell):
                    updateBoard = True
            elif self.mouseEvent:
                if self.mouseEvent[0] == 'click' and self.game.judge(self.mouseEvent[1]):
                    updateBoard = True
                elif self.mouseEvent[0] == 'flag' and self.game.flagCell(self.mouseEvent[1]):
                    updateBoard = True
                self.mouseEvent = None
            
            if self.game.status in ['won', 'lost']:
                self.gamegui.gameStatusText = self.game.status.capitalize() + '!'
            if updateBoard:
                cv2.imshow(self.windowName, self.gamegui.drawGameBoard(self.game.getPlayerBoard()))
            else:
                cv2.imshow(self.windowName, self.gamegui.drawGameBoard())

        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cell = self.gamegui.coordToCell((y, x))
            self.mouseEvent = ['click', cell]
        elif event == cv2.EVENT_RBUTTONDOWN:
            cell = self.gamegui.coordToCell((y, x))
            self.mouseEvent = ['flag', cell]