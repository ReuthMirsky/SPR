from Queue import Queue
from copy import deepcopy 
from Explanation import Explanation
from Sigma import NT, Sigma
from Rule import Rule
from Tree import Tree
import random
from math import log
import sys
import xml.etree.ElementTree as ET
import time
import Algorithm
import itertools
import collections

oldNumExps = 0;
oldNumTrees = 0;
queriesNumber = 0;

first = True
subtrees = []
subtreesID = []

treesMatrix={}

##############################################################################################################################
#                                            Basic Functions
##############################################################################################################################
def NormalizeProbabilities(exps):
    totalProbability = 0.0
    for exp in exps:
        totalProbability += exp.getExpProbability()
    
    for exp in exps:
        probability = exp.getExpProbability() / totalProbability
        exp.setExpProbability(probability)        

# Best is the set of trees to compare to
# other is the tree to compare
# Operator is either Refine/Match
def compareToBestExp(best, other, operator):   
    for tree in best:
        if operator(tree, other):
            return True
    return False

##############################################################################################################################
#                                            Refine / Match / Contain
##############################################################################################################################
###  MATCH OPERATOR ######        
def Match(this, other):
#   1. if this.name!=other.name
    if not other.getRoot().matchPartialLetter(this.getRoot()):
        return False

#   2. if one of them is open
    if (not this.isComplete()) or (not other.isComplete()):
        return True 

#   3.      If p1 and p2 are basic actions return True - implicitly checked 
#   4.      If p1 and p2 are complex actions
    if len(other._children) == len(this._children):

    #   5. recursive check for children
        for childIndex in range(len(other._children)):
            if not Match(this._children[childIndex], other._children[childIndex]):
                return False
        return True
    
    elif len(other._children)==0 or len(this._children)==0:
        return True
    
    return False

###  Refine OPERATOR ######               
def Refines(this, other):      #"This" is the bigger tree and we want to know if it is a refinement of "other"   
    if not other.getRoot().matchPartialLetter(this.getRoot()):
        return False
    
    if type(this.getRoot().get())==Sigma:
        return True 

    if other.isComplete() and not this.isComplete():
        return False
        
    if len(other._children) > len(this._children):  #This is > because the smaller tree can have no children yet
        return False
    
    for childIndex in range(len(other._children)):

        if not Refines(this._children[childIndex], other._children[childIndex]):
            return False
            
    return True

###  Equals OPERATOR ######  
def Equals(this, other):
    return this==other

def readRefinesProbabilites(biggerTreeIndex, smallerTreeIndex):
    global treesMatrix
    
    return smallerTreeIndex in treesMatrix[biggerTreeIndex][0] 

def readContainsProbabilites(biggerTreeIndex, smallerTreeIndex):
    global treesMatrix
    
    return biggerTreeIndex in treesMatrix[smallerTreeIndex][0] 
    
def readMatchProbabilites(biggerTreeIndex, smallerTreeIndex):
    global treesMatrix
    
    return smallerTreeIndex in treesMatrix[biggerTreeIndex][1]

#Creates 2 matrices to capture all "refine" and all "match" relations between different plans
def createMatrices(exps):
    global subtrees
    global treesMatrix
    for biggerTree in subtrees:
        biggerTreeID = biggerTree.getID()
        treesMatrix[biggerTreeID] = ([biggerTreeID],[biggerTreeID]) #0 is contains, 1 is match
        for smallerTree in subtrees:
            smallerTreeID = smallerTree.getID()
            if smallerTreeID in treesMatrix[biggerTreeID]:
                continue
            else:
                if Refines(biggerTree, smallerTree):
                    treesMatrix[biggerTreeID][0].append(smallerTreeID)
                if Match(biggerTree, smallerTree):
                    treesMatrix[biggerTreeID][1].append(smallerTreeID)                          
    
    return

# Tree is the tree to get probability of
# Exps is the set of all explanations
# Operator is either readRefinesProbabilites/readContainesProbabilites/readMatchProbabilites
def GetProbability(tree, exps, operator):
    probabilityWithTree = 0.0
    probabilityWithoutTree = 0.0
    expsWith = 0
    expsWithout = 0
    for exp in exps:
        contains = False
        for biggerTree in exp.getTrees():
            if operator(biggerTree.getID(), tree.getID()):
                contains = True
                break
        if contains:
            probabilityWithTree += exp.getExpProbability()
            expsWith += 1
        else:
            probabilityWithoutTree += exp.getExpProbability()
            expsWithout += 1
    
    treeProbability = probabilityWithTree / (probabilityWithTree+probabilityWithoutTree)
    return treeProbability


##############################################################################################################################
#                                            Read Best Exp for Different Domains
##############################################################################################################################            
  
def readBestExpFromFile(PL):
    xmltree = ET.parse(sys.argv[4])
    explanation = xmltree.getroot()
    children = explanation.getchildren()
    parsedExp=[]
    for child in children:
        parsedTree = parseTreeFromXML(child, PL)
        parsedExp.append(parsedTree)
    return parsedExp
    
def parseTreeFromXML(root, PL):
    children = root.getchildren()
    if root.tag[0] == "A":
        t = Tree("Basic", Sigma(root.tag, []), [], [], PL)
        t._isComplete=True
        return t
    else:
        tree = Tree("Complex", NT(root.tag, []), [], [], PL)
        isComplete=True
        for child in children:
            treeChild = parseTreeFromXML(child, PL)
            if not treeChild.isComplete():
                isComplete=False
            tree._children.append(treeChild)
        tree._isComplete=isComplete
        return tree 

##############################################################################################################################
#                                            Probe Strategies
##############################################################################################################################

###  MPP  ######    
def probeByMostProbablePlan(exps=[], askedAbout=[]):
    IDsAndProbs = {}
    IDsAndTrees = {}
    treesOrderedByProbability = {}
   
    #Calculate the probabilities of the remaining trees
    for exp in exps:
        for tree in exp.getTrees():
            if tree.getID() not in IDsAndProbs.keys():
                IDsAndProbs[tree.getID()] = GetProbability(tree, exps, readRefinesProbabilites) 
                IDsAndTrees[tree.getID()] = tree
                if IDsAndProbs[tree.getID()] not in treesOrderedByProbability.keys():
                    treesOrderedByProbability[IDsAndProbs[tree.getID()]] = [tree.getID()]
                else:
                    treesOrderedByProbability[IDsAndProbs[tree.getID()]].append(tree.getID())
    
    #Remove Trees already asked about
    probabilityToSearch = 0
    treeIDToProb = -1
    while 0==probabilityToSearch or (treeIDToProb in askedAbout):
        if probabilityToSearch!=0:
            treesOrderedByProbability[probabilityToSearch].pop()
            if 0==len(treesOrderedByProbability[probabilityToSearch]):
                del treesOrderedByProbability[probabilityToSearch]

        if len(treesOrderedByProbability)==0:
            return [-1, []]     #Meaning all trees were queried about once
        
        probabilityToSearch = max(treesOrderedByProbability.keys())
        treeIDToProb = treesOrderedByProbability[probabilityToSearch][-1]
        treeToProbeFor = IDsAndTrees[treeIDToProb]
    
    #Ask about this tree
    askedAbout.append(treeIDToProb) 
    return [treeToProbeFor, askedAbout]

