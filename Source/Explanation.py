class Explanation(object):

    def __init__(self, trees=[]):
        '''
        Constructor
        '''
        self._trees = []    # A list of the current trees
        self._pendingSets = []  # A list of each tree's pending set
        for tree in self._trees:
            self._pendingSets.append(tree.getFrontier(True))
        self._probRoots = 1.0
        self._probChoices = 1.0
        self._age = 0
        self._probability = -1.0
        
    def myCopy(self):
        '''
        Deep-copy constructor
        '''
        newone = type(self)()
        for tree in self._trees:
            newone._trees.append(tree.myCopy())
        newone._probRoots = self._probRoots
        newone._probchoices=self._probChoices
        newone._age = self._age
        newone._probability = self._probability
        return newone

    #  toString
    def __repr__(self):
        if self._trees == []:
            return "Empty Explanation"
        res = "Explanation ("
        res += str(self.getExpProbability())
        res += "):\n"
        treeNums = []
        for tree in self._trees:
            treeNums.append(tree.getID())
            res += tree.reprWithParams(depth="\t")
            res += "\tfrontier: \n"
            res += "\t"+str(tree.getFrontier(withIndices=True))
            res += "\n"
        res+="Trees:"
        res+=str(treeNums)
        res+="\n"
        
        return res

    #Prints the Explanation's probability    
    def printExpProbability(self):
        print "roots=",self._probRoots
        print "probChoices=",self._probChoices
        psIndex=0
        for PS in self._pendingSets:
            if len(PS)!=0:
                print "ps at ",psIndex,"=",len(PS)
            psIndex+=1
        
#---------------------------Getters and Setters -----------------------------------------------
 
    #Returns all tress in the explanation (list of trees)        
    def getTrees(self):
        return self._trees
    
    #Returns the index-th tree in the explanation (tree)
    def getTree(self, index=0):
        if len(self._trees)<index:
            return self._trees[-1]
        else:
            return self._trees[index] 
        
    #Replaces the index-th tree in the explanation with newTree (void)
    def setTree(self, newTree, index=-1):
        if len(self._trees)<index or -1==index:
            self._trees.append(newTree)
            self._pendingSets.append(newTree.getFrontier(True))
        else:
            self._trees[index]=newTree
            
    #Returns a list of all the trees in the explanation (list of ints)  
    def getTreeIDs(self):
        treeNums = []
        for tree in self._trees:
            treeNums.append(tree.getID())
        return treeNums
    
    #Removes the index-th tree from the list of trees  
    def removeTree(self, index):
        if not (len(self._trees)<index or -1==index):
            self._trees.pop(index)   
    
    #Returns the probability of this explanation (double)
    def getExpProbability(self):
        if self._probability != -1:
            return self._probability
        else:
            res = 1.0
            res *= self._probRoots
            res *= self._probChoices
            for PS in self._pendingSets:
                if len(PS)!=0:
                    res *= 1.0/len(PS)
            return res

    #Sets the probability of this explanation to be prob (void)
    #This function is mostly used for normalization of probabilities
    def setExpProbability(self, prob):
        self._probability = prob 
    
    #Returns the size of the frontier (int)
    def getFrontierSize(self):
        res = 0
        for tree in self._trees:
            res += len(tree.getFrontier(False))
        return res
 
    #Returns the average size of a tree in the explanation (int)
    def getAvgTreeSize(self):
        res = 0.0
        amoutOfTrees=0
        for tree in self._trees:
            res += tree.getDepth()
            amoutOfTrees+=1
        return res / len(self._trees) 
    
    #Returns the number of trees in the explanation (int)
    def getSize(self):
        return len(self.getTrees())
    
    #Increment the age counter (void)
    def incrementAge(self):
        self._age += 1
        
    #Resets the age counter (void)
    def resetAge(self):
        self._age = 0
    
    #Returns the age of this explanation (integer)    
    def getAge(self):
        return self._age
    
#-------------------------Probability Related Functions -----------------------------------------------------
    #Assisting function to help calculate probabilities correctly - because a new tree might be added in a later step            
    # we need to remember that it was an optional tree to fulfill in previous steps.
    
    def backpatchPS(self, tAddition):
        for PS in self._pendingSets:
            PS.append(tAddition)   
            
                    
    def updateLocalProbChoices(self, tree):
        self._probChoices *= tree.getProbability()
        
    def updateLocalProbRoots(self, newRootProbability):
        self._probRoots *= newRootProbability
        
# End of Explanation.py 