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
# from kivy.uix.recycleview import RecycleView
# from kivy.uix.recycleview.views import RecycleDataViewBehavior
# from kivy.uix.behaviors import FocusBehavior
# from kivy.uix.recycleview.layout import LayoutSelectionBehavior
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
				text:"Database:  "
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
			CalendarManager:
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

#Multiple classes will share the same calendar data, thus it is instantiated here
today = datetime.date.today()
calendar = Calendar(today)

# class DateView(GridLayout):
	# dateView = ObjectProperty()
	
	# def __init__(self, **kwargs):
		# self.cols = 7
		# self.size_hint_y = 0.7
		# self.pos_hint = {"center_x":0.5, "bottom":0}	
		# super(DateView, self).__init__(**kwargs)
		# self.monLabel = Label(text="Mo")
		# self.add_widget(self.monLabel)
		# self.tueLabel = Label(text="Tu")
		# self.add_widget(self.tueLabel)
		# self.wedLabel = Label(text="We")
		# self.add_widget(self.wedLabel)
		# self.thursLabel = Label(text="Th")
		# self.add_widget(self.thursLabel)
		# self.friLabel = Label(text="Fr")
		# self.add_widget(self.friLabel)
		# self.satLabel = Label(text="Sa")
		# self.add_widget(self.satLabel)
		# self.sunLabel = Label(text="Su")
		# self.add_widget(self.sunLabel)
		# for day in calendar.calendarObjFlat:
			# if day.month != calendar.currentMonth:
				# self.newButton = Button(text=str(day.day), background_normal="", background_color=[0.1,0.1,0.1,1])
				# self.add_widget(self.newButton)
			# else:
				# self.newButton = Button(text=str(day.day), background_normal="", background_color=[0,0.4,0.3,1])
				# self.add_widget(self.newButton)
	
	# def update(self):
		# self.dateView.sunLabel.text ="HI"
		
	
#Management of the date view
# class CalendarView(RecycleView):
		
	# def __init__(self, **kwargs):
		# super(CalendarView, self).__init__(**kwargs)
		# self.data = []
		# for day in calendar.calendarObjFlat:
			# if day.month != calendar.currentMonth:
				# self.data.append({'text': str(day.day), 'background_normal':'', 'background_color':[0.1,0.1,0.1,1]})
			# else:
				# self.data.append({'text': str(day.day), 'background_normal':'', 'background_color':[0,0.4,0.3,1]})
				
	# def update(self):
		# self.data = []
		# for day in calendar.calendarObjFlat:
			# # self.data.append({'text': str(day.day)})
			# if day.month != calendar.currentMonth:
				# self.data.append({'text': str(day.day), 'background_normal':'', 'background_color':[0.1,0.1,0.1,1]})
			# else:
				# self.data.append({'text': str(day.day), 'background_normal':'', 'background_color':[0,0.4,0.3,1]})

# class SelectableButtonSet(RecycleDataViewBehavior, Button):
	# index = None
	
	# def refresh_view_attrs(self, rv, index, data):
		# self.index = index
		# return super(SelectableButtonSet, self).refresh_view_attrs(rv, index, data)
		
	
	
# class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
	# pass

#Management of month selection
# class MonthSelector(RelativeLayout):
	# def __init__(self, **kwargs):
		# self.size_hint_y = 0.3
		# self.pos_hint = {"center_x":0.5, "top":1}
		# super(MonthSelector, self).__init__(**kwargs)
		# self.backButton = Button(text="<",pos_hint={"left":0,"center_y":0.5},size_hint_x=0.25,size_hint_y=0.5)
		# self.backButton.bind(on_press=self.decrementMonth)
		# self.add_widget(self.backButton)
		# self.monthSelected = Label(text=(str(calendar.currentMonth)+", "+str(calendar.currentYear)))
		# self.add_widget(self.monthSelected)
		# self.forwardButton = Button(text=">",pos_hint={"right":1,"center_y":0.5},size_hint_x=0.25,size_hint_y=0.5)
		# self.forwardButton.bind(on_press=self.incrementMonth)
		# self.add_widget(self.forwardButton)
	
	# def update(self):
		# self.monthSelected.text=(str(calendar.currentMonth)+", "+str(calendar.currentYear))
		
	# def incrementMonth(self,instance):
		# calendar.incrementMonth()
		# self.update()
	
	# def decrementMonth(self,instance):
		# calendar.decrementMonth()
		# self.update()
		
		
