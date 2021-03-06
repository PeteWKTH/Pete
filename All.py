#############################
import csv 
import copy 
import networkx as nx 
from collections import OrderedDict 
import matplotlib.pyplot as plt
import sys 
import pylab 
import numpy as np
from random import randint
import random
############################

CONST_POPULATION = "population" 
CONST_ACTIVITY = "activity" 
CONST_INC = "increase" 
CONST_DEC = "decrease" 
CONST_NONE = "none" 
CONST_ACTMAXVAL = 10 
CONST_ACTMINVAL = -10 
CONST_POPMAXVAL = 10 
CONST_POPMINVAL = -10 
CONST_CELLFILE = 'cellListV1.csv'
#CONST_RULEFILE = 'ruleSetSamefActivity_PBedit.csv'
CONST_RULEFILE = 'test.csv'
#################################

cycleLength = 0

cellNameList =[]
#################################

class Cell(object):
    
    def __init__(self, name, population = 5, activity = 1):
        self.name = name
        self.population = population
        self.activity = activity
        
    def __str__ (self):        
        return 'Cell %s ,%s ,%s' % (str(self.name), str(self.population), str(self.activity))

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def increaseByValue(self, iProperty, iValue):                    # iProperty tells whether you want to increase the population or activity amount by "iValue"
        if(iProperty == CONST_POPULATION):
            #if (int(self.population)) < CONST_POPMAXVAL :
            ap = int(self.population) + int(iValue)
            self.population = str(ap)
        elif(iProperty == CONST_ACTIVITY):
            #if(int(self.activity)) < CONST_ACTMAXVAL:
            ap = int(self.activity) + int(iValue)
            self.activity = str(ap)
        else:
            print('bad cell propery in increaseByValue method of Cell object')
            sys.exit(0)


    def decreaseByValue(self, iProperty, iValue):
        if(iProperty == CONST_POPULATION):
            #if(int(self.population)) > CONST_POPMINVAL :
            ap = int(self.population) - int(iValue)
            self.population = str(ap)
        elif(iProperty == CONST_ACTIVITY):
            #if(int(self.activity)) > CONST_ACTMINVAL:
            ap = int(self.activity) - int(iValue)
            self.activity = str(ap)
        else:
            print('bad cell propery in decreaseByValue method of Cell object')
            sys.exit(0)

    def changeProperty(self, iProperty,iValue):
        if(iProperty == CONST_POPULATION):
            self.population = str(iValue)
        elif(iProperty == CONST_ACTIVITY):
            self.activity = str(iValue)
        else:
            print('bad cell propery in changeProperty method of Cell object')
            sys.exit(0)
        
#############################################
# this is for reading the file and put the name pop activity into cellNameList
cellDict = dict ()                                          #making a dictionary http://stackoverflow.com/questions/1024847/add-to-a-dictionary-in-python
with open(CONST_CELLFILE, 'r') as f:			    # opens cellList.csv
    reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
    for row in reader:
        name, population, activity =row[0].split(';')
        if(int(population) < CONST_POPMINVAL or int(population) > CONST_POPMAXVAL):
            print('error! you have population value in input cell file higher than maximum or lower than minimum accepted population value!')
            sys.exit(0)
        elif(int(activity) < CONST_ACTMINVAL or int(activity) > CONST_ACTMAXVAL):
            print('error! you have activity value in input cell file higher than maximum or lower than minimum accepted activity value!')
            sys.exit(0)
        else:
            cellDict[name]= Cell(name, population, activity)
            cellNameList.append(name)

print('now we have all cell objects in cellDict')
###############################################
class myCondition(object):
    def __init__(self, cellName, cellProperty, compOp, Value):
        self.cellName = cellName
        self.cellProperty = cellProperty
        self.compOp = compOp    
        self.Value = Value
	
    def __str__ (self):
        return 'if %s.%s %s %s' % (self.cellName, self.cellProperty, self.compOp, self.Value)
    
##################################################
class myAction(object):
    
    def __init__(self, ruleID, TcellName, Tproperty, Toperation, Tvalue, ScellName, Sproperty, Soperation, Svalue, Time):
        self.ruleID = ruleID
        self.TcellName = TcellName
        self.Tproperty = Tproperty
        self.Toperation = Toperation
        self.Tvalue = Tvalue
        self.ScellName = ScellName
        self.Sproperty = Sproperty
        self.Soperation = Soperation
        self.Svalue = Svalue
        self.Time = Time

   # def __str__ (self):
   #     return 'Action for rule number %s : %s.%s %s by %s and %s.%s %s by %s in time %s' % (self.ruleID, self.TcellName, self.Tproperty, self.Toperation, str(self.Tvalue), #self.ScellName,self.Sproperty, self.Soperation, str(self.Svalue), str(self.Time))
    def __str__(self):
	return 'Action for rule %s : %s.%s %s by %s in time %s'  %(self.ruleID, self.TcellName, self.Tproperty, self.Toperation, self.Tvalue, self.Time)	
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
    
    def isApplicable(self):
        if int(self.Time) == 1:
            return True
        else:
            return False
            
    def decreaseTime(self):
        if(int(self.Time) > 1):
            tempTime = int(self.Time) - 1
            self.Time = str(tempTime)
        else:
            print('error in decrease time of myAction class, time is <= 1 !')
            sys.exit(0)

