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
			text: "Database"
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
		size_hint_y: None
		height:"60dp"
		pos_hint: {"center_x": 0.5, "top": 1}
		Label:
			halign: "center"
			valign: "center"
			text: "Database"
		Button:
			size_hint_x: None
			size_hint_y: None
			height:"40dp"
			length:"40dp"
			text: "Back"
			pos_hint: {"right": 0.99, "center_y": 0.5}
			on_press:
				root.manager.transition.direction = "right"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_mainmenu"
			
<ScreenCalendar>
	orientation: "vertical"
	padding: 20
	spacing: 40
	RelativeLayout:
		size_hint_y: None
		height:"60dp"
		pos_hint: {"center_x": 0.5, "top": 1}
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
			pos_hint: {"right": 0.99, "center_y": 0.5}
			on_press:
				root.manager.transition.direction = "right"
				root.manager.transition.duration = 0.5
				root.manager.current = "screen_mainmenu"
			
""")

class ScreenMainMenu(Screen):
	pass
	
class ScreenDatabase(Screen):
	pass

class ScreenCalendar(Screen):
	pass

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
