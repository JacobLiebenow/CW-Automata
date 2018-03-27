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
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton

#Import MapView
from kivy.garden.mapview import MapView

#Import geopy
from geopy import geocoders

#Import Calendar classes
import datetime

#Import custom classes
from datacls import state
from datacls import city
from datacls import venue
from datacls import datacenter
from datacls import dayinfo
from datacls import contact
from datacls import band

kivy.require('1.9.0')
Builder.load_string("""
#:import MapSouce mapview.MapSource

<ScreenMainMenu>:
	orientation: "vertical"
	padding: 40
	spacing: 40
	
	RelativeLayout:
		size_hint_y: 0.75
		pos_hint: {"center_x": 0.5, "top": 1}
		Label:
			text: "Welcome to Waves In Motion"
		
	RelativeLayout:
		orientation: "vertical"
		padding: 10
		size_hint_y: 0.25
		pos_hint: {"center_x": 0.5, "y": 0}
		Button:
			text: "Database Manager"
			pos_hint: {"center_x": 0.5, "top": 1}
			size_hint_x: 0.5
			size_hint_y: 0.5
			on_press: 
				root.manager.transition.direction = "left"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_database"
		Button:
			text: "Calendar"
			pos_hint: {"center_x": 0.5, "bottom": 0}
			size_hint_x: 0.5
			size_hint_y: 0.5
			on_press: 
				root.manager.transition.direction = "left"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_calendar"
		
		
				

<ScreenDatabase>
	orientation: "vertical"
	padding: 20
	spacing: 40
	RelativeLayout:
		size_hint_y: 0.02
		pos_hint: {"center_x": 0.5, "top": 1}
	RelativeLayout:
		size_hint_y: 0.18
		pos_hint: {"center_x": 0.5, "top": 0.98}
		Label:
			halign: "center"
			valign: "center"
			text: "Database Manager"
		
		Button:
			size_hint_x: None
			size_hint_y: None
			height:"40dp"
			length:"40dp"
			text: "Back"
			pos_hint: {"right": 0.99, "top": 1}
			on_press:
				root.manager.transition.direction = "right"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_mainmenu"
		BoxLayout:
			size_hint_y: 0.3
			size_hint_x: 0.8
			pos_hint: {"center_x": 0.5, "bottom": 0}
			Label:
				size_hint_x: 0.2
				text:"Link to Database"
			TextInput:
				size_hint_x: 0.6
				id: spreadsheet
				pos_hint: {"left": 0, "bottom": 0}
			Button:
				size_hint_x: 0.2
				text: "Submit"
				pos_hint: {"right": 1, "bottom": 0}
			
<ScreenCalendar>
	spreadsheetLink: spreadsheet
	datetimePicker: datetime
	orientation: "vertical"
	padding: 20
	spacing: 40
	RelativeLayout:
		size_hint_y: 0.02
		pos_hint: {"center_x": 0.5, "top": 1}
	RelativeLayout:
		size_hint_y: 0.18
		pos_hint: {"center_x": 0.5, "top": 0.98}
		Label:
			halign: "center"
			valign: "center"
			text: "Calendar"
		
		Button:
			size_hint_x: None
			size_hint_y: None
			height:"40dp"
			length:"40dp"
			text: "Back"
			pos_hint: {"right": 0.99, "top": 1}
			on_press:
				root.manager.transition.direction = "right"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_mainmenu"
		BoxLayout:
			size_hint_y: 0.3
			size_hint_x: 0.8
			pos_hint: {"center_x": 0.5, "bottom": 0}
			Label:
				size_hint_x: 0.1
				text:"Database:  "
			TextInput:
				size_hint_x: 0.7
				id: spreadsheet
				pos_hint: {"left": 0, "bottom": 0}
			Button:
				size_hint_x: 0.2
				text: "Submit"
				pos_hint: {"right": 1, "bottom": 0}
		
	RelativeLayout:	
		size_hint_y: 0.8
		pos_hint: {"center_x": 0.5, "bottom": 0}
		Button:
			id: datetime
			size_hint_y: 0.5
			size_hint_x: 0.3
			pos_hint: {"left": 0, "top": 1}
		Button:
			size_hint_y: 0.5
			size_hint_x: 0.3
			pos_hint: {"left": 0, "bottom": 0}
			text: "Day Info"
		MapView:	
			size_hint_x: 0.7
			size_hint_y: 1
			pos_hint: {"right": 1, "bottom": 0}
			id: mapview
			lat: 50.6394
			lon: 3.057
			zoom: 8
	
""")

