from All import *
##################################################################################
Gmain = nx.Graph()
isInitialG = True
stateCounterG = 1

def constructFirstState():
    global stateCounter
    global Gmain
    global isInitialG
    global firstState 		
    stateCounter = 1
    isInitialG = True
    waitedActions1= []
    Gmain.clear()
    firstState = myState(stateCounter, cellDict, isInitialG, waitedActions1)       
    Gmain.add_node(stateCounterG,data = firstState)   
    isInitialG = False

def printCellDict(inputCellDic):
    print('\nList of cells in dictionary:')
    for keys, values in inputCellDic.items():
        #print(keys)
        print(values)
############################################################################  

def MainLoop(inputState):
	global nextState
	global stateCounter 
	global queue1             
	#constructFirstState()		
	queue1                = []                        # main queue for the algorithm
	queue2                = []                               # temporary queue for the algorithm
	actionList            = []
	waitingActionList     = []
	currentState          = copy.deepcopy(inputState)	 # testing
	#currentState          = copy.deepcopy(firstState)        # begin at the first state
	print('currentState is %s' %currentState)
	print('its dictionary is')
	printCellDict(currentState.ScellDict)	
	queue1.append(currentState)
		
	for rule in ruleList:					 # try to check if there are fulfilled rules on currentState
		bool = checkingRule(rule, currentState)
		if(bool == True and rule.ruleAction.isApplicable() == True):    # isApplicable() checks if the time is 1 or not):
			newAction = copy.deepcopy(rule.ruleAction)
			actionList.append(newAction)
			
		elif(bool == True and rule.ruleAction.isApplicable() == False):
			newAction = copy.deepcopy(rule.ruleAction)
			newAction.decreaseTime()			# decrease the time with 1
			waitingActionList.append(newAction)
              
	print('actionList contains')
	for action in actionList:	
		print(action)
	print('waitingActionList contains')
	for action in waitingActionList:
		print(action)
	# important algorithm
	index = 0
	while(index < len(actionList)):
		action = actionList[index]
		index += 1
		print('action to apply: %s' %action)
		while(queue1):                                          # while queue1 is not empty
			nextState = queue1.pop(0)			# pop the first element
			print(nextState)
			# this is creating 2 branches part
			NotOccuredCellDict = nextState.ScellDict
			OccuredCellDict    = performAction(nextState.ScellDict,action)
			stateCounter      += 1
			tmpStateOccured    = myState(stateCounter, OccuredCellDict, isInitialG, waitingActionList)
			stateCounter      += 1
			tmpStateNotOccured = myState(stateCounter, NotOccuredCellDict, isInitialG, waitingActionList)
			#
			queue2.append(tmpStateOccured)
			queue2.append(tmpStateNotOccured)
		queue1 = copy.deepcopy(queue2)                          # if queue1 = queue2  we will get stuck in while(queue1)			
		queue2 = copy.deepcopy([])				# emptying queue2
				
	actionList = copy.deepcopy([])					# emptying the actionList
	#

	for state in queue1:
		currentState.childList.append(state)
	#print('currentState is %s' %currentState)
	#print('childlist has')
	#for state in currentState.childList:
	#	print(state)	
	#if(currentState.waitedActions):		  # if there are waited actions
	#	for action in currentState.waitedActions:     
	#		if(action.isApplicable()):               # if the time is 1			        
	#			actionList.append(action)        # put the action in the actionList 
	#			print(action)
	
	#print(currentState.childList[4])
	#printCellDict(currentState.childList[4].ScellDict)
	#for waitedaction in currentState.childList[4].waitedActions:
	#	print(waitedaction)
	
	for state in currentState.childList:
		Gmain.add_node(state.stateID)
		Gmain.add_edge(currentState.stateID, state.stateID)
	
	
	#nx.draw_spring(Gmain)
	#plt.show()

############################################################################   Execution part
constructFirstState()
currentState          = copy.deepcopy(firstState)        # begin at the first state
MainLoop(currentState)
for state in queue1:
	MainLoop(state)
nx.draw_spring(Gmain)
plt.show()
