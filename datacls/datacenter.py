#Written by: Jacob S Liebenow
#
#
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
from datacls import contact
from datacls import band

class Datacenter: 
	
	stateNumber = 0
	
	
	#The datacenter's primary branches are provinces/states, which contain cities, venues, etc.  However, I
	#also want to allow for a separate type of branch from the datacenter root - contacts, which contains
	#bands, bookers, promoters, and whoever else might be considered relevant.  Contacts might normally be
	#organized by city, but I'd like overall contact searching functionality irrespective of location.  Another
	#possible branch - days, which has one or more associated states/cities (otherwise considered travel days)
	def __init__(self, states=None, contacts=None, bands=None):
		if states is None:
			self.states = []
		else: 
			self.states = states
		
		if contacts is None:
			self.contacts = []
		else:
			self.contacts = contacts
			
		if bands is None:
			self.bands = []
		else:
			self.bands = bands
	
	
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
			
	
	
	#The datacenter should be the primary table for contact object management
	def addContact(self, contact):
		if contact not in self.contacts:
			self.contacts.append(contact)
	
	def removeContact(self, contact):
		if contact in self.contacts:
			self.contacts.remove(contact)
			
	def printContacts(self):
		for contact in self.contacts:
			print(contact.name)
			
	def selectContact(self, contactName):
		contactFound = False
		
		for contact in self.contacts:
			if contactName == contact.name:
				contactFound = True
				return contact
		
		if contactFound == False:
			print("No contact found by the name of '",contactName,"'")
			print("Check spelling and make sure contact was initialized")
	
	
	
	#The datacenter will manage band objects, as well
	def addBand(self, band):
		if band not in self.bands:
			self.bands.append(band)
			
	def removeBand(self, band):
		if band in self.band:
			self.bands.remove(band)
			
	def printBands(self):
		for band in self.bands:
			print(band.bandName)
			
	def selectBand(self, bandName):
		bandFound = False
		
		for band in self.bands:
			if bandName == band.bandName:
				bandFound = True
				return band
			
		if bandFound == False:
			print("No band found by the name of '",bandName,"'")
			print("Check spelling and make sure contact was initialized")
