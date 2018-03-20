#Written by: Jacob S Liebenow
#Version: 0.0.2
#Stage: InDev/Pre-alpha
#
#
#
#This program is designed primarily to organize venues, bands, bookers, etc. into workable data.  If
#possible, this data will be analyzed for future use, potentially using data mining. All data will be
#uploaded to Google Sheets/Drive, and can be managed from there.  However, in this initial state, I
#want to work with local data to make sure flow of said data is correct.
#
#It's possible the directories could be better managed than this, but because of interchangability of
#the classes and data types, and early stage of development I've decided to organize them into a single
#datacls directory for the time being.

from datacls import state
from datacls import city
from datacls import venue
from datacls import datacenter

#The database can effectively be traversed using the "pointer" variables province, town, and showstage.
#Using this, exact positions in memory can be editted, thus allowing for interchangability of inheritance.
def main():
	
	#In future iterations, data won't be hardcoded in but rather able to be input via a GUI
	#These are simply test cases
	database = datacenter.Datacenter()
	
	#Creating the state of Ohio, and adding it to the database
	province = state.State("Ohio")
	database.addState(province)
	
	#Populating cities within Ohio
	town = city.City("Columbus")
	province.addCity(town)	
	town = city.City("Cleveland")
	province.addCity(town)	
	town = city.City("Cincinnati")
	province.addCity(town)	
	town = city.City("Dayton")
	province.addCity(town)
	
	#Searching for the city of Columbus within state of Ohio, and thereby selecting it for manipulation
	town = province.selectCity("Columbus")
	
	showstage = venue.Venue("Kafe Kerouac")
	town.addVenue(showstage)
	
	showstage = venue.Venue("Ace of Cups")
	town.addVenue(showstage)
	
	#Searching for Cincinnati, and adding Bogart's as a venue
	town = province.selectCity("Cincinnati")
	showstage = venue.Venue("Bogarts's")
	town.addVenue(showstage)
	
	#Print all state-related data within the datacenter object
	database.printStates()
	
	
	province = database.selectState("Indiana")
	
	#This is only in the code so that the console remains open if run via double-click as opposed to shell
	input()

if __name__ == '__main__':
	main()