##########################################
class myRule(object):
    
    def __init__(self, ruleID, ruleCondition, ruleAction, active, probability):    # ruleCondition is something like  B_Cells.activity = 3 etc.
        self.ruleID        = ruleID  
        self.ruleCondition = ruleCondition
        self.ruleAction    = ruleAction
        self.active        = active
        self.probability   = probability
    def __str__ (self):
        return str(ruleID)+'   '+str(self.ruleCondition) + '       ' +str(self.ruleAction)+' with active:'+str(active)

    def makeActive(self):
        self.active = True
        
    def makePassive(self):
        self.active = False 
####################################
def isRuleCellNameValid(inCellName):
    if not((inCellName in cellDict)):
        print('error! The cell name: ', inCellName, ' in Rule file is not available in list of cells in cell File!')
        sys.exit(0)
def isRuleCellPropertyValid(inCellProperty):
    if(inCellProperty != CONST_POPULATION and inCellProperty!= CONST_ACTIVITY):
        print('error! The cell property in Rule file is not valid: ', inCellProperty)
        sys.exit(0)
def isRuleCompOpValid(inCompOp):
    if(inCompOp != '=' and inCompOp != '<' and inCompOp != '>'):
        print('error! The Comparing operator in Rule file is not valid: ', inCompOp)
        sys.exit(0)
def isValueValid(inValue):
    try:
        f = int(inValue)
    except ValueError:
        print ('error! Could not convert value in Rule file to an integer.')
        sys.exit(0)
def isOperationValid(inOperation):
    if(inOperation != CONST_INC and inOperation != CONST_DEC and inOperation != CONST_NONE):
        print('error! The Operation in Rule file is not valid: ', inOperation)
        sys.exit(0)
def isTimeValid(inTime):
     try:
        f = int(inTime)
     except ValueError:
        print ('error! Could not convert Time in Rule file to an integer.')
        sys.exit(0)
#######################################
ruleList    = []
ruleCounter = 1
with open(CONST_RULEFILE, 'rU') as f:
    reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
    for row in reader:
        cellName, cellProperty, compOp, Value, TcellName, Tproperty, Toperation, Tvalue, ScellName, Sproperty, Soperation, Svalue, Time = row
        isRuleCellNameValid(cellName)
        isRuleCellNameValid(TcellName)
        isRuleCellNameValid(ScellName)

        isRuleCellPropertyValid(cellProperty)
        isRuleCellPropertyValid(Tproperty)
        isRuleCellPropertyValid(Sproperty)

        isRuleCompOpValid(compOp)
        isValueValid(Value)
        isValueValid(Tvalue)
        isValueValid(Svalue)
        isOperationValid(Toperation)
        isOperationValid(Soperation)

        isTimeValid(Time)
        currentCondition = myCondition(cellName, cellProperty, compOp, Value)
        currentAction = myAction(ruleCounter,TcellName, Tproperty, Toperation, Tvalue, ScellName, Sproperty, Soperation, Svalue, Time)
        ruleList.append(myRule(ruleCounter, currentCondition, currentAction, False, 1))
	ruleCounter += 1
#### addition 
ruleList[0].probability = 0.5
ruleList[1].probability = 0.6
ruleList[2].probability = 0.7
ruleList[3].probability = 0.8
####
print('now we have all rule objects in ruleList')
print('rule Counter is: ', ruleCounter - 1)
###########################################################
class myState(object):
    def __init__ (self, stateID, ScellDict, isInitial, waitedActions,childList = []):
        self.stateID       = stateID
        self.ScellDict     = ScellDict
        self.isInitial 	   = isInitial
        self.waitedActions = waitedActions
	self.childList     = childList
    #def __str__ (self):
    #    return 'state %s , with isInitial %r and waited actions:\n' % (str(self.stateID), str(self.isInitial)) + ''.join('\n'.join(str(x) for x in self.waitedActions))
    def  __str__ (self):
	return 'state %s'  % self.stateID
    def __cmp__ (self, other):
        if self.stateID >= other.stateID: return 1
        else: return -1
    def printChild(self):
	for child in self.childList:
		print('\n' + child)
