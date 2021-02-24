import datetime

class dataBase: 
    def __init__(self,data,dataBank,indirectArr,scores):
        self.dataBank = dataBank
        self.indirectArr = indirectArr
        self.data = data
        self.numButtons = len(data)
        self.words = ["" for i in range(self.numButtons)]
        self.wordLim = [6,10,10]
        self.whichSquare = -1
        self.errorMess = ['', "First Name/Number not long enough", "Name/Number already taken", "Preexisting Name/Number cannot be used with new Number/Name"]
        self.scores = scores
        self.newStuff = [[],[],[]] #Returning Played,New Players,Updated Scores
        self.showScore = ""
        self.showDate = ""
        
    def showStuff(self): #displays the elements
        for i in range(self.numButtons):
            if i == self.whichSquare:
                fill(200)
            else:
                fill(255)
            rect(self.data[i][0],self.data[i][1],self.data[i][2] - self.data[i][0],self.data[i][3] - self.data[i][1])
            fill(0)
            text(self.words[i],self.data[i][0],self.data[i][1],self.data[i][2] - self.data[i][0],self.data[i][3] - self.data[i][1])
                
    def checkClick(self): # checks click boundaries,changes self.whichSquare based on what button was clicked
        for i in range(self.numButtons):
            inBound = (self.data[i][0] <= mouseX <= self.data[i][2]) and (self.data[i][1] <= mouseY <= self.data[i][3])
            if inBound:
                self.whichSquare = i
                return()
        self.whichSquare = -1
    
    def changeWord(self): #changes the word and screen based on the input
        if self.whichSquare != -1:
            if key != CODED:
                if key == BACKSPACE:
                    if len(self.words[self.whichSquare]) == 0:
                        if self.whichSquare > 0 :
                            self.whichSquare -= 1
                    else:
                        self.words[self.whichSquare] = self.words[self.whichSquare][:-1]
                elif key == ENTER:
                    if self.whichSquare == 0:
                        self.whichSquare = 1
                    elif self.whichSquare < 3:
                        self.whichSquare += 1

                else:
                    if len(self.words[self.whichSquare]) < self.wordLim[self.whichSquare]:
                        if (self.whichSquare == 0 and key.isnumeric()) or (self.whichSquare != 0 and not(key.isnumeric())) :
                            self.words[self.whichSquare] += key
                    if len(self.words[self.whichSquare]) == self.wordLim[self.whichSquare]:
                        if self.whichSquare == 0:
                            if self.words[0] in self.dataBank.keys():
                                self.words[1] = self.dataBank[self.words[0]][0]
                                self.words[2] = self.dataBank[self.words[0]][1]
                                self.showScore = str(self.dataBank[self.words[0]][2])
                                self.showDate = self.dataBank[self.words[0]][3]
                                self.whichSquare = 2
                            else:
                                self.whichSquare = 1
                        elif self.whichSquare < 3:
                            self.whichSquare = 2
                            combined = self.words[1].upper() + "/" + self.words[2].upper()
                            found,index = binarySearch(self.indirectArr,combined)
                            if found:
                                self.words[0] = self.indirectArr[index][1]
                                
        if 0 < self.whichSquare < 3:
            combined = self.words[1].upper() + "/" + self.words[2].upper()
            found,index = binarySearch(self.indirectArr,combined)
            if found:
                if self.words[0] != self.indirectArr[index][1]:
                    self.words[0] = self.indirectArr[index][1]
                    self.showScore = str(self.dataBank[self.indirectArr[index][1]][2])
                    self.showDate = self.dataBank[self.indirectArr[index][1]][3]
                            
    def checkNotMatch(self): #if the name or number exists, checks that the name and number match
        num = self.words[0]
        name = self.words[1].upper() + "/" + self.words[2].upper()
        for i in self.indirectArr:
            nameMatch = name == i[0]
            numMatch = num == i[1]
            if (nameMatch and not(numMatch)) or (not(nameMatch) and numMatch):
                return True
        return False
    
    def newEntry(self): #puts the data on the screen into the database
        w = self.words
        combined = w[1] + "/" + w[2]
        associatedList = [combined,self.words[0]]
        found,index = binarySearch(self.indirectArr,combined)
        if not found:
            self.indirectArr.insert(index,associatedList)

        if w[0] in self.dataBank.keys():
            if not(associatedList in self.newStuff[0]) and not(associatedList  in self.newStuff[1]):
                self.newStuff[0].append(associatedList)
            self.dataBank[w[0]][3] = str(datetime.datetime.today())[:10]
        else:
            if not(associatedList in self.newStuff[0]) and not(associatedList in self.newStuff[1]):
                self.newStuff[1].append(associatedList)
            self.dataBank[w[0]] = [w[1].upper(),w[2].upper(),0,str(datetime.datetime.today())[:10]]
        print("______________________________________________________________________")
        print("DataBank:",self.dataBank)
        print("______________________________________________________________________")
        print("Indirect Array:",self.indirectArr)
        
    def updateScores(self,winners):# adds 1 win to each winner, updates the highscores list, receives list of 2 player objects (the winners)
        for i in winners:
            num = i.number
            combined = self.dataBank[num][0].upper() + "/" + self.dataBank[num][1].upper()
            associatedList = [combined,num]
            if not(associatedList in self.newStuff[2]):
                self.newStuff[2].append(associatedList)
            myList = [self.dataBank[num][2],num]
            if myList in self.scores:
                self.scores.remove(myList)
            myList[0] += 1
            added = False
            numScores = len(self.scores)
            for j in range(numScores):
                if myList[0] > self.scores[j][0]:
                    self.scores.insert(j,myList)
                    added = True
                    break
            if not added:
                self.scores.append(myList)
                
            self.dataBank[num][2] += 1
            
        overFlow = len(self.scores) - 5
        for i in range(overFlow):
            self.scores.pop()
                      
    def reset(self):# resets the entering data screen
        self.words = ["" for i in range(self.numButtons)]
        self.words[-1] = "Submit"
        self.whichSquare = 0
        self.showScore = ""
        self.showDate = ""
        
def binarySearch(inList,num): # binary search, returns if num/name is found and where it would be if found 
    bottom = 0
    top = len(inList) - 1
    middle = (top+bottom)//2
    while ((inList[middle][0] != num) and (top != bottom)):
        if num < inList[middle][0]:
            top = middle
        else:
            bottom = middle + 1
        middle = (top+bottom)//2
    if inList[middle][0] == num:
        return(True,middle)
    return(False,middle)
