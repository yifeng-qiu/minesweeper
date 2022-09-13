'''
Author: Yifeng Qiu (https://github.com/yifeng-qiu)
Last updated: 2022-09-12

Play Minesweep with hand gesture. 

The game currently recongizes 3 hand gestures: pointer(index finger), open palm and fist
While in the pointer mode, the game tracks the position of the index finger tip and moves
between cells. The selected cell is highlighted by a blue box. 
An open palm gesture will open the currently selected cell, if compliant with game rules.
A fist gesture will flag the currently selected cell if the cell is currently masked. 
'''

from engine import GamePlay


if __name__ == '__main__':
    game = GamePlay('Easy')
    game.startGame()
