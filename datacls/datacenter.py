#Written by: Jacob S Liebenow
#
#
#
#This module was created upon the determination that a general, all-encompassing data unit with which to
#place all other objects within was necessary - a general "sheet," if you will, that's able to point
#to all other data points.  This, decidedly, should make it easier to manipulate data using interchangable
#inheritance - IE, bands within venues, venues containing bands, state management, etc.  Ideally, this
#module and class won't ever really be shown, and is only for handling data.
#
#The datacenter class will be instantiated with all current data from Google, and all subsequent objects of
#associated classes will be managed from there.
from __future__ import print_function
from datacls import state
from datacls import city
from datacls import venue
from datacls import dayinfo
from datacls import contact
from datacls import band

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Create the scopes for Waves In Motion database
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Waves In Motion'

class Datacenter: 
	
	stateNumber = 0
	
	
	#The datacenter's primary branches are provinces/states, which contain cities, venues, etc.  However, I
	#also want to allow for a separate type of branch from the datacenter root - contacts, which contains
	#bands, bookers, promoters, and whoever else might be considered relevant.  Contacts might normally be
	#organized by city, but I'd like overall contact searching functionality irrespective of location.  Another
	#possible branch - days, which has one or more associated states/cities (otherwise considered travel days)
	def __init__(self, link, states = None, stateNames = None, individuals = None, individualNames = None, organizations = None, organizationNames = None):
		self.link = link
		self.spreadsheetID = "Dummy ID"
		self.service = None
		self.linkValid = False
		
		if states is None:
			self.states = []
		else: 
			self.states = states
		
		if stateNames is None:
			self.stateNames = []
		else:
			self.stateNames = stateNames
		
		if individuals is None:
			self.individuals = []
		else:
			self.individuals = individuals
			
		if individualNames is None:
			self.individualNames = []
			
		if organizations is None:
			self.organizations = []
		else:
			self.organizations = organizations
			
		if organizationNames is None:
			self.organizationNames = []
		else:
			self.organizationNames = organizationNames
			
	#Function to obtain user's google OAuth2.0 credentials from client_secret.json
	def getCredentials(self):
		"""Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
			Credentials, the obtained credential.
		"""
		self.home_dir = os.path.expanduser('~')
		self.credential_dir = os.path.join(self.home_dir, '.credentials')
		if not os.path.exists(self.credential_dir):
			os.makedirs(self.credential_dir)
		self.credential_path = os.path.join(self.credential_dir,
									   'sheets.googleapis.com-waves-in-motion.json')

		store = Storage(self.credential_path)
		self.credentials = store.get()
		if not self.credentials or self.credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			if flags:
				self.credentials = tools.run_flow(flow, store, flags)
			else: # Needed only for compatibility with Python 2.6
				self.credentials = tools.run(flow, store)
			print('Storing credentials to ' + self.credential_path)
		return self.credentials
	
	
	
	#Connect to the database from the given link
	def databaseConnect(self, credentials):
		self.credentials = credentials
		self.http = self.credentials.authorize(httplib2.Http())
		self.discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
						'version=v4')
		self.service = discovery.build('sheets', 'v4', http=self.http,
								  discoveryServiceUrl=self.discoveryUrl)
		
		#Set up the database, if necessary
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		self.title = self.sheets[0].get("properties", {}).get("title", "someTitle")
		population = self.populate()
		
		#Initialize the sheet setup from a fresh spreadsheet
		if self.title == "Sheet1" and len(self.sheets) == 1:
			self.sheetId = self.sheets[0].get("properties", {}).get("sheetId", 1000006)
			print(self.sheetId)
			requests = []
			requests.append({
				"addSheet": {
					"properties": {
						"title": "Venues"
					}
				}
			})
			requests.append({
				"addSheet": {
					"properties": {
						"title": "Individual Contacts"
					}
				}
			})
			requests.append({
				"addSheet": {
					"properties": {
						"title": "Organizational Contacts"
					}
				}
			})
			requests.append({
				"deleteSheet": {
					"sheetId":self.sheetId
				}
			})
			
			body = {
				"requests": requests
			}
			response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#Clean up the spreadsheet if a spreadsheet was already made
		elif self.title == "Sheet1" and len(self.sheets) > 1:
			self.sheetId = self.sheets[0].get("properties", {}).get("sheetId", 1000006)
			print(self.sheetId)
			requests = []
			requests.append({
				"deleteSheet": {
					"sheetId":self.sheetId
				}
			})
			
			body = {
				"requests": requests
			}
			response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
			
	
	def submitVenueDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes):
		print("****************")
		print(submittedState)
		print(submittedCity)
		print(submittedName)
		print(submittedAddress)
		print(submittedZip)
		print(submittedPhone)
		print(submittedLinks)
		print(submittedContacts)
		print(submittedNotes)
		print("****************")
		
		#Submit all relevant data to the google sheet
		rangeName = "Venues!A1:I1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes]]
		request = ({
			"majorDimension": "ROWS",
			"values": values
		})
		response = self.service.spreadsheets().values().append(spreadsheetId = self.spreadsheetId, range = rangeName, body = request, valueInputOption = "RAW").execute()
		
		#Resize the data after the entries
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 9
				}
			}
		})
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS"
				}
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 0,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 2,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 1,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
	def submitIndividualDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes):
		print("****************")
		print(submittedState)
		print(submittedCity)
		print(submittedName)
		print(submittedAddress)
		print(submittedZip)
		print(submittedPhone)
		print(submittedLinks)
		print(submittedContacts)
		print(submittedNotes)
		print("****************")
		
		#Submit all relevant data to the google sheet
		rangeName = "Individual Contacts!A1:I1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes]]
		request = ({
			"majorDimension": "ROWS",
			"values": values
		})
		response = self.service.spreadsheets().values().append(spreadsheetId = self.spreadsheetId, range = rangeName, body = request, valueInputOption = "RAW").execute()
		
		#Resize the data after the entries
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 9
				}
			}
		})
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS"
				}
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 0,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 2,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 1,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
	def submitOrganizationDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes):
		print("****************")
		print(submittedState)
		print(submittedCity)
		print(submittedName)
		print(submittedAddress)
		print(submittedZip)
		print(submittedPhone)
		print(submittedLinks)
		print(submittedContacts)
		print(submittedNotes)
		print("****************")
		
		#Submit all relevant data to the google sheet
		rangeName = "Organizational Contacts!A1:I1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedNotes]]
		request = ({
			"majorDimension": "ROWS",
			"values": values
		})
		response = self.service.spreadsheets().values().append(spreadsheetId = self.spreadsheetId, range = rangeName, body = request, valueInputOption = "RAW").execute()
		
		#Resize the data after the entries, and sort it according to name of individual, followed by name of city, followed by name of state
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 9
				}
			}
		})
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS"
				}
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 0,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 2,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"startColumnIndex": 0,
					"endColumnIndex": 9
				},
				"sortSpecs": [
					{
					"dimensionIndex": 1,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
			
	
	#Populate the database's objects 
	def populate(self):
		self.states = []
		self.stateNames = []
		rangeName = "Venues!A1:I"
		self.venueGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		print(self.venueGrouping)
		self.values = self.venueGrouping.get('values', [])
		print(self.values)
		if not self.values:
			print("No values found, spreadsheet empty")
		else:
			for row in self.values:
				print(row[1])
				if row[1] not in self.stateNames:
					newState = state.State(row[1])
					newCity = city.City(row[2])
					newVenue = venue.Venue(row[0])
					newCity.addVenue(newVenue)
					newCity.venueNames.append(row[0])
					newState.addCity(newCity)
					newState.cityNames.append(row[2])
					self.states.append(newState)
					self.stateNames.append(row[1])
				else:
					selectedState = self.selectState(row[1])
					if row[2] not in selectedState.cityNames:
						newCity = city.City(row[2])
						newVenue = venue.Venue(row[0])
						newCity.addVenue(newVenue)
						newCity.venueNames.append(row[0])
						selectedState.addCity(newCity)
						selectedState.cityNames.append(row[2])
					else:
						selectedCity = selectedState.selectCity(row[2])
						newVenue = venue.Venue(row[0])
						selectedCity.addVenue(newVenue)
						selectedCity.venueNames.append(row[0])
						
		print("*****")
		print("*****")
		print("*****")
		for province in self.states:
			print(province.stateName)
			for locale in province.cities:
				print("----->"+locale.cityName)
				for shop in locale.venues:
					print("---------->"+shop.venueName)
					
		#ADD FOR CONTACTS AS WELL
		
		return "Self"
	
	
	
	#The following 3 functions are self-explanatory by title - add, remove, and print states
	def addState(self, state):
		if state not in self.states:
			self.states.append(state)
			self.stateNumber += 1
		
	def removeState(self, state):
		if state in self.states:
			self.states.remove(state)
					
	def printStates(self):
		for state in self.states:
			print(state.stateName)
			state.printCities()
			
			
	#The selectState function should allow for a variable in main.py to grab the exact state searched		
	def selectState(self, stateName):
		stateFound = False
		
		for state in self.states:
			if stateName == state.stateName:
				stateFound = True
				return state
		
		if stateFound == False:
			print("No state found by the name '",stateName,"'")
			return None
			
	
	
	#The datacenter should be the primary table for contact object management
	def addIndividual(self, individual):
		if individual not in self.individuals:
			self.individuals.append(individual)
	
	def removeIndividual(self, individual):
		if individual in self.individuals:
			self.individuals.remove(individual)
			
	def printIndividuals(self):
		for individual in self.individuals:
			print(individual.name)
			
	def selectIndividual(self, individualName):
		individualFound = False
		
		for individual in self.individuals:
			if individualName == individual.name:
				individualFound = True
				return individual
		
		if individualFound == False:
			print("No contact found by the name of '",individualName,"'")
			print("Check spelling and make sure contact was initialized")
	
	
	
	#The datacenter will manage organization objects, as well
	def addOrganization(self, organization):
		if organization not in self.organizations:
			self.organizations.append(organization)
			
	def removeOrganization(self, organization):
		if organization in self.organization:
			self.organizations.remove(organization)
			
	def printOrganizations(self):
		for organization in self.organizations:
			print(organization.bandName)
			
	def selectOrganization(self, organizationName):
		organizationFound = False
		
		for organization in self.organizations:
			if organizationName == organization.bandName:
				organizationFound = True
				return organization
			
		if organizationFound == False:
			print("No organization found by the name of '",organizationName,"'")
			print("Check spelling and make sure contact was initialized")
