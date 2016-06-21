import defs.Sigma
import defs.NT
import defs.Rule
import defs.PL
#import defs.Explanation
#import defs.Algorithm
import defs.Tree
from copy import deepcopy 
from Algorithm import ExplainAndCompute
global reuthAlgo
global reuthObservations

if __name__ == '__main__':
    
    # Test Sigma and NT
    print ("Test Sigmas and NTs:")
    sigma1 = defs.Sigma.Sigma('sm', ['sc','dc','sid','did','vol','rcd','scd','dcd','svol','dvol','rvol'])
    
    nt1 = defs.NT.NT('C', ['sc','dc','sid','did','vol','rcd','scd','dcd','svol','dvol','rvol'])
    nt2 = defs.NT.NT('SM', ['sc','dc','sid','did','vol','rcd','scd','dcd','svol','dvol','rvol'])
    print (sigma1, nt1)
    
    #Test Rule
    print ("\n\nTest Rules:")
    # SM -> sm | []
    #    C.sid=sm.sid, C.did=sm.did, C.sc=sm.sc,C.dc=sm.dc,C.vol=sm.vol,C.rcd=sm.rcd,C.scd=sm.scd,C.dcd=sm.dcd,C.svol=sm.svol,C.dvol=sm.dvol,C.rvol=sm.rvol
    rule1 = defs.Rule.Rule(nt2, [sigma1], [], [(-1,'sid',0,'sid'),(-1,'did',0,'did'),(-1,'sc',0,'sc'),(-1,'dc',0,'dc'),(-1,'vol',0,'vol'),(-1,'rcd',0,'rcd'),(-1,'scd',0,'scd'),(-1,'dcd',0,'dcd'),(-1,'svol',0,'svol'),(-1,'dvol',0,'dvol'),(-1,'rvol',0,'rvol')])
    print (rule1)
    print ("    right childs: ", rule1.rightChilds())             #[]
    print ("    leftmost childs: ", rule1.leftMostChilds())       #[sm]
    # C -> SM1 SM2 | [SM1 < SM2] (same destination flask)
    # C1.did=C2.did, C1.rcd=C2.dcd, C1.rvol=C2.dvol, C.did=C1.did C.did=C2.did
    rule2 = defs.Rule.Rule(nt1, [nt2, nt2], [], [(0,'did',1,'did'),(0,'rcd',1,'dcd'),(0,'rvol',1,'dvol'),(-1,'did',0,'did'),(-1,'did',1,'did')])
    print (rule2)
    print ("    right childs: ", rule2.rightChilds())             #[]
    print ("    leftmost childs: ", rule2.leftMostChilds())       #[C,C]
    # C -> SM1 SM2 | [] (intermediate flask)
    # C1.did=C2.sid C1.rcd=C2.scd C1.rvol=C2.svol
    # C.sc=C1.sc C.dc=C2.dc C.sid=C1.sid, C.did=C2.did C.vol=C2.vol C.rcd=C2.rcd C.scd=C2.scd C.dcd=C2.dcd C.svol=C2.svol C.dvol=C2.dvol C.rvol=C2.rvol
    rule3 = defs.Rule.Rule(nt1, [nt2, nt2], [(0,1)], [(0,'did',1,'sid'),(0,'rcd',1,'scd'),(0,'rvol',1,'svol'),(-1,'sc',0,'sc'),(-1,'dc',1,'dc'),(-1,'sid',0,'sid'),(-1,'did',1,'did'),(-1,'vol',1,'vol'),(-1,'rcd',1,'rcd'),(-1,'scd',1,'scd'),(-1,'dcd',1,'dcd'),(-1,'svol',1,'svol'),(-1,'dvol',1,'dvol'),(-1,'rvol',1,'rvol')])
    print (rule3)
    print ("    right childs: ", rule3.rightChilds())             #[]
    print ("    leftmost childs: ", rule3.leftMostChilds())       #[C,C]
    # SM -> MS1 SM2 | [SM1 < SM2]
    # C1.did=C2.did, C1.rcd=C2.dcd, C1.rvol=C2.dvol, C.did=C1.did, C.did=C2.did
    rule4 = defs.Rule.Rule(nt2, [nt2, nt2], [], [(0,'did',1,'did'),(0,'rcd',1,'dcd'),(0,'rvol',1,'dvol'),(-1,'did',0,'did'),(-1,'did',1,'did')])
    print (rule4)
    print ("    right childs: ", rule4.rightChilds())             #[]
    print ("    leftmost childs: ", rule4.leftMostChilds())       #[C,C]
    # SM -> SM1 SM2 | []
    # C1.did=C2.sid C1.rcd=C2.scd C1.rvol=C2.svol
    # C.sc=C1.sc C.dc=C2.dc C.sid=C1.sid, C.did=C2.did C.vol=C2.vol C.rcd=C2.rcd C.scd=C2.scd C.dcd=C2.dcd C.svol=C2.svol C.dvol=C2.dvol C.rvol=C2.rvol
    rule5 = defs.Rule.Rule(nt2, [nt2, nt2], [], [(0,'did',1,'sid'),(0,'rcd',1,'scd'),(0,'rvol',1,'svol'),(-1,'sc',0,'sc'),(-1,'dc',1,'dc'),(-1,'sid',0,'sid'),(-1,'did',1,'did'),(-1,'vol',1,'vol'),(-1,'rcd',1,'rcd'),(-1,'scd',1,'scd'),(-1,'dcd',1,'dcd'),(-1,'svol',1,'svol'),(-1,'dvol',1,'dvol'),(-1,'rvol',1,'rvol')])
    print (rule5)
    print ("    right childs: ", rule5.rightChilds())             #[]
    print ("    leftmost childs: ", rule5.leftMostChilds())       #[C,C]


    
    # Test PL
    print ("\n\nTest PL:")
    sigmas = [sigma1]
    nts = [nt1, nt2]
    goals = [nt1]
    rules = [rule1, rule2, rule3, rule4, rule5]
    myPL = defs.PL.PL(sigmas, nts, goals, rules)
    print (myPL)
    genSet = myPL.generatingSet(nts)
    
    print ("\n\nTest Generating Set:")   
    for tree in genSet:
        print (tree)
        print ("Is Leftmost=", tree.isLeftMostTree())
        print ("Its frontier=", tree.getFrontier(True))
    
    #Test Tree
    print ("\n\nTest Tree:")
    sm_Tree = defs.Tree.Tree("Basic", deepcopy(sigma1), [], [], myPL)
    print (sm_Tree)
    print(sm_Tree.getFrontier())
    #print(sm_Tree.getPS())
    SM_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), [], [], myPL)
    print (SM_Tree)
    #print ("SM_Tree rule=", SM_Tree._rule)
    print(SM_Tree.getFrontier())
    #print ("SM_Tree rule=", SM_Tree._rule)
    #print(SM_Tree.getPS())
    #print ("SM_Tree rule=", SM_Tree._rule)
    SMsm_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), rule1, [deepcopy(sm_Tree)], myPL)    
    print (SMsm_Tree)
    print(SMsm_Tree.getFrontier())
    #print(SMsm_Tree.getPS())
    CSMsmSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt1), rule3, [deepcopy(SMsm_Tree), deepcopy(SM_Tree)], myPL)
    print (CSMsmSM_Tree)
    print(CSMsmSM_Tree.getFrontier())
    #print(CSMsmSM_Tree.getPS())
    SMSMsmSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), rule5, [deepcopy(SMsm_Tree), deepcopy(SM_Tree)], myPL)
    print (SMSMsmSM_Tree)
    print(SMSMsmSM_Tree.getFrontier())
    #print(SMSMsmSM_Tree.getPS())
    CSMSMsmSMSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt1), rule2, [deepcopy(SMSMsmSM_Tree), deepcopy(SM_Tree)], myPL)
    print (CSMSMsmSMSM_Tree)
    print(CSMSMsmSMSM_Tree.getFrontier())
    #for (index,tree) in CSMSMsmSMSM_Tree.getPS():
    #    print (tree)


    print ("\n\nTest Tree With Indices:")
    sm_Tree = defs.Tree.Tree("Basic", deepcopy(sigma1), [], [], myPL)
    print (sm_Tree)
    print(sm_Tree.getFrontier(True))
    #print(sm_Tree.getPS())
    SM_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), [], [], myPL)
    print (SM_Tree)
    #print ("SM_Tree rule=", SM_Tree._rule)
    print(SM_Tree.getFrontier(True))
    #print ("SM_Tree rule=", SM_Tree._rule)
    #print(SM_Tree.getPS())
    #print ("SM_Tree rule=", SM_Tree._rule)
    SMsm_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), rule1, [deepcopy(sm_Tree)], myPL)    
    print (SMsm_Tree)
    print(SMsm_Tree.getFrontier(True))
    #print(SMsm_Tree.getPS())
    CSMsmSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt1), rule3, [deepcopy(SMsm_Tree), deepcopy(SM_Tree)], myPL)
    print (CSMsmSM_Tree)
    print(CSMsmSM_Tree.getFrontier(True))
    #print(CSMsmSM_Tree.getPS())
    SMSMsmSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), rule5, [deepcopy(SMsm_Tree), deepcopy(SM_Tree)], myPL)
    print (SMSMsmSM_Tree)
    print(SMSMsmSM_Tree.getFrontier(True))
    #print(SMSMsmSM_Tree.getPS())
    CSMSMsmSMSM_Tree = defs.Tree.Tree("Complex", deepcopy(nt1), rule2, [deepcopy(SMSMsmSM_Tree), deepcopy(SM_Tree)], myPL)
    print (CSMSMsmSMSM_Tree)
    print(CSMSMsmSMSM_Tree.getFrontier(True))
    
    
    #Test Tree.getNodeByFrontierIndex
    print ("\n\nTest Tree.getNodeByFrontierIndex")
    print("01:")  
    print(CSMSMsmSMSM_Tree.getNodeByFrontierIndex("01"))
    print("0:")
    print(CSMSMsmSMSM_Tree.getNodeByFrontierIndex("0"))
    print("1:")
    print(CSMSMsmSMSM_Tree.getNodeByFrontierIndex("1"))
    print("000:")
    print(CSMSMsmSMSM_Tree.getNodeByFrontierIndex("000"))
    print("root:")
    print(CSMSMsmSMSM_Tree.getNodeByFrontierIndex(""))
    

    #Test Substitution Functions
    print ("\n\nTest Subtitution Functions")
    obsSigma1 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
    obsSigma1.setParam('vol', '1')
    obsSigma1.setParam('sid', 'ID1')
    obsSigma1.setParam('scd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
    obsSigma1.setParam('svol', '100')
    obsSigma1.setParam('did', 'ID2')
    obsSigma1.setParam('dcd', 'None')
    obsSigma1.setParam('dvol', '0')
    obsSigma1.setParam('rcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
    obsSigma1.setParam('rvol', '1')    
#    for tree in genSet:
#        print ("\n~*~*~*~*~*~*~")
#        print (tree)
#        newCopy = deepcopy(tree)
#        for (node, index) in newCopy.getFrontier(withIndices=True):
#            print ("node no. ",index,"in the froniter=", node)
#            if newCopy.sameParameters(obsSigma1, index):
#                print ("same parameters, trying to substitue")
#                if newCopy.substitute(obsSigma1, index):
#                    print ("substitution successful, new Tree is:", newCopy.reprWithParams())
#                    print ("frontier after adding: ", newCopy.getFrontier(True))
#                else:
#                    print ("substitution failed")
#            else:
#                print ("Different parameters")
       

    #Test Explanation
    print ("\n\nTest Explanation")
    obsSigma2 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
    obsSigma2.setParam('vol', '1')
    obsSigma2.setParam('sid', 'ID2')
    obsSigma2.setParam('scd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
    obsSigma2.setParam('svol', '100')
    obsSigma2.setParam('did', 'ID3')
    obsSigma2.setParam('dcd', 'None')
    obsSigma2.setParam('dvol', '0')
    obsSigma2.setParam('rcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
    obsSigma2.setParam('rvol', '1')    
    res = ExplainAndCompute(myPL, [obsSigma1, obsSigma2])
    if res.empty():
        print("No Explanations")
    numOfExps = 0
    while not res.empty():
        numOfExps += 1
        exp = res.get_nowait()
        print(exp)
    print ("num of exps =", numOfExps)

    print ("\n\nTest Explanation 2")
    obsSigma3 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
    obsSigma3.setParam('sid', 'ID4')
    obsSigma3.setParam('did', 'ID3')   
    obsSigma4 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
    obsSigma4.setParam('sid', 'ID3')
    obsSigma4.setParam('did', 'ID3')
    res = ExplainAndCompute(myPL, [obsSigma1, obsSigma2, obsSigma3, obsSigma4])
    if res.empty():
        print("No Explanations")
    numOfExps = 0
    numOfExpsBySize = {1:0, 2:0, 3:0, 4:0}
    while not res.empty():
        numOfExps += 1
        exp = res.get_nowait()
        if numOfExps==4:
            print (exp)
        numOfExpsBySize[len(exp._trees)] += 1 
        if len(exp._trees)==1:
            print(exp)
    print ("num of exps =", numOfExps)
    print ("num of exps by size =", numOfExpsBySize)
    
#    Algo_sm_Tree = defs.Tree.Tree("Basic", deepcopy(obsSigma), [], [], myPL)
#    Algo_SMsm_Tree = defs.Tree.Tree("Complex", deepcopy(nt2), [], [deepcopy(Algo_sm_Tree)], myPL)
#    Algo_SMsmSM_Tree =  defs.Tree.Tree("Complex", deepcopy(nt2), rule4, [deepcopy(Algo_SMsm_Tree), deepcopy(SM_Tree)], myPL)   
#    C_Tree = defs.Tree.Tree("Complex", deepcopy(nt1), rule3, [deepcopy(Algo_SMsmSM_Tree), deepcopy(SM_Tree)], myPL)
#    C_Tree._children[1]._rule = rule5
#    print(C_Tree.reprWithParams())
#    print(C_Tree.getFrontier())
#    print(C_Tree.substitubeLeaf('000', obsSigma))
#    print(C_Tree.reprWithParams())
#    
#    explain1 = defs.Explanation.Explanation([C_Tree], [])
#    print (explain1)
#    
##    Test Algorithm :)
#    print ("\n\nTest Algorithm :)")
#    algo = defs.Algorithm.Algorithm(myPL)
#    
#    obsSigma2 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
##    obsSigma2.setParam('vol', '1')
#    obsSigma2.setParam('sid', 'ID2')
##    obsSigma2.setParam('scd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of B')
##    obsSigma2.setParam('svol', '100')
#    obsSigma2.setParam('did', 'ID1')
##    obsSigma2.setParam('dcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
##    obsSigma2.setParam('dvol', '1')
##    obsSigma2.setParam('rcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 5E-1M of A, 5E-1M of B')
##    obsSigma2.setParam('rvol', '2')
#    
#    obsSigma3 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
##    obsSigma3.setParam('vol', '1')
#    obsSigma3.setParam('sid', 'ID1')
##    obsSigma3.setParam('scd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
##    obsSigma3.setParam('svol', '99')
#    obsSigma3.setParam('did', 'ID5')
##    obsSigma3.setParam('dcd', 'None')
##    obsSigma3.setParam('dvol', '0')
##    obsSigma3.setParam('rcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
##    obsSigma3.setParam('rvol', '1')
#    
#    obsSigma4 = defs.Sigma.Sigma('sm', ['sid','did','vol'])
##    obsSigma4.setParam('vol', '1')
#    obsSigma4.setParam('sid', 'ID5')
##    obsSigma4.setParam('scd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of C')
##    obsSigma4.setParam('svol', '100')
#    obsSigma4.setParam('did', 'ID6')
##    obsSigma4.setParam('dcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1E0M of A')
##    obsSigma4.setParam('dvol', '1')
##    obsSigma4.setParam('rcd', '0E0g of H2O, 1E-7M of H+, 1E-7M of OH-, 1.03E-25M of A, 2.5E-1M of C, 5E-1M of B, 2.5E-1M of D')
##    obsSigma4.setParam('rvol', '2')