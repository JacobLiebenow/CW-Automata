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
from datacls import dayinfo
from datacls import contact
from datacls import band

#The database can effectively be traversed using the "pointer" variables province, town, and showstage.
#Using this, exact positions in memory can be editted, thus allowing for interchangability of inheritance.
def main():
	
	#In future iterations, data won't be hardcoded in but rather able to be input via a GUI
	#These are simply test cases
	database = datacenter.Datacenter()
	
	#Creating the states of Ohio and Illinois, and adding it to the database
	province = state.State("Illinois")
	database.addState(province)
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
	
	#Select a state not present in the database already to test a false response
	province = database.selectState("Pennsyltucky")
	
	
	#Generating a test day in the database, and seeing how it handles crossover of objects
	newDay = dayinfo.DayInfo(2018,4,1,database)
	province = database.selectState("Ohio")
	provinceName = province.stateName
	town = province.selectCity("Columbus")
	townName = town.cityName
	showstage = town.selectVenue("Kafe Kerouac")
	stageName = showstage.venueName
	newDay.addState(provinceName)
	newDay.addCity(provinceName, townName)
	newDay.addVenue(provinceName, townName, stageName)
	showstage = town.selectVenue("Ace of Cups")
	stageName = showstage.venueName
	newDay.addVenue(provinceName, townName, stageName)
	
	print()
	print("On",newDay.calendarDate,"you will be in the state(s) of..")
	newDay.printStates()
	print("While there, you will visit....")
	newDay.printCities()
	print("and perform at......")
	newDay.printVenues()
	
	print()
	newDay.removeVenue(provinceName, townName, stageName)
	print("REMOVED ACE OF CUPS")
	print("On",newDay.calendarDate,"you will be in the state(s) of..")
	newDay.printStates()
	print("While there, you will visit....")
	newDay.printCities()
	print("and perform at......")
	newDay.printVenues()
	
	print()
	print()
	print("Database check")
	database.printStates()
	
	###################
	######CONTACT######
	######TESTING######
	###################
	
	newContact = contact.Contact(database, "Sandeep", "123 House With No Name Dr.", 6145555555, "cool.email@email.com")
	database.addContact(newContact)
	newContact = database.selectContact("Sandeep")
	newBand = band.Band("Canadian Waves")
	newBand.addRole("Manager", newContact)
	newBand.addRole("DIY Artist", newContact)
	
	print()
	print()
	newContact.printRoles()
	
	showstage = venue.Venue("THWNN")
	province = database.selectState("Ohio")
	town = province.selectCity("Columbus")
	town.addVenue(showstage)
	showstage.addManager("Former Owner",newContact)
	
	print()
	print("Added THWNN to Columbus")
	print()
	newContact.printRoles()
	
	

if __name__ == '__main__':
	main()
