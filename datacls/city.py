#Written by: Jacob S Liebenow



from datacls import venue
from datacls import contact
from datacls import organization

#The city is the primary unit of organization, containing the most data. Cities are
#organized into states, but the cities themselves contain venues, bands, etc.

class City:


	#Each city consists of its own name, venues, bands (to be added), and promoters/bookers (to be added)
	def __init__(self, cityName, venues = None, venueNames = None, contacts = None, contactNames = None, organizations = None, organizationNames = None):
		self.cityName = cityName
		
		if venues is None:
			self.venues = []
		else:
			self.venues = venues
		
		if venueNames is None:
			self.venueNames = []
		else: 
			self.venueNames = venueNames
		
		if contacts is None:
			self.contacts = []
		else:
			self.contacts = contacts
			
		if contactNames is None:
			self.contactNames = []
		else:
			self.contactNames = contactNames
		
		if organizations is None:
			self.organizations = []
		else:
			self.organizations = organizations
			
		if organizationNames is None:
			self.organizationNames = []
		else:
			self.organizationNames = organizationNames
		
	#The following 3 functions are self explanatory by title - add, remove, or print venues
	def addVenue(self, venue):
		if venue not in self.venues:
			self.venues.append(venue)
			
	def removeVenue(self, venue):
		if venue in self.venues:
			self.venues.remove(venue)
			
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
			print(("No venue found by the name '"+venueName+"'"))
			return None
		

		
	def addContact(self, contact):
		if contact not in self.contacts:
			self.contacts.append(contact)
			
	def removeContact(self, contact):
		if contact in self.contacts:
			self.contacts.remove(contact)
			
	def selectContact(self, contactName):
		contactFound = False
		
		for contact in self.contacts:
			if contactName == contact.name:
				contactFound = True
				return contact
		
		if contactFound == False:
			print(("No contact found by the name '"+contactName+"'"))
			return None
			
			
	def addOrganization(self, organization):
		if organization not in self.organizations:
			self.organizations.append(organization)
			
	def removeOrganization(self, organization):
		if organization in self.organizations:
			self.organizations.remove(organization)
			
	def selectOrganization(self, organizationName):
		organizationFound = False
		
		for organization in self.organizations:
			if organizationName == organization.organizationName:
				organizationFound = True
				return organization
		
		if organizationFound == False:
			print(("No organization found by the name '"+organizationName+"'"))
			return None
