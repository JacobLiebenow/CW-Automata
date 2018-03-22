#Written by: Jacob S Liebenow
#
#
#
#Each day will have one or more associated states/cities/venues.  Contacts will be associated with them.
#Each day also has a datetime associated with it, similar to an index for an array.
#Likewise, datetime will only have a single associated day object.

import datetime
from datacls import state
from datacls import city
from datacls import venue
from datacls import datacenter

class DayInfo:

	stateNumber = 0
	cityNumber = 0
	venueNumber = 0
	stateNamePointer = ""
	
	def __init__(self, year, month, day, database, states = None, cities = None, venues = None):
		self.calendarDate = datetime.date(year, month, day)
		self.datacenter = database
		
		if states is None:
			self.states = []
		else: 
			self.states = states
			for state in self.states:
				self.stateNumber += 1
			
		if cities is None:
			self.cities = []
		else:
			self.cities = cities
			for city in self.cities:
				self.cityNumber += 1
		
		if venues is None:
			self.venues = []
		else:
			self.venues = venues
			for venue in self.venues:
				self.venueNumber += 1
			
	
	#The way a day will store its data will be a little different from the other classes.
	#Similar to datacenter, it will select states, cities, and venues based off their names.  However, 
	#the states, cities, and venues, while being identical to that info stored in the datacenter, will
	#be copies of those objects as opposed to the objects themselves.
	#
	#These functions add states, cities, and venues found in the Datacenter object...
	def addState(self, stateName):
		statePointer = self.datacenter.selectState(stateName)
		if statePointer not in self.states:
			self.states.append(statePointer)
			self.stateNumber += 1
		else:
			print("State by the name of '",stateName,"' not found.  Check spelling or if the state was in the database.")
			
	def addCity(self, stateName, cityName):
		statePointer = self.datacenter.selectState(stateName)
		cityPointer = statePointer.selectCity(cityName)
		if cityPointer not in self.cities:
			self.cities.append(cityPointer)
			self.cityNumber += 1
		else:
			print("City by the name of '",cityName,"' not found.  Check spelling or if the city was in the database.")
			
	def addVenue(self, stateName, cityName, venueName):
		statePointer = self.datacenter.selectState(stateName)
		cityPointer = statePointer.selectCity(cityName)
		venuePointer = cityPointer.selectVenue(venueName)
		if venuePointer not in self.venues:
			self.venues.append(venuePointer)
			self.venueNumber += 1
		else: 
			print("Venue by the name of '",venueName,"' not found.  Check spelling or if the venue was in the database.")
	

	#...remove states, cities, and venues found in the DayInfo object...
	def removeState(self, stateName):
		statePointer = self.datacenter.selectState(stateName)
		if statePointer in self.states:
			self.states.remove(statePointer)
			self.stateNumber -= 1
		
	def removeCity(self, stateName, cityName):
		statePointer = self.datacenter.selectState(stateName)
		cityPointer = statePointer.selectCity(cityName)
		if cityPointer in self.cities:
			self.cities.remove(cityPointer)
			self.cityNumber -= 1
			
	def removeVenue(self, stateName, cityName, venueName):
		statePointer = self.datacenter.selectState(stateName)
		cityPointer = statePointer.selectCity(cityName)
		venuePointer = cityPointer.selectVenue(venueName)
		if venuePointer in self.venues:
			self.venues.remove(venuePointer)
			self.venueNumber -= 1
	
	
	#...and print data from the DayInfo object.
	def printStates(self):
		for state in self.states:
			print(state.stateName)
	
	def printCities(self):
		for city in self.cities:
			print(city.cityName)
			
	def printVenues(self):
		for venue in self.venues:
			print(venue.venueName)
