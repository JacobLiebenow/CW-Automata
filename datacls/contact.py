#Written by: Jacob S Liebenow
#
#
#
#This is the contact superclass that will be utilized by CW-Automata.  Contacts can be broken down into
#a few different categories - bands (which have a name, and members within a band with various roles),
#promoters, venue managers, and general contacts which might be useful but harder to classify.  However,
#irrespective of their roles, they will all have consistent data requirements among them - name, address, 
#phone number, email address, associated links.
#
#A band might consist of multiple contacts, and thus can be considered a grouping of contact objects.  Each
#contact within the band might have a specific role (guitarist, manager, etc.).  Likewise, all contacts
#will be stored in the datacenter.  However, a contact (namely a promoter) might also manage bands, too.
#
#An expected complication is multiple contacts that might have the same name (IE: multiple John Smiths), 
#and the need to have some sort of ID placed on them that would make them searchable.
#
#DevNote (3/22/2018, 12:56 PM): I could have contact names selectable from a dropdown list (listing all
#contacts), or even(and this would likely be in conjunction with the dropdown list) list all contacts, 
#since multiple copies of the same name could be added as an identifier.  Basically, the addContact() function 
#would search for the same contact object as opposed to the same name, unlike cities, states, and venues.

from datacls import datacenter
from datacls import state
from datacls import city
from datacls import venue

class Contact:
	
	
	def __init__(self, database, name, address, phoneNumber, email, links=None, roles=None, bands=None):
		self.datacenter = database
		self.name = name
		self.address = address
		self.phoneNumber = phoneNumber
		self.email = email
		
		if links is None:
			self.links = []
		else: 
			self.links = links
			
		if roles is None:
			self.roles = []
		else:
			self.roles = roles
			
		if bands is None:
			self.bands = []
		else:
			self.bands = bands

	
	
	
	def addLink(self, linkName):
		if linkName not in self.links:
			self.links.append(linkName)	
			
	#Because of the nature of multiple roles in a band, the ability to add more than one role is key
	def addBandRole(self, bandName, roleName):
		if (bandName+"-"+roleName) not in self.roles:
			self.roles.append(bandName+"-"+roleName)
	
	def addManagerRole(self, venueName, roleName):
		if (venueName+"-"+roleName) not in self.roles:
			self.roles.append(venueName+"-"+roleName)
		
	def printRoles(self):
		print(self.name,":")
		for role in self.roles:
			print(role)