#Create the base calendar class for use as a widget in the Calendar screen
class Calendar():
	
	def __init__(self, tday):
		#Create the general data structure of the calendar - 6 rows of 7 days each
		self.fillerDate = datetime.date.today()
		self.tdelta = datetime.timedelta(days=1)
		self.row1 = [self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate]
		self.row2 = []
		self.row3 = []
		self.row4 = []
		self.row5 = []
		self.row6 = []
		self.calendarObj = [self.row1, self.row2, self.row3, self.row4, self.row5, self.row6]
		self.today = tday
		self.rowIncrementerIndex = 0
		self.day = datetime.date(tday.year,tday.month,1)
		self.dayPlaceholder = datetime.date(tday.year,tday.month,1)
		self.currentYear = tday.year
		self.currentMonth = tday.month
		
		#Populate calendar for the current month
		self.row1[self.day.weekday()] = self.day
		if self.day.weekday() != 0:
			while self.day.weekday() != 0:
				self.day -= self.tdelta
				self.row1[self.day.weekday()] = self.day
			self.day = self.dayPlaceholder
		while self.day.weekday() != 6:
			self.day += self.tdelta
			self.row1[self.day.weekday()] = self.day
		self.rowIncrementerIndex += 1
		self.day += self.tdelta
		while self.rowIncrementerIndex != 6:
			while self.day.weekday() != 6:
				self.calendarObj[self.rowIncrementerIndex].append(self.day)
				self.day += self.tdelta
			if self.rowIncrementerIndex != 6:
				self.calendarObj[self.rowIncrementerIndex].append(self.day)
				self.day += self.tdelta
			self.rowIncrementerIndex += 1
		
		for row in self.calendarObj:
			for day in row:
				print(day)
		#Reset the row incrementer so the decrement and increment month functions can reuse variable
		self.rowIncrementerIndex = 0
	
	def update(self, day):
		#Reset the general data structure of the calendar
		self.fillerDate = datetime.date.today()
		self.tdelta = datetime.timedelta(days=1)
		self.row1 = [self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate, self.fillerDate]
		self.row2 = []
		self.row3 = []
		self.row4 = []
		self.row5 = []
		self.row6 = []
		self.calendarObj = [self.row1, self.row2, self.row3, self.row4, self.row5, self.row6]
		self.rowIncrementerIndex = 0
		self.day = day
		self.dayPlaceholder = day
		
		#Populate calendar for the chosen month
		self.row1[self.day.weekday()] = self.day
		if self.day.weekday() != 0:
			while self.day.weekday() != 0:
				self.day -= self.tdelta
				self.row1[self.day.weekday()] = self.day
			self.day = self.dayPlaceholder
		while self.day.weekday() != 6:
			self.day += self.tdelta
			self.row1[self.day.weekday()] = self.day
		self.rowIncrementerIndex += 1
		self.day += self.tdelta
		while self.rowIncrementerIndex != 6:
			while self.day.weekday() != 6:
				self.calendarObj[self.rowIncrementerIndex].append(self.day)
				self.day += self.tdelta
			if self.rowIncrementerIndex != 6:
				self.calendarObj[self.rowIncrementerIndex].append(self.day)
				self.day += self.tdelta
			self.rowIncrementerIndex += 1
			
		for row in self.calendarObj:
			for day in row:
				print(day)
		
		#Reset the row incrementer so the decrement and increment month functions can reuse variable
		self.rowIncrementerIndex = 0
	
	
	
	#Self-explanatory functions to increment/decrement the month when a button is pressed
	def incrementMonth(self):
		self.currentMonth += 1
		if self.currentMonth > 12:
			self.currentMonth = 1
			self.currentYear += 1
		day = datetime.date(self.currentYear, self.currentMonth, 1)
		print()
		print("Up Month")
		print()
		print()
		self.update(day)
			
	def decrementMonth(self):
		self.currentMonth -= 1
		if self.currentMonth < 1:
			self.currentMonth = 12
			self.currentYear -= 1
		day = datetime.date(self.currentYear, self.currentMonth, 1)
		print()
		print("Down Month")
		print()
		print()
		self.update(day)
		

class ScreenMainMenu(Screen):
	pass
	
class ScreenDatabase(Screen):
	spreadsheetLink = ObjectProperty()

class ScreenCalendar(Screen):
	spreadsheetLink = ObjectProperty()
	today = datetime.date.today()
	calendar = Calendar(today)
		

screenManager = ScreenManager()

screenManager.add_widget(ScreenMainMenu(name="screen_mainmenu"))
screenManager.add_widget(ScreenDatabase(name="screen_database"))
screenManager.add_widget(ScreenCalendar(name="screen_calendar"))

	
class WavesInMotion(App):
	
	def build(self):
		return screenManager



def main():
	WIMApp = WavesInMotion()
	WIMApp.run()
	
	

if __name__ == '__main__':
	main()
