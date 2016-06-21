import sys
import time
import random

sys.path.append( "Source" )
from Rule import Rule
from Sigma import Sigma, NT
from PL import PL
from Algorithm import ExplainAndCompute
from Explanation import Explanation

currentLetter = 0
Letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
Letters2 = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
currentNumber = 1#{letter: 1 for letter in Letters2.split(" ")}
AllNTs = []     #List of strings
AllRules = ""
AllRulesAsList = []

def runAlgorithm(stringObs):
    global AllRulesAsList
    Sigmas = []
    NTs = []
    Goals = []
    Observations = []
    for i in range(100):
        Sigmas.append(Sigma("A"+str(i+1)))
    
    for nt in AllNTs:
        if nt[0]=="*":
            Goals.append(NT(nt[1:]))
            NTs.append(NT(nt[1:]))
        else:
            NTs.append(NT(nt))
                
    for obs in stringObs[1:]:
        if len(obs)>1:
            if obs[len(obs)-1]=='\n':
                obs = obs[:-1]
            Observations.append(Sigma(obs))

    newPL = PL(Sigmas, NTs, Goals, AllRulesAsList)
    exps = ExplainAndCompute(newPL, Observations)
 
    
def addRule(ruleToPrint):
    global AllRules
    global AllRulesAsList
    
    toPrint = "\n"
    toPrint += str(ruleToPrint._A) #ruleToPrint._A.get()[1:]
    toPrint += " -> "
    for child in ruleToPrint._alpha:
        if child.get()[0]=="A":
            toPrint += (str(child)+" ") # str(int(child.get()[1:])+99) + " "
        elif child.get()[0]=="B":
            toPrint += (str(child)+" ") #child.get()[1:] + " "
    toPrint += str(ruleToPrint._order)
    toPrint += "\n[]\n\n"
    AllRules += toPrint
    AllRulesAsList.append(ruleToPrint)

def generateNextLetter(definedLetter=False):
    global currentLetter
    global Letters
    global currentNumber
    
    if not definedLetter:
        letterToReturn = Letters2.split(" ")[currentLetter]
    else:
        letterToReturn = definedLetter
        
    numberToReturn = currentNumber
    currentNumber += 1
    
    return letterToReturn+str(numberToReturn)

def getDelimiters(line):
    indices = []
    openBrackets = 0
    changed = False
    
    for i in range(len(line)):
        if line[i]=="(":
            openBrackets += 1
            changed = True
        elif line[i]==")":
            openBrackets -= 1
        
        if openBrackets==0 and changed:
            indices.append(i)
            changed = False
            
    return indices 

def parseWholeFile(currentLine):
    global currentLetter
    global Letters2
    global currentNumber
    global AllNTs
    
    delimiter = currentLine.rindex("\n")
   
    recipeLibrary=currentLine[:delimiter].strip()[1:-1]
    observations =currentLine[delimiter:].strip()[:-1]
    parseRecipeLibrary(recipeLibrary)
    runAlgorithm(observations.split(" "))

def parseOrder(order):
    pairs = "["+order.replace(".", ",")+"]"
    pairs = pairs.replace(") (", "),(")
    pairs = pairs.replace("\n ", ",")
    order = eval(pairs)
    return order

def parseOrRecipe(line):
    global AllNTs
    line = line[3:-1].strip()
    newRules = []
    newNT = generateNextLetter("B")
    AllNTs.append(newNT)
    
    if line[1:-1].count("(")==0:
        sigmas = line.split()
        for sigma in sigmas:
            newRules.append(Rule(NT(newNT), [Sigma(sigma)]))
       
    else: 
        rules = []   
        delims = getDelimiters(line)
        i=0
        del1 = 0
        del2 = delims[0]+2 if len(delims) >=2 else len(line)
        while True:
            i+=1
            if len(line[del1:del2])<2:
                if i==len(delims)+1:
                    break
            resultOfAnd = parseAndRecipe(line[del1:del2])
            alpha = NT(resultOfAnd[0])
            newRules.append(Rule(NT(newNT), [alpha]))
        
            del1=del2
            if i==len(delims)+1:
                break
            if i==len(delims):
                del2=len(line)
            else:        
                del2=delims[i]+2
                
    for rule in newRules:
        addRule(rule)
                    
    return (newNT, newRules) 
            
def parseAndRecipe(recipe):
    global AllNTs
    recipe = recipe.strip()
    if recipe[0]=="(":
        recipe=recipe[1:]
    if recipe[-1]==")":
        recipe=recipe[:-1]
    recipe = recipe.strip()        
    recipeDelimiters = getDelimiters(recipe)

    alphaLetters = []
    del1 = 0
    del2 = recipeDelimiters[0]+2 if len(recipeDelimiters) >= 1 else len(recipe)
    currentPiece = recipe[del1:del2].strip()
    
    # Parse first piece - should always be some direction of order
    if currentPiece[1]=="(":                          #If we reached a partial order piece e.g. (((0 . 1) (0 . 2)) (OR ...
        order = parseOrder(currentPiece[1:-1])
    elif currentPiece[0]=="N":                        #If we reached a non-ordered piece e.g. (NIL (OR ...
        order = []
        orRecipe = currentPiece[4:].strip()
        resultOfOr = parseOrRecipe(orRecipe)
        alphaLetters.append(NT(resultOfOr[0]))
    elif currentPiece[0]=="F":                        #If we reached a fully-ordered piece e.g. (FULL-ORDER (OR ...
        order = []
        for num in range(len(alphaLetters)-1):
            order.append((num,num+1))   
        orRecipe = currentPiece[8:].strip()      
        resultOfOr = parseOrRecipe(orRecipe)
        alphaLetters.append(NT(resultOfOr[0]))
        
    del1 = del2
    del2 = recipeDelimiters[1]+2 if len(recipeDelimiters) >= 2 else len(recipe)
    i=0
    
    #Parse other pieces which are only each of type OR
    while True:
        i+=1
        currentPiece = recipe[del1:del2].strip()
        #print i,":",currentPiece
        if currentPiece=="":                                #If we reached the end of the piece
            del1=del2
            if i<len(recipeDelimiters):
                del2=recipeDelimiters[i]+2
            else:
                break
            continue
        elif currentPiece[1]=="O": #OR
                        #(Place in sentence, (NT, rules))
            resultOfOr = parseOrRecipe(currentPiece.strip())
            alphaLetters.append(NT(resultOfOr[0]))
                      
        del1=del2
        if i==len(recipeDelimiters)+1:
            break
        elif i==len(recipeDelimiters):
            del2=len(recipe)
        else:        
            del2=recipeDelimiters[i]+2
                      
    letter = generateNextLetter("B")
    AllNTs.append(letter)
    newRule = Rule(NT(letter), alphaLetters, order)
    addRule(newRule)
    return (letter, newRule)
    
def parseRecipeLibrary(currentLine):
    currentLine = currentLine[1:].strip()
     
    delimiters = getDelimiters(currentLine[:-1])
    i=0
    recipes = []
    recipes.append(currentLine[:delimiters[0]+1])
    while i<len(delimiters)-1:
        recipes.append(currentLine[delimiters[i]+4:delimiters[i+1]+1])
        i+=1
    
    recipes.append(currentLine[delimiters[i]+4:])
        
    for i in range(len(recipes)):
        result = parseAndRecipe(recipes[i])
        AllNTs.remove(result[0])
        AllNTs.append("*"+str(result[0])) 

def main():
    #Usage
    if len(sys.argv) != 5:
        print "Usage: SPR.py     <Domain file>    <Observations>     <Strategy>    <Gold Standard>\n"
        sys.exit()
    
    grammarPath = str(sys.argv[1])
    grammarFile = open(grammarPath)
    grammarAsLine = grammarFile.read()
    
    parseWholeFile(grammarAsLine)
    
if __name__ == '__main__': main()    