###  MPH  ######    
def probeByMostProbableHypothesis(exps=[], askedAbout=[]):
    expsByProbability= {}
    trees = []

    # Collect explanations by probability            
    for exp in exps:
        for tree in exp.getTrees():
            if tree.getID() not in trees:
                trees.append(tree.getID())
        expProb = exp.getExpProbability()
        if expProb not in expsByProbability.keys():
            expsByProbability[expProb] = [exp]
        else:
            expsByProbability[expProb].append(exp)
       
    #Remove Trees already asked about
    probabilityToSearch = 0
    treeIDToProb = -1

    while 0==probabilityToSearch or (treeIDToProb in askedAbout):
        if probabilityToSearch!=0:
            expsByProbability[probabilityToSearch].pop(len(expsByProbability[probabilityToSearch])-1)
            if 0==len(expsByProbability[probabilityToSearch]):
                del expsByProbability[probabilityToSearch]
        if len(expsByProbability)==0:
            return [-1, []]     #Meaning all trees were queried about once
        
        probabilityToSearch = max(expsByProbability.keys())
        i = 0 
        while i==0 or i<len(expsByProbability[probabilityToSearch][len(expsByProbability[probabilityToSearch])-1].getTrees()):
            treeToProbeFor = expsByProbability[probabilityToSearch][len(expsByProbability[probabilityToSearch])-1].getTrees()[i]
            treeIDToProb = treeToProbeFor.getID()    
            if (treeIDToProb not in askedAbout):
                break
            i+=1
        
    #Ask about this tree
    askedAbout.append(treeIDToProb) 
    return [treeToProbeFor, askedAbout]    
  
###  Entropy  ######      
def probeByEntropy(exps=[], askedAbout=[]):
    treeIDtoTree = {}
    
    for exp in exps:
        for tree in exp.getTrees():
            treeID = tree.getID()
            if treeID not in treeIDtoTree:  #If this is the first time we see this tree
                treeIDtoTree[treeID] = tree              

    #Collect probabilities of all explanations remaining in the system with and without tree
    informationGainPerTree = {}
    
    for treeID in treeIDtoTree.keys():
        entropyWithTree=0
        entropyWithoutTree=0
        
        #Calculate Ent(phi(H, t, True)) and Ent(phi(H, t, False))
        for exp in exps:
            refines = False
            for bigTree in exp.getTrees():
                if readRefinesProbabilites(bigTree.getID(), treeID):
                    expProb=exp.getExpProbability()
                    entropyWithTree-=(expProb * log(expProb,2))
                    refines = True
                    break
                if readMatchProbabilites(bigTree.getID(), treeID):
                    expProb=exp.getExpProbability()
                    entropyWithTree-=(expProb * log(expProb,2))
                    break
            if not refines:
                expProb=exp.getExpProbability()
                entropyWithoutTree-=(expProb * log(expProb,2))
        
        #Calculate Information Gain    
        tree = treeIDtoTree[treeID]
        treeProbabilityR = GetProbability(tree, exps, readRefinesProbabilites)
        treeProbabilityM = GetProbability(tree, exps, readMatchProbabilites)
        informationGain = treeProbabilityM*entropyWithTree + (1-treeProbabilityR)*entropyWithoutTree
        
        if informationGain in informationGainPerTree:
            informationGainPerTree[informationGain].append(treeID) 
        else:
            informationGainPerTree[informationGain] = [treeID]

    treeIDToProb = 0
    #Remove Trees already asked about
    while 0==treeIDToProb or (treeIDToProb in askedAbout):
        if treeIDToProb!=0:
            minEntropy = min(informationGainPerTree.keys())
            informationGainPerTree[minEntropy].remove(treeIDToProb)
            if 0==len(informationGainPerTree[minEntropy]):
                del informationGainPerTree[minEntropy]

        if len(informationGainPerTree)==0:
            return [-1, []]     #Meaning all trees were queried about once
        
        minEntropy = min(informationGainPerTree.keys())
        print "minEntropy=", minEntropy
        treeIDToProb = informationGainPerTree[minEntropy][0]
        treeToProbeFor = treeIDtoTree[treeIDToProb] 
    
    #Ask about this tree
    askedAbout.append(treeIDToProb) 
    return [treeToProbeFor, askedAbout]
    
    
