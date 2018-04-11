#Written by: Jacob S Liebenow
#
#
#
#Each venue has an associated name, address, bands, and promoters that frequent the establishment.
#
#DevNote(3/20/2018, 11:48AM EST): I have to wonder if it would be more efficient to organize this into 
#multiple classes in a single python module.  It would make the imports decidedly less messy, however it
#would make the modules themselves more messy.  Something to weigh, although I'm inclined to continue down
#the multi-module route.  It's good OOP practice if nothing else, and what I'm used to from Java.

from datacls import datacenter
from datacls import state
from datacls import city
from datacls import contact
from datacls import organization

class Venue:
	
	#Each venue has associated bands and promoters/bookers...
	#...however those bands and bookers aren't tied solely to a specific venue, or even a city or state
	def __init__(self, venueName, stateName, cityName, address, zip, phone, links, contacts, email, notes, roles=None, managers=None):
		self.venueName = venueName
		self.stateName = stateName
		self.cityName = cityName
		self.address = address
		self.zip = str(zip)
		self.phone = str(phone)
		self.links = links
		self.contacts = contacts
		self.email = email
		self.notes = notes

		self.latitude = 0
		self.longitude = 0
		
		
		if roles is None:
			self.roles = []
		else: 
			self.roles = roles
		
		if managers is None:
			self.managers = []
		else:
			self.managers = managers
		
	
	def addManager(self, roleName, contact):
	
		if roleName not in self.roles:
			contact.addManagerRole(self.venueName, roleName)
			self.roles.append(roleName)
		
		if contact not in self.managers:	
			self.managers.append(contact)
