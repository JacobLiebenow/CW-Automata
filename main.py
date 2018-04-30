#Written by: Jacob S Liebenow
#Version: 0.2.2
#Stage: Alpha
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
from kivy.uix.spinner import SpinnerOption
from kivy.uix.scrollview import ScrollView
from kivy.config import Config

#Import MapView
from mapview import MapView
from mapview import MapMarker

#Import geopy
from geopy.geocoders import Nominatim

#Import Calendar classes
import datetime
import sys
import codecs

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
		CalendarViewer:	
			
	
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
	dateManagerLayout = RelativeLayout(size_hint = (0.3, 1), pos_hint = {"left": 0, "top": 1})
	monthViewer = RelativeLayout(size_hint_y = 0.15, pos_hint = {"center_x":0.5, "top":1})
	dateViewer = GridLayout(cols = 7, size_hint_y = 0.35, pos_hint = {"center_x":0.5, "top":0.85})
	dateInfoViewer = RelativeLayout(size_hint_y = 0.45, pos_hint = {"center_x":0.5, "top":0.5})
	dateInfoButtons = BoxLayout(size_hint_y = 0.05, pos_hint = {"center_x":0.5, "bottom":0})
	mapViewer = RelativeLayout (size_hint = (0.7, 1), pos_hint = {"right": 1, "top": 1})
	geolocator = Nominatim()
	
	
	def __init__(self, **kwargs):
		self.size_hint_y = 0.8
		self.pos_hint = {"center_x": 0.5, "bottom": 0}
		self.selectedState = None
		self.selectedCity = None
		self.selectedVenue = None
		self.selectedContact = None
		self.selectedOrganization = None
		self.selectedDate = None
		self.statePicked = False
		self.cityPicked = False
		self.venuePicked = False
		self.locations = []
		super(CalendarViewer, self).__init__(**kwargs)
		
		#Add the month viewer to the layout
		self.add_widget(self.dateManagerLayout)
		self.dateManagerLayout.add_widget(self.monthViewer)
		self.monthViewer.backButton = Button(text = "<", pos_hint = {"left":0,"center_y":0.5}, size_hint_x = 0.25, size_hint_y = 0.5)
		self.monthViewer.backButton.bind(on_press = self.decrementMonth)
		self.monthViewer.add_widget(self.monthViewer.backButton)
		self.monthViewer.monthSelected = Label(text = (calendar.currentMonthString()+", "+str(calendar.currentYear)))
		self.monthViewer.add_widget(self.monthViewer.monthSelected)
		self.monthViewer.forwardButton = Button(text = ">", pos_hint = {"right":1,"center_y":0.5}, size_hint_x = 0.25, size_hint_y = 0.5)
		self.monthViewer.forwardButton.bind(on_press = self.incrementMonth)
		self.monthViewer.add_widget(self.monthViewer.forwardButton)
		
		#Add the date viewer to the layout
		self.dateManagerLayout.add_widget(self.dateViewer)
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
		self.dateManagerLayout.add_widget(self.dateInfoViewer)
		self.dateNameLabel = Label(text = "Day Info", size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
		self.dateInfoVenueNameLabel = Label(text = "Venues:", size_hint = (0.25, 0.1), pos_hint = {"center_x": 0.5, "top": 0.9})
		self.dateInfoVenueScrollView = ScrollView(size_hint = (1, 0.3), pos_hint = {"center_x": 0.5, "top": 0.8})
		self.dateInfoVenueText = Label(size_hint = (1, None))
		self.dateInfoVenueText.bind(width = lambda *x: self.dateInfoVenueText.setter("text_size")(self.dateInfoVenueText, (self.dateInfoVenueText.width, None)), texture_size = lambda *x: self.dateInfoVenueText.setter("height")(self.dateInfoVenueText, self.dateInfoVenueText.texture_size[1]))
		self.dateInfoVenueScrollView.add_widget(self.dateInfoVenueText)
		self.dateInfoContactNameLabel = Label(text = "Contacts:", size_hint = (0.25, 0.1), pos_hint = {"center_x": 0.5, "top": 0.5})
		self.dateInfoContactScrollView = ScrollView(size_hint = (1, 0.3), pos_hint = {"center_x": 0.5, "top": 0.4})
		self.dateInfoContactText = Label(size_hint = (1, None))
		self.dateInfoContactText.bind(width = lambda *x: self.dateInfoContactText.setter("text_size")(self.dateInfoContactText, (self.dateInfoContactText.width, None)), texture_size = lambda *x: self.dateInfoContactText.setter("height")(self.dateInfoContactText, self.dateInfoContactText.texture_size[1]))
		self.dateInfoContactScrollView.add_widget(self.dateInfoContactText)
		self.dateInfoViewer.add_widget(self.dateNameLabel)
		self.dateInfoViewer.add_widget(self.dateInfoVenueNameLabel)
		self.dateInfoViewer.add_widget(self.dateInfoVenueScrollView)
		self.dateInfoViewer.add_widget(self.dateInfoContactNameLabel)
		self.dateInfoViewer.add_widget(self.dateInfoContactScrollView)
		
		self.dateManagerLayout.add_widget(self.dateInfoButtons)
		self.newDateButton = Button(text = "New/Edit", size_hint_x = 0.33, on_press = self.addOrChangeDate)
		self.remDateButton = Button(text = "Remove", size_hint_x = 0.33, on_press = self.removeDate)
		self.expandDateButton = Button(text = "Expand", size_hint_x = 0.33, on_press = self.expandDate)
		self.dateInfoButtons.add_widget(self.newDateButton)
		self.dateInfoButtons.add_widget(self.remDateButton)
		self.dateInfoButtons.add_widget(self.expandDateButton)
		
		
		#Add the map view to the layout
		self.add_widget(self.mapViewer)
		self.map = MapView(lat = 50.6394, lon = 3.057, zoom = 8)
		self.mapViewer.add_widget(self.map)
				
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
					self.dateViewer.newButton.bind(on_release = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year > calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_release = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			elif day.month > calendar.currentMonth:
				if day.year >= calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.2,0.2,0.2,1])
					self.dateViewer.newButton.bind(on_release = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
				elif day.year < calendar.currentYear:
					self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0.1,0.1,0.1,1])
					self.dateViewer.newButton.bind(on_release = self.dateSelector)
					self.dateViewer.add_widget(self.dateViewer.newButton)
			else:
				self.dateViewer.newButton = Button(text = str(day.day), background_normal = "", background_color = [0,0.4,0.3,1])
				self.dateViewer.newButton.bind(on_release = self.dateSelector)
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
			self.dateNameLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
		elif instance.background_color == [0.1,0.1,0.1,1]:
			monthSelected -= 1
			if monthSelected < 1:
				monthSelected = 12
				yearSelected -= 1
			self.dateNameLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
		elif instance.background_color == [0.2,0.2,0.2,1]:
			monthSelected += 1
			if monthSelected > 12:
				monthSelected = 1
				yearSelected += 1
			self.dateNameLabel.text = (str(monthSelected)+"/"+instance.text+"/"+str(yearSelected))
		
		if datacenter.linkValid is True:
			dateFound = datacenter.dateFinder(self.dateNameLabel.text)
			self.dateInfoVenueText.text = ""
			self.dateInfoContactText.text = ""
			if dateFound is True:
				population = datacenter.populateDate(self.dateNameLabel.text)
				self.selectedDate = datacenter.selectDate(self.dateNameLabel.text)
				self.locations = []
				locationIndex = 0
				for venue in self.selectedDate.venues:
					if venue.address != "N/A" and venue.cityName != "N/A" and venue.stateName != "N/A":
						location = self.geolocator.geocode(venue.address+" "+venue.cityName+" "+venue.stateName)
						if location is not None:
							self.locations.append(location)
						else:
							popupLabel = Label(text = "Address added has an illegal character.\n\n\nLocation not shown on map, but still accessible in expanded view.")
							popup = Popup(title = "Address Not Plotted", content = popupLabel, size_hint = (0.7, 0.45))
							popup.open()
					if self.dateInfoVenueText.text == "":
						self.dateInfoVenueText.text = venue.venueName
					else:
						self.dateInfoVenueText.text += (", "+venue.venueName)
				for contact in self.selectedDate.contacts:
					if self.dateInfoContactText.text == "":
						self.dateInfoContactText.text = contact.name
					else:
						self.dateInfoContactText.text += (", "+contact.name)
				for organization in self.selectedDate.organizations:
					if self.dateInfoContactText.text == "":
						self.dateInfoContactText.text = organization.organizationName
					else:
						self.dateInfoContactText.text += (", "+organization.organizationName)
				
				for location in self.locations:
					if locationIndex == 0:
						self.mapViewer.remove_widget(self.map)
						self.map = MapView(lat = location.latitude, lon = location.longitude, zoom = 10)
						self.mapViewer.add_widget(self.map)
						locationIndex += 1
					marker = MapMarker(lat = location.latitude, lon = location.longitude)
					self.map.add_widget(marker)
		
			
	#Add a date's info if it's not there, or edit it if it is
	def addOrChangeDate(self, instance):
		if self.dateNameLabel.text != "Day Info" and datacenter.linkValid is True:
			dateFound = datacenter.dateFinder(self.dateNameLabel.text)
			
			#Edit the given day
			if dateFound is True:
				population = datacenter.populateDate(self.dateNameLabel.text)
				self.selectedDate = datacenter.selectDate(self.dateNameLabel.text)
				
				#Create a popup with which to edit the day's associated info
				self.popupLayout = RelativeLayout()
				self.stateSpinner = Spinner(text = "State", size_hint = (0.2, 0.1), pos_hint = {"center_x": 0.4, "top": 1}, on_press = self.stateSelection)
				self.citySpinner = Spinner(text = "City", size_hint = (0.2, 0.1), pos_hint = {"center_x": 0.6, "top": 1}, on_press = self.citySelection)
				self.venueSpinner = Spinner(text = "Venue", size_hint = (0.3, 0.1), pos_hint = {"center_x": 0.2, "top": 0.875}, on_press = self.venueSelection)
				self.addVenueButton = Button (text ="Add", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.38125, "top": 0.875}, on_press = self.addVenueToDate)
				self.removeVenueButton = Button (text ="Rem", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.38125, "top": 0.825}, on_press = self.removeVenueFromDate)
				self.contactSpinner = Spinner(text = "Contact", size_hint = (0.25, 0.1), pos_hint = {"center_x": 0.7625, "top": 0.875}, on_press = self.contactSelection)
				self.addContactButton = Button (text = "Add", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.91875, "top": 0.875}, on_press = self.addContactToDate)
				self.removeContactButton = Button (text = "Rem", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.91875, "top": 0.825}, on_press = self.removeContactFromDate)
				self.individualRadio = CheckBox(size_hint = (0.05, 0.05), pos_hint = {"center_x": 0.6125, "top": 0.875})
				self.individualRadio.active = True
				self.individualRadio.group = "ContactSelection"
				self.organizationRadio = CheckBox(size_hint = (0.05, 0.05), pos_hint = {"center_x": 0.6125, "top": 0.825})
				self.organizationRadio.active = False
				self.organizationRadio.group = "ContactSelection"
				self.individualLabel = Label(text = "Individual:", size_hint = (0.2, 0.05), pos_hint = {"center_x": 0.5125, "top": 0.875})
				self.organizationLabel = Label(text = "Organization:", size_hint = (0.2, 0.05), pos_hint = {"center_x": 0.5125, "top": 0.825})
				self.noteLabel = Label(text = "Notes:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.75})
				self.noteInput = TextInput(size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.75}, multiline = True)
				self.noteInput.text = self.selectedDate.notes
				self.currentVenuesLabel = Label(text = "Current Venues:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.525})
				self.currentVenuesScrollView = ScrollView(size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.525})
				self.currentVenuesText = Label(size_hint = (1, None))
				self.currentVenuesText.bind(width = lambda *x: self.currentVenuesText.setter("text_size")(self.currentVenuesText, (self.currentVenuesText.width, None)), texture_size = lambda *x: self.currentVenuesText.setter("height")(self.currentVenuesText, self.currentVenuesText.texture_size[1]))
				self.currentVenuesScrollView.add_widget(self.currentVenuesText)
				self.relevantContactsLabel = Label(text = "Relevant Contacts:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.3})
				self.relevantContactsScrollView = ScrollView(size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.3})
				self.relevantContactsText = Label(size_hint = (1, None))
				self.relevantContactsText.bind(width = lambda *x: self.relevantContactsText.setter("text_size")(self.relevantContactsText, (self.relevantContactsText.width, None)), texture_size = lambda *x: self.relevantContactsText.setter("height")(self.relevantContactsText, self.relevantContactsText.texture_size[1]))
				self.relevantContactsScrollView.add_widget(self.relevantContactsText)
				self.submitDateButton = Button(text = "Submit", size_hint = (0.2, 0.075), pos_hint = {"right": 0.8, "bottom": 0})
				self.closeButton = Button(text = "Close", size_hint = (0.2, 0.075), pos_hint = {"right": 1, "bottom": 0})
				self.popupLayout.add_widget(self.individualLabel)
				self.popupLayout.add_widget(self.organizationLabel)
				self.popupLayout.add_widget(self.noteLabel)
				self.popupLayout.add_widget(self.currentVenuesLabel)
				self.popupLayout.add_widget(self.relevantContactsLabel)
				self.popupLayout.add_widget(self.addVenueButton)
				self.popupLayout.add_widget(self.removeVenueButton)
				self.popupLayout.add_widget(self.addContactButton)
				self.popupLayout.add_widget(self.removeContactButton)
				self.popupLayout.add_widget(self.submitDateButton)
				self.popupLayout.add_widget(self.closeButton)
				self.popupLayout.add_widget(self.noteInput)
				self.popupLayout.add_widget(self.currentVenuesScrollView)
				self.popupLayout.add_widget(self.relevantContactsScrollView)
				self.popupLayout.add_widget(self.individualRadio)
				self.popupLayout.add_widget(self.organizationRadio)
				self.popupLayout.add_widget(self.stateSpinner)
				self.popupLayout.add_widget(self.citySpinner)
				self.popupLayout.add_widget(self.venueSpinner)
				self.popupLayout.add_widget(self.contactSpinner)
				
				#Populate the popup's text boxes so that it contains all relevant data
				for venue in self.selectedDate.venues:
					print(venue.venueName)
					if self.currentVenuesText.text == "":
						self.currentVenuesText.text = venue.venueName
					else:
						self.currentVenuesText.text += (", "+venue.venueName)
				for contact in self.selectedDate.contacts:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = contact.name
					else:
						self.relevantContactsText.text += (", "+contact.name)
				for organization in self.selectedDate.organizations:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = organization.organizationName
					else:
						self.relevantContactsText.text += (", "+organization.organizationName)
					
				self.popup = Popup(title = "Edit Date", content = self.popupLayout, size_hint = (0.8, 0.85))
				self.popup.open()
				self.submitDateButton.bind(on_press = self.submitEditedDateData)
				self.closeButton.bind(on_press = self.popup.dismiss)
				
			#If the day isn't found, add it
			else: 
				#Add a new date to the database
				self.selectedDate = dayinfo.DayInfo(self.dateNameLabel.text)
				
				#Create a popup with which to create the day's associated info
				self.popupLayout = RelativeLayout()
				self.stateSpinner = Spinner(text = "State", size_hint = (0.2, 0.1), pos_hint = {"center_x": 0.4, "top": 1}, on_press = self.stateSelection)
				self.citySpinner = Spinner(text = "City", size_hint = (0.2, 0.1), pos_hint = {"center_x": 0.6, "top": 1}, on_press = self.citySelection)
				self.venueSpinner = Spinner(text = "Venue", size_hint = (0.3, 0.1), pos_hint = {"center_x": 0.2, "top": 0.875}, on_press = self.venueSelection)
				self.addVenueButton = Button (text ="Add", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.38125, "top": 0.875}, on_press = self.addVenueToDate)
				self.removeVenueButton = Button (text ="Rem", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.38125, "top": 0.825}, on_press = self.removeVenueFromDate)
				self.contactSpinner = Spinner(text = "Contact", size_hint = (0.25, 0.1), pos_hint = {"center_x": 0.7625, "top": 0.875}, on_press = self.contactSelection)
				self.addContactButton = Button (text = "Add", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.91875, "top": 0.875}, on_press = self.addContactToDate)
				self.removeContactButton = Button (text = "Rem", size_hint = (0.0625, 0.05), pos_hint = {"center_x": 0.91875, "top": 0.825}, on_press = self.removeContactFromDate)
				self.individualRadio = CheckBox(size_hint = (0.05, 0.05), pos_hint = {"center_x": 0.6125, "top": 0.875})
				self.individualRadio.active = True
				self.individualRadio.group = "ContactSelection"
				self.organizationRadio = CheckBox(size_hint = (0.05, 0.05), pos_hint = {"center_x": 0.6125, "top": 0.825})
				self.organizationRadio.active = False
				self.organizationRadio.group = "ContactSelection"
				self.individualLabel = Label(text = "Individual:", size_hint = (0.2, 0.05), pos_hint = {"center_x": 0.5125, "top": 0.875})
				self.organizationLabel = Label(text = "Organization:", size_hint = (0.2, 0.05), pos_hint = {"center_x": 0.5125, "top": 0.825})
				self.noteLabel = Label(text = "Notes:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.75})
				self.noteInput = TextInput(text = "Insert notes here", size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.75}, multiline = True)
				self.currentVenuesLabel = Label(text = "Current Venues:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.525})
				self.currentVenuesScrollView = ScrollView(size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.525})
				self.currentVenuesText = Label(size_hint = (1, None))
				self.currentVenuesText.bind(width = lambda *x: self.currentVenuesText.setter("text_size")(self.currentVenuesText, (self.currentVenuesText.width, None)), texture_size = lambda *x: self.currentVenuesText.setter("height")(self.currentVenuesText, self.currentVenuesText.texture_size[1]))
				self.currentVenuesScrollView.add_widget(self.currentVenuesText)
				self.relevantContactsLabel = Label(text = "Relevant Contacts:", size_hint = (0.1, 0.05), pos_hint = {"center_x": 0.1, "top": 0.3})
				self.relevantContactsScrollView = ScrollView(size_hint = (0.7, 0.225), pos_hint = {"center_x": 0.6, "top": 0.3})
				self.relevantContactsText = Label(size_hint = (1, None))
				self.relevantContactsText.bind(width = lambda *x: self.relevantContactsText.setter("text_size")(self.relevantContactsText, (self.relevantContactsText.width, None)), texture_size = lambda *x: self.relevantContactsText.setter("height")(self.relevantContactsText, self.relevantContactsText.texture_size[1]))
				self.relevantContactsScrollView.add_widget(self.relevantContactsText)
				self.submitDateButton = Button(text = "Submit", size_hint = (0.2, 0.075), pos_hint = {"right": 0.8, "bottom": 0})
				self.closeButton = Button(text = "Close", size_hint = (0.2, 0.075), pos_hint = {"right": 1, "bottom": 0})
				self.popupLayout.add_widget(self.individualLabel)
				self.popupLayout.add_widget(self.organizationLabel)
				self.popupLayout.add_widget(self.noteLabel)
				self.popupLayout.add_widget(self.currentVenuesLabel)
				self.popupLayout.add_widget(self.relevantContactsLabel)
				self.popupLayout.add_widget(self.addVenueButton)
				self.popupLayout.add_widget(self.removeVenueButton)
				self.popupLayout.add_widget(self.addContactButton)
				self.popupLayout.add_widget(self.removeContactButton)
				self.popupLayout.add_widget(self.submitDateButton)
				self.popupLayout.add_widget(self.closeButton)
				self.popupLayout.add_widget(self.noteInput)
				self.popupLayout.add_widget(self.currentVenuesScrollView)
				self.popupLayout.add_widget(self.relevantContactsScrollView)
				self.popupLayout.add_widget(self.individualRadio)
				self.popupLayout.add_widget(self.organizationRadio)
				self.popupLayout.add_widget(self.stateSpinner)
				self.popupLayout.add_widget(self.citySpinner)
				self.popupLayout.add_widget(self.venueSpinner)
				self.popupLayout.add_widget(self.contactSpinner)
				
				self.popup = Popup(title = "Add Date", content = self.popupLayout, size_hint = (0.8, 0.85))
				self.popup.open()
				self.submitDateButton.bind(on_press = self.submitDateData)
				self.closeButton.bind(on_press = self.popup.dismiss)
				
		else:
			popup = Popup(title = "Date not initialized", size_hint = (0.4, 0.45))
			popup.open()
	
	#Remove the date from Google Sheets altogether
	def removeDate(self, instance):
		if self.dateNameLabel.text != "Day Info" and datacenter.linkValid is True:
			dateFound = datacenter.dateFinder(self.dateNameLabel.text)
			if dateFound is True:
				datacenter.removeDateFromSpreadsheet(self.dateNameLabel.text)
				popup = Popup(title = "Date Removed", size_hint = (0.4, 0.45))
				popup.open()
			else: 
				popup = Popup(title = "Date Not Found", size_hint = (0.4, 0.45))
				popup.open()
		else:
			popup = Popup(title = "Date Not Initialized", size_hint = (0.4, 0.45))
			popup.open()
	
	#Generate a popup to give more detailed date info
	def expandDate(self, instance):
		if self.dateNameLabel.text != "Day Info" and datacenter.linkValid is True:
			dateFound = datacenter.dateFinder(self.dateNameLabel.text)
			if dateFound is True:
				population = datacenter.populateDate(self.dateNameLabel.text)
				self.selectedDate = datacenter.selectDate(self.dateNameLabel.text)
				self.expandedView = RelativeLayout()
				#self.expandedScrollView = ScrollView(size_hint = (1, 0.9), pos_hint = {"center_x": 0.5, "top": 1})
				#self.expandedText = Label(size_hint = (1, None))
				#self.expandedText.bind(width = lambda *x: self.expandedText.setter("text_size")(self.expandedText, (self.expandedText.width, None)), texture_size = lambda *x: self.expandedText.setter("height")(self.expandedText, self.expandedText.texture_size[1]))
				#self.expandedScrollView.add_widget(self.expandedText)
				self.expandedText = TextInput(size_hint = (1, 0.9), pos_hint = {"center_x": 0.5, "top": 1}, multiline = True)
				self.closeButton = Button(text = "Close", size_hint = (0.2, 0.075), pos_hint = {"right": 1, "bottom": 0})
				#self.expandedView.add_widget(self.expandedScrollView)
				self.expandedView.add_widget(self.expandedText)
				self.expandedView.add_widget(self.closeButton)
				
				for venue in self.selectedDate.venues:
					print(venue.venueName)
					if self.expandedText.text == "":
						self.expandedText.text = venue.venueName
						self.expandedText.text += ("\n    "+venue.address+"\n    "+venue.cityName+", "+venue.stateName+" "+venue.zip+"\n    Phone: "+venue.phone+"    Email: "+venue.email+"\n    Links: "+venue.links+"\n    Associated Contacts: "+venue.contacts+"\nNotes:\n"+venue.notes)
					else:
						self.expandedText.text += ("\n\n"+venue.venueName)
						self.expandedText.text += ("\n    "+venue.address+"\n    "+venue.cityName+", "+venue.stateName+" "+venue.zip+"\n    Phone: "+venue.phone+"    Email: "+venue.email+"\n    Links: "+venue.links+"\n    Associated Contacts: "+venue.contacts+"\nNotes:\n"+venue.notes)
				for contact in self.selectedDate.contacts:
					if self.expandedText.text == "":
						self.expandedText.text = contact.name
						self.expandedText.text += ("\n    "+contact.address+"\n    "+contact.cityName+", "+contact.stateName+" "+contact.zip+"\n    Phone: "+contact.phone+"    Email: "+contact.email+"\n    Links: "+contact.links+"\n    Associated Contacts: "+contact.associations+"\nNotes:\n"+contact.notes)
					else:
						self.expandedText.text += ("\n\n"+contact.name)
						self.expandedText.text += ("\n    "+contact.address+"\n    "+contact.cityName+", "+contact.stateName+" "+contact.zip+"\n    Phone: "+contact.phone+"    Email: "+contact.email+"\n    Links: "+contact.links+"\n    Associated Contacts: "+contact.associations+"\nNotes:\n"+contact.notes)
				for organization in self.selectedDate.organizations:
					if self.expandedText.text == "":
						self.expandedText.text = organization.organizationName
						self.expandedText.text += ("\n    "+organization.address+"\n    "+organization.cityName+", "+organization.stateName+" "+organization.zip+"\n    Phone: "+organization.phone+"    Email: "+organization.email+"\n    Links: "+organization.links+"\n    Associated Contacts: "+organization.members+"\nNotes:\n"+organization.notes)
					else:
						self.expandedText.text += ("\n\n"+organization.organizationName)
						self.expandedText.text += ("\n    "+organization.address+"\n    "+organization.cityName+", "+organization.stateName+" "+organization.zip+"\n    Phone: "+organization.phone+"    Email: "+organization.email+"\n    Links: "+organization.links+"\n    Associated Contacts: "+organization.members+"\nNotes:\n"+organization.notes)
				
				self.popup = Popup(title = "Expanded Date", content = self.expandedView, size_hint = (0.8, 0.85))
				self.popup.open()
				self.closeButton.bind(on_press = self.popup.dismiss)
			else: 
				popup = Popup(title = "Date Not Found", size_hint = (0.4, 0.45))
				popup.open()
		else:
			popup = Popup(title = "Date Not Initialized", size_hint = (0.4, 0.45))
			popup.open()
	
	#Add the selected venue or contact on button press
	def addVenueToDate(self, instance):
		if len(self.venueSpinner.values) > 0:
			self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
			self.selectedDate.addVenue(self.selectedVenue)
			self.currentVenuesText.text = ""
			for venue in self.selectedDate.venues:
				if self.currentVenuesText.text == "":
					self.currentVenuesText.text = venue.venueName
				else:
					self.currentVenuesText.text += (", "+venue.venueName)
	
	def addContactToDate(self, instance):
		if self.individualRadio.active == True and len(self.contactSpinner.values) > 0:
			self.selectedContact = self.selectedCity.selectContact(self.contactSpinner.text)
			self.selectedDate.addContact(self.selectedContact)
			self.relevantContactsText.text = ""
			for contact in self.selectedDate.contacts:
				if self.relevantContactsText.text == "":
					print("Accessed this field")
					print(contact.name)
					print("End field")
					self.relevantContactsText.text = contact.name
				else:
					self.relevantContactsText.text += (", "+contact.name)
			for organization in self.selectedDate.organizations:
				if self.relevantContactsText.text == "":
					self.relevantContactsText.text = organization.organizationName
				else:
					self.relevantContactsText.text += (", "+organization.organizationName)
		elif self.organizationRadio.active == True and len(self.contactSpinner.values) > 0:
			self.selectedOrganization = self.selectedCity.selectOrganization(self.contactSpinner.text)
			self.selectedDate.addOrganization(self.selectedOrganization)
			self.relevantContactsText.text = ""
			for contact in self.selectedDate.contacts:
				if self.relevantContactsText.text == "":
					self.relevantContactsText.text = contact.name
				else:
					self.relevantContactsText.text += (", "+contact.name)
			for organization in self.selectedDate.organizations:
				if self.relevantContactsText.text == "":
					self.relevantContactsText.text = organization.organizationName
				else:
					self.relevantContactsText.text += (", "+organization.organizationName)
				
	#Likewise, remove selected venue or contact on button press			
	def removeVenueFromDate(self, instance):
		if len(self.venueSpinner.values) > 0:
			self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
			if self.selectedVenue.venueName in self.selectedDate.venueNames:
				#While the name might be correct and within selectedDate, the selectedContact object is not actually within selectedDate
				#Ergo, this points to the object actually stored within selectedDate
				self.selectedVenue = self.selectedDate.selectVenue(self.selectedVenue.venueName)
				self.selectedDate.removeVenue(self.selectedVenue)
				self.currentVenuesText.text = ""
				for venue in self.selectedDate.venues:
					if self.currentVenuesText.text == "":
						self.currentVenuesText.text = venue.venueName
					else:
						self.currentVenuesText.text += (", "+venue.venueName)
	
	def removeContactFromDate(self, instance):
		if self.individualRadio.active == True and len(self.contactSpinner.values) > 0:
			self.selectedContact = self.selectedCity.selectContact(self.contactSpinner.text)
			if self.selectedContact.name in self.selectedDate.contactNames:
				#While the name might be correct and within selectedDate, the selectedContact object is not actually within selectedDate
				#Ergo, this points to the object actually stored within selectedDate
				self.selectedContact = self.selectedDate.selectContact(self.selectedContact.name)
				print(self.selectedContact.name)
				self.selectedDate.removeContact(self.selectedContact)
				print(self.selectedDate.contactNames)
				self.relevantContactsText.text = ""
				for contact in self.selectedDate.contacts:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = contact.name
					else:
						self.relevantContactsText.text += (", "+contact.name)
				for organization in self.selectedDate.organizations:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = organization.organizationName
					else:
						self.relevantContactsText.text += (", "+organization.organizationName)
		elif self.organizationRadio.active == True and len(self.contactSpinner.values) > 0:
			self.selectedOrganization = self.selectedCity.selectOrganization(self.contactSpinner.text)
			print(self.selectedOrganization.organizationName)
			print(self.selectedDate.organizationNames)
			if self.selectedOrganization.organizationName in self.selectedDate.organizationNames:
				self.selectedOrganization = self.selectedDate.selectOrganization(self.selectedOrganization.organizationName)
				print(self.selectedOrganization.organizationName)
				self.selectedDate.removeOrganization(self.selectedOrganization)
				print(self.selectedDate.organizationNames)
				for contact in self.selectedDate.contacts:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = self.selectedContact.name
					else:
						self.relevantContactsText.text += (", "+self.selectedContact.name)
				for organization in self.selectedDate.organizations:
					if self.relevantContactsText.text == "":
						self.relevantContactsText.text = self.selectedOrganization.organizationName
					else:
						self.relevantContactsText.text += (", "+self.selectedOrganization.organizationName)
			
	def submitDateData(self, instance):
		if self.noteInput.text != "":
			self.selectedDate.notes = self.noteInput.text
		else:
			self.selectedDate.notes = "No notes given."
		datacenter.addDateToSpreadsheet(self.dateNameLabel.text)
		datacenter.submitDate(self.selectedDate)
		
		popupContent = RelativeLayout()
		popupLabel = Label(text = "Date submission was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
		popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
		popupContent.add_widget(popupLabel)
		popupContent.add_widget(popupClose)
		popup = Popup(title = "Submission Successful", content = popupContent, size_hint = (0.85, 0.4))
		popup.open()
		popupClose.bind(on_press = popup.dismiss)
		
	def submitEditedDateData(self, instance):
		if self.noteInput.text != "":
			self.selectedDate.notes = self.noteInput.text
		else:
			self.selectedDate.notes = "No notes given."
		datacenter.submitEditedDate(self.selectedDate)
		
		popupContent = RelativeLayout()
		popupLabel = Label(text = "Date edit was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
		popupClose = Button(text = "Close", size_hint = (0.5, 0.3), pos_hint = {"center_x": 0.5, "bottom": 0.25})
		popupContent.add_widget(popupLabel)
		popupContent.add_widget(popupClose)
		popup = Popup(title = "Edit Successful", content = popupContent, size_hint = (0.85, 0.4))
		popup.open()
		popupClose.bind(on_press = popup.dismiss)
		
	#Populate the spinners on click if the link to the database is valid and set up error catching
	def stateSelection(self, instance):
		self.cityPicked = False
		print(self.stateSpinner.text)
		if datacenter.linkValid is True:
			datacenter.stateNames.sort()
			self.stateSpinner.values = datacenter.stateNames
			self.statePicked = True
			self.citySpinner.values = []
			self.citySpinner.text = "City"
			self.venueSpinner.values = []
			self.venueSpinner.text = "Venue"
			self.contactSpinner.values = []
			self.contactSpinner.text = "Contact"
	
	def citySelection(self, instance): 
		print(self.citySpinner.text)
		if datacenter.linkValid is True:
			if self.statePicked is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					self.selectedState.cityNames.sort()
					self.citySpinner.values = self.selectedState.cityNames
					self.cityPicked = True
					self.venueSpinner.values = []
					self.venueSpinner.text = "Venue"
					self.contactSpinner.values = []
					self.contactSpinner.text = "Contact"
	
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
		self.contactSpinner.values = []
		self.contactSpinner.text = "Contact"
		print(self.contactSpinner.text)
		if self.individualRadio.active == True:
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.contactNames) > 0:
							self.selectedCity.contactNames.sort()
							self.contactSpinner.values = self.selectedCity.contactNames
		elif self.organizationRadio.active == True:
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.organizationNames) > 0:
							self.selectedCity.organizationNames.sort()
							self.contactSpinner.values = self.selectedCity.organizationNames
			
			

