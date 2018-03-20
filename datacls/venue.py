#Written by: Jacob S Liebenow
#
#Each venue has an associated name, address, bands, and promoters that frequent the establishment.
#
#DevNote(3/20/2018, 11:48AM EST): I have to wonder if it would be more efficient to organize this into 
#multiple classes in a single python module.  It would make the imports decidedly less messy, however it
#would make the modules themselves more messy.  Something to weigh, although I'm inclined to continue down
#the multi-module route.  It's good OOP practice if nothing else, and what I'm used to from Java.

class Venue:
	
	#Each venue has associated bands and promoters/bookers...
	#...however those bands and bookers aren't tied solely to a specific venue, or even a city or state
	def __init__(self, venueName):
		self.venueName = venueName
