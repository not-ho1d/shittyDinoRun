import os
import readchar
import threading
import time
import random

maxObstacle = 2
playerRowPosition = 16
playerColPosition = 16
playerCharacter = "O"
rows = []
screenWidth = 50
screenHeight = 20
floorRow = 19
obstacleList = []
floorIndicator = "_"


class PlayerPosition:
    def __init__(self,row,column):
        self.row = row
        self.column = column
    def jump(self):
        self.row-=1
    def duck(self):
        self.row+=1

class PositionManager:
    def __init__(self,li):
        self.position_list = li
    def changeCharacter(self,newChar,column):
        self.position_list[column] = newChar

class Obstacle:
    def __init__(self,obstacleShape = "█"):
        self.obstacleShape = obstacleShape
        self.rowPosition = floorRow
        self.colPosition = screenWidth - 1

player = PlayerPosition(10,5)


def initializeRowsAndCharacterOG():
    rows.append( PositionManager(["-" for i in range(screenWidth)]) )

    for i in range(screenHeight - 2):
        row = PositionManager(["█"]+[" " for i in range(screenWidth - 2)]+["█"])
        rows.append(row)
    rows.append( PositionManager(["-" for i in range(screenWidth)]) )

    player.row = int(screenHeight / 2)
    player.column = 10
    rows[player.row].changeCharacter(playerCharacter,player.column)

def initializeRowsAndCharacter():
    rows.append( PositionManager([" " for i in range(screenWidth)]) )

    for i in range(screenHeight - 2):
        row = PositionManager([" "]+[" " for i in range(screenWidth - 2)]+[" "])
        rows.append(row)
    floorRow = PositionManager([floorIndicator for i in range(screenWidth)])
    rows.append(floorRow)

    player.row = 19
    player.column = 10
    rows[player.row].changeCharacter(playerCharacter,player.column)

def createScreen():
    os.system("stty -echo")
    print("\033[2J\033[H\033[?25l")

def returnScreenToNormal():
    print("\033[?25h\033[2J\033[H")
    os.system("stty -echo")

def displayAt():
    for row in rows:
        print("".join(row.position_list))


def jumpAnimation():
    rows[player.row].changeCharacter(" ",player.column)
    player.jump()
    rows[player.row].changeCharacter(playerCharacter,player.column)
    if(rows[floorRow].position_list[10]==" "):
        rows[floorRow].changeCharacter(floorIndicator,player.column)

def duckAnimation():
    rows[player.row].changeCharacter(" ",player.column)
    player.duck()
    rows[player.row].changeCharacter(playerCharacter,player.column)

def listenInput():
    while True:
        key = readchar.readkey()
        if key == "w":
            for i in range(3):
                jumpAnimation()
                displayAt()
                time.sleep(0.20)
            for i in range(3):
                duckAnimation()
                displayAt()
                time.sleep(0.17)

def addObstacle():
    obstacleShape = "█"
    rows[floorRow].changeCharacter(obstacleShape,screenWidth-1)

def moveObstacles():
    rows[floorRow].position_list.pop(0)
    rows[floorRow].position_list.append(floorIndicator)
    if(rows[floorRow].position_list[9] == "O"):
        rows[floorRow].position_list[9] = floorIndicator

    rows[player.row].changeCharacter("O",player.column)

def mainLoop():
    createScreen()
    thread = threading.Thread(target = listenInput,daemon = True)
    thread.start()
    initializeRowsAndCharacter()
    try:
        luckCount = 0
        while True:
            createScreen()
            displayAt()

            if(random.randint(0,5) == 3):
                luckCount+=1
            if(luckCount > 3):
                luckCount = 0
                addObstacle()
            else:
                moveObstacles()
            time.sleep(0.15)

    except KeyboardInterrupt:
        pass

    finally:
        returnScreenToNormal()

if __name__ == "__main__":
    mainLoop()
