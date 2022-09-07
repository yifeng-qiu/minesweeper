import cv2
from engine import MineSweeper, GameGraphics


class GamePlay:
    def __init__(self, difficulty='Hard'):
        self.game = MineSweeper(difficulty=difficulty)
        self.gamegui = GameGraphics(self.game)
        self.mouse_event = None
        self.boardSize = self.gamegui.boardImg.shape
        self.windowName = 'MineSweeper'

    def start_game(self):
        cv2.namedWindow(self.windowName)
        x, y = self.gamegui.getWindowTopCornerCoordCenterAligned()
        print(x, y)
        # cv2.moveWindow(self.windowName, x=x, y=y)
        print(cv2.getWindowImageRect(self.windowName))
        cv2.setMouseCallback(self.windowName, self.mouse_callback)
        while True:
            if self.mouse_event:
                if self.mouse_event[0] == 'click' and self.game.judge(self.mouse_event[1]):
                    self.gamegui.draw_game_board()
                elif self.mouse_event[0] == 'flag' and self.game.flag_cell(self.mouse_event[1]):
                    self.gamegui.draw_game_board()
                self.mouse_event = None
            if self.game.status in ['won', 'lost']:
                board = self.gamegui.get_board()
                if self.game.status == 'won':
                    text = 'WON!'
                    textColor = (0, 255, 0)
                else:
                    text = 'LOST!'
                    textColor = (0, 0, 255)
                cv2.putText(board, text, (self.boardSize[1] // 2 + 20, self.boardSize[0] //
                            2 - 50), cv2.FONT_HERSHEY_PLAIN, 10, textColor, 10, cv2.LINE_AA)
                cv2.imshow(self.windowName, board)
            else:
                cv2.imshow(self.windowName, self.gamegui.get_board())
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == ord('R') or key == ord('r'):
                self.game.reset()
                self.gamegui.draw_game_board()
        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cell = self.gamegui.coord_to_cell((y, x))
            self.mouse_event = ['click', cell]
        elif event == cv2.EVENT_RBUTTONDOWN:
            cell = self.gamegui.coord_to_cell((y, x))
            self.mouse_event = ['flag', cell]


if __name__ == '__main__':
    game = GamePlay('Easy')
    game.start_game()
