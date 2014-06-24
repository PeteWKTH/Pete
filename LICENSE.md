__code__ = "Applying Agent Based Modeling On Immune System Cells - Master thesis"
__author__ = "Maryam Oryani <oryani@kth.se>"
__version__ = "AgentBasedImmuneCell.py 2014-05-19"
 
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
CONST_RULEFILE = 'ruleSetSamefActivity_PBedit.csv'
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

    def increaseByValue(self, iProperty, iValue):                    # iProperty tells whether you want to increase the population or activity amount by "IValue"
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

    def __str__ (self):
        return 'then rule number %s : %s.%s %s by %s and %s.%s %s by %s in time %s' % (self.ruleID, self.TcellName, self.Tproperty, self.Toperation, str(self.Tvalue), self.ScellName,self.Sproperty, self.Soperation, str(self.Svalue), str(self.Time))

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
    
    def __init__(self, ruleID, ruleCondition, ruleAction, active):
        self.ruleID = ruleID
        self.ruleCondition = ruleCondition
        self.ruleAction = ruleAction
        self.active = active

    
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
ruleList = []
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
        ruleList.append(myRule(ruleCounter, currentCondition, currentAction, False))
        ruleCounter += 1

###########################################################
class myState(object):
    def __init__ (self, stateID, ScellDict, isInitial, waitedActions):
        self.stateID = stateID
        self.ScellDict = ScellDict
        self.isInitial = isInitial
        self.waitedActions = waitedActions

    def __str__ (self):
        return 'state %s , with isInitial %r and waited actions:\n' % (str(self.stateID), str(self.isInitial)) + ''.join('\n'.join(str(x) for x in self.waitedActions))
                
    def __cmp__ (self, other):
        if self.stateID >= other.stateID: return 1
        else: return -1
#############################################################
def checkingRule(inputRule, inputState):  
    thisCondition = inputRule.ruleCondition
    thisProperty = thisCondition.cellProperty
    thisCompOp = thisCondition.compOp
        
    ruleCellName = thisCondition.cellName
    ScellDict = inputState.ScellDict
    thisCell = ScellDict[ruleCellName]
    if thisCompOp == '=':
        if((getattr(thisCell,thisProperty)) == thisCondition.Value):
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
def doAction(inputCellDict, inputActionL):
    Tbool = False
    Sbool = False
    newRetCellDict = copy.deepcopy(inputCellDict)
    for actionItem in inputActionL:
        if(actionItem.isApplicable()):
            ruleList[(actionItem.ruleID)-1].makePassive()
            actionCellNT = actionItem.TcellName
            if(actionItem.Toperation == CONST_INC):
                newRetCellDict[actionCellNT].increaseByValue(actionItem.Tproperty, actionItem.Tvalue)
                Tbool = True
            elif(actionItem.Toperation == CONST_DEC):
                newRetCellDict[actionCellNT].decreaseByValue(actionItem.Tproperty, actionItem.Tvalue)
                Tbool = True
            elif(actionItem.Toperation == CONST_NONE):
                Tbool = True
            else:
                print('Bad operation in target action of rule in doAction method!')
                print(actionItem)
                sys.exit(0)

            actionCellNS = actionItem.ScellName
            if(actionItem.Soperation == CONST_INC):
                newRetCellDict[actionCellNS].increaseByValue(actionItem.Sproperty, actionItem.Svalue)
                Sbool = True
            elif(actionItem.Soperation == CONST_DEC):
                newRetCellDict[actionCellNS].decreaseByValue(actionItem.Sproperty, actionItem.Svalue)
                Sbool = True
            elif(actionItem.Soperation == CONST_NONE):
                Sbool = True
            else:
                print('Bad operation in source action of rule in doAction method!')
                sys.exit(0)
        else: 
            print('you asked to do an action that is not applicable by time!')
            sys.exit(0)
    return newRetCellDict        

##################################################################################
Gmain = nx.Graph()
isInitialG = True
stateCounterG = 1

def constructFirstState():
    global stateCounterG
    global Gmain
    global isInitialG

    stateCounterG = 1
    isInitialG = True
    waitedActions1= []
    Gmain.clear()
    Gmain.add_node('state1', data = myState(stateCounterG, cellDict, isInitialG, waitedActions1))
    isInitialG = False


def printCellDict(inputCellDic):
    print('\nList of cells in dictionary:')
    for keys, values in inputCellDic.items():
        #print(keys)
        print(values)

def printGraph():
    print('Graph printing:')
    global stateCounterG
    global Gmain
    global isInitialG
    print('Number of nodes in graph: ' ,Gmain.number_of_nodes())
    print('Number of edges in graph: ' , Gmain.number_of_edges())
    
    i = 1
    stateNameStr = ''