#Provide an overall view for the Database Manager screen
class DatabaseViewer(RelativeLayout):
	stateCitySorterLayout = RelativeLayout(size_hint = (0.3,0.12), pos_hint = {"center_x": 0.5, "top": 0.985})
	venueSelectorLayout = RelativeLayout(size_hint = (0.4, 0.12), pos_hint = {"center_x": 0.25, "top": 0.85})
	venueAlterationLayout = RelativeLayout(size_hint = (0.125, 1), pos_hint = {"right": 1, "center_y": 0.5})
	updateVenueLayout = RelativeLayout(size_hint = (0.45, 0.05), pos_hint = {"center_x": 0.275, "top": .7125})
	contactSelectorLayout = RelativeLayout(size_hint = (0.4, 0.12), pos_hint = {"center_x": 0.75, "top": 0.85})
	contactTypeLayout = RelativeLayout(size_hint = (0.4, 1), pos_hint = {"left": 0, "center_y": 0.5})
	contactAlterationLayout = RelativeLayout(size_hint = (0.125, 1), pos_hint = {"right": 1, "center_y": 0.5})
	updateContactLayout = RelativeLayout(size_hint = (0.45, 0.05), pos_hint = {"center_x": 0.725, "top": .7125})
	infoBoxLayout = RelativeLayout(size_hint = (0.9,0.65), pos_hint = {"center_x": 0.5, "bottom": 0.02})
	locationInfoLayout = RelativeLayout(size_hint = (0.5, 1), pos_hint = {"left": 0, "center_y": 0.5})
	contactInfoLayout = RelativeLayout(size_hint = (0.5, 1), pos_hint = {"right": 1, "center_y": 0.5})
	
	def __init__(self, **kwargs):
		self.pos_hint = {"center_x": 0.5, "bottom": 0}
		self.selectedState = None
		self.selectedCity = None
		self.selectedVenue = None
		self.selectedContact = None
		self.selectedOrganization = None
		self.statePicked = False
		self.cityPicked = False
		self.venuePicked = False
		self.rowNum = 0
		self.range = ""
		super(DatabaseViewer, self).__init__(**kwargs)
		
		#Add embedded layout design
		self.add_widget(self.stateCitySorterLayout)
		self.add_widget(self.venueSelectorLayout)
		self.add_widget(self.updateVenueLayout)
		self.add_widget(self.contactSelectorLayout)
		self.add_widget(self.updateContactLayout)
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
		self.stateSpinner = Spinner(text= "State", size_hint_x = 0.5, pos_hint = {"left": 0, "center_y": 0.5}, on_press = self.stateSelection)
		self.citySpinner = Spinner(text = "City", size_hint_x = 0.5, pos_hint = {"right": 1, "center_y": 0.5}, on_press = self.citySelection)
		self.stateCitySorterLayout.add_widget(self.stateSpinner)
		self.stateCitySorterLayout.add_widget(self.citySpinner)
		
		#Manage widgets within the venue selector layout
		self.venueSpinnerOption = SpinnerOption(on_press = self.updateVenueInfoBox)
		self.venueSpinner = Spinner(text = "Venue", size_hint_x = 0.875, pos_hint = {"left": 0, "center_y": 0.5}, on_press = self.venueSelection)
		self.venueSpinner.bind(on_text = self.updateVenueInfoBox)
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
		
		#Manage button to update venue text
		self.updateVenueInfoBoxButton = Button(text = "Update Venue Info Below:", on_press = self.updateVenueInfoBox)
		self.updateVenueLayout.add_widget(self.updateVenueInfoBoxButton)
		
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
		
		#Manage button to update venue text
		self.updateContactInfoBoxButton = Button(text = "Update Contact Info Below:", on_press = self.updateContactInfoBox)
		self.updateContactLayout.add_widget(self.updateContactInfoBoxButton)
		
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
		self.venueNameLabel = Label(text = "Venue:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 1})
		self.venueNameText = Label(size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 1})
		self.stateVenueNameLabel = Label(text = "State:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.94})
		self.stateVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.94})
		self.cityVenueNameLabel = Label(text = "City:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.88})
		self.cityVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.88})
		self.addressVenueNameLabel = Label(text = "Address:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.82})
		self.addressVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.82})
		self.zipVenueNameLabel = Label(text = "Zip:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.76})
		self.zipVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.76})
		self.phoneVenueNameLabel = Label(text = "Phone:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.7})
		self.phoneVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.7})
		self.emailVenueNameLabel = Label(text = "Email:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.64})
		self.emailVenueNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.64})
		self.linksVenueNameLabel = Label(text = "Links:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.58})
		self.linksVenueScrollView = ScrollView(size_hint = (0.8, 0.12), pos_hint = {"right": 1, "top": 0.58})
		self.linksVenueLabel = Label(size_hint = (1, None))
		self.linksVenueLabel.bind(width = lambda *x: self.linksVenueLabel.setter("text_size")(self.linksVenueLabel, (self.linksVenueLabel.width, None)), texture_size = lambda *x: self.linksVenueLabel.setter("height")(self.linksVenueLabel, self.linksVenueLabel.texture_size[1]))
		self.linksVenueScrollView.add_widget(self.linksVenueLabel)
		self.contactsVenueNameLabel = Label(text = "Contacts:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.46})
		self.contactsVenueScrollView = ScrollView(size_hint = (0.8, 0.12), pos_hint = {"right": 1, "top": 0.46})
		self.contactsVenueLabel = Label(size_hint = (1, None))
		self.contactsVenueLabel.bind(width = lambda *x: self.contactsVenueLabel.setter("text_size")(self.contactsVenueLabel, (self.contactsVenueLabel.width, None)), texture_size = lambda *x: self.contactsVenueLabel.setter("height")(self.contactsVenueLabel, self.contactsVenueLabel.texture_size[1]))
		self.contactsVenueScrollView.add_widget(self.contactsVenueLabel)
		self.notesVenueNameLabel = Label(text = "Notes:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.34})
		self.notesVenueScrollView = ScrollView(size_hint = (0.8, 0.24), pos_hint = {"right": 1, "top": 0.34})
		self.notesVenueLabel = Label(size_hint = (1, None))
		self.notesVenueLabel.bind(width = lambda *x: self.notesVenueLabel.setter("text_size")(self.notesVenueLabel, (self.notesVenueLabel.width, None)), texture_size = lambda *x: self.notesVenueLabel.setter("height")(self.notesVenueLabel, self.notesVenueLabel.texture_size[1]))
		self.notesVenueScrollView.add_widget(self.notesVenueLabel)
		
		self.locationInfoLayout.add_widget(self.venueNameLabel)
		self.locationInfoLayout.add_widget(self.venueNameText)
		self.locationInfoLayout.add_widget(self.stateVenueNameLabel)
		self.locationInfoLayout.add_widget(self.stateVenueNameText)
		self.locationInfoLayout.add_widget(self.cityVenueNameLabel)
		self.locationInfoLayout.add_widget(self.cityVenueNameText)
		self.locationInfoLayout.add_widget(self.addressVenueNameLabel)
		self.locationInfoLayout.add_widget(self.addressVenueNameText)
		self.locationInfoLayout.add_widget(self.zipVenueNameLabel)
		self.locationInfoLayout.add_widget(self.zipVenueNameText)
		self.locationInfoLayout.add_widget(self.phoneVenueNameLabel)
		self.locationInfoLayout.add_widget(self.phoneVenueNameText)
		self.locationInfoLayout.add_widget(self.emailVenueNameLabel)
		self.locationInfoLayout.add_widget(self.emailVenueNameText)
		self.locationInfoLayout.add_widget(self.linksVenueNameLabel)
		self.locationInfoLayout.add_widget(self.linksVenueScrollView)
		self.locationInfoLayout.add_widget(self.contactsVenueNameLabel)
		self.locationInfoLayout.add_widget(self.contactsVenueScrollView)
		self.locationInfoLayout.add_widget(self.notesVenueNameLabel)
		self.locationInfoLayout.add_widget(self.notesVenueScrollView)
		
		#Manage widgets within the info box's contact info layout
		self.contactNameLabel = Label(text = "Contact:", size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 1})
		self.contactNameText = Label(size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 1})
		self.stateContactNameLabel = Label(text = "State:",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.94})
		self.stateContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.94})
		self.cityContactNameLabel = Label(text = "City:", size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.88})
		self.cityContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.88})
		self.addressContactNameLabel = Label(text = "Address:", halign = "center", valign = "middle", text_size = self.size,  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.82})
		self.addressContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.82})
		self.zipContactNameLabel = Label(text = "Zip:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.76})
		self.zipContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.76})
		self.phoneContactNameLabel = Label(text = "Phone:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.7})
		self.phoneContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.7})
		self.emailContactNameLabel = Label(text = "Email:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.64})
		self.emailContactNameText = Label(halign = "left", size_hint = (0.8, 0.06),  pos_hint = {"right": 1, "top": 0.64})
		self.linksContactNameLabel = Label(text = "Links:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.58})
		self.linksContactScrollView = ScrollView(size_hint = (0.8, 0.12), pos_hint = {"right": 1, "top": 0.58})
		self.linksContactLabel = Label(size_hint = (1, None))
		self.linksContactLabel.bind(width = lambda *x: self.linksContactLabel.setter("text_size")(self.linksContactLabel, (self.linksContactLabel.width, None)), texture_size = lambda *x: self.linksContactLabel.setter("height")(self.linksContactLabel, self.linksContactLabel.texture_size[1]))
		self.linksContactScrollView.add_widget(self.linksContactLabel)
		self.groupsContactNameLabel = Label(text = "Assoc.:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.46})
		self.groupsContactScrollView = ScrollView(size_hint = (0.8, 0.12), pos_hint = {"right": 1, "top": 0.46})
		self.groupsContactLabel = Label(size_hint = (1, None))
		self.groupsContactLabel.bind(width = lambda *x: self.groupsContactLabel.setter("text_size")(self.groupsContactLabel, (self.groupsContactLabel.width, None)), texture_size = lambda *x: self.groupsContactLabel.setter("height")(self.groupsContactLabel, self.groupsContactLabel.texture_size[1]))
		self.groupsContactScrollView.add_widget(self.groupsContactLabel)
		self.notesContactNameLabel = Label(text = "Notes:", halign = "left",  size_hint = (0.2, 0.06),  pos_hint = {"left": 0, "top": 0.34})
		self.notesContactScrollView = ScrollView(size_hint = (0.8, 0.24), pos_hint = {"right": 1, "top": 0.34})
		self.notesContactLabel = Label(size_hint = (1, None))
		self.notesContactLabel.bind(width = lambda *x: self.notesContactLabel.setter("text_size")(self.notesContactLabel, (self.notesContactLabel.width, None)), texture_size = lambda *x: self.notesContactLabel.setter("height")(self.notesContactLabel, self.notesContactLabel.texture_size[1]))
		self.notesContactScrollView.add_widget(self.notesContactLabel)
		
		self.contactInfoLayout.add_widget(self.contactNameLabel)
		self.contactInfoLayout.add_widget(self.contactNameText)
		self.contactInfoLayout.add_widget(self.stateContactNameLabel)
		self.contactInfoLayout.add_widget(self.stateContactNameText)
		self.contactInfoLayout.add_widget(self.cityContactNameLabel)
		self.contactInfoLayout.add_widget(self.cityContactNameText)
		self.contactInfoLayout.add_widget(self.addressContactNameLabel)
		self.contactInfoLayout.add_widget(self.addressContactNameText)
		self.contactInfoLayout.add_widget(self.zipContactNameLabel)
		self.contactInfoLayout.add_widget(self.zipContactNameText)
		self.contactInfoLayout.add_widget(self.phoneContactNameLabel)
		self.contactInfoLayout.add_widget(self.phoneContactNameText)
		self.contactInfoLayout.add_widget(self.emailContactNameLabel)
		self.contactInfoLayout.add_widget(self.emailContactNameText)
		self.contactInfoLayout.add_widget(self.linksContactNameLabel)
		self.contactInfoLayout.add_widget(self.linksContactScrollView)
		self.contactInfoLayout.add_widget(self.groupsContactNameLabel)
		self.contactInfoLayout.add_widget(self.groupsContactScrollView)
		self.contactInfoLayout.add_widget(self.notesContactNameLabel)
		self.contactInfoLayout.add_widget(self.notesContactScrollView)
	
	
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
						self.rowNum = datacenter.obtainVenueRowNumber(self.stateSpinner.text, self.citySpinner.text, self.venueSpinner.text)
						self.range = ("Venues!A"+str(self.rowNum)+":J"+str(self.rowNum))
						print(self.range)
						#Create the new overall layout of the popup to be inserted in as content
						newVenuePopupLayout = RelativeLayout()
						
						#Create new lines for input...
						#...State and city...
						stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
						stateLabel = Label(text = "State:", size_hint_x = 0.1)
						self.stateInput = TextInput(text = self.selectedState.stateName, size_hint_x = 0.4)
						cityLabel = Label(text = "City:", size_hint_x = 0.1)
						self.cityInput = TextInput(text = self.selectedCity.cityName, size_hint_x = 0.4)
						stateCityLayout.add_widget(stateLabel)
						stateCityLayout.add_widget(self.stateInput)
						stateCityLayout.add_widget(cityLabel)
						stateCityLayout.add_widget(self.cityInput)
						newVenuePopupLayout.add_widget(stateCityLayout)
						
						#...Name...
						nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
						nameLabel = Label(text = "Name:", size_hint_x = 0.1)
						self.nameInput = TextInput(text = self.selectedVenue.venueName, size_hint_x = 0.9)
						nameLayout.add_widget(nameLabel)
						nameLayout.add_widget(self.nameInput)
						newVenuePopupLayout.add_widget(nameLayout)
						
						#...Address...
						addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
						addressLabel = Label(text = "Address:", size_hint_x = 0.1)
						self.addressInput = TextInput(text = self.selectedVenue.address, size_hint_x = 0.6)
						zipLabel = Label(text = "Zip Code:", size_hint_x = 0.1)
						self.zipInput = TextInput(text = self.selectedVenue.zip, size_hint_x = 0.2)
						addressLayout.add_widget(addressLabel)
						addressLayout.add_widget(self.addressInput)
						addressLayout.add_widget(zipLabel)
						addressLayout.add_widget(self.zipInput)
						newVenuePopupLayout.add_widget(addressLayout)
						
						#...Phone #...
						phoneLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.7})
						phoneLabel = Label(text = "Phone #:", size_hint_x = 0.1)
						self.phoneInput = TextInput(text = self.selectedVenue.phone, size_hint_x = 0.9)
						phoneLayout.add_widget(phoneLabel)
						phoneLayout.add_widget(self.phoneInput)
						newVenuePopupLayout.add_widget(phoneLayout)
						
						#...Links...
						linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
						linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
						self.linksInput = TextInput(text = self.selectedVenue.links, size_hint_x = 0.6)
						linksLayout.add_widget(linksLabel)
						linksLayout.add_widget(self.linksInput)
						newVenuePopupLayout.add_widget(linksLayout)
						
						#...Contacts...
						contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
						contactLabel = Label(text = "Contacts (separate with commas):", size_hint_x = 0.4)
						self.contactInput = TextInput(text = self.selectedVenue.contacts, size_hint_x = 0.6)
						contactLayout.add_widget(contactLabel)
						contactLayout.add_widget(self.contactInput)
						newVenuePopupLayout.add_widget(contactLayout)
						
						#...Email...
						emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
						emailLabel = Label(text = "Email:", size_hint_x = 0.1)
						self.emailInput = TextInput(text = self.selectedVenue.email, size_hint_x = 0.9)
						emailLayout.add_widget(emailLabel)
						emailLayout.add_widget(self.emailInput)
						newVenuePopupLayout.add_widget(emailLayout)
						
						#...notes on the contact itself...
						notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
						notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
						self.notesInput = TextInput(text = self.selectedVenue.notes, size_hint_x = 0.9, multiline = True)
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
						submitButton.bind(on_press = self.submitEditedVenueData)
						cancelButton.bind(on_press = self.newVenuePopup.dismiss)
	
	def removeVenue(self, instance):
		if datacenter.linkValid is True:
			if self.stateSpinner.text in datacenter.stateNames:
				self.selectedState = datacenter.selectState(self.stateSpinner.text)
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.venueSpinner.text in self.selectedCity.venueNames:
						self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
						self.rowNum = datacenter.obtainVenueRowNumber(self.stateSpinner.text, self.citySpinner.text, self.venueSpinner.text)
						self.range = ("Venues!A"+str(self.rowNum)+":J"+str(self.rowNum))
						print(self.range)
						self.rowNum -= 1
						datacenter.removeVenueRow(self.rowNum)
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
							self.rowNum = datacenter.obtainIndividualRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							self.range = ("Individual Contacts!A"+str(self.rowNum)+":J"+str(self.rowNum))
							print(self.range)
							#Create the new overall layout of the popup to be inserted in as content
							newContactPopupLayout = RelativeLayout()
							
							#Create new lines for input...
							#...State and city...
							stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
							stateLabel = Label(text = "State:", size_hint_x = 0.1)
							self.stateInput = TextInput(text = self.selectedState.stateName, size_hint_x = 0.4)
							cityLabel = Label(text = "City:", size_hint_x = 0.1)
							self.cityInput = TextInput(text = self.selectedCity.cityName, size_hint_x = 0.4)
							stateCityLayout.add_widget(stateLabel)
							stateCityLayout.add_widget(self.stateInput)
							stateCityLayout.add_widget(cityLabel)
							stateCityLayout.add_widget(self.cityInput)
							newContactPopupLayout.add_widget(stateCityLayout)
							
							#...Name...
							nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
							nameLabel = Label(text = "Name:", size_hint_x = 0.1)
							self.nameInput = TextInput(text = self.selectedContact.name, size_hint_x = 0.9)
							nameLayout.add_widget(nameLabel)
							nameLayout.add_widget(self.nameInput)
							newContactPopupLayout.add_widget(nameLayout)
							
							#...Address...
							addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
							addressLabel = Label(text = "Address:", size_hint_x = 0.1)
							self.addressInput = TextInput(text = self.selectedContact.address, size_hint_x = 0.6)
							zipLabel = Label(text = "Zip Code:", size_hint_x = 0.1)
							self.zipInput = TextInput(text = self.selectedContact.zip, size_hint_x = 0.2)
							addressLayout.add_widget(addressLabel)
							addressLayout.add_widget(self.addressInput)
							addressLayout.add_widget(zipLabel)
							addressLayout.add_widget(self.zipInput)
							newContactPopupLayout.add_widget(addressLayout)
							
							#...Phone #...
							phoneLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.7})
							phoneLabel = Label(text = "Phone #:", size_hint_x = 0.1)
							self.phoneInput = TextInput(text = self.selectedContact.phone, size_hint_x = 0.9)
							phoneLayout.add_widget(phoneLabel)
							phoneLayout.add_widget(self.phoneInput)
							newContactPopupLayout.add_widget(phoneLayout)
							
							#...Links...
							linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
							linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
							self.linksInput = TextInput(text = self.selectedContact.links, size_hint_x = 0.6)
							linksLayout.add_widget(linksLabel)
							linksLayout.add_widget(self.linksInput)
							newContactPopupLayout.add_widget(linksLayout)
							
							#...Associations...
							contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
							contactLabel = Label(text = "Associations (separate with commas):", size_hint_x = 0.4)
							self.contactInput = TextInput(text = self.selectedContact.associations, size_hint_x = 0.6)
							contactLayout.add_widget(contactLabel)
							contactLayout.add_widget(self.contactInput)
							newContactPopupLayout.add_widget(contactLayout)
							
							#...Email...
							emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
							emailLabel = Label(text = "Email:", size_hint_x = 0.1)
							self.emailInput = TextInput(text = self.selectedContact.email, size_hint_x = 0.9)
							emailLayout.add_widget(emailLabel)
							emailLayout.add_widget(self.emailInput)
							newContactPopupLayout.add_widget(emailLayout)
							
							#...notes on the contact itself...
							notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
							notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
							self.notesInput = TextInput(text = self.selectedContact.notes, size_hint_x = 0.9, multiline = True)
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
							submitButton.bind(on_press = self.submitEditedIndividualData)
							cancelButton.bind(on_press = self.newContactPopup.dismiss)
		elif self.organizationRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.organizationNames:
							self.selectedOrganization = self.selectedCity.selectOrganization(self.contactSelectorSpinner.text)
							self.rowNum = datacenter.obtainOrganizationRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							self.range = ("Organizational Contacts!A"+str(self.rowNum)+":J"+str(self.rowNum))
							print(self.range)
							#Create the new overall layout of the popup to be inserted in as content
							newContactPopupLayout = RelativeLayout()
							
							#Create new lines for input...
							#...State and city...
							stateCityLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.9})
							stateLabel = Label(text = "State:", size_hint_x = 0.1)
							self.stateInput = TextInput(text = self.selectedState.stateName, size_hint_x = 0.4)
							cityLabel = Label(text = "City:", size_hint_x = 0.1)
							self.cityInput = TextInput(text = self.selectedCity.cityName, size_hint_x = 0.4)
							stateCityLayout.add_widget(stateLabel)
							stateCityLayout.add_widget(self.stateInput)
							stateCityLayout.add_widget(cityLabel)
							stateCityLayout.add_widget(self.cityInput)
							newContactPopupLayout.add_widget(stateCityLayout)
							
							#...Name...
							nameLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 1})
							nameLabel = Label(text = "Name:", size_hint_x = 0.1)
							self.nameInput = TextInput(text = self.selectedOrganization.organizationName, size_hint_x = 0.9)
							nameLayout.add_widget(nameLabel)
							nameLayout.add_widget(self.nameInput)
							newContactPopupLayout.add_widget(nameLayout)
							
							#...Address...
							addressLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.8})
							addressLabel = Label(text = "Address:", size_hint_x = 0.1)
							self.addressInput = TextInput(text = self.selectedOrganization.address, size_hint_x = 0.6)
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
							self.phoneInput = TextInput(text = self.selectedOrganization.phone, size_hint_x = 0.9)
							phoneLayout.add_widget(phoneLabel)
							phoneLayout.add_widget(self.phoneInput)
							newContactPopupLayout.add_widget(phoneLayout)
							
							#...Links...
							linksLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.6})
							linksLabel = Label(text = "Links (separate with commas):", size_hint_x = 0.4)
							self.linksInput = TextInput(text = self.selectedOrganization.links, size_hint_x = 0.6)
							linksLayout.add_widget(linksLabel)
							linksLayout.add_widget(self.linksInput)
							newContactPopupLayout.add_widget(linksLayout)
							
							#...Members...
							contactLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.5})
							contactLabel = Label(text = "Members (separate by commas):", size_hint_x = 0.4)
							self.contactInput = TextInput(text = self.selectedOrganization.members, size_hint_x = 0.6)
							contactLayout.add_widget(contactLabel)
							contactLayout.add_widget(self.contactInput)
							newContactPopupLayout.add_widget(contactLayout)
							
							#...Email...
							emailLayout = BoxLayout(size_hint_y = 0.1, pos_hint = {"center_x": 0.5, "top": 0.4})
							emailLabel = Label(text = "Email:", size_hint_x = 0.1)
							self.emailInput = TextInput(text = self.selectedOrganization.email, size_hint_x = 0.9)
							emailLayout.add_widget(emailLabel)
							emailLayout.add_widget(self.emailInput)
							newContactPopupLayout.add_widget(emailLayout)
							
							#...notes on the contact itself...
							notesLayout = BoxLayout(size_hint_y = 0.2, pos_hint = {"center_x": 0.5, "top": 0.3})
							notesLabel = Label(text = "Notes:", size_hint_x = 0.1)
							self.notesInput = TextInput(text = self.selectedOrganization.notes, size_hint_x = 0.9, multiline = True)
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
							submitButton.bind(on_press = self.submitEditedOrganizationData)
							cancelButton.bind(on_press = self.newContactPopup.dismiss)
	
	def removeContact(self, instance):
		if self.individualRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.contactNames:
							self.selectedContact = self.selectedCity.selectContact(self.contactSelectorSpinner.text)
							self.rowNum = datacenter.obtainIndividualRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							self.range = ("Individual Contacts!A"+str(self.rowNum)+":J"+str(self.rowNum))
							print(self.range)
							self.rowNum -= 1
							datacenter.removeIndividualRow(self.rowNum)
							self.stateSpinner.text = "State"
							self.citySpinner.text = "City"
							self.contactSelectorSpinner.text = "Contact"
		elif self.organizationRadio.active == True:
			if datacenter.linkValid is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.contactSelectorSpinner.text in self.selectedCity.organizationNames:
							self.selectedContact = self.selectedCity.selectOrganization(self.contactSelectorSpinner.text)
							self.rowNum = datacenter.obtainOrganizationRowNumber(self.stateSpinner.text, self.citySpinner.text, self.contactSelectorSpinner.text)
							self.range = ("Organizational Contacts!A"+str(self.rowNum)+":J"+str(self.rowNum))
							print(self.range)
							self.rowNum -= 1
							datacenter.removeOrganizationRow(self.rowNum)
							self.stateSpinner.text = "State"
							self.citySpinner.text = "City"
							self.contactSelectorSpinner.text = "Contact"
	
	
	
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
	
	def submitEditedVenueData(self, instance):
		if datacenter.linkValid is True:
			print("Edited venue submitted.")
			datacenter.submitEditedVenueDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text, self.range)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Venue edit was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
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
	
	def submitEditedIndividualData(self, instance):
		if datacenter.linkValid is True:
			print("Edited individual submitted.")
			datacenter.submitEditedIndividualDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text, self.range)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Contact edit was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
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
			
	def submitEditedOrganizationData(self, instance):
		if datacenter.linkValid is True:
			print("New organization submitted.")
			datacenter.submitEditedOrganizationDatabaseInfo(self.stateInput.text, self.cityInput.text, self.nameInput.text, self.addressInput.text, self.zipInput.text, self.phoneInput.text, self.linksInput.text, self.contactInput.text, self.emailInput.text, self.notesInput.text, self.range)
			popupContent = RelativeLayout()
			popupLabel = Label(text = "Contact edit was successful!", size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "top": 0.75})
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
		self.cityPicked = False
		if datacenter.linkValid is True:
			datacenter.stateNames.sort()
			self.stateSpinner.values = datacenter.stateNames
			self.statePicked = True
			self.citySpinner.values = []
			self.citySpinner.text = "City"
			self.venueSpinner.values = []
			self.venueSpinner.text = "Venue"
			self.contactSelectorSpinner.values = []
			self.contactSelectorSpinner.text = "Contact"
	
	def citySelection(self, instance): 
		if datacenter.linkValid is True:
			if self.statePicked is True:
				if self.stateSpinner.text in datacenter.stateNames:
					self.selectedState = datacenter.selectState(self.stateSpinner.text)
					self.selectedState.cityNames.sort()
					self.citySpinner.values = self.selectedState.cityNames
					self.cityPicked = True
					self.venueSpinner.values = []
					self.venueSpinner.text = "Venue"
					self.contactSelectorSpinner.values = []
					self.contactSelectorSpinner.text = "Contact"
	
	def venueSelection(self, instance):
		if self.cityPicked is True:
			if datacenter.linkValid is True:
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.venueNames) > 0:
						self.selectedCity.venueNames.sort()
						self.venueSpinner.values = self.selectedCity.venueNames
	
	def contactSelection(self, instance):
		self.contactSelectorSpinner.values = []
		self.contactSelectorSpinner.text = "Contact"
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
							
							
	#Create a handler for the infoboxes
	def updateVenueInfoBox(self, instance):
		if self.cityPicked is True:
			if datacenter.linkValid is True:
				if self.citySpinner.text in self.selectedState.cityNames:
					self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
					if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.venueNames) > 0:
						self.selectedCity.venueNames.sort()
						if self.venueSpinner.text in self.selectedCity.venueNames:
							self.selectedVenue = self.selectedCity.selectVenue(self.venueSpinner.text)
							self.venueNameText.text = self.selectedVenue.venueName
							self.stateVenueNameText.text = self.selectedVenue.stateName
							self.cityVenueNameText.text = self.selectedVenue.cityName
							self.addressVenueNameText.text = self.selectedVenue.address
							self.zipVenueNameText.text = self.selectedVenue.zip
							self.phoneVenueNameText.text = self.selectedVenue.phone
							self.emailVenueNameText.text = self.selectedVenue.email
							self.linksVenueLabel.text = self.selectedVenue.links
							self.contactsVenueLabel.text = self.selectedVenue.contacts
							self.notesVenueLabel.text = self.selectedVenue.notes
	
	def updateContactInfoBox(self, instance):
		if self.individualRadio.active == True:
			self.groupsContactNameLabel.text = "Assoc.:"
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.contactNames) > 0:
							self.selectedCity.contactNames.sort()
							if self.contactSelectorSpinner.text in self.selectedCity.contactNames:
								self.selectedContact = self.selectedCity.selectContact(self.contactSelectorSpinner.text)
								self.contactNameText.text = self.selectedContact.name
								self.stateContactNameText.text = self.selectedState.stateName
								self.cityContactNameText.text = self.selectedCity.cityName
								self.addressContactNameText.text = self.selectedContact.address
								self.zipContactNameText.text = self.selectedContact.zip
								self.phoneContactNameText.text = self.selectedContact.phone
								self.emailContactNameText.text = self.selectedContact.email
								self.linksContactLabel.text = self.selectedContact.links
								self.groupsContactLabel.text = self.selectedContact.associations
								self.notesContactLabel.text = self.selectedContact.notes
		elif self.organizationRadio.active == True:
			self.groupsContactNameLabel.text = "Members:"
			if self.cityPicked is True:
				if datacenter.linkValid is True:
					if self.citySpinner.text in self.selectedState.cityNames:
						self.selectedCity = self.selectedState.selectCity(self.citySpinner.text)
						if self.selectedCity.cityName in self.selectedState.cityNames and len(self.selectedCity.organizationNames) > 0:
							self.selectedCity.organizationNames.sort()
							if self.contactSelectorSpinner.text in self.selectedCity.organizationNames:
								self.selectedOrganization = self.selectedCity.selectOrganization(self.contactSelectorSpinner.text)
								self.contactNameText.text = self.selectedOrganization.organizationName
								self.stateContactNameText.text = self.selectedState.stateName
								self.cityContactNameText.text = self.selectedCity.cityName
								self.addressContactNameText.text = self.selectedOrganization.address
								self.zipContactNameText.text = self.selectedOrganization.zip
								self.phoneContactNameText.text = self.selectedOrganization.phone
								self.emailContactNameText.text = self.selectedOrganization.email
								self.linksContactLabel.text = self.selectedOrganization.links
								self.groupsContactLabel.text = self.selectedOrganization.members
								self.notesContactLabel.text = self.selectedOrganization.notes
		
		
		
		
	
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
				datacenter.databaseConnect(credentials)	
				popup = Popup(title = "Link Established", content = (Label(text = "Link to Google Sheets successfully established!")), size_hint = (0.85, 0.4))
				popup.open()
			else:
				popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
				popup.open()
		else:
			popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
			popup.open()
			
		
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
				datacenter.databaseConnect(credentials)	
				popup = Popup(title = "Link Established", content = (Label(text = "Link to Google Sheets successfully established!")), size_hint = (0.85, 0.4))
				popup.open()
			else:
				popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
				popup.open()
		else:
			popup = Popup(title = "Invalid Link", content = (Label(text = "The link you provided is invalid.  Check to make sure it's the right link.")), size_hint = (0.85, 0.4))
			popup.open()
			
		
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
