import os
import readchar
import threading
import time
import random
import sys


maxObstacle = 2
playerRowPosition = 16
playerColPosition = 16
playerCharacter = "💃"
rows = []
screenWidth = 50
screenHeight = 20
floorRow = 19
obstacleList = []
floorIndicator = "󠁩󠁩󠁩_"
obstacleShape = "🚗"
actualFloor = "▒"
obstacleNearFlag = False
initialShouldJumpCountDown = 3
shouldJumpCountDown = initialShouldJumpCountDown
score = 0
exitFlag = False


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


player = PlayerPosition(10,5)


def initializeRowsAndCharacterOG():
    rows.append( PositionManager(["-" for i in range(screenWidth)]) )

    for i in range(screenHeight - 2):
        row = PositionManager([obstacleShape]+[" " for i in range(screenWidth - 2)]+[obstacleShape])
        rows.append(row)
    rows.append( PositionManager(["-" for i in range(screenWidth)]) )
    rows.append( PositionManager(["🟫" for i in range(screenWidth)]) )

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
    rows.append(PositionManager([actualFloor for i in range(screenWidth+3)]))

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


def jumpAnimation(jumpNo):
    if jumpNo == 0:
        rows[player.row].changeCharacter("_",player.column)
        rows[player.row].position_list.append("_")
    else:
        rows[player.row].changeCharacter(" ",player.column)
    player.jump()
    rows[player.row].changeCharacter(playerCharacter,player.column)

def duckAnimation(duckNo):
    rows[player.row].changeCharacter(" ",player.column)
    player.duck()
    rows[player.row].changeCharacter(playerCharacter,player.column)
    if(duckNo == 2):
        rows[player.row].position_list.pop(-1)
def checkForCollision():
    global shouldJumpCountDown,obstacleNearFlag

    if obstacleNearFlag:
        if(shouldJumpCountDown == 0):
            return True
        shouldJumpCountDown-=1
    return False


def listenInput():
    global shouldJumpCountDown,initialShouldJumpCountDown,obstacleNearFlag,exitFlag

    while True:
        key = readchar.readkey()
        if key == "w":
            shouldJumpCountDown = initialShouldJumpCountDown
            obstacleNearFlag = False
            for i in range(3):
                jumpAnimation(i)
                displayAt()
                time.sleep(0.20)
            moveObstacles()
            for i in range(3):
                duckAnimation(i)
                displayAt()
                time.sleep(0.17)
        elif key == "q":
            exitFlag = True
            sys.exit(1)


def addObstacle():
    rows[floorRow].changeCharacter(obstacleShape,screenWidth-1)

def moveObstacles():
    rows[floorRow].position_list.pop(0)
    rows[floorRow].position_list.append(floorIndicator)
    if(rows[floorRow].position_list[9] == playerCharacter):
        rows[floorRow].position_list[9] = floorIndicator

    rows[player.row].changeCharacter(playerCharacter,player.column)
def updateScore():
    global score
    score+=5
    rows[floorRow - 4].changeCharacter(str(score),23)
def mainLoop():
    global obstacleNearFlag,shouldJumpCountDown,exitFlag


    createScreen()
    thread = threading.Thread(target = listenInput,daemon = True)
    thread.start()
    initializeRowsAndCharacter()
    try:
        clock = 10
        while True:

            if(exitFlag == True):
                sys.exit(1)

            createScreen()
            displayAt()

            if(rows[floorRow].position_list[player.column + 3] == obstacleShape):
                obstacleNearFlag = True

            #with open("log.txt","a") as file:
                #file.write(f'obs near = {obstacleNearFlag} shd jump = {shouldJumpCountDown}\n')
                #file.write(f"{len(rows[floorRow].position_list)}\n")

            if(checkForCollision()):
                time.sleep(1)
                break

            if(clock > 8):
                if(random.randint(0,10) == 3):
                    addObstacle()
                    clock = 0

            moveObstacles()
            clock+=1
            updateScore()
            time.sleep(0.2)

    except KeyboardInterrupt:
        pass

    finally:
        returnScreenToNormal()
        print(f"you scored {score}")
if __name__ == "__main__":
    mainLoop()
