#Written by: Jacob S Liebenow

from datacls import venue

#The city is the primary unit of organization, containing the most data. Cities are
#organized into states, but the cities themselves contain venues, bands, etc.

class City:
	
	venueNumber = 0

	#Each city consists of its own name, venues, bands (to be added), and promoters/bookers (to be added)
	def __init__(self, cityName, venues=None):
		self.cityName = cityName
		if venues is None:
			self.venues = []
		else:
			self.venues = venues
		
	#The following 3 functions are self explanatory by title - add, remove, or print venues
	def addVenue(self, venue):
		if venue not in self.venues:
			self.venues.append(venue)
			self.venueNumber += 1
			
	def removeVenue(self, venue):
		if venue in self.venues:
			self.venues.remove(venue)
			self.venueNumber -= 1
			
	def printVenues(self):
		for venue in self.venues:
			print("----->", venue.venueName)
			
	def selectVenue(self, venueName):
		venueFound = False
		
		for venue in self.venues:
			if venueName == venue.venueName:
				venueFound = True
				return venue
		
		if venueFound == False:
			print("No venue found by the name '", venueName, "'")
			return None
