import random
import time  
import datetime
import pickle
import sys
from database import dataBase
from Files import readFile



class Display(): ##Class responsible for all the displays
    global bridgeGame
    def __init__(self,numImages,numObjects): ##Initilizes the class, receives the number of images/buttons and receives the number of all non button items to be displayed(mostly texts)
        self.numImages = numImages
        self.numObjects = numObjects
        self.activeStuff = [False for i in range(numImages+numObjects)]
        self.dataBank = []
        self.fList = []
        self.addingName = True

        self.lastScreen = self.startMode
        
    def showStuff(self): ##Display images
        for i in range(self.numImages):
            if self.activeStuff[i]:
                #if i == self.numImages-1:
                myImage = self.dataBank[i]
                image(myImage[1],myImage[0][0],myImage[0][1],myImage[0][2],myImage[0][3])
                
    def checkClick(self): #Check click for buttons
        for i in range(self.numImages-1,-1,-1):
            if self.activeStuff[i]:
                button = self.dataBank[i]
                if button[2] != -1:
                    inX = button[0][0] < mouseX < (button[0][0] + button[0][2])
                    inY = button[0][1] < mouseY < (button[0][1] + button[0][3])
                    if inX and inY:
                        self.fList[button[2]]()
                        return(True)
                            
    def reset(self): #Reset display
        self.activeStuff = [False for i in range(self.numImages+self.numObjects)]
        
    def toggle(self,toggleList): #change displayed elements, receives a list of indexes to toggle
        for i in toggleList:
            self.activeStuff[i] = not(self.activeStuff[i])

    def turnOn(self,onList): #change display status, receives a list of indexes to turn on 
        self.reset()
        for i in onList:
            self.activeStuff[i] = True
            
    def softNameMode(self):#Changes to names Mode without reseting 
        self.turnOn([-2,6])
        
    def nameMode(self): #Changes Display to names Mode
        self.turnOn([-2,6])
        self.lastScreen = self.softNameMode
        DBmyInputs.reset()
        bridgeGame.__init__()
        bridgeGame.bidXY = [MYDISPLAY.dataBank[7][0][0],MYDISPLAY.dataBank[7][0][1]]
    
    def startMode(self): #Changes Display to start Mode
        for player in bridgeGame.players:
            player.name = ""
            player.number = ""
        self.lastScreen = self.startMode
        self.turnOn([0,1,2,12])
        
    def bidMode(self): #Changes Display to bidding process
        self.lastScreen = self.bidMode
        self.turnOn([6,7,-3,-4,-7])
    
    def playMode(self): #Changes Display to playing tricks mode
        self.lastScreen = self.playMode
        self.turnOn([5,6,-1,-3])
        
    def helpMode(self): #Changes Display to help menu
        self.turnOn([3,4])
        
    def scoresMode(self): #Changes Display to high scores
        self.turnOn([4,-6])
        
    def winScreen(self): #Changes Display to screen after winning
        self.turnOn([11,6,-5])
        self.lastScreen = self.winScreen
        
    def returnScreen(self): #returning to last screen
        self.lastScreen()
        
    def exitMode(self):
        self.turnOn([-8])
        
    def pause(self): #pause the game
        self.toggle([8,9,10,13,14])
        
    #these 1-line methods are needed so they can be held and called in variables
        
        