##################################################################
def printGraph2():
    print('Graph printing:')
    global stateCounterG
    global Gmain
    global isInitialG
    print('Number of nodes in graph: ' ,Gmain.number_of_nodes())
    print('Number of edges in graph: ' , Gmain.number_of_edges())
    
    i = 1
    stateNameStr = ''
    while i <= stateCounterG:
        stateNameStr = 'state' + str(i)
        print('\nstateNameStr', stateNameStr)
        print('degree is: ', Gmain.degree(stateNameStr))
        currentState = Gmain.node[stateNameStr]['data']
        print('graph node state:',currentState)
        orderedCellDict = OrderedDict(sorted(currentState.ScellDict.items(), key=lambda t: t[0]))
        printCellDict(orderedCellDict)
        i += 1
    
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
def CheckSumLimit(inputCellDict):
    for keys, Values in inputCellDict.items():
        if (int(inputCellDict[keys].population) < CONST_POPMINVAL):
            inputCellDict[keys].changeProperty(CONST_POPULATION,CONST_POPMINVAL)

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
        if(itemRule.active == False):
            b1 = checkingRule(itemRule, inputState)
            if(b1==True and itemRule.ruleAction.isApplicable() == True):
                newAction = copy.deepcopy(itemRule.ruleAction)
                doApplyActionL.append(newAction)
                itemRule.makeActive()
                
            elif (b1==True and itemRule.ruleAction.isApplicable() ==False):
                newAction = copy.deepcopy(itemRule.ruleAction)
                newAction.decreaseTime()
                nextWaitedActionL.append(newAction)
                itemRule.makeActive()
                
            else:
                newRule = copy.deepcopy(itemRule)
                falseCondRuleL.append(newRule)
        
    for itemWaction in currentWaitedActionL:
        if(itemWaction.isApplicable() == True):
            doApplyActionL.append(itemWaction)
        else:
            newWAction = copy.deepcopy(itemWaction)
            newWAction.decreaseTime()
            nextWaitedActionL.append(newWAction)

    if(doApplyActionL):
        nextCellDict1 = doAction(inputState.ScellDict, doApplyActionL)
        nextCellDict = CheckSumLimit(nextCellDict1)
        
    else:
        nextCellDict = copy.deepcopy(inputState.ScellDict)
        

    orderNextCellDict = OrderedDict(sorted(nextCellDict.items(), key=lambda t: t[0]))
    orderScellDict = OrderedDict(sorted(inputState.ScellDict.items(), key=lambda t: t[0]))
    retI = NodeChecking(nextCellDict, nextWaitedActionL)
    
    if(retI == 0): 
        previousState = 'state' + str(stateCounterG)
        stateCounterG += 1
       
        stateNumstr = 'state' + str(stateCounterG)
        data = myState(stateCounterG, nextCellDict, isInitialG, nextWaitedActionL)
        Gmain.add_node(stateNumstr, data = myState(stateCounterG, nextCellDict, isInitialG, nextWaitedActionL))        
        Gmain.add_edge(previousState, stateNumstr)
        if(stateCounterG < 100):
            myMainFunc(data)
    else:
        print('we have this state number in graph: ', retI)
        previousState = 'state' + str(stateCounterG)
        print('previousState: ', previousState)
        stateNumstr = 'state' + str(retI)
        print('retI: ', retI)
        print('stateNumstr: ', stateNumstr)
        Gmain.add_edge(previousState, stateNumstr)
        print('we returned to a previousely created node in graph and it is finished :)')
        
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
    currentState = Gmain.node['state1']['data']
    im = Gmain.number_of_nodes()
        
    myMainFunc(currentState)
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

def doAllTests(runCount):
    testCounter = 0

    valuesBCell = []
    valuesNeu = []

    valuesTDC = []
    valuesCD4 = []
    valuesCD8 = []
    valuesTNK = []

    
    valuesMono = []
    valuesTregs = []
    valuesNKTC = []
    valuesGamma = []
    valuesEOS = []
    valuesBASO = []
    valuesHSC = []
    valuesPlasma = []
    
    #########
    graphLengthL = [0 for i in range(runCount)]
    cycleLengthL = [0 for i in range(runCount)]

    global cycleLength
    global Gmain
    global cellNameList
    
    while(testCounter < runCount):
        print('test counter: ', testCounter)
        doTest()
        #########
        valuesBCell = valuesBCell + findcellValuesD('B_cells','activity')
        valuesNeu = valuesNeu + findcellValuesD('Neutrophils', 'activity')
        valuesTDC = valuesTDC + findcellValuesD('Total_DCs', 'activity')
        valuesCD4 = valuesCD4 + findcellValuesD('CD4pos_T_cells', 'activity')
        valuesCD8 = valuesCD8 + findcellValuesD('CD8pos_T_cells', 'activity')
        valuesTNK = valuesTNK + findcellValuesD('Total_NK_cells', 'activity')
        valuesMono = valuesMono + findcellValuesD('Monocytes', 'activity')
        valuesTregs = valuesTregs + findcellValuesD('Tregs', 'activity')
        valuesNKTC = valuesNKTC +findcellValuesD('NKT_cells', 'activity')
        valuesGamma = valuesGamma + findcellValuesD('GammaDelta_T_cells', 'activity')
        valuesEOS = valuesEOS + findcellValuesD('Eosinophils', 'activity')
        valuesBASO = valuesBASO + findcellValuesD('Basophils', 'activity')
        valuesHSC = valuesHSC + findcellValuesD('HSC', 'activity')
        valuesPlasma = valuesPlasma + findcellValuesD('Plasma_cells', 'activity')
        
        testCounter = testCounter + 1
    
    #######################
    allCellValueMatrix = [valuesTDC,valuesMono,valuesBCell,valuesTNK, valuesCD8, valuesCD4, valuesTregs, valuesNKTC,valuesNeu,valuesGamma,valuesEOS,valuesBASO,valuesHSC,valuesPlasma]
###############################################
doAllTests(10)
