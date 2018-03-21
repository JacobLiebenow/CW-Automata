#Written by: Jacob S Liebenow
#
#This module was created upon the determination that a general, all-encompassing data unit with which to
#place all other objects within was necessary - a general "sheet," if you will, that's able to point
#to all other data points.  This, decidedly, should make it easier to manipulate data using interchangable
#inheritance - IE, bands within venues, venues containing bands, state management, etc.  Ideally, this
#module and class won't ever really be shown, and is only for handling data.
#
#The datacenter class will be instantiated with all current data from Google, and all subsequent objects of
#associated classes will be managed from there.

from datacls import state
from datacls import city
from datacls import venue
from datacls import dayinfo

class Datacenter: 
	
	stateNumber = 0
	
	
	#The datacenter's primary branches are provinces/states, which contain cities, venues, etc.  However, I
	#also want to allow for a separate type of branch from the datacenter root - contacts, which contains
	#bands, bookers, promoters, and whoever else might be considered relevant.  Contacts might normally be
	#organized by city, but I'd like overall contact searching functionality irrespective of location.  Another
	#possible branch - days, which has one or more associated states/cities (otherwise considered travel days)
	def __init__(self, states=None):
		if states is None:
			self.states = []
		else: 
			self.states = states
	
	
	#The following 3 functions are self-explanatory by title - add, remove, and print states
	def addState(self, state):
		if state not in self.states:
			self.states.append(state)
			self.stateNumber += 1
		
	def removeState(self, state):
		if state in self.states:
			self.states.remove(state)
					
	def printStates(self):
		for state in self.states:
			print(state.stateName)
			state.printCities()
			
			
	#The selectState function should allow for a variable in main.py to grab the exact state searched		
	def selectState(self, stateName):
		stateFound = False
		
		for state in self.states:
			if stateName == state.stateName:
				stateFound = True
				return state
		
		if stateFound == False:
			print("No state found by the name '",stateName,"'")
			return None
