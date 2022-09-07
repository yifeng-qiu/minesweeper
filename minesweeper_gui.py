import cv2
from engine import MineSweeper, GameGraphics, FingerController


class GamePlay:
    def __init__(self, difficulty='Hard'):
        self.game = MineSweeper(difficulty=difficulty)
        self.gamegui = GameGraphics(self.game)
        self.mouse_event = None
        self.boardSize = self.gamegui.boardImg.shape
        self.windowName = 'MineSweeper'
        self.fingerController = FingerController()

    def start_game(self):
        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName, self.mouse_callback)
        self.fingerController.start_controller()
        self.gamegui.toggle_focus_box()

        while True:
            x, y, _, _ = cv2.getWindowImageRect(self.windowName)
            y = self.gamegui.screen_height - self.boardSize[0] - y  # get the top-right corner y-axis coordinate value
            fingerPos = self.fingerController.get_finger_pos() # this is a triplet of floating values between 0 and 1
            """
                First we calculate the position of the index finger on the screen
                Then we derive the finger position once it moves inside the game 
            """
            
            fingerX = int(self.gamegui.screen_width * fingerPos[0])
            fingerY = int(self.gamegui.screen_height * fingerPos[1])
            if x <fingerX< (x + self.boardSize[1]) and y < fingerY < (y + self.boardSize[0]):
                cell = self.gamegui.coord_to_cell((fingerY - y, fingerX - x))
                self.gamegui.set_focus_box(cell)

            self.gamegui.add_text('x: {} y: {}'.format(x, y), (5, self.boardSize[0] - 10), (0, 255, 0), seq=0)
            self.gamegui.add_text('Finger pos x {} y {}'.format(fingerX, fingerY), (5, 20), (0, 255, 0), seq=1)
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
                cv2.putText(board, text, (self.boardSize[1] // 2 -200, self.boardSize[0] //
                            2), cv2.FONT_HERSHEY_PLAIN, 10, textColor, 10, cv2.LINE_AA)
                cv2.imshow(self.windowName, board)
            else:
                cv2.imshow(self.windowName, self.gamegui.get_board())
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == ord('R') or key == ord('r'):
                self.game.reset()
                self.gamegui.draw_game_board()
            elif key == ord('f') or key == ord('F'):
                self.gamegui.toggle_focus_box()
        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cell = self.gamegui.coord_to_cell((y, x))
            self.mouse_event = ['click', cell]
        elif event == cv2.EVENT_RBUTTONDOWN:
            cell = self.gamegui.coord_to_cell((y, x))
            self.mouse_event = ['flag', cell]
        # elif event == cv2.EVENT_MOUSEMOVE:
        #     cell = self.gamegui.coord_to_cell((y, x))
        #     self.gamegui.set_focus_box(cell)


if __name__ == '__main__':
    game = GamePlay('Easy')
    game.start_game()
