import os
import readchar
import threading
import time
import random
import sys
import json


class Color:
    @staticmethod
    def red(text):
        return f'\033[31m{text}\033[0m'

    @staticmethod
    def green(text):
        return f'\033[32m{text}\033[0m'

    @staticmethod
    def yellow(text):
        return f'\033[34m{text}\033[0m'

    @staticmethod
    def blue(text):
        return f"\033[36m{text}\033[0m"

winSize = os.get_terminal_size()
playerCharacter = "o"
rows = []
screenWidth = winSize.columns
screenHeight = winSize.lines
floorRow = screenHeight - 1
floorIndicator = "󠁩󠁩󠁩_"
obstacleShape = "▒"
#added floor just for making it look good
actualFloor = "▒"
#json config
config = ""
score = 0
exitFlag = False
#used to store copy of the obstacles to check for collison
collisionRow = []
collision = False
speed = 0.16
speedIncreasePoint = 500

class PlayerPosition:
    def __init__(self,row,column):
        self.row = row
        self.column = column
    def jump(self):
        self.row-=1
    def duck(self):
        self.row+=1

#contains lists used to represent the screen
class PositionManager:
    def __init__(self,li):
        self.position_list = li
    #changes the character at given index of the list
    def changeCharacter(self,newChar,column):
        self.position_list[column] = newChar


player = PlayerPosition(0,0)

def log(message):
    with open ("log.txt","a") as f:
        f.write(f"{message}\n")

def logCollision(message):
    global collisionRow

    log(f"{message}\n{''.join(collisionRow)}\n{''.join(rows[floorRow].position_list)}\n")

def getConfig():
    global config
    with open("config.json","r") as config:
        config = json.load(config)

def displayHighScore():
    global config
    rows[floorRow - 5].changeCharacter(Color.red(f"'q':quit"),1)
    rows[floorRow - 5].changeCharacter(Color.yellow(f"high score: {str(config['game_details']['highscore'])}"),int(screenWidth/2)-16)


def initializeRandomObstacles(obstacleLimit,minPosition,listLength):
    tempList = ["_" for i in range(listLength)]
    possibleObstacleCount = int((listLength - minPosition)/obstacleLimit)

    start = minPosition+7
    while ((start + obstacleLimit) < listLength):
        randomPosition = random.randint(start,start+obstacleLimit)
        tempList[randomPosition] = obstacleShape
        start += (obstacleLimit * 2)

    #log(f"obsLim:{obstacleLimit}:minPosition{minPosition}:listLength:{listLength}\n {''.join(tempList)}")
    return tempList

#set up the screen and initialize the lists used to represent the screen
def initializeRowsAndCharacter():
    global collisionRow

    getConfig()

    #make list with " " elements to fill terminal screen
    for i in range(screenHeight - 1):
        row = PositionManager([" "]+[" " for i in range(screenWidth - 2)]+[" "])
        rows.append(row)
    #fill in the floor
    #floorRow = PositionManager([floorIndicator for i in range(screenWidth)])
    floorRow = PositionManager(initializeRandomObstacles(5,10,screenWidth))
    #copy the ground floor (where obstacles collide with player) to detect collsion
    collisionRow = list(floorRow.position_list)
    rows.append(floorRow)

    #fill in the decoration floor
    rows.append(PositionManager([actualFloor for i in range(screenWidth+3)]))

    player.row = screenHeight-1
    player.column = 10
    rows[player.row].changeCharacter(playerCharacter,player.column)


    #logCollision("start:")

    displayHighScore()

def createScreen():
    os.system("stty -echo")
    print("\033[2J\033[H\033[?25l")

def returnScreenToNormal():
    print("\033[?25h\033[2J\033[H")
    os.system("stty -echo")

#display each lists at each row by converting them into string
def displayAt():
    for row in rows:
        print(" "+"".join(row.position_list[:screenWidth-2]))


