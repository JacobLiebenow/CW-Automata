#Written by: Jacob S Liebenow

from datacls import city
from datacls import venue

#This is the primary unit of location-based organization within the datacenter.  States contain cities, which contain venues and contacts
class State:
	
	cityNumber = 0
	
	#Each state contains cities, and within those cities are venues, bands, promoters/bookers, etc.
	def __init__(self, stateName, cities=None):
		self.stateName = stateName
		if cities is None:
			self.cities = []
		else: 
			self.cities = cities
	
	#The following 3 functions serve the relative same function as in city.py - add, remove, or print cities
	def addCity(self, city):
		if city not in self.cities:
			self.cities.append(city)
			self.cityNumber += 1
		
	def removeCity(self, city):
		if city in self.cities:
			self.cities.remove(city)
			self.cityNumber -= 1
			
	def printCities(self):
		for city in self.cities:
			print("-->",city.cityName)
			city.printVenues()
	
	
	#The selectCity function searches for a city name within the State object, and returns the whole city object
	def selectCity(self, cityName):
		cityFound = False
		
		for city in self.cities:
			if cityName == city.cityName:
				cityFound = True
				return city
		
		if cityFound == False:
			print("No city found by the name '", cityName, "'")
			return None
				
	
	#This function might be unnecessary now that the data is searchable, but this should add a venue to a state
	def addVenueToCity(self, city, venue):
		if city in self.cities:
			if venue not in city.venues:
				city.venues.append(venue)
				city.venueNumber += 1