class CalendarManager(RelativeLayout):
	monthSelector = RelativeLayout(size_hint_y = 0.3, pos_hint = {"center_x":0.5, "top":1})
	dateViewer = GridLayout(cols = 7, size_hint_y = 0.7, pos_hint = {"center_x":0.5, "bottom":0})
	def __init__(self, **kwargs):
		self.size_hint_y = 0.5
		self.size_hint_x = 0.3
		self.pos_hint = {"left": 0, "top": 1}
		super(CalendarManager, self).__init__(**kwargs)
		
		#Add the month selector to the layout
		self.add_widget(self.monthSelector)
		self.monthSelector.backButton = Button(text="<",pos_hint={"left":0,"center_y":0.5},size_hint_x=0.25,size_hint_y=0.5)
		self.monthSelector.backButton.bind(on_press=self.decrementMonth)
		self.monthSelector.add_widget(self.monthSelector.backButton)
		self.monthSelector.monthSelected = Label(text=(calendar.currentMonthString()+", "+str(calendar.currentYear)))
		self.monthSelector.add_widget(self.monthSelector.monthSelected)
		self.monthSelector.forwardButton = Button(text=">",pos_hint={"right":1,"center_y":0.5},size_hint_x=0.25,size_hint_y=0.5)
		self.monthSelector.forwardButton.bind(on_press=self.incrementMonth)
		self.monthSelector.add_widget(self.monthSelector.forwardButton)
		
		#Add the date viewer to the layout
		self.add_widget(self.dateViewer)
		self.dateViewer.monLabel = Label(text="Mo")
		self.dateViewer.add_widget(self.dateViewer.monLabel)
		self.dateViewer.tueLabel = Label(text="Tu")
		self.dateViewer.add_widget(self.dateViewer.tueLabel)
		self.dateViewer.wedLabel = Label(text="We")
		self.dateViewer.add_widget(self.dateViewer.wedLabel)
		self.dateViewer.thursLabel = Label(text="Th")
		self.dateViewer.add_widget(self.dateViewer.thursLabel)
		self.dateViewer.friLabel = Label(text="Fr")
		self.dateViewer.add_widget(self.dateViewer.friLabel)
		self.dateViewer.satLabel = Label(text="Sa")
		self.dateViewer.add_widget(self.dateViewer.satLabel)
		self.dateViewer.sunLabel = Label(text="Su")
		self.dateViewer.add_widget(self.dateViewer.sunLabel)
		for day in calendar.calendarObjFlat:
			if day.month != calendar.currentMonth:
				self.dateViewer.newButton = Button(text=str(day.day), background_normal="", background_color=[0.1,0.1,0.1,1])
				self.dateViewer.add_widget(self.dateViewer.newButton)
			else:
				self.dateViewer.newButton = Button(text=str(day.day), background_normal="", background_color=[0,0.4,0.3,1])
				self.dateViewer.add_widget(self.dateViewer.newButton)
				
	def update(self):
		self.monthSelector.monthSelected.text=(calendar.currentMonthString()+", "+str(calendar.currentYear))
		self.dateViewer.clear_widgets()
		self.dateViewer.monLabel = Label(text="Mo")
		self.dateViewer.add_widget(self.dateViewer.monLabel)
		self.dateViewer.tueLabel = Label(text="Tu")
		self.dateViewer.add_widget(self.dateViewer.tueLabel)
		self.dateViewer.wedLabel = Label(text="We")
		self.dateViewer.add_widget(self.dateViewer.wedLabel)
		self.dateViewer.thursLabel = Label(text="Th")
		self.dateViewer.add_widget(self.dateViewer.thursLabel)
		self.dateViewer.friLabel = Label(text="Fr")
		self.dateViewer.add_widget(self.dateViewer.friLabel)
		self.dateViewer.satLabel = Label(text="Sa")
		self.dateViewer.add_widget(self.dateViewer.satLabel)
		self.dateViewer.sunLabel = Label(text="Su")
		self.dateViewer.add_widget(self.dateViewer.sunLabel)
		for day in calendar.calendarObjFlat:
			if day.month != calendar.currentMonth:
				self.dateViewer.newButton = Button(text=str(day.day), background_normal="", background_color=[0.1,0.1,0.1,1])
				self.dateViewer.add_widget(self.dateViewer.newButton)
			else:
				self.dateViewer.newButton = Button(text=str(day.day), background_normal="", background_color=[0,0.4,0.3,1])
				self.dateViewer.add_widget(self.dateViewer.newButton)
		
	def incrementMonth(self,instance):
		calendar.incrementMonth()
		self.update()
	
	def decrementMonth(self,instance):
		calendar.decrementMonth()
		self.update()
	
		
	
	
