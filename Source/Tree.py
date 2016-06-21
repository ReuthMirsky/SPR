from Sigma import Sigma, NT
import Rule
from pprint import _id
from copy import deepcopy

class Tree(object):
    idCounter=1

    def __init__(self, actionType, root, rule, children=[], PL=[], id=0):
        '''
        Constructor
        '''
        if id==0:
            self._id = Tree.idCounter
            Tree.idCounter+=1
        else: 
            self._id=id
        
        if actionType == "Complex":
            self._rule = rule                       #type Rule or list of Rule
            self._root = root                       #either NT or Sigma
            self._children = children               #list of nodes
            self._PL = PL                           #Plan Library
            self._isComplete = False                #Once all of this tree's children are full, this flag will become true
        elif actionType == "Basic":
            self._rule = ()                 #always null for node representing an atomic action
            self._root = root               #type NT or Sigma
            self._children = []             #always null for node representing an atomic action
            self._PL = PL                   #Plan Library
            self._isComplete = False        #Will become true when a real observation will be put here
        else:
            print "Unknown Node type"
        self._actionType=actionType


    def myCopy(self):
        '''
        Deep-copy constructor
        '''
        newChilden = []
        for child in self._children:
            newChilden.append(child.myCopy())
        newone = type(self)(self._actionType, self._root.myCopy(), self._rule , newChilden, self._PL, self._id)
        newone._isComplete=self._isComplete
        return newone
    
    # equals
    def __eq__(self, other):
        if type(other)!=type(self):
            return False
        
        if not other.getRoot().matchFullLetter(self.getRoot()):
            return False
             
        if len(other._children) != len(self._children):
            return False
        
        for childIndex in range(len(other._children)):
    
            if not self._children[childIndex]==other._children[childIndex]:
                return False
          
        return True
    
#--------------------------- Printing Functions -----------------------------------------------
    
    # toString
    def __repr__(self, depth=""):
        if [] == self._children:
            return depth+self._root.get()+"\n"
        res = depth+self._root.get()+"\n"
        for child in self._children:
            res+=child.__repr__(depth+"  ")
        return res
    
    # detailed toString
    def reprWithParams(self, depth=""): 
        res = self.innerReprWithParams(depth)
        res+= depth
        res+= "("
        res+= str(self._id)
        res+= ")"
        return res
    
    # service function for reprWithParams
    def innerReprWithParams(self, depth=""):
        if [] == self._children:
            return depth+str(self._root)+" "+str(self._PL.getRuleProb(self.getRoot())) +str(self.isComplete())+"\n"
        res = depth+str(self._root)+" "+str(self._PL.getRuleProb(self.getRoot())) +str(self.isComplete())+"\n" #if withParams else depth+self._root.get()+"\n") 
        for child in self._children:
            res+=child.innerReprWithParams(depth+" ")
        return res
    
    # toString in XML form
    def asXML(self, depth=""):
        if self.getRoot()._ch[0]=="A":
            return depth+"<"+self.getRoot()._ch+" />\n"
        
        res = depth+"<"+self.getRoot()._ch+">\n"
        for child in self._children:
            res += child.asXML(depth=depth+"  ")
        
        res += depth+"</"+self.getRoot()._ch+">\n"
        return res
    
#---------------------------Getters and Setters -----------------------------------------------

    #Returns the root of the tree (Letter)                       
    def getRoot(self):
        return self._root
    
    #Returns the id of the tree (int)
    def getID(self):
        return self._id

    #Sets the id of the tree to be num or the next available number (int)
    def setID(self, num=0):
        if num!=0:
            self._id = num
            return num
        self._id = Tree.idCounter
        Tree.idCounter+=1
        return self._id
    
    #Return true if this node has no children    
    def isLeaf(self):
        if self._children == []:
            return True;
        return False
    
    #Returns true iff self is a deeper tree than other
    def compareDepth(self, other):
        return self.getDepth()>other.getDepth()
    
    #Returns the depth of this tree (int)
    def getDepth(self):
        if [] == self._children:
            return 1
        maxDepth = 0
        for child in self._children:
            childDepth = child.getDepth() 
            if maxDepth< childDepth:
                maxDepth = childDepth
        return maxDepth+1
    
    #Gets a value (either NT or Sigma) and return the first child with this value as root
    def getChild(self, value):
        for child in self._children:
            if value == child._root:
                return child
        return ()
    
    #Gets a numeric value and return the child with this value as root
    def getChildByIndex(self, value):
        if value==-1:
            return self
        if value > len(self._children):
                return False
        return self._children[value]
   
    #Sets the child numbered as "index" to be "newChild" (boolean)
    #If fails, returns False, other returns True
    #index is the number of the child to replace, starting from 0
    #newChild is the child to replace with
    def setChildByIndex(self, index, newChild):
        if index > len(self._children):
            return False
        self._children[index] = newChild       
   
    #Gets a numeric value and return the index-numbered child in the frontier as root (Tree)
    def getNodeByFrontierIndex(self, index):
        if len(index)==1:
            return self.getChildByIndex(int(index))
        if index=='-1' or index=='':
            return self
        childIndex = int(index[0])
        child = self.getChildByIndex(childIndex)
        return child.getNodeByFrontierIndex(index[1:])

    #Sets the value of the index-th node in the tree to be newNode
    def setNodeByFrontierIndex(self, index, newNode):
        if len(index)==1:
            self.setChildByIndex(int(index), newNode)
        elif index=='-1' or index=='':
            self = newNode      #Don't you just love Python for letting you do this?
        else:
            childIndex = int(index[0])
            child = self.getChildByIndex(childIndex)
            child.setNodeByFrontierIndex(index[1:], newNode)

    #Returns the probability of this tree (double)             
    def getProbability(self):
        if self.isLeaf():
            return 1
        probabilityOfRootRule = self._PL.getRuleProbNotUniform(self._rule)
        totalProbability = probabilityOfRootRule
        for child in self._children:
            totalProbability *= child.getProbability()
        return totalProbability

    #This function returns all possible items in the Frontier. It can contain both Sigmas and NTs
    def getFrontier(self, withIndices=False): 
        if self.isLeaf() or type(self._rule)==type([]):   #If this node is leaf
            if self._isComplete: #If this node is a terminal leaf that got its parameters
                return []
            else:       #If this node is a leaf who needs to be expanded / filled with parametes - it's in the frontier
                return [self] if not withIndices else [(self,'')]
            
        else:   #Important: We're assuming that if a rule has children, its rule is known for sure
            childrenFrontiers = []
            expandableChildren = self.currentExpandableChilds(withIndices)
            #print ("current Expandable=", expandableChildren)
            for child in expandableChildren:
                if withIndices:                             #If you want the record of indices
                    childIndex = child[1]                   #This is the index of the child
                    for frontierItem in child[0].getFrontier(True):     #FrontierItem[0] is the node inside the child that can be expended
                                                                    #FrontierItem[1] is the index of that node relative to our child
                        childrenFrontiers.append((frontierItem[0], childIndex+frontierItem[1]))
                    
                else:
                    childrenFrontiers.extend(child.getFrontier())   #Add each child's frontier to the complete frontier                
            
            return childrenFrontiers        

#--------------------------- Conditions Checking -----------------------------------------------

    # Check condition 1+2
    # Condition 1: "every node in T is labeled with a symbol from Sigma union NT"
    # Condition 2: "every interior node in T is labeled with a symbol from NT"
    def isEveryNodeCorrect(self):
        if NT == type(self._root) or Sigma == type(self._root):
            if self._children:
                return True
            elif Sigma == type(self._root):
                return False
            else:
                for subTree in self._children:
                    if not subTree.isEveryNodeCorrect():
                        return False
                    else:
                        return True
        else:
            return False

    # Check condition 3: "if an interior node, n(=self), labeled A(=root) in T has children
    # with labels beta_1...beta_k(=self.children.roots()), then..."
    def allInteriorCorrect(self, byIndex=False):
        if self.isLeaf():
            return self if not byIndex else (self, '')
        
        # if this node matches cond3 (and it's an interior node) - find the foot of this branch
        if self._rule:
            foot=False
            childIndex = 0
            for child in self._children:
                (childMatchRule, prevIndex) = child.allInteriorCorrect(byIndex=True)
                #if even child does not match some rule
                if not childMatchRule:
                    return False
                #only one child can be "the foot bearer":              
                if type(childMatchRule._root) == Sigma:
                    #if other child already took this position as the "foot bearer", return False 
                    if foot:
                        return False if not byIndex else (False, False)
                    #else (foot has not been claimed and child ends with Sigma)
                    foot = childMatchRule if not byIndex else (childMatchRule, str(childIndex)+prevIndex)
                childIndex += 1
                 
            #if exactly one child ends with a foot - return the foot
            #notice that if no child is a foot bearer - returns False
            return foot
            
        #if does not match any rule
        return False                           
    
    # Return Foot of tree iff this tree is a leftmost derivation of self._rule (byIndex also returns the string coding for the place of the foot)
    # Else, return False 
    def isLeftMostTree(self, byIndex=False):
        #conditions 1+2 - every node is either NT or Sigma, every inner node in NT 
        if not self.isEveryNodeCorrect():
            return False;
        
        return self.allInteriorCorrect(byIndex)
    
#------------------ New Functions for Parametered-PHATT ---------------------------------------------

    #Returns True iff all leafs of this tree are terminal letters with parameter assignment
    #If withIndices is true, returns a list of tuples, of the form (<Tree>,<Index>) where tree is a child and index is its location in the tree
    def isComplete(self):
        if self._isComplete:
            return True
        #If the reason this tree is not complete is that it needs to be filled itself with content or to be expanded
        if self.isLeaf() or type(self._rule)==type([]):
            return False       
        for child in self._children:
            if not child.isComplete():
                return False
        #getting here means that this child is now complete, will never be incomplete again
        self._isComplete = True
        return True

    #Returns a list of all expandable children
    def currentExpandableChilds(self, withIndices=False):
        expandableChildren = []
        childIndex = 0
        for child in self._children:
            if child.isComplete():  #No need to expand an already complete tree
                childIndex+=1
                continue
            childConstrains = self._rule.allChildConstraints(childIndex)    #Look who's limiting this child
            childFree = True
            for otherChild in childConstrains:
                #If this child has some constraining child that is not complete - it cannot be expanded now
                if not self._children[otherChild].isComplete():
                    childFree = False
            #If this child has no incomplete preceding brothers, it can be in the frontier
            if childFree:
                childStringIndex=''+str(childIndex)
                if withIndices:
                    expandableChildren.append((child, childStringIndex))
                else:
                    expandableChildren.append(child)
            childIndex+=1
        return expandableChildren
            

 
##########################################################################
#             Parameter-related Functions
##########################################################################      

    #This function is "const" in that it does not change anything - 
    # it only looks to see if a suggested node has the same parameters as
    # in the frontier item is should replace
    def sameParameters(self, suggestedSubstituteLetter, childIndex):
        if childIndex=='' or childIndex=='-1':
            child = self
        else:
            child = self.getNodeByFrontierIndex(childIndex)
        return child._root.matchPartialLetter(suggestedSubstituteLetter)
        
    #This is the main function that substitutes the needed child with the new tree
    #If the substitution succeeded, it returns true, else it returns False
    def substitute(self, suggestedSubstituteLetter, childIndex):
        #If you with to substitute self you only need to change root and see if it works well below you
        if childIndex=='' or childIndex=='-1':
            self._root = suggestedSubstituteLetter
            if self._rule==():  #If we got here, this means we're a terminal letter which got its assignment, so it's now complete
                self._isComplete=True
            #else:       # Else, meaning we're substituting a node which might have more than one rule - need to eliminate some
            return self.substituteDownwards('-1')
        #If you wish to change one of your children, you need to make sure:
        # 1. It suits the child
        # 2. It suits you and other children below you
        immediateChildIndex = int(childIndex[0])
        if (self.getChildByIndex(immediateChildIndex).substitute(suggestedSubstituteLetter, childIndex[1:])):  #substitute according to child's rule
            #self.isComplete()  #Update that you are complete if needed
            return self.substituteDownwards(childIndex[0]) #substitute self and children
            
        
    #This is the function that assumes child no. X has changed its parameters
    # What we need to do here is update self and other children to see if the new rule fits
    # Notice that we might also update child no. X with additional parameters due to this connection
    def substituteDownwards(self, changedNodeIndex):
        if changedNodeIndex=='':        #Needed to make sure matchParameters will handle correctly
            changedNodeIndex='-1'
        if not (self.matchParameters(int(changedNodeIndex))):  #Update Self
            return False
        for child in self._children: 
            success = child.substituteDownwards('-1')         #Inform all children they need to update according to their rule too
            if not success:
                return False          
        return True #All tree below self has updated successfully
                
                
    #This is the bottom-est function with a significant value that actually performs the setting of new parameters, according to self's rule, such that:
    # 1. self's relevant parameters will have matched all of changedNode's parameters
    # 2. self's children's relevant parameters will have matched all of changedNode's parameters
    # 3. changedNode's relevant parameters will have matched other's
    # Notice - if this function returns false, it means the whole macro-substitution cannot be done!
    # changedNodeIndex is at most of length of 1 (excluding -1)
    def matchParameters(self, changedNodeIndex):
        changedNode = self.getChildByIndex(changedNodeIndex)
        if self._rule==():
            return True   
        if type(self._rule)==Rule.Rule:
            for (i,iname,j,jname) in self._rule._paramConst:
                if i==changedNodeIndex:
                    if not self.setConstraint(changedNode, j, iname, jname):
                        return False
                elif j==changedNodeIndex:
                    if not self.setConstraint(changedNode, i, jname, iname):
                        return False
            return True
        #What to do if this node's rule is still not determined:
        # can remove rules which no longer comply, or ignore for now
        # our choice (for the meanwhile) is let all rules be     
        else:
            return True
                
    # This is a helping function that takes a constraint and changes nodes accordingly
    def setConstraint(self, changedNode, toChangeIndex, changedParamName, toChangeParamName): 
        toChange = self.getChildByIndex(toChangeIndex)
        oldParamValue = toChange._root.getParam(toChangeParamName)
        if (oldParamValue==None):       #if parameter is free for assignment
            valToAssign = changedNode._root.getParam(changedParamName)
            toChange._root.setParam(toChangeParamName, valToAssign)
            return True
        
        valToAssign = changedNode._root.getParam(changedParamName)
        if valToAssign==None: #If parameters can agree
            changedNode._root.setParam(changedParamName, toChange._root.getParam(toChangeParamName))
            return True
        elif valToAssign==oldParamValue: #If parameters already agree
            return True
        else:
            return False       #ChangedNode Already has another assignment for the parameter, wrong substitution
        
# End of Tree.py