###  Entropy-Subtrees  ######   
def probeByEntropySubtrees(exps=[], askedAbout=[]):
    global subtrees
    global subtreesID

    treeIDtoTree = {}
    
    for subtree in subtrees:
        treeID = subtree.getID()
        if treeID not in treeIDtoTree:  #If this is the first time we see this tree
            treeIDtoTree[treeID] = subtree              

    #Collect probabilities of all explanations remaining in the system with and without tree
    informationGainPerTree = {}
    
    for treeID in treeIDtoTree.keys():
        entropyWithTree=0
        entropyWithoutTree=0
        
        #Calculate Ent(phi(H, t, True)) and Ent(phi(H, t, False))
        for exp in exps:
            refines = False
            for bigTree in exp.getTrees():
                if readRefinesProbabilites(bigTree.getID(), treeID):
                    expProb=exp.getExpProbability()
                    entropyWithTree-=(expProb * log(expProb,2))
                    refines = True
                    break
                    
                if readMatchProbabilites(bigTree.getID(), treeID):
                    expProb=exp.getExpProbability()
                    entropyWithTree-=(expProb * log(expProb,2))
                    break
            if not refines:
                expProb=exp.getExpProbability()
                entropyWithoutTree-=(expProb * log(expProb,2))
        
        #Calculate Information Gain    
        tree = treeIDtoTree[treeID]
        treeProbabilityR = GetProbability(tree, exps, readRefinesProbabilites)
        treeProbabilityM = GetProbability(tree, exps, readMatchProbabilites)
        informationGain = treeProbabilityM*entropyWithTree + (1-treeProbabilityR)*entropyWithoutTree        
        if informationGain in informationGainPerTree:
            informationGainPerTree[informationGain].append(treeID) 
        else:
            informationGainPerTree[informationGain] = [treeID]

    treeIDToProb = 0
    treeToProbeFor = None
    #Remove Trees already asked about
    informationGainPerTree = collections.OrderedDict(sorted(informationGainPerTree.items()))
    while 0==treeIDToProb or len(informationGainPerTree)!=0:
        if treeIDToProb!=0:
            minEntropy = min(informationGainPerTree.keys())
            informationGainPerTree[minEntropy].remove(treeIDToProb)
            if 0==len(informationGainPerTree[minEntropy]):
                del informationGainPerTree[minEntropy]

        if len(informationGainPerTree)==0:
            return [-1, []]     #Meaning all trees were queried about once
        
        minEntropy = min(informationGainPerTree.keys())
        possibleTreeIDs = informationGainPerTree[minEntropy]
        possibleTrees=[]
        for treeID in possibleTreeIDs:
            possibleTrees.append(treeIDtoTree[treeID])
        possibleTrees = sorted(possibleTrees, key=Tree.getDepth)
        treeToProbeFor = possibleTrees[-1]
        return [treeToProbeFor, askedAbout]


###  Random  ######        
def probeByRandom(exps=[], askedAbout=[]):
    trees = []
    IDs = []
        
    for exp in exps:
        for tree in exp.getTrees():
            if tree.getID() not in IDs:
                trees.append(tree)
                IDs.append(tree.getID())
    
    #Remove Trees already asked about
    treeIDToProb = 0
    treeToProbeFor = None
    while 0==treeIDToProb or (treeIDToProb in askedAbout):
        if treeIDToProb!=0:
            IDs.remove(treeIDToProb)
            trees.remove(treeToProbeFor)
        if len(IDs)==0:
            return [-1, []]     #Meaning all trees were queried about once
        
        #Find Tree by random 
        treeToProbeFor = random.choice(trees)
        treeIDToProb = treeToProbeFor.getID()
        
    #Ask about this tree
    askedAbout.append(treeIDToProb) 
    return [treeToProbeFor, askedAbout]

