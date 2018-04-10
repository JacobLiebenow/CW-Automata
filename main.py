#Written by: Jacob S Liebenow
#Version: 0.0.6
#Stage: InFDev/Pre-alpha
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
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.config import Config

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
from datacls import organization

Config.set("input", "mouse", "mouse,multitouch_on_demand")

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
			DatabaseManagementDatabaseLinkView:
				size_hint_y: 0.3
				size_hint_x: 0.8
				pos_hint: {"center_x": 0.5, "bottom": 0}
		DatabaseViewer:
			size_hint_x: 1
			size_hint_y: 0.8
		

		
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
credentials = None


		
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
			
			

#Provide an overall view for the Database Manager screen
class DatabaseViewer(RelativeLayout):
	stateCitySorterLayout = RelativeLayout(size_hint = (0.3,0.12), pos_hint = {"center_x": 0.5, "top": 0.985})
	venueSelectorLayout = RelativeLayout(size_hint = (0.4, 0.12), pos_hint = {"center_x": 0.25, "top": 0.85})
	venueAlterationLayout = RelativeLayout(size_hint = (0.125, 1), pos_hint = {"right": 1, "center_y": 0.5})
	contactSelectorLayout = RelativeLayout(size_hint = (0.4, 0.12), pos_hint = {"center_x": 0.75, "top": 0.85})
	contactTypeLayout = RelativeLayout(size_hint = (0.4, 1), pos_hint = {"left": 0, "center_y": 0.5})
	contactAlterationLayout = RelativeLayout(size_hint = (0.125, 1), pos_hint = {"right": 1, "center_y": 0.5})
	infoBoxLayout = RelativeLayout(size_hint = (0.9,0.6), pos_hint = {"center_x": 0.5, "bottom": 0.02})
	locationInfoLayout = RelativeLayout(size_hint = (0.5, 1), pos_hint = {"left": 0, "center_y": 0.5})
	contactInfoLayout = RelativeLayout(size_hint = (0.5, 1), pos_hint = {"right": 1, "center_y": 0.5})
	
	def __init__(self, **kwargs):
		self.pos_hint = {"center_x": 0.5, "bottom": 0}
		self.selectedState = None
		self.selectedCity = None
		self.selectedVenue = None
		self.statePicked = False
		self.cityPicked = False
		self.venuePicked = False
		super(DatabaseViewer, self).__init__(**kwargs)
		
		#Add embedded layout design
		self.add_widget(self.stateCitySorterLayout)
		self.add_widget(self.venueSelectorLayout)
		self.add_widget(self.contactSelectorLayout)
		self.add_widget(self.infoBoxLayout)
		
		#Add venue selection layouts
		self.venueSelectorLayout.add_widget(self.venueAlterationLayout)
		
		#Add contact selection layouts
		self.contactSelectorLayout.add_widget(self.contactTypeLayout)
		self.contactSelectorLayout.add_widget(self.contactAlterationLayout)
		
		#Add info box layouts
		self.infoBoxLayout.add_widget(self.locationInfoLayout)
		self.infoBoxLayout.add_widget(self.contactInfoLayout)
		
		#Manage widgets within the state and city selector - ON PRESS FOR STATE, REFRESH DATA WITHIN DATABASE IF LINK VALIDATED
		self.stateSpinner = Spinner(text = "State", size_hint_x = 0.5, pos_hint = {"left": 0, "center_y": 0.5}, on_press = self.stateSelection)
		self.citySpinner = Spinner(text = "City", size_hint_x = 0.5, pos_hint = {"right": 1, "center_y": 0.5}, on_press = self.citySelection)
		self.stateCitySorterLayout.add_widget(self.stateSpinner)
		self.stateCitySorterLayout.add_widget(self.citySpinner)
		
		#Manage widgets within the venue selector layout
		self.venueSpinner = Spinner(text = "Venue", size_hint_x = 0.875, pos_hint = {"left": 0, "center_y": 0.5}, on_press = self.venueSelection)
		self.venueSelectorLayout.add_widget(self.venueSpinner)
		
		#Manage widgets within the venue selector's venue alteration layout
		self.newVenueButton = Button(text = "New", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "top": 1})
		self.newVenueButton.bind(on_press = self.newVenue)
		self.editVenueButton = Button(text = "Edit", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "center_y": 0.5})
		self.editVenueButton.bind(on_press = self.editVenue)
		self.removeVenueButton = Button(text = "Rem", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "bottom": 0})
		self.removeVenueButton.bind(on_press = self.removeVenue)
		self.venueAlterationLayout.add_widget(self.newVenueButton)
		self.venueAlterationLayout.add_widget(self.editVenueButton)
		self.venueAlterationLayout.add_widget(self.removeVenueButton)
		
		#Manage widgets within the contact selector layout
		self.contactSelectorSpinner = Spinner(text = "Contact", size_hint_x = 0.5, pos_hint = {"center_x": 0.625, "center_y": 0.5}, on_press = self.contactSelection)
		self.contactSelectorLayout.add_widget(self.contactSelectorSpinner)
		
		#Manage widgets within the contact selector's contact type layout
		self.contactTypeLayout.add_widget(Label(text = "Individual", size_hint = (0.5, 0.5), pos_hint = {"left": 0.4, "top": 1}))
		self.contactTypeLayout.add_widget(Label(text = "Organization", size_hint = (0.5, 0.5), pos_hint = {"left": 0.4, "bottom": 0}))
		self.individualRadio = CheckBox(size_hint = (0.25, 0.5), pos_hint = {"right": 0.9, "top": 1})	
		self.organizationRadio = CheckBox(size_hint = (0.25, 0.5), pos_hint = {"right": 0.9, "bottom": 0})	
		self.individualRadio.text = "Individual"
		self.individualRadio.active = True
		self.individualRadio.group = "ContactSelection"
		self.organizationRadio.text = "Organization"
		self.organizationRadio.active = False
		self.organizationRadio.group = "ContactSelection"
		self.contactTypeLayout.add_widget(self.individualRadio)
		self.contactTypeLayout.add_widget(self.organizationRadio)
		
		
		#Manage widgets within the contact selector's contact alteration layout
		self.newContactButton = Button(text = "New", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "top": 1})
		self.newContactButton.bind(on_press = self.newContact)
		self.editContactButton = Button(text = "Edit", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "center_y": 0.5})
		self.editContactButton.bind(on_press = self.editContact)
		self.removeContactButton = Button(text = "Rem", size_hint_y = 0.33, pos_hint = {"center_x": 0.5, "bottom": 0})
		self.removeContactButton.bind(on_press = self.removeContact)
		self.contactAlterationLayout.add_widget(self.newContactButton)
		self.contactAlterationLayout.add_widget(self.editContactButton)
		self.contactAlterationLayout.add_widget(self.removeContactButton)
		
		#Manage widgets within the info box's location info layout
		self.locationInfoLayout.add_widget(Button(text = "Location Information", pos_hint = {"center_x": 0.5, "center_y": 0.5}))
		
		#Manage widgets within the info box's contact info layout
		self.contactInfoLayout.add_widget(Button(text = "Contact Information", pos_hint = {"center_x": 0.5, "center_y": 0.5}))
	
	
	#Provide functionality for button alterations - bring up popups for new data and for editing data, provide an alert to make sure user wants to remove data
	def newVenue(self, instance):
		#Create the new overall layout of the popup to be inserted in as content
		newVenuePopupLayout = RelativeLayout()
		
		#Create new lines for input...
		#...State and city...
		stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
		stateLabel = Label(text = "State:", size_hint_x = 0.1)
		self.stateInput = TextInput(size_hint_x = 0.4)
		cityLabel = Label(text = "City:", size_hint_x = 0.1)
		self.cityInput = TextInput(size_hint_x = 0.4)
		stateCityLayout.add_widget(stateLabel)
		stateCityLayout.add_widget(self.stateInput)
		stateCityLayout.add_widget(cityLabel)
		stateCityLayout.add_widget(self.cityInput)
		newVenuePopupLayout.add_widget(stateCityLayout)
		
		#...Name...
		nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
		nameLabel = Label(text = "Name:", size_hint_x = 0.1)
		self.nameInput = TextInput(size_hint_x = 0.9)
		nameLayout.add_widget(nameLabel)
		nameLayout.add_widget(self.nameInput)
		newVenuePopupLayout.add_widget(nameLayout)
		
		#...Address...
		addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
		addressLabel = Label(text = "Address:", size_hint_x = 0.1)
		self.addressInput = TextInput(size_hint_x = 0.6)
		zipLabel = Label(text = "Zip Code:", size_hint_x = 0.1)
		self.zipInput = TextInput(size_hint_x = 0.2)
		addressLayout.add_widget(addressLabel)
		addressLayout.add_widget(self.addressInput)
		addressLayout.add_widget(zipLabel)
		addressLayout.add_widget(self.zipInput)
		newVenuePopupLayout.add_widget(addressLayout)
		
		#...Phone #...
		phoneLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.7})
		phoneLabel = Label(text = "Phone #:", size_hint_x = 0.1)
		self.phoneInput = TextInput(size_hint_x = 0.9)
		phoneLayout.add_widget(phoneLabel)
		phoneLayout.add_widget(self.phoneInput)
		newVenuePopupLayout.add_widget(phoneLayout)
		
		#...Links...
		linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
		linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
		self.linksInput = TextInput(size_hint_x = 0.6)
		linksLayout.add_widget(linksLabel)
		linksLayout.add_widget(self.linksInput)
		newVenuePopupLayout.add_widget(linksLayout)
		
		#...Contacts...
		contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
		contactLabel = Label(text = "Contacts (separate with commas):", size_hint_x = 0.4)
		self.contactInput = TextInput(size_hint_x = 0.6)
		contactLayout.add_widget(contactLabel)
		contactLayout.add_widget(self.contactInput)
		newVenuePopupLayout.add_widget(contactLayout)
		
		#...Email...
		emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
		emailLabel = Label(text = "Email:", size_hint_x = 0.1)
		self.emailInput = TextInput(size_hint_x = 0.9)
		emailLayout.add_widget(emailLabel)
		emailLayout.add_widget(self.emailInput)
		newVenuePopupLayout.add_widget(emailLayout)
		
		#...notes on the contact itself...
		notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
		notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
		self.notesInput = TextInput(size_hint_x = 0.9, multiline = True)
		notesLayout.add_widget(notesLabel)
		notesLayout.add_widget(self.notesInput)
		newVenuePopupLayout.add_widget(notesLayout)
		
		#...and finally buttons to submit to sheets or cancel.
		buttonLayout = BoxLayout(size_hint = (0.3, 0.09), pos_hint = {"right": 1, "bottom": 0})
		submitButton = Button(text = "Submit", size_hint_x = 0.5)
		cancelButton = Button(text = "Close", size_hint_x = 0.5)
		buttonLayout.add_widget(submitButton)
		buttonLayout.add_widget(cancelButton)
		newVenuePopupLayout.add_widget(buttonLayout)
		
		self.newVenuePopup = Popup(title = "New Venue", content = newVenuePopupLayout, size_hint = (0.85, 0.8))
		self.newVenuePopup.open()
		submitButton.bind(on_press = self.submitVenueData)
		cancelButton.bind(on_press = self.newVenuePopup.dismiss)
	
	def editVenue(self, instance):
		if datacenter.linkValid is True:
			if self.stateSpinner.text in datacenter.stateNames:
				self.selectedState = datacenter.selectState(self.stateSpinner.text)
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.venueSpinner.text in self.selectedCity.venueNames:
						self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
						rowNum = datacenter.obtainVenueRowNumber(self.stateSpinner.text, self.citySpinner.text, self.venueSpinner.text)
						range = ("Venues!A"+str(rowNum)+":J"+str(rowNum))
						print(range)
	
	def removeVenue(self, instance):
		if datacenter.linkValid is True:
			if self.stateSpinner.text in datacenter.stateNames:
				self.selectedState = datacenter.selectState(self.stateSpinner.text)
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.venueSpinner.text in self.selectedCity.venueNames:
						self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
						rowNum = datacenter.obtainVenueRowNumber(self.stateSpinner.text, self.citySpinner.text, self.venueSpinner.text)
						range = ("Venues!A"+str(rowNum)+":J"+str(rowNum))
						print(range)
						rowNum -= 1
						datacenter.removeVenueRow(rowNum)
						self.stateSpinner.text = "State"
						self.citySpinner.text = "City"
						self.venueSpinner.text = "Venue"
		
	def newContact(self, instance):
		if self.individualRadio.active == True:
			#Create the new overall layout of the popup to be inserted in as content
			newContactPopupLayout = RelativeLayout()
			
			#Create new lines for input...
			#...State and city...
			stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
			stateLabel = Label(text = "State:", size_hint_x = 0.1)
			self.stateInput = TextInput(size_hint_x = 0.4)
			cityLabel = Label(text = "City:", size_hint_x = 0.1)
			self.cityInput = TextInput(size_hint_x = 0.4)
			stateCityLayout.add_widget(stateLabel)
			stateCityLayout.add_widget(self.stateInput)
			stateCityLayout.add_widget(cityLabel)
			stateCityLayout.add_widget(self.cityInput)
			newContactPopupLayout.add_widget(stateCityLayout)
			
			#...Name...
			nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
			nameLabel = Label(text = "Name:", size_hint_x = 0.1)
			self.nameInput = TextInput(size_hint_x = 0.9)
			nameLayout.add_widget(nameLabel)
			nameLayout.add_widget(self.nameInput)
			newContactPopupLayout.add_widget(nameLayout)
			
			#...Address...
			addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
			addressLabel = Label(text = "Address:", size_hint_x = 0.1)
			self.addressInput = TextInput(size_hint_x = 0.6)
			zipLabel = Label(text = "Zip Code:", size_hint_x = 0.1)
			self.zipInput = TextInput(size_hint_x = 0.2)
			addressLayout.add_widget(addressLabel)
			addressLayout.add_widget(self.addressInput)
			addressLayout.add_widget(zipLabel)
			addressLayout.add_widget(self.zipInput)
			newContactPopupLayout.add_widget(addressLayout)
			
			#...Phone #...
			phoneLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.7})
			phoneLabel = Label(text = "Phone #:", size_hint_x = 0.1)
			self.phoneInput = TextInput(size_hint_x = 0.9)
			phoneLayout.add_widget(phoneLabel)
			phoneLayout.add_widget(self.phoneInput)
			newContactPopupLayout.add_widget(phoneLayout)
			
			#...Links...
			linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
			linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
			self.linksInput = TextInput(size_hint_x = 0.6)
			linksLayout.add_widget(linksLabel)
			linksLayout.add_widget(self.linksInput)
			newContactPopupLayout.add_widget(linksLayout)
			
			#...Associations...
			contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
			contactLabel = Label(text = "Associations (separate with commas):", size_hint_x = 0.4)
			self.contactInput = TextInput(size_hint_x = 0.6)
			contactLayout.add_widget(contactLabel)
			contactLayout.add_widget(self.contactInput)
			newContactPopupLayout.add_widget(contactLayout)
			
			#...Email...
			emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
			emailLabel = Label(text = "Email:", size_hint_x = 0.1)
			self.emailInput = TextInput(size_hint_x = 0.9)
			emailLayout.add_widget(emailLabel)
			emailLayout.add_widget(self.emailInput)
			newContactPopupLayout.add_widget(emailLayout)
			
			#...notes on the contact itself...
			notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
			notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
			self.notesInput = TextInput(size_hint_x = 0.9, multiline = True)
			notesLayout.add_widget(notesLabel)
			notesLayout.add_widget(self.notesInput)
			newContactPopupLayout.add_widget(notesLayout)
			
			#...and finally buttons to submit to sheets or cancel.
			buttonLayout = BoxLayout(size_hint = (0.3, 0.09), pos_hint = {"right": 1, "bottom": 0})
			submitButton = Button(text = "Submit", size_hint_x = 0.5)
			cancelButton = Button(text = "Close", size_hint_x = 0.5)
			buttonLayout.add_widget(submitButton)
			buttonLayout.add_widget(cancelButton)
			newContactPopupLayout.add_widget(buttonLayout)
			
			self.newContactPopup = Popup(title = "New Individual", content = newContactPopupLayout, size_hint = (0.85, 0.8))
			self.newContactPopup.open()
			submitButton.bind(on_press = self.submitIndividualData)
			cancelButton.bind(on_press = self.newContactPopup.dismiss)
			
		elif self.organizationRadio.active == True:
			#Create the new overall layout of the popup to be inserted in as content
			newContactPopupLayout = RelativeLayout()
			
			#Create new lines for input...
			#...State and city...
			stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
			stateLabel = Label(text = "State:", size_hint_x = 0.1)
			self.stateInput = TextInput(size_hint_x = 0.4)
			cityLabel = Label(text = "City:", size_hint_x = 0.1)
			self.cityInput = TextInput(size_hint_x = 0.4)
			stateCityLayout.add_widget(stateLabel)
			stateCityLayout.add_widget(self.stateInput)
			stateCityLayout.add_widget(cityLabel)
			stateCityLayout.add_widget(self.cityInput)
			newContactPopupLayout.add_widget(stateCityLayout)
			
			#...Name...
			nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
			nameLabel = Label(text = "Name:", size_hint_x = 0.1)
			self.nameInput = TextInput(size_hint_x = 0.9)
			nameLayout.add_widget(nameLabel)
			nameLayout.add_widget(self.nameInput)
			newContactPopupLayout.add_widget(nameLayout)
			
			#...Address...
			addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
			addressLabel = Label(text = "Address:", size_hint_x = 0.1)
			self.addressInput = TextInput(size_hint_x = 0.6)
			zipLabel = Label(text = "Zip Code:", size_hint_x = 0.1)
			self.zipInput = TextInput(size_hint_x = 0.2)
			addressLayout.add_widget(addressLabel)
			addressLayout.add_widget(self.addressInput)
			addressLayout.add_widget(zipLabel)
			addressLayout.add_widget(self.zipInput)
			newContactPopupLayout.add_widget(addressLayout)
			
			#...Phone #...
			phoneLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.7})
			phoneLabel = Label(text = "Phone #:", size_hint_x = 0.1)
			self.phoneInput = TextInput(size_hint_x = 0.9)
			phoneLayout.add_widget(phoneLabel)
			phoneLayout.add_widget(self.phoneInput)
			newContactPopupLayout.add_widget(phoneLayout)
			
			#...Links...
			linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
			linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
			self.linksInput = TextInput(size_hint_x = 0.6)
			linksLayout.add_widget(linksLabel)
			linksLayout.add_widget(self.linksInput)
			newContactPopupLayout.add_widget(linksLayout)
			
			#...Members...
			contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
			contactLabel = Label(text = "Members (separate by commas):", size_hint_x = 0.4)
			self.contactInput = TextInput(size_hint_x = 0.6)
			contactLayout.add_widget(contactLabel)
			contactLayout.add_widget(self.contactInput)
			newContactPopupLayout.add_widget(contactLayout)
			
			#...Email...
			emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
			emailLabel = Label(text = "Email:", size_hint_x = 0.1)
			self.emailInput = TextInput(size_hint_x = 0.9)
			emailLayout.add_widget(emailLabel)
			emailLayout.add_widget(self.emailInput)
			newContactPopupLayout.add_widget(emailLayout)
			
			#...notes on the contact itself...
			notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
			notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
			self.notesInput = TextInput(size_hint_x = 0.9, multiline = True)
			notesLayout.add_widget(notesLabel)
			notesLayout.add_widget(self.notesInput)
			newContactPopupLayout.add_widget(notesLayout)
			
			#...and finally buttons to submit to sheets or cancel.
			buttonLayout = BoxLayout(size_hint = (0.3, 0.09), pos_hint = {"right": 1, "bottom": 0})
			submitButton = Button(text = "Submit", size_hint_x = 0.5)
			cancelButton = Button(text = "Close", size_hint_x = 0.5)
			buttonLayout.add_widget(submitButton)
			buttonLayout.add_widget(cancelButton)
			newContactPopupLayout.add_widget(buttonLayout)
			
			self.newContactPopup = Popup(title = "New Organization", content = newContactPopupLayout, size_hint = (0.85, 0.8))
			self.newContactPopup.open()
			submitButton.bind(on_press = self.submitOrganizationData)
			cancelButton.bind(on_press = self.newContactPopup.dismiss)
			
		else:
			errorPopup = Popup(title = "Invalid Selection", content = (Label(text = "No contact choice was selected - make sure you choose either an individual or an organization.")), size_hint = (0.85, 0.4))
			errorPopup.open()
	
	def editContact(self, instance):
		if self.individualRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.contactNames:
							self.selectedContact = self.selectedCity.selectContact(self.contactSelectorSpinner.text)
							rowNum = datacenter.obtainIndividualRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							range = ("Individual Contacts!A"+str(rowNum)+":J"+str(rowNum))
							print(range)
		elif self.organizationRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.organizationNames:
							self.selectedContact = self.selectedCity.selectOrganization(self.contactSelectorSpinner.text)
							rowNum = datacenter.obtainOrganizationRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							range = ("Organizational Contacts!A"+str(rowNum)+":J"+str(rowNum))
							print(range)
	
	def removeContact(self, instance):
		if self.individualRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.contactNames:
							self.selectedContact = self.selectedCity.selectContact(self.contactSelectorSpinner.text)
							rowNum = datacenter.obtainIndividualRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							range = ("Individual Contacts!A"+str(rowNum)+":J"+str(rowNum))
							print(range)
		elif self.organizationRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.organizationNames:
							self.selectedContact = self.selectedCity.selectOrganization(self.contactSelectorSpinner.text)
							rowNum = datacenter.obtainOrganizationRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							range = ("Organizational Contacts!A"+str(rowNum)+":J"+str(rowNum))
							print(range)
	
	#Handle cases for submission of data to sheets
	def submitVenueData(self, instance):
		if datacenter.linkValid is True:
			print("New venue submitted.")
			datacenter.submitVenueDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Venue submission was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Successful", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
		else:
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Link to database was not initialized.  Please submit link.", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Failed", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
	
	def submitIndividualData(self, instance):
		if datacenter.linkValid is True:
			print("New individual submitted.")
			datacenter.submitIndividualDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Contact submission was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Successful", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
		else:
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Link to database was not initialized.  Please submit link.", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Failed", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
	
	def submitOrganizationData(self, instance):
		if datacenter.linkValid is True:
			print("New organization submitted.")
			datacenter.submitOrganizationDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Contact submission was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Successful", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
		else:
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Link to database was not initialized.  Please submit link.", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
			popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
			popupContent.add_widget(popupLabel)
			popupContent.add_widget(popupClose)
			popup = Popup(title = "Submission Failed", content = popupContent, size_hint = (0.85, 0.4))
			popup.open()
			popupClose.bind(on_press = popup.dismiss)
			
	#Populate the spinners on click if the link to the database is valid and set up error catching
	def stateSelection(self, instance):
		print(self.stateSpinner.text)
		if datacenter.linkValid is True:
			datacenter.stateNames.sort()
			self.stateSpinner.values = datacenter.stateNames
			self.statePicked = True
	
	def citySelection(self, instance): 
		print(self.citySpinner.text)
		if datacenter.linkValid is True:
			if self.statePicked is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					self.selectedState.cityNames.sort()
					self.citySpinner.values = self.selectedState.cityNames
					self.cityPicked = True
	
	def venueSelection(self, instance):
		print(self.venueSpinner.text)
		if self.cityPicked is True:
			if datacenter.linkValid is True:
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.venueNames) > 0:
						self.selectedCity.venueNames.sort()
						self.venueSpinner.values = self.selectedCity.venueNames
	
	def contactSelection(self, instance):
		print(self.contactSelectorSpinner.text)
		if self.individualRadio.active == True:
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.contactNames) > 0:
							self.selectedCity.contactNames.sort()
							self.contactSelectorSpinner.values = self.selectedCity.contactNames
		elif self.organizationRadio.active == True:
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.organizationNames) > 0:
							self.selectedCity.organizationNames.sort()
							self.contactSelectorSpinner.values = self.selectedCity.organizationNames
		
		
		
		
	
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
		credentials = datacenter.getCredentials()
		
		linkSegments = datacenter.link.split("/")
		
		#Make sure the link provided won't cause an error, and if it will, prevent it from passing through
		if len(linkSegments) >= 6:
			if linkSegments[2] == "docs.google.com" and linkSegments[3] == "spreadsheets":
				datacenter.spreadsheetId = linkSegments[5]
				datacenter.linkValid = True
				popup = Popup(title = "Link Established", content = (Label(text = "Link to Google Sheets successfully established!")), size_hint = (0.85, 0.4))
				popup.open()
			else:
				popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
				popup.open()
		else:
			popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
			popup.open()
			
		datacenter.databaseConnect(credentials)	
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
		credentials = datacenter.getCredentials()
		
		linkSegments = datacenter.link.split("/")
		
		#Make sure the link provided won't cause an error, and if it will, prevent it from passing through
		if len(linkSegments) >= 6:
			if linkSegments[2] == "docs.google.com" and linkSegments[3] == "spreadsheets":
				datacenter.spreadsheetId = linkSegments[5]
				datacenter.linkValid = True
				popup = Popup(title = "Link Established", content = (Label(text = "Link to Google Sheets successfully established!")), size_hint = (0.85, 0.4))
				popup.open()
			else:
				popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
				popup.open()
		else:
			popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
			popup.open()
			
		datacenter.databaseConnect(credentials)	
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
