#Written by: Jacob S Liebenow
#Version: 0.0.4
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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.button import Button

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
#: import MapSouce mapview.MapSource

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
			DatabaseManagementDatabaseLinkView:
				size_hint_y: 0.3
				size_hint_x: 0.8
				pos_hint: {"center_x": 0.5, "bottom": 0}
		

		
<ScreenCalendar>
	orientation: "vertical"
	padding: 20
	spacing: 40
	RelativeLayout:
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
			CalendarDatabaseLinkView:
				size_hint_y: 0.3
				size_hint_x: 0.8
				pos_hint: {"center_x": 0.5, "bottom": 0}
		RelativeLayout:	
			size_hint_y: 0.8
			pos_hint: {"center_x": 0.5, "bottom": 0}
			CalendarViewer:
				size_hint_x: 0.3
				pos_hint: {"left": 0, "top": 1}	
			MapView:	
				size_hint_x: 0.7
				size_hint_y: 1
				pos_hint: {"right": 1, "bottom": 0}
				id: mapview
				lat: 50.6394
				lon: 3.057
				zoom: 8
	
""")

#Create the base calendar class for use as a widget in the Calendar screen (Model)
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
		self.currentYear = self.day.year
		self.currentMonth = self.day.month
		
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
		
		#Reset the row incrementer so the decrement and increment month functions can reuse variable
		self.rowIncrementerIndex = 0
		
		#Create flat calendar data
		self.calendarObjFlat = []
		for row in self.calendarObj:
			for day in row:
				self.calendarObjFlat.append(day)
				
	
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
			
		
		#Reset the row incrementer so the decrement and increment month functions can reuse variable
		self.rowIncrementerIndex = 0
		
		#Update flat calendar data
		self.calendarObjFlat = []
		for row in self.calendarObj:
			for day in row:
				self.calendarObjFlat.append(day)
	
	
	
	#Self-explanatory functions to increment/decrement the month when a button is pressed
	def incrementMonth(self):
		self.currentMonth += 1
		if self.currentMonth > 12:
			self.currentMonth = 1
			self.currentYear += 1
		day = datetime.date(self.currentYear, self.currentMonth, 1)
		self.update(day)
			
	def decrementMonth(self):
		self.currentMonth -= 1
		if self.currentMonth < 1:
			self.currentMonth = 12
			self.currentYear -= 1
		day = datetime.date(self.currentYear, self.currentMonth, 1)
		self.update(day)
		
	#Returns the Calendar Month as a string (1 = January, 2 = February, etc.)
	def currentMonthString(self):
		if self.currentMonth == 1:
			return "January"
		elif self.currentMonth == 2:
			return "February"
		elif self.currentMonth == 3:
			return "March"
		elif self.currentMonth == 4:
			return "April"
		elif self.currentMonth == 5:
			return "May"
		elif self.currentMonth == 6:
			return "June"
		elif self.currentMonth == 7:
			return "July"
		elif self.currentMonth == 8:
			return "August"
		elif self.currentMonth == 9:
			return "September"
		elif self.currentMonth == 10:
			return "October"
		elif self.currentMonth == 11:
			return "November"
		elif self.currentMonth == 12:
			return "December"
		else:
			return "MONTH NOT FOUND"

#Multiple classes will share the same data-centric object information, thus they're instantiated here
today = datetime.date.today()
calendar = Calendar(today)
datacenter = datacenter.Datacenter("DummyLink")
		
#Provide an overall view for the Calendar for managing data provided from the Calendar object (View)
class CalendarViewer(RelativeLayout):
	#Define the general layout of the internal widgets of the Calendar
	monthViewer = RelativeLayout(size_hint_y = 0.15, pos_hint = {"center_x":0.5, "top":1})
	dateViewer = GridLayout(cols = 7, size_hint_y = 0.35, pos_hint = {"center_x":0.5, "top":0.85})
	dateInfoViewer = RelativeLayout (size_hint_y = 0.5, pos_hint = {"center_x":0.5, "bottom":0})
	dateSelected = datetime.date.today()
	
	def __init__(self, **kwargs):
		self.size_hint_y = 1
		self.size_hint_x = 0.3
		self.pos_hint = {"left": 0, "top": 1}
		super(CalendarViewer, self).__init__(**kwargs)
		
		#Add the month viewer to the layout
		self.add_widget(self.monthViewer)
		self.monthViewer.backButton = Button(text = "<", pos_hint = {"left":0,"center_y":0.5}, size_hint_x = 0.25, size_hint_y = 0.5)
		self.monthViewer.backButton.bind(on_press = self.decrementMonth)
		self.monthViewer.add_widget(self.monthViewer.backButton)
		self.monthViewer.monthSelected = Label(text = (calendar.currentMonthString()+", "+str(calendar.currentYear)))
		self.monthViewer.add_widget(self.monthViewer.monthSelected)
		self.monthViewer.forwardButton = Button(text = ">", pos_hint = {"right":1,"center_y":0.5}, size_hint_x = 0.25, size_hint_y = 0.5)
		self.monthViewer.forwardButton.bind(on_press = self.incrementMonth)
		self.monthViewer.add_widget(self.monthViewer.forwardButton)
		
		#Add the date viewer to the layout
		self.add_widget(self.dateViewer)
		self.dateViewer.monLabel = Label(text = "Mo")
		self.dateViewer.add_widget(self.dateViewer.monLabel)
		self.dateViewer.tueLabel = Label(text = "Tu")
		self.dateViewer.add_widget(self.dateViewer.tueLabel)
		self.dateViewer.wedLabel = Label(text = "We")
		self.dateViewer.add_widget(self.dateViewer.wedLabel)
		self.dateViewer.thursLabel = Label(text = "Th")
		self.dateViewer.add_widget(self.dateViewer.thursLabel)
		self.dateViewer.friLabel = Label(text = "Fr")
		self.dateViewer.add_widget(self.dateViewer.friLabel)
		self.dateViewer.satLabel = Label(text = "Sa")
		self.dateViewer.add_widget(self.dateViewer.satLabel)
		self.dateViewer.sunLabel = Label(text = "Su")
		self.dateViewer.add_widget(self.dateViewer.sunLabel)
		for day in calendar.calendarObjFlat:
			if day.month < calendar.currentMonth:
				if day.year <= calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.1,0.1,0.1,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year > calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			elif day.month > calendar.currentMonth:
				if day.year >= calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year < calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.1,0.1,0.1,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			else:
				self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0,0.4,0.3,1])
				self.dateViewer.newButton.bind(on_press = self.dateSelector)
				self.dateViewer.add_widget(self.dateViewer.newButton)
				
		#Add the day info viewer to the layout
		self.add_widget(self.dateInfoViewer)
		self.dateInfoViewer.placeholderLabel = Label(text = "DayInfo", pos_hint = {"center_x":0.5,"bottom":0})
		self.dateInfoViewer.add_widget(self.dateInfoViewer.placeholderLabel)
				
	#Remake the dates based off the new month selection
	def updateMonth(self):
		self.monthViewer.monthSelected.text = (calendar.currentMonthString()+", "+str(calendar.currentYear))
		self.dateViewer.clear_widgets()
		self.dateViewer.monLabel = Label(text = "Mo")
		self.dateViewer.add_widget(self.dateViewer.monLabel)
		self.dateViewer.tueLabel = Label(text = "Tu")
		self.dateViewer.add_widget(self.dateViewer.tueLabel)
		self.dateViewer.wedLabel = Label(text = "We")
		self.dateViewer.add_widget(self.dateViewer.wedLabel)
		self.dateViewer.thursLabel = Label(text = "Th")
		self.dateViewer.add_widget(self.dateViewer.thursLabel)
		self.dateViewer.friLabel = Label(text = "Fr")
		self.dateViewer.add_widget(self.dateViewer.friLabel)
		self.dateViewer.satLabel = Label(text = "Sa")
		self.dateViewer.add_widget(self.dateViewer.satLabel)
		self.dateViewer.sunLabel = Label(text = "Su")
		self.dateViewer.add_widget(self.dateViewer.sunLabel)
		for day in calendar.calendarObjFlat:
			if day.month < calendar.currentMonth:
				if day.year <= calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.1,0.1,0.1,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year > calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			elif day.month > calendar.currentMonth:
				if day.year >= calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year < calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.1,0.1,0.1,1])
					self.dateViewer.newButton.bind(on_press = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			else:
				self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0,0.4,0.3,1])
				self.dateViewer.newButton.bind(on_press = self.dateSelector)
				self.dateViewer.add_widget(self.dateViewer.newButton)
		
	def incrementMonth(self,instance):
		calendar.incrementMonth()
		self.updateMonth()
	
	def decrementMonth(self,instance):
		calendar.decrementMonth()
		self.updateMonth()
	
	#Obtain the date from the date button pressed
	def dateSelector(self,instance):
		monthSelected = calendar.currentMonth
		yearSelected = calendar.currentYear
		if instance.background_color == [0,0.4,0.3,1]:
			self.dateInfoViewer.placeholderLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
			self.dateSelected = datetime.date(yearSelected, monthSelected, int(instance.text))
		elif instance.background_color == [0.1,0.1,0.1,1]:
			monthSelected -= 1
			if monthSelected < 1:
				monthSelected = 12
				yearSelected -= 1
			self.dateInfoViewer.placeholderLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
			self.dateSelected = datetime.date(yearSelected, monthSelected, int(instance.text))
		elif instance.background_color == [0.2,0.2,0.2,1]:
			monthSelected += 1
			if monthSelected > 12:
				monthSelected = 1
				yearSelected += 1
			self.dateInfoViewer.placeholderLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
			self.dateSelected = datetime.date(yearSelected, monthSelected, int(instance.text))

#Handle the Google Sheets database link management (two made - one for the database management page, one for the calendar page)
class DatabaseManagementDatabaseLinkView(BoxLayout):
	generalLayout = BoxLayout()
	
	def __init__(self, **kwargs):
		super(DatabaseManagementDatabaseLinkView, self).__init__(**kwargs)
		self.add_widget(self.generalLayout)
		self.generalLayout.databaseLabel = Label(text = "Database:  ", size_hint_x = 0.1)
		self.generalLayout.add_widget(self.generalLayout.databaseLabel)
		self.generalLayout.databaseText = TextInput(size_hint_x = 0.7, multiline = False)
		self.generalLayout.databaseText.bind(on_text_validate = self.linkDatabase)
		self.generalLayout.add_widget(self.generalLayout.databaseText)
		self.generalLayout.databaseSubmit = Button(text = "Submit", size_hint_x = 0.2)
		self.generalLayout.databaseSubmit.bind(on_press = self.linkDatabase)
		self.generalLayout.add_widget(self.generalLayout.databaseSubmit)
	
	def linkDatabase(self, instance): 
		datacenter.link = self.generalLayout.databaseText.text
		print(datacenter.link)
		self.generalLayout.databaseText.text = ""
		
class CalendarDatabaseLinkView(BoxLayout):
	generalLayout = BoxLayout()
	
	def __init__(self, **kwargs):
		super(CalendarDatabaseLinkView, self).__init__(**kwargs)
		self.add_widget(self.generalLayout)
		self.generalLayout.databaseLabel = Label(text = "Database:  ", size_hint_x = 0.1)
		self.generalLayout.add_widget(self.generalLayout.databaseLabel)
		self.generalLayout.databaseText = TextInput(size_hint_x = 0.7, multiline = False)
		self.generalLayout.databaseText.bind(on_text_validate = self.linkDatabase)
		self.generalLayout.add_widget(self.generalLayout.databaseText)
		self.generalLayout.databaseSubmit = Button(text = "Submit", size_hint_x = 0.2)
		self.generalLayout.databaseSubmit.bind(on_press = self.linkDatabase)
		self.generalLayout.add_widget(self.generalLayout.databaseSubmit)
	
	def linkDatabase(self, instance): 
		datacenter.link = self.generalLayout.databaseText.text
		print(datacenter.link)
		self.generalLayout.databaseText.text = ""
	
	
	
#General view classes of the GUI
class ScreenMainMenu(Screen):
	pass
	
class ScreenDatabase(Screen):
	spreadsheetLink = ObjectProperty()

#(Controller for Calendar)
class ScreenCalendar(Screen):
	spreadsheetLink = ObjectProperty()

	
	
screenManager = ScreenManager()

screenManager.add_widget(ScreenMainMenu(name = "screen_mainmenu"))
screenManager.add_widget(ScreenDatabase(name = "screen_database"))
screenManager.add_widget(ScreenCalendar(name = "screen_calendar"))

	
class WavesInMotion(App):
	
	def build(self):
		return screenManager



def main():
	WIMApp = WavesInMotion()
	WIMApp.run()
	
	

if __name__ == '__main__':
	main()
