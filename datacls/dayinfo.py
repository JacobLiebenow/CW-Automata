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
from datacls import contact
from datacls import organization
from datacls import datacenter

class DayInfo:

	stateNamePointer = ""
	
	def __init__(self, dateName, venues = None, venueNames = None, contacts = None, contactNames = None, organizations = None, organizationName = None):
		self.dateName = dateName
		
		if venues is None:
			self.venues = []
		else:
			self.venues = venues
			
		if venueNames is None:
			self.venueNames = []
		else:
			self.venueNames = venueNames
			
		# if coordinates is None:
			# self.coordinates = []
		# else:
			# self.coordinates = coordinates	
			
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
			
		
			
	
	#The way a day will store its data will be a little different from the other classes.
	#Similar to datacenter, it will select venues, contacts, and organizations based off their names.
	#These objects will be sourced from datacenter
			
	#Add venues, contacts, and organizations based off of the datacenter object
	def addVenue(self, state, city, venue):
		if venue not in self.venues:
			self.venues.append(venue)
			self.venueNames.append(venue.venueName)
		else: 
			print("Venue by the name of '",venue.venueName,"' not found.  Check spelling or if the venue was in the database.")
			
	def addContact(self, contact):
		if contact not in self.contacts:
			self.contacts.append(contact)
			self.contactNames.append(contact.name)
		else: 
			print("Organization by the name of '",contact.name,"' not found.  Check spelling or if the organization was in the database.")
			
	def addOrganization(self, organization):
		if organization not in self.organizations:
			self.organizations.append(organization)
			self.organizationNames.append(organization.organizationName)
		else: 
			print("Organization by the name of '",organization.organizationName,"' not found.  Check spelling or if the organization was in the database.")
	
	
	#Remove a selected venue, contact, or organization		
	def removeVenue(self, venue):
		if venue in self.venues:
			self.venues.remove(venue)
			self.venueNames.remove(venue.venueName)
			
	def removeContact(self, contact):
		if contact in self.contacts:
			self.contacts.remove(contact)
			self.contactNames.remove(contact.name)
	
	def removeOrganization(self, organization):
		if organization in self.organizations:
			self.organizations.remove(organization)
			self.organizationNames.remove(organization.organizationName)
	
	
	#Add functionality to select venue, contact, and organization within the dayinfo object
	def selectVenue(self, venueName):
		venueFound = False
		
		for venue in self.venues:
			if venueName == venue.venueName:
				venueFound = True
				return venue
		
		if venueFound == False:
			print("No venue found by the name '"+venueName+"'")
			return None
			
	def selectContact(self, contactName):
		contactFound = False
		
		for contact in self.contacts:
			if contactName == contact.name:
				contactFound = True
				return contact
		
		if contactFound == False:
			print("No contact found by the name '"+contactName+"'")
			return None
			
	def selectOrganization(self, organizationName):
		organizationFound = False
		
		for organization in self.organizations:
			if organizationName == organization.organizationName:
				organizationFound = True
				return organization
		
		if organizationFound == False:
			print("No organization found by the name '"+organizationName+"'")
			return None
			
			
			
	def printVenues(self):
		for venue in self.venues:
			print(venue.venueName)