#General view classes of the GUI
class ScreenMainMenu(Screen):
	pass
	
class ScreenDatabase(Screen):
	spreadsheetLink = ObjectProperty()

class ScreenCalendar(Screen):
	spreadsheetLink = ObjectProperty()
	
# class ScreenCalendar(Screen):
	# spreadsheetLink = ObjectProperty()
	# mainScreen = RelativeLayout()
	# topSpacing = RelativeLayout(size_hint_y = 0.02, pos_hint = {"center_x": 0.5, "top": 1})
	# mainScreen.add_widget(topSpacing)
	# titleBar = RelativeLayout(size_hint_y = 0.18, pos_hint = {"center_x": 0.5, "top": 0.98})
	# mainScreen.add_widget(titleBar)
	
	# titleLabel = Label(text="Calendar", halign = "center", valign = "center")
	# titleBar.add_widget(titleLabel)
	# backButton = Button(text="Back", size_hint_x = 0.25, size_hint_y = 0.25, pos_hint = {"right": 0.99, "top": 1})
	# titleBar.add_widget(backButton)
	# spreadsheetBar = BoxLayout(size_hint_x = 0.8, size_hint_y = 0.3, pos_hint = {"center_x": 0.5, "bottom": 0})
	# titleBar.add_widget(spreadsheetBar)
	
	# spreadsheetLinkLabel = Label(text="Database:  ", size_hint_x = 0.1)
	# spreadsheetBar.add_widget(spreadsheetLinkLabel)
	# spreadsheetTextInput = TextInput(size_hint_x = 0.7)
	# spreadsheetBar.add_widget(spreadsheetTextInput)
	# spreadsheetSubmit = Button(text="Submit", size_hint_x = 0.2)
	# spreadsheetBar.add_widget(spreadsheetSubmit)
	
	# widgetViews = RelativeLayout(size_hint_y = 0.8, pos_hint = {"center_x": 0.5, "bottom": 0})
	# mainScreen.add_widget(widgetViews)
	# monthSelector = MonthSelector()
	# widgetViews.add_widget(monthSelector)
	# dateManager = CalendarView()
	# widgetViews.add_widget(dateManager)
	# dayInfo = Button(text = "Day Info", size_hint_x = 0.3, size_hint_y = 0.5, pos_hint = {"left": 0, "bottom": 0})
	# widgetViews.add_widget(dayInfo)
	# mapView = MapView()
	# widgetViews.add_widget(mapView)
	
	# mainScreen.remove_widget(widgetViews)


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