class Game():
    global MYDISPLAY,DBmyInputs
    global cardSuits
    def __init__(self): #initializes the game
        self.scores = stringToDict()
        self.sortedKeyList = self.scores.keys()
        self.sortedKeyList.sort()
        self.numScores = len(self.scores)
        self.bidXY = []
        self.numPlayers = 4
        self.NS = 0 #North and South Score
        self.EW = 0 #East and West Score
        self.NSCap = -1 #Tricks needs to be winned by North and South
        self.trump = ''
        self.players = [Player() for i in range(self.numPlayers)]
        self.curPlayer = 0
        self.deal()
        self.inputPlayer = 0
        self.count = 0
        self.cardsPlayed = ['' for i in range (self.numPlayers)]
        self.curSuit = ''
        self.highestBid = [-1, -1, -1] #0-6 value, 0-4 is suit, 5*value+suit
        self.passCounter = 0
        self.bidWinner = ""
        self.winner = ""
        self.displayCards = [100,200]
        self.pause = False
        self.card = Card(1,1)
        
    def deal (self): #deals the cards, fills each player object's self.hand
        go = True
        while go:
            cnt = 0
            deck = [[False for i in range (13)] for j in range (4)]
            hands = [[],[],[],[]]
            while (cnt<52):
                suit = random.randint(0, 3)
                val = random.randint(0, 12)
                if (deck[suit][val]): continue
                hands[cnt//13].append(Card(suit, val))
                deck[suit][val] = True
                cnt+=1
            for i in range (self.numPlayers):
                self.players[i].hand = hands[i]
                self.players[i].Sort(hands[i])
            go = not self.openningBidder()
        
    
    def openningBidder(self): #check if the opening bidder has 13 points, returns a bool of if the current player can bid
        for i in range (self.numPlayers):
            pts = 0
            for j in range (len(self.players[i].hand)):
                if self.players[i].hand[j].value>8:
                    pts+= self.players[i].hand[j].value-8
            #print (pts, 'num', i)
            if pts >=13:
                self.curPlayer = i
                return (True)
        return (False)
        
    def playerBids(self): #bidding function
        if not MYDISPLAY.activeStuff[10]:
            if (mouseY-self.bidXY[1]>407):
                self.passCounter += 1
                self.curPlayer = (self.curPlayer+1)%4
                if self.passCounter == 3:
                    if self.highestBid != [-1,-1,-1]:
                        self.trump = cardSuits[self.highestBid[0]]
                        if (self.curPlayer == 0 or self.curPlayer == 2):
                            self.NSCap = self.highestBid[1]+6
                        else:
                            self.NSCap = 7 - self.highestBid[1]
                        MYDISPLAY.playMode()
                elif self.passCounter == 4:
                    self.deal()
                    self.passCounter = 0
            else:
                x = 4 - (mouseX-self.bidXY[0])//113
                y = (mouseY-self.bidXY[1])//57
                if (y*5 + x) > self.highestBid[2]: 
                    self.highestBid = [x,y,y*5 + x]
                    self.passCounter = 0
                    self.curPlayer = (self.curPlayer+1)%4
                else:
                    pass
                
    def play(self, starter): #playing tricks, returns the winner of the trick if there have been 4 cards played
        global card
        self.display()
        if self.count<self.numPlayers:
            if self.count == 3:
                self.pause = True
            self.curPlayer = self.count+starter - 4 if self.count+starter-4>=0 else self.count+starter 
            for i in range(1,5):
                showPlayer = (bridgeGame.curPlayer - i)%4
                bridgeGame.showCards(showPlayer,520+(20*i))
            if (self.cardsPlayed[self.curPlayer] != ''):
                self.count+=1
                if (self.curPlayer == starter):
                    self.curSuit = self.cardsPlayed[self.curPlayer].suit
            return(-1)
        curSuit = self.cardsPlayed[starter].suit
        if not self.pause:
            winner = trickWinner (self.cardsPlayed, curSuit, self.trump)
            self.cardsPlayed = ['' for i in range (4)]
            self.count = 0
            if winner == 0 or winner == 2:
                self.NS += 1
            else:
                self.EW += 1
            self.checkWin()
            return (winner)
    
    def checkWin(self): #check who wins the game
        if (self.NS + self.EW) == 13:
            if self.NS >= self.NSCap:
                self.winner = "NS"
            else:
                self.winner = "EW"
            MYDISPLAY.winScreen()
            self.addToWinner()
            
    def addToWinner(self): #adding to high score document
        if self.winner == "NS":
            winners = [self.players[0],self.players[2]]
        else:
            winners = [self.players[1],self.players[3]]
            
        DBmyInputs.updateScores(winners)
    
    def display(self): #displaying the cards played
        for i in range(self.numPlayers):
            if self.cardsPlayed[i] == "": continue
            self.cardsPlayed[i].showCard(self.displayCards[0]+(i%2)*700, self.displayCards[1] + (i//2)*100)
        
    def showCards(self, playerNum,Y): #showing the hand, receives which players hand to show and the Y value of where to show it
        hand = self.players[playerNum].hand
        numCards = len(hand)
        startX = (width - numCards*(self.card.w+2))/2
        for i in range (numCards):
            x = startX + i*(self.players[playerNum].hand[i].w-1)
            y = Y
            self.players[playerNum].hand[i].showCard(x, y)
            
    def playCard(self): #playing the card
        if self.count > 3:
            return()
        numCards  = len(self.players[self.curPlayer].hand)
        startX = (width - numCards*(self.card.w-1))/2
        for i in range (numCards):
            x = startX + i*(self.card.w-1)
            y = height-(self.card.h)
            if x<mouseX and mouseX<x+(self.card.w+2) and mouseY>y and mouseY<height and self.players[self.curPlayer].cardPlayable(self.players[self.curPlayer].hand[i], self.curSuit):
                self.cardsPlayed[self.curPlayer] = self.players[self.curPlayer].hand.pop(i)
                break
            
    def enterName(self,data): #entering the name for the player, receives the data to be entered as the name
        player = self.players[self.inputPlayer]
        player.number = data[0]
        player.nameF = data[1]
        player.nameL = data[2]
        
    def checkTaken(self,data): #check if name is taken,  receives the data to be entered as the name, returns a bool of if its taken
        num = data[0]
        nameF = data[1]
        nameL = data[2]
        for player in self.players:
            if player.nameF != "" and player.number != "":
                if (player.nameF == nameF and player.nameL == nameL) or (player.number == num):
                    return(True)
        return(False)
        
                
class Player():
    def __init__(self):
        self.hand = []
        self.nameF = ""
        self.nameL = ""
        self.number = ""
        
    def cardPlayable(self, card, curSuit): #check if card is playable, receives the card and the current suit thats allowed to be played, returns of the card is playable
        if (card.suit == curSuit): return True
        hasCard = False
        for i in range (len(self.hand)):
            if self.hand[i].suit == curSuit:
                hasCard = True
        if (not hasCard): return True
        return False
    
    def Sort(self, Hand): #sorts the hand, receives the hand
        dict = {}
        arr = []
        for i in range (len(self.hand)):
            dict[self.hand[i].Size] = i
            arr.append (self.hand[i].Size)
        arr.sort()
        for i in range (len(self.hand)):
            arr[i] = Hand[dict.get(arr[i])]
        self.hand = arr

        
class Card():
    global cardSuits,cardValues,cards
    def __init__(self, suit, value):
        self.suit = cardSuits [suit]
        self.suitNum = suit
        self.value = value #self.cardNumVal[value]
        self.w = 73
        self.h = 98
        self.Size = self.suitNum*13+self.value
    
    def showCard(self, x, y): #displays card, receives its x and y coordinates
        image(cards, x, y, self.w,self.h,self.w * self.value,self.h * self.suitNum,self.w * (self.value + 1), self.h * (self.suitNum + 1))
            
def compareCards (card1, card2, curSuit, trump): #compares two cards, receives thes cards, and the trump, returns the higher card
    if (card1.suit == card2.suit):
        if (card1.value>card2.value):
            return (card1)
        return card2
    if (card1.suit == trump):
        return (card1)
    if (card2.suit == trump):
        return (card2)
    if (card1.suit == curSuit):
        return (card1)
    if (card2.suit == curSuit):
        return (card2)
    return (card1)

def trickWinner (cardsPlayed, curSuit, trump): #determines who wins the trick, receives the cards played, trump and current suit, returns the winner
    winnerCard = cardsPlayed [0]
    n = len(cardsPlayed)
    winner = 0
    for i in range (1, n):
        if winnerCard != compareCards (winnerCard, cardsPlayed[i], curSuit, trump):
            winner = i
            winnerCard = compareCards(winnerCard, cardsPlayed[i], curSuit, trump)
    return (winner)

def stringToData(string): #convert string from text to usable data, receives a string, returns a list of the data
    string = string.strip().split("/")
    numbers = list(map(int,string[0].split(",")))
    img = loadImage(string[1])
    func = int(string[2])
    return([numbers,img,func])
    
def stringToDict(): #convert string to dict, receives a string, returns a dict of the data
    myLine = loadStrings("myOutputFile.txt")
    if len(myLine) == 0:
        return({})
    myLine = myLine[0][1:].strip().split()
    numKey = len(myLine)
    myDic = {}
    for i in range(numKey):
        myLine[i] = myLine[i].split(",")
        myDic[myLine[i][0]] = int(myLine[i][1])
    return(myDic)

def showAnimation():#shows the exit animation
    global showX,showY,showW,showH,incrX,incrY,bridgePNG
    
    image(bridgePNG,showX,showY,showW,showH)
    showX += incrX
    showY += incrY
    if showX < 0 or (showX + showW) > width:
        incrX = -incrX
    if showY < 0 or (showY + showH) > height:
        incrY = -incrY
    if showX < 0:
        showX = 0
    if showX > width:
        showX = width
    if showY < 0:
        showY = 0
    if showX > height:
        showX = height

    
def setup():
    global MYDISPLAY,bridgeGame,cards,firstPlayer
    global acceptedChars,acceptedNums,nameMaxLen,numberMaxLen
    global cards
    global playerList
    global myTextSize
    global cardSuits,cardValues
    global showX,showY,showW,showH,incrX,incrY,bridgePNG
    global animationCounter,animationMax
    global DBmyInputs
    global DBtextX,DBYVals,DBdisWords, textLocation, whichMsg
    
    size(1000,700)
    
    fill(0)
    myTextSize = 30
    textSize(myTextSize)
    
    DBtextX = 100
    DBinputsX = 300
    
    DBstudentNumY = 200
    DBfNameY = 300
    DBlNameY = 400
    
    DBinputsW = 300
    DBinputsH = 50
    
    DBXVals = [ DBtextX,DBinputsX ]
    DBYVals = [ DBstudentNumY,DBfNameY,DBlNameY,400,500 ]  
    DBdisWords = [ "Student #","First Name", "Last Name"]
    
    DBdata = []
    for i in range(3):
        DBdata.append([DBinputsX,DBYVals[i],DBinputsX + DBinputsW,DBYVals[i] + DBinputsH])
        
    DBdata.append([300,500,450,550])
    
    DBdataBank = {}
    DBinArr = []
    
    text("Loading...",0,0,width,height)
    
    #Assumes that if any of the files don't exist, all of them dont exist
    try:
        DBdataBank = pickle.load(open("dataBank.txt", "rb"))
        DBinArr = pickle.load(open("indirectarray.txt", "rb"))
        scores = pickle.load(open("highscore.txt","rb"))
    except:
        SETUP = readFile("setup.txt")
        if SETUP == None:
            print("Can't Open Program")
            sys.exit()
        while SETUP[-1] == '':
            SETUP.pop()
        highscore = open("highscore.txt","wb")
        indirectarray = open("indirectarray.txt","wb")
        databank = open("databank.txt","wb")
        report = open("report.txt","w+")
        report.write("Setup: " + str(datetime.datetime.today())[:10] + "_______________________\n")
        report.write("Setup Players:_____\n")
        scores = []
        DBinArr = []
        DBdataBank = {}
        for myLine in SETUP:
            myList = myLine.split(",")
            myList[1] = myList[1].upper()
            myList[2] = myList[2].upper()
            scores.append([int(myList[3]),myList[0]])
            DBinArr.append([myList[1] + "/" + myList[2],myList[0]])
            DBdataBank[myList[0]] = [myList[1],myList[2],int(myList[3]),myList[4]]
            report.write(myList[1] + " " + myList[2] + "/" + myList[0] +"\n")
        scores.sort(reverse = True)
        DBinArr.sort()
        pickle.dump(scores,highscore)
        pickle.dump(DBinArr,indirectarray) 
        pickle.dump(DBdataBank,databank)
        report.close()
        highscore.close()
        indirectarray.close()
        databank.close()
        DBdataBank = pickle.load(open("dataBank.txt", "rb"))
        DBinArr = pickle.load(open("indirectarray.txt", "rb"))
        scores = pickle.load(open("highscore.txt","rb"))
                    
    
    print("DataBank:",DBdataBank)
    print("______________________________________________________________________")
    print("Indirect Array:",DBinArr)
    print("______________________________________________________________________")
    print("High Scores:",scores)
    
    DBmyInputs = dataBase(DBdata,DBdataBank,DBinArr,scores)
    
    DBmyInputs.words[-1] = "Submit"
    
    lines = loadStrings("myFile.txt")
    cards = loadImage("cards1.png")
    
    numImages = len(lines)
    numObjects = 8
    
    playerList = ["North","East","South","West"]
    cardSuits = ["Clubs", "Diamonds", "Hearts", "Spades","NO TRUMP"]
    cardValues = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace","" ]
    
    MYDISPLAY = Display(numImages,numObjects)
    bridgeGame = Game()
    
    fList = [MYDISPLAY.startMode,
             MYDISPLAY.playMode,
             MYDISPLAY.helpMode,
             MYDISPLAY.returnScreen,
             MYDISPLAY.pause,
             MYDISPLAY.nameMode,
             MYDISPLAY.bidMode,
             bridgeGame.playerBids,
             MYDISPLAY.scoresMode,
             MYDISPLAY.exitMode
             ]
    
    MYDISPLAY.fList = fList
    
    for string in lines:
        MYDISPLAY.dataBank.append(stringToData(string))
        
    MYDISPLAY.startMode()
    
    bridgeGame.bidXY = [MYDISPLAY.dataBank[7][0][0],MYDISPLAY.dataBank[7][0][1]]

    firstPlayer = 0
                
    acceptedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    acceptedNums = "1234567890"
    
    showX = 400
    showY = 500
    showW = 300
    showH = 200
    incrX = 5
    incrY = 5
    bridgePNG = loadImage("bridge.png")
    
    animationCounter = 0
    animationMax = 300
    
    textLocation = [ [[400,10,300,100],[100,100,300,100],[500,100,300,100],[100,50,150,200,200]],
                    [[400,50,300,100]],
                    [[10,300,300,100],[10,350,300,100]],
                    [[10,10,500,100],[10,50,200,100]],
                    [[100,100,200,100], [100,600,500,500],[200,100],[700,200,300,300],[700,400,300,300]],
                    [[400, 10, 100, 100],[500, 10, 100, 100],[600, 10, 300, 100]] ]
    whichMsg = 0
        

def draw():
    global MYDISPLAY,bridgeGame,firstPlayer
    global cardSuits, cardValues
    global playerList
    global myTextSize
    global animationCounter,animationMax
    global DBmyInputs
    global DBtextX,DBYVals,DBdisWords
    global whichMsg, textLocation
    background(255)
    
    
    if MYDISPLAY.activeStuff[-8]:
        showAnimation()
        animationCounter += 1
        if animationCounter == animationMax:
            databank = open("databank.txt","wb")
            pickle.dump(DBmyInputs.dataBank,databank)
            databank.close()
            highscore = open("highscore.txt","wb")
            pickle.dump(DBmyInputs.scores,highscore)
            highscore.close()
            indirectarray = open("indirectarray.txt","wb")
            pickle.dump(DBmyInputs.indirectArr,indirectarray)
            indirectarray.close() 
            report = open("report.txt","a+")
            report.write(str(datetime.datetime.today())[:10] + "_______________________\n")
            report.write("Returning Players:_____\n")
            for i in range(3):
                DBmyInputs.newStuff[i].sort()
            for i in DBmyInputs.newStuff[0]:
                report.write("Name: " + i[0] + " Number: " + i[1] + "\n")
            report.write("New Players:_____\n")
            for i in DBmyInputs.newStuff[1]:
                report.write("Name: " + i[0] + " Number: " + i[1] + "\n")
            report.write("Score Updates:_____\n")
            for i in DBmyInputs.newStuff[2]:
                report.write("Name: " + i[0] + " Number: " + i[1] + " NEWSCORE: " + str(DBmyInputs.dataBank[i[1]][2]) + "\n")
            report.close()
            exit()
            
    if MYDISPLAY.activeStuff[-7]:
        show = 520
        interval = 20
        for i in range(1,5):
            showPlayer = (bridgeGame.curPlayer - i)%4
            bridgeGame.showCards(showPlayer,show+(interval*i))
    
    if MYDISPLAY.activeStuff[-6]:
        text("HIGHSCORES",textLocation[0][0][0],textLocation[0][0][1],textLocation[0][0][2],textLocation[0][0][3])
        text("Student Number:",textLocation[0][1][0],textLocation[0][1][1],textLocation[0][1][2],textLocation[0][1][3])
        text("# Wins", textLocation[0][2][0],textLocation[0][2][1],textLocation[0][2][2],textLocation[0][2][3])
        for i,score in enumerate(DBmyInputs.scores):
            text(score[1],textLocation[0][3][0],(i*textLocation[0][3][1]) + textLocation[0][3][2],textLocation[0][3][3],textLocation[0][3][4]) 
            text(str(score[0]),textLocation[0][3][0]*5,(i*textLocation[0][3][1]) + textLocation[0][3][2],textLocation[0][3][3],textLocation[0][3][4])
    
    if MYDISPLAY.activeStuff[-5]:
        text("Winner is: " + bridgeGame.winner,textLocation[1][0][0],textLocation[1][0][1],textLocation[1][0][2],textLocation[1][0][3])
        
    if MYDISPLAY.activeStuff[-4]:
        text("Highest Bid:",textLocation[2][0][0],textLocation[2][0][1],textLocation[2][0][2],textLocation[2][0][3])
        if bridgeGame.highestBid != [-1,-1,-1]:
            text(str(bridgeGame.highestBid[1]+1) + " " + cardSuits[bridgeGame.highestBid[0]],textLocation[2][1][0],textLocation[2][1][1],textLocation[2][1][2],textLocation[2][1][3])
            
    if MYDISPLAY.activeStuff[-3]:
        text("Current Player: " + playerList[bridgeGame.curPlayer],textLocation[3][0][0],textLocation[3][0][1],textLocation[3][0][2],textLocation[3][0][3])
        text(bridgeGame.players[bridgeGame.curPlayer].nameF + "\n" + bridgeGame.players[bridgeGame.curPlayer].nameL,textLocation[3][1][0],textLocation[3][1][1],textLocation[3][1][2],textLocation[3][1][3])
    
    if MYDISPLAY.activeStuff[-2]:
        text("Player " + str(bridgeGame.inputPlayer + 1),textLocation[4][0][0],textLocation[4][0][1],textLocation[4][0][2],textLocation[4][0][3])
        DBmyInputs.showStuff()
        text(DBmyInputs.showScore,textLocation[4][3][0],textLocation[4][3][1],textLocation[4][3][2],textLocation[4][3][3])
        text(DBmyInputs.showDate,textLocation[4][4][0],textLocation[4][4][1],textLocation[4][4][2],textLocation[4][4][3])
        text(DBmyInputs.errorMess[whichMsg],textLocation[4][1][0],textLocation[4][1][1],textLocation[4][1][2],textLocation[4][1][3])
        for i in range(3):
            text(DBdisWords[i],DBtextX,DBYVals[i],textLocation[4][2][0],textLocation[4][2][1])
            
        if DBmyInputs.whichSquare == 3:
            DBmyInputs.whichSquare = 0
            DBmyInputs.words[1] = DBmyInputs.words[1].upper()
            DBmyInputs.words[2] = DBmyInputs.words[2].upper()
            if len(DBmyInputs.words[0]) != DBmyInputs.wordLim[0] or len(DBmyInputs.words[1]) < 1:
                whichMsg = 1
            elif bridgeGame.checkTaken(DBmyInputs.words):
                whichMsg = 2
            elif DBmyInputs.checkNotMatch():
                whichMsg = 3
            else:
                whichMsg = 0
                bridgeGame.enterName(DBmyInputs.words)
                DBmyInputs.newEntry()
                DBmyInputs.reset()
                if bridgeGame.inputPlayer == 3:
                    MYDISPLAY.bidMode()
                else:
                    bridgeGame.inputPlayer = (bridgeGame.inputPlayer + 1)%4
                    
    MYDISPLAY.showStuff()
        
    if MYDISPLAY.activeStuff[-1]:
        winner = bridgeGame.play(firstPlayer) 
        text("NS: " + str(bridgeGame.NS), textLocation[5][0][0], textLocation[5][0][1], textLocation[5][0][2], textLocation[5][0][3])
        text("EW: " + str(bridgeGame.EW), textLocation[5][1][0], textLocation[5][1][1], textLocation[5][1][2], textLocation[5][1][3])
        text("Trump: " + bridgeGame.trump, textLocation[5][2][0], textLocation[5][2][1], textLocation[5][2][2], textLocation[5][2][3])
        if not bridgeGame.pause:
            if winner != -1:
                firstPlayer = winner
                bridgeGame.curSuit = ''
            
def mousePressed():
    global MYDISPLAY,bridgeGame
    global DBmyInputs
        
    if MYDISPLAY.activeStuff[-2]:
        if not MYDISPLAY.activeStuff[8]:
            DBmyInputs.checkClick()
        MYDISPLAY.checkClick()
    elif MYDISPLAY.activeStuff[-1]:
        if bridgeGame.pause:
            if not(MYDISPLAY.checkClick()):
                if not MYDISPLAY.activeStuff[8]:
                    bridgeGame.pause = False
        else:
            MYDISPLAY.checkClick()
        if not MYDISPLAY.activeStuff[8]:
            bridgeGame.playCard()
    else:
        MYDISPLAY.checkClick()


def keyPressed():
    global MYDISPLAY
    global DBmyInputs
    
    if MYDISPLAY.activeStuff[-2]:
        if DBmyInputs.whichSquare != 3:
            DBmyInputs.changeWord()