#############################################################
def checkingRule(inputRule, inputState):  
    thisCondition = inputRule.ruleCondition		# from rule
    thisProperty = thisCondition.cellProperty		# from rule       thisProperty = activity, population
    thisCompOp = thisCondition.compOp			# from rule        
    ruleCellName = thisCondition.cellName		# from rule
    ScellDict = inputState.ScellDict			# from state
    thisCell = ScellDict[ruleCellName]			# from state	
    if thisCompOp == '=':
        if((getattr(thisCell,thisProperty)) == thisCondition.Value):     # getattr returns the value of the property (same property as in the Rule) for a cell
            return True
        else:
            return False
      
    elif thisCompOp == '<':
        if (getattr(thisCell,thisProperty)) < thisCondition.Value:
            return True
        else:
            return False
        
    elif thisCompOp == '>':
        if (getattr(thisCell,thisProperty)) > thisCondition.Value:
            return True
        else:
            return False
    else:
        print('bad comparing operator in condition of rule')
        sys.exit(0)
        return False

######################################################################
def performAction(cellDict, action):
	returnCellDict = copy.deepcopy(cellDict)
	actionTCell = action.TcellName
	if  (action.Toperation == CONST_INC):
		returnCellDict[actionTCell].increaseByValue(action.Tproperty, action.Tvalue)
	elif(action.Toperation == CONST_DEC):
		returnCellDict[actionTCell].decreaseByValue(action.Tproperty, action.Tvalue)
	actionSCell = action.ScellName
	if  (action.Soperation == CONST_INC):
		returnCellDict[actionSCell].increaseByValue(action.Sproperty, action.Svalue)
	elif(action.Soperation == CONST_DEC):
		returnCellDict[actionSCell].decreaseByValue(action.Sproperty, action.Svalue)	
	 
	return returnCellDict	
               		
################################################################
def NodeChecking(inputCellDict, inputWActionL):
    global stateCounterG
    global Gmain
    global isInitialG
    orderInputCellDict = OrderedDict(sorted(inputCellDict.items(), key=lambda t: t[0]))
    counter = 0
    currentCellDict = dict()
    cellEqualityCheck = False
    wAEqualityCheck = False
    
    while ((cellEqualityCheck == False or wAEqualityCheck == False) and  counter < stateCounterG):
        counter += 1
        counterState = 'state' + str(counter)
        counterCellDict = Gmain.node[counterState]['data'].ScellDict
        orderCCellDict = OrderedDict(sorted(counterCellDict.items(), key=lambda t: t[0]))
        if (orderInputCellDict == orderCCellDict):
            cellEqualityCheck = True
        else:
            cellEqualityCheck = False

        counterWAlist = Gmain.node[counterState]['data'].waitedActions
        if(inputWActionL == counterWAlist):
            wAEqualityCheck = True
        else:
            wAEqualityCheck = False
        
    if (cellEqualityCheck == True and wAEqualityCheck == True):
        return counter
    else:
        return 0
########################################################
def CheckSumLimit(inputCellDict):                                     # checking if any value is above or below the upper/ lower limits, then change that value to the limit.
    for keys, Values in inputCellDict.items():
        if (int(inputCellDict[keys].population) < CONST_POPMINVAL):
            inputCellDict[keys].changeProperty(CONST_POPULATION,CONST_POPMINVAL)    # change the value to the threshold value  changeProperty is in Cell class      

        if(int(inputCellDict[keys].population) > CONST_POPMAXVAL):
            inputCellDict[keys].changeProperty(CONST_POPULATION,CONST_POPMAXVAL)

        if(int(inputCellDict[keys].activity) < CONST_ACTMINVAL):
            inputCellDict[keys].changeProperty(CONST_ACTIVITY,CONST_ACTMINVAL)
            
        if(int(inputCellDict[keys].activity) > CONST_ACTMAXVAL):
            inputCellDict[keys].changeProperty(CONST_ACTIVITY,CONST_ACTMAXVAL)

    return inputCellDict
            
