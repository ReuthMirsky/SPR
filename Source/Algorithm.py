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
from Probes import *


#PL is the plan library for this run
# observations is a set of sigmas that needs to be explained
# explanation is the set of explanations to build upon
def ExplainAndCompute(PL, observations, explanations=[]):
    exps = explanations
    if len(exps)==0:
        exps.append(Explanation())
    goalsGeneratingSet = PL.generatingSet(PL.getGoals())
    allGeneratingSet = {}

    treesInAllGenSet = 0
    
    for nt in PL._NT:
        allGeneratingSet[nt.get()] = PL.generatingSet([nt])
        treesInAllGenSet += len(allGeneratingSet[nt.get()])

    #Loop over all observations
    obsNum = 1
    for obs in observations:  
        expsTemp = []
        treesTotal = 0
        probabilityTotal = 0.0
        ageTotal = 0
        frontierTotal = 0
        numOfExps = 0.0
        oldExpNum = 0
        
        #Loop over all the explanations in the queue
        for i in range(len(exps)):
            oldExpNum+=1
            currentExp = exps[i]
            
            treeIndexInExp = 0

            #Consider all the existing plans the observation could extend
            for tree in currentExp.getTrees():
                treeFrontier = tree.getFrontier(withIndices=True)
                for (node, index) in treeFrontier:

                    #Try to complete the frontier by expanding the tree from this point
                    #First, create all trees that start in the frontier item and ends with obs
                    if type(node.getRoot()) == Sigma:
                        genSetForObs = []
                    else:
                        genSetTrees = []
                        for subtree in allGeneratingSet[node.getRoot().get()]:
                            genSetTrees.append(subtree.myCopy())
                        genSetForObs = PL.generatingSetForObs(genSetTrees, obs)


                    #Then, try to see if the new sub-tree can be inserted instead of the frontier item
                    for newExpandedTree in genSetForObs:
                        if tree.sameParameters(newExpandedTree.getRoot(), index):
                            newCopy = tree.myCopy()
                            newCopy.setNodeByFrontierIndex(index, newExpandedTree)
                            if newCopy.substitute(newExpandedTree.getRoot(), index):
                                newCopy.setID()
                                newExp = currentExp.myCopy()
                                newExp.setTree(newCopy, treeIndexInExp)
                                newExp.updateLocalProbChoices(newCopy)
                                newExp.resetAge()
                                expsTemp.append(newExp)
                                numOfExps += 1
                                treesTotal += len(newExp.getTrees())
                                probabilityTotal += newExp.getExpProbability()
                                ageTotal += newExp.getAge()
                                frontierTotal += newExp.getFrontierSize()
                            else:
                                del(newCopy)
                                
                treeIndexInExp+=1
                            
            #Consider all the new plans the observation could introduce
            for possTree in goalsGeneratingSet:
                treeFrontier = possTree.getFrontier(withIndices=True)
                for (node, index) in treeFrontier: 
                    if possTree.sameParameters(obs, index):
                        newCopy = possTree.myCopy()
                        newCopy.setID()
                        if newCopy.substitute(obs, index):
                                newExp = currentExp.myCopy()
                                newExp.setTree(newCopy)
                                newExp.backpatchPS(allGeneratingSet[possTree.getRoot().get()])
                                newExp.updateLocalProbChoices(newCopy)
                                newExp.updateLocalProbRoots(PL.getRootProb())
                                newExp.incrementAge()
                                expsTemp.append(newExp)
                                numOfExps += 1
                                treesTotal += len(newExp.getTrees())
                                probabilityTotal += newExp.getExpProbability()
                                ageTotal += newExp.getAge()
                                frontierTotal += newExp.getFrontierSize()
                        else:
                            del(newCopy)
        

        del[exps]
        exps=expsTemp
            
        if int(sys.argv[2])==obsNum:
            print "Time - Before SPR", time.clock()
            uniteIDs(exps)
            print "Time - after ID Unification", time.clock()
            createMatrices(exps)
            print "Time - after matrices creation", time.clock()
            exps = query(exps, [], eval(sys.argv[3]))
            print "Time - after queries", time.clock()
            return exps
        obsNum += 1
        
    return exps


def uniteIDs(exps):
    global subtrees
    global subtreesID
    accumulatedTrees=0    
    
    trees = []
    for exp in exps:
        for tree in exp.getTrees():
            accumulatedTrees+=1
            if tree not in subtrees:
                trees.append(tree)
                subtrees.append(tree)
                subtreesID.append(tree.getID())
                
                # Consider subtrees as well as complete trees - uncomment to use with the probing strategy "probeByEntropySubtrees"
#                 newSubtrees = rootSubTrees(tree)
#                 for subtree in newSubtrees:
#                     if subtree not in subtrees:
#                         subtrees.append(subtree)
#                         subtreesID.append(subtree.getID())
#                     else:
#                         subtree.setID(getFirstTree(subtree, subtrees)) 
                        
            else:
                tree.setID(getFirstTree(tree, subtrees))
                
    subtrees = list(set(subtrees))
    subtreesID = list(set(subtreesID))  
    
    
# End of Algorithm.py