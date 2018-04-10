#Written by: Jacob S Liebenow
#
#
#
#A organization is a conglomerate of contacts, each with their own associated role (which might or might not be
#specified).  Bands are scheduled to play at various venues during certain days.  They might also frequent
#venues, and be worked with promoters.

from datacls import contact

class Organization:
	
	def __init__(self, name, contacts=None, roles=None):
		self.organizationName = name
		
		if contacts is None:
			self.contacts = []
		else: 
			self.contacts = contacts
		
		if roles is None:
			self.roles = []
		else:
			self.roles = roles
			
	
	
	def addRole(self, roleName, contact):
		
		#Eventually, because of the chance of multiple same-titled roles occuring within the organization, the user
		#should be told that a organization role exists if already put in, and should be allowed the chance to confirm
		#if "yes" or "y" is input, and to avoid adding for any other input. 
		#
		#For now, however, we are assuming roles are singular, and thus only noted once.
		
		if roleName not in self.roles:
			contact.addBandRole(self.bandName, roleName)
			self.roles.append(roleName)
		
		if contact not in self.contacts:
			self.contacts.append(contact)
		