def jumpAnimation(jumpNo):
    global collisionRow


    #when jumping,player character is put in one row above the current row .so we have to delete player character from previous row. otherwise there would be multiple player characters on all the rows in jumping area

    #in first jump we have to restore the floor where the player was standing,since it's now visible again

    if jumpNo == 0:
        if collisionRow[player.column] == obstacleShape:
            rows[player.row].changeCharacter(obstacleShape,player.column)
        else:
            rows[player.row].changeCharacter(floorIndicator,player.column)
        collisionRow.append(floorIndicator)
        rows[player.row].position_list.append(floorIndicator)

    #if its not the first jump , that means player is already in the air , so we just have to -> draw " " on current position and move player one row up
    else:
        rows[player.row].changeCharacter(" ",player.column)
    player.jump()
    rows[player.row].changeCharacter(playerCharacter,player.column)

def gravityAnimation(duckNo):
    global collisionRow
    #logCollision("duck :")

    #just like jump we remove the previous positions of player but put the player one row down
    rows[player.row].changeCharacter(" ",player.column)
    player.duck()
    rows[player.row].changeCharacter(playerCharacter,player.column)
    if(duckNo == 2):
        rows[player.row].position_list.pop(-1)
        collisionRow.pop(-1)
    #logCollision("after duck :")

def checkForCollision():
    global collisionRow,floorRow
    if(player.row == floorRow and collisionRow[player.column] == obstacleShape):
        return True
    return False


def listenInput():
    global exitFlag,collisionRow,speed

    while True:
        key = readchar.readkey()
        if key == "w" or key == readchar.key.UP:
            for i in range(2):
                jumpAnimation(i)
                displayAt()
                time.sleep(speed+0.02)
            moveObstacles()
            for i in range(2):
                gravityAnimation(i)
                displayAt()
                if i < 1:
                    time.sleep(speed-0.01)
        elif key == "q":
            exitFlag = True
            sys.exit(1)


def addObstacle():
    global collisionRow
    rows[floorRow].changeCharacter(obstacleShape,screenWidth-1)
    collisionRow[screenWidth-1]=obstacleShape


def moveObstacles():
    global collisionRow
    #logCollision("move :")
    rows[floorRow].position_list.pop(0)
    collisionRow.pop(0)
    rows[floorRow].position_list.append(floorIndicator)
    collisionRow.append(floorIndicator)
    if(rows[floorRow].position_list[9] == playerCharacter):
        rows[floorRow].position_list[9] = floorIndicator

    rows[player.row].changeCharacter(playerCharacter,player.column)


def updateScore():
    global score
    rows[floorRow - 4].changeCharacter(Color.green(str(score)),int(screenWidth/2)-2)

def scoreUpdate():
    global score
    while True:
        score+=5
        time.sleep(0.2)

def mainLoop():

    global exitFlag,speed,speedIncreasePoint,collision,timer

    createScreen()
    thread = threading.Thread(target = listenInput,daemon = True)
    scoreThread = threading.Thread(target = scoreUpdate,daemon = True)
    scoreThread.start()
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

            if(checkForCollision()):
                time.sleep(0.1)
                break

            if(score>speedIncreasePoint):
                speed-=0.02
                speedIncreasePoint+=speedIncreasePoint

            if(clock > 5):
                if(random.randint(0,6) == 3):
                    addObstacle()
                    clock = 0

            moveObstacles()
            clock+=1
            updateScore()
            time.sleep(speed)
    except KeyboardInterrupt:
        pass

    finally:
        returnScreenToNormal()

        if(score > config["game_details"]["highscore"]):

            config["game_details"]["highscore"] = score
            with open("config.json","w") as orginalConf:
                json.dump(config,orginalConf)
            print(f"congrats! ... you got the new highscore of {score}")
        else:
            print(f"you scored: {score} , highscore:{config['game_details']['highscore']}")
if __name__ == "__main__":
    mainLoop()
