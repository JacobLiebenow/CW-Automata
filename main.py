#Written by: Jacob S Liebenow
#Version: 0.0.3
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

#Import Kivy GUI Framework
import kivy
from kivy.app import App
from kivy.uix.button import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton

#Import custom classes
from datacls import state
from datacls import city
from datacls import venue
from datacls import datacenter
from datacls import dayinfo
from datacls import contact
from datacls import band

kivy.require('1.9.0')

class MainMenuButton(ListItemButton):
	pass

class MainMenuLayout(BoxLayout):
	def goToDatabase(self):
		pass
	
	def goToCalendar(self):
		pass
	
class MainMenu(App):
	def build(self):
		return MainMenuLayout()
		

def main():
	mainMenu = MainMenu()
	mainMenu.run()
	
	

if __name__ == '__main__':
	main()