##############################################################################################################################
#                                            Query Function
##############################################################################################################################    
#Return all subtrees of tree such that they start at the same root and every node either has all its children or none
def rootSubTrees(tree, setOfPrevious=[]):
    if tree.getDepth()==1:
        return [tree.myCopy()]
    childrenOptions=[[]]
    for child in tree._children:
        child.setID()
        singleChildOptions = rootSubTrees(child.myCopy())
        childrenOptionsWithCurrentChild = []
        for olderChildrenOption in childrenOptions:
            for option in singleChildOptions:
                newOption = option.myCopy()
                newOption.setID()
                newOlderChildrenOption = []
                for childTree in olderChildrenOption:
                    newChildTree = childTree.myCopy()
                    newChildTree.setID()
                    newOlderChildrenOption.append(newChildTree)
                newOlderChildrenOption.append(newOption)
                childrenOptionsWithCurrentChild.append(newOlderChildrenOption)
        childrenOptions.extend(childrenOptionsWithCurrentChild)
    toReturnList=[]
    for option in childrenOptions:
        newTree = tree.myCopy()
        newTree.setID()
        newTree._children = option
        if option==[]:
            newTree._isComplete=False
        for child in newTree._children:
            if not child._isComplete:
                newTree._isComplete=False
        if len(newTree._children)==0 or len(newTree._children)==len(tree._children):
            toReturnList.append(newTree)
    return list(set(toReturnList))
            
#Returns the id of the first tree in trees which is equal to imitator. If there is no such tree, returns -1    
def getFirstTree(imitator, trees):
    for tree in trees:
        if tree==imitator:
            return tree.getID()
    return -1
      
def query(exps=[], askedAbout=[], probingStrategy=probeByRandom):
    global first
    global subtrees
    global subtreesID

    NormalizeProbabilities(exps)
    bestExp = readBestExpFromFile(exps[0].getTrees()[0]._PL) 
   
    if first: 
        print "------------------ Starting the Query Process -------------------"
        print "Best is:"
        for tree in bestExp:
            print tree.reprWithParams()
        print
        first=False
   
    [treeToProbeFor, newAskedAbout] = probingStrategy(exps, askedAbout)
    
    if treeToProbeFor == -1:
        print "------------------ Cannot Discard Any More Hypotheses -------------------"
        return exps    
   
    newAskedAbout.append(treeToProbeFor.getID())
   
    print "Is this part of your plan?"
    print treeToProbeFor.reprWithParams()
    
    ### See if the treeToProbeFor can be refined to one of the trees in "best"
    isPart = compareToBestExp(bestExp, treeToProbeFor, Refines)
    print isPart
    print
        
    newExps = []
    toRemove=[]
    
    ### QA(p)=True, we need to keep all hypotheses with p' s.t. p ~m p'
    if isPart:
        for exp in exps:
            for tree in exp.getTrees():
                if Match(tree, treeToProbeFor):
                    newExps.append(exp)
                    break
        
        for subtree in subtrees:
            if Refines(treeToProbeFor, subtree):
                toRemove.append(subtree)
                
    ### QA(p)=False, we need to keep all hypotheses with no p' s.t. p ~r p'      
    else:
        for exp in exps:
            toPut=True
            for tree in exp.getTrees():
                if Refines(tree, treeToProbeFor):
                    toPut=False
                    break
    
            if toPut:
                newExps.append(exp)
        for subtree in subtrees:
            if Refines(subtree, treeToProbeFor):
                toRemove.append(subtree)

    ###  Inferred Queries  - discard queries which are redundant to the last one   
    for treeToRemove in toRemove:
        subtrees.remove(treeToRemove)
        subtreesID.remove(treeToRemove.getID())

    if treeToProbeFor.getID() is subtreesID: 
        subtrees.remove(treeToProbeFor)
        subtreesID.remove(treeToProbeFor.getID())

    ### Do we need to perform another query? 
    if 1==len(newExps):
        print newExps[0]
        print "------------------ Exactly One Explanation Remaining -------------------"
        return newExps
    
    elif 1<len(newExps):
        return query(newExps, newAskedAbout, probingStrategy)
            
    else:
        print "------------------ No Explanation Fits the Probing ------------------"
        return []    
    
# End of Probes.py