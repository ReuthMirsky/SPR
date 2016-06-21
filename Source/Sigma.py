class Letter(object):
   
    def __init__(self, ch='', params=[]):
        '''
        Constructor
        '''
        self._ch=ch                 # Type string
        self._params=[]         # Type list of tuples <paramName, paramVal> with initial value None 
        for param in params:
            if type(param)==tuple:
                self._params.append(param)
            else:
                self._params.append((param, None))

    def myCopy(self):
        '''
        Deep-copy constructor
        '''
        newParams = []
        for param in self._params:
            newParams.append((param[0],param[1]))
        newone = type(self)()
        newone._ch=self._ch
        newone._params=newParams
        newone._type=self._type
        return newone

    #  toString    
    def __repr__(self):
        res = self.get()
        res += '[]'
        return res    

#---------------------------Getters and Setters -----------------------------------------------

    #Returns the symbol of this letter (string)
    def get(self):
        return self._ch

    #Returns the value of an argument given name
    def getParam(self, name): 
        if name==None or self._params==[]:
            return None
        for pair in self._params:
            if pair[0]==name:
                return pair[1]
       
    #Sets the value of argument 'name' to be 'val'
    def setParam(self, name, val): 
        if name==None or self._params==[]:
            return None
        for paramIndex in range(len(self._params)):
            param = self._params[paramIndex]
            if param[0] == name:
                self._params[paramIndex] = (name,val)
        return None
    
    #Returns the index-th argument name
    def getParamName(self, index):
        return self._params[index][0];
    
    #Returns the index-th argument value
    def getParamVal(self, index):
        return self._params[index][1];
    
    #Returns the list of all agrument names and values (list of <name, val> tuples)
    def getParamList(self):
        return self._params
    
#--------------------------- Boolean Tests -----------------------------------------------
    
    #Returns True iff list of arguments has an argument name 'other_name'
    def hasParam(self, other_name):
        for param in self._params:
            if param[0]==other_name:
                return True
        return False

    #Returns True iff self and letter represent the same symbol and all argument values assigned in self are also assigned with the same value in letter
    def matchPartialLetter(self, letter):
        if letter.get()==self.get() and self.matchTerminalLetterParams(letter):
            return True
        return False
    
    #Returns True iff letter is equal in symbol and all values to self
    def matchFullLetter(self, letter):
        if letter.get()==self.get() and self.matchFullyLetterParams(letter):
                return True
        return False
    
    #Returns true iff all argument values assigned in self are also assigned with the same value in obs
    def matchTerminalLetterParams(self, obs):
        for (name, val) in self._params:
            if val!=None:
                if obs.getParam(name)!=val:
                    return False
        return True    
    
    #Returns True iff letter's arguments values all equal to self's argument values
    def matchFullyLetterParams(self, obs):
        for (name, val) in self._params:
            if obs.getParam(name)!=val:
                return False
        return True   
    

#--------------------------- Inherited Classes -----------------------------------------------
    
#Class for Terminal letters    
class Sigma(Letter):
    _type='Sigma'
 
#Class for Non-terminal letters
class NT(Letter):
    _type='NT'


# End of Sigma.py