##########################################################
def myMainFunc(inputState):
    
    global ruleList
    global stateCounterG
    global Gmain
    global isInitialG
    global cycleLength
    
    
    isNextState = False
    nextWaitedActionL = [] 
    doApplyActionL = [] 
    falseCondRuleL = [] 
    currentWaitedActionL = inputState.waitedActions 
    nextCellDict = dict() 

    for itemRule in ruleList:
        if(itemRule.active == False):				   # initial active for every rule is False!!!!!
            b1 = checkingRule(itemRule, inputState)                	   # b1 is boolean
            if(b1==True and itemRule.ruleAction.isApplicable() == True):   # isApplicable() checks if the time is 1 or not
                newAction = copy.deepcopy(itemRule.ruleAction)
                doApplyActionL.append(newAction)
                itemRule.makeActive()
                
            elif (b1==True and itemRule.ruleAction.isApplicable() ==False):
                newAction = copy.deepcopy(itemRule.ruleAction)
                newAction.decreaseTime()                          # why decrease time? look at the thesis chart
                nextWaitedActionL.append(newAction)
                itemRule.makeActive()
                
            else:
                newRule = copy.deepcopy(itemRule)
                falseCondRuleL.append(newRule)
        
    for itemWaction in currentWaitedActionL:
        if(itemWaction.isApplicable() == True):                 # if the time is 1
            doApplyActionL.append(itemWaction)
        else:
            newWAction = copy.deepcopy(itemWaction)
            newWAction.decreaseTime()				# why decrease time? look at the thesis chart
            nextWaitedActionL.append(newWAction)

    if(doApplyActionL):    ## what is it checking?   checking if the list is empty or not
        nextCellDict1 = doAction(inputState.ScellDict, doApplyActionL)
        nextCellDict = CheckSumLimit(nextCellDict1)
        
    else:  # if the list is empty
        nextCellDict = copy.deepcopy(inputState.ScellDict)
        

    orderNextCellDict = OrderedDict(sorted(nextCellDict.items(), key=lambda t: t[0]))     # ? sorting the order somehow.
    orderScellDict = OrderedDict(sorted(inputState.ScellDict.items(), key=lambda t: t[0]))
    retI = NodeChecking(nextCellDict, nextWaitedActionL)    # we check if the state is already existed before
    
    if(retI == 0):       # if there are no previous state that is identical with this current (next) one.
        previousState = 'state' + str(stateCounterG)
        stateCounterG += 1
       
        stateNumstr = 'state' + str(stateCounterG)
        data = myState(stateCounterG, nextCellDict, isInitialG, nextWaitedActionL)
        Gmain.add_node(stateNumstr, data = myState(stateCounterG, nextCellDict, isInitialG, nextWaitedActionL))       # here we add nodes  
        Gmain.add_edge(previousState, stateNumstr)								       # here we add edges
        if(stateCounterG < 100):  # 100 can be chosen as a boundary
            myMainFunc(data)      # continue looping the same thing 
    else:                         # else if there exists previous state that is exactly the same as this one, we stop.
        print('we have this state number in graph: ', retI)
        previousState = 'state' + str(stateCounterG)
        print('previousState: ', previousState)
        stateNumstr = 'state' + str(retI)
        print('retI: ', retI)
        print('stateNumstr: ', stateNumstr)
        Gmain.add_edge(previousState, stateNumstr)             # here we add edges
        print('we returned to a previously created node in graph and it is finished :)')
        
        if(previousState == stateNumstr):
            print('we have a self transition loop in node ', previousState)

        
#################################

def randInitialCells():
    for keys, Values in cellDict.items():
        randAct = randint(1,3)
        cellDict[keys].changeProperty(CONST_ACTIVITY, randAct)
###########################################
def makeRulesPassive():
    for ruleItem in ruleList:
        ruleItem.makePassive()

###########################################
def doTest():
    global stateCounterG
    global Gmain
    global isInitialG
    randInitialCells()
    isInitialG = True
    stateCounterG = 1
    constructFirstState()
    makeRulesPassive()
    currentState = Gmain.node['state1']['data']             # what is it doing? Gmain.node[][] returns the current state (state1 with its data = myState(.......)) 'data' is key!
    im = Gmain.number_of_nodes()
        
    myMainFunc(currentState)
    #printGraph2()    
    #nx.draw_circular(Gmain)
    #nx.draw_graphviz(Gmain, node_size=1000)
    #nx.draw_spring(Gmain)
    #nx.draw(Gmain)
    from random import random
    colors = [(random(), random(), random()) for _i in range(10)]
    nx.draw_circular(Gmain, node_color = colors)
    plt.show()
#############################
def findcellValuesD(cellName, cellProperty):
    global stateCounterG
    global Gmain
    global isInitialG

    i = 1
    outputList = []
    stateNameStr = ''
    
    while i <= stateCounterG:
        stateNameStr = 'state' + str(i)
        currentState = Gmain.node[stateNameStr]['data']
        thisCell = currentState.ScellDict[cellName]
        cellPropertyValue = int(getattr(thisCell, cellProperty))
        outputList.append(cellPropertyValue)
        i += 1
    return outputList

############################################
