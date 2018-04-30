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
from datacls import organization

import httplib2
import os
import codecs

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
	def __init__(self, link, states = None, stateNames = None, individuals = None, individualNames = None, organizations = None, organizationNames = None, dates = None, dateNames = None):
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
			
		if dates is None:
			self.dates = []
		else:
			self.dates = dates
		
		if dateNames is None:
			self.dateNames = []
		else:
			self.dateNames = dateNames
			
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
			#flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			constructor_kwargs = {
                'redirect_uri': ["urn:ietf:wg:oauth:2.0:oob","http://localhost"],
                'auth_uri': "https://accounts.google.com/o/oauth2/auth",
                'token_uri': "https://accounts.google.com/o/oauth2/token",
            }
			flow = client.OAuth2WebServerFlow("181019670663-4tqat2a6ojf4k1v8ac2a943p06hr8tu5.apps.googleusercontent.com", "avagdlQNxR-BsXck7bTst0J6", SCOPES, **constructor_kwargs)
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
		self.title = self.sheets[0].get("properties", {}).get("title", "")
		
		#Initialize the sheet setup from a fresh spreadsheet
		if self.title != "Venues":
			self.sheetId = self.sheets[0].get("properties", {}).get("sheetId", 1000006)
			# print(self.sheetId)
			requests = []
			requests.append({
				"addSheet": {
					"properties": {
						"title": "Organizational Contacts"

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
					"title": "Venues"						
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
		elif self.title != "Venues" and len(self.sheets) > 1:
			self.sheetId = self.sheets[0].get("properties", {}).get("sheetId", 1000006)
			# print(self.sheetId)
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
			
		population = self.populate()	
	
	def submitVenueDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
			
		#Submit all relevant data to the google sheet
		rangeName = "Venues!A1:J1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes]]
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
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
		
	def submitEditedVenueDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes, range):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
			
		#Submit all relevant data to the google sheet
		rangeName = range
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes]]
		data = [
			{
				"range": rangeName,
				"values": values
			}
		]
		body = ({
			"valueInputOption": "RAW",
			"data": data
		})
		response = self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#Resize the data after the entries
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
		
	def submitIndividualDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
		
		#Submit all relevant data to the google sheet
		rangeName = "Individual Contacts!A1:J1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts, submittedEmail, submittedNotes]]
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
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
		
	def submitEditedIndividualDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes, range):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
		
		#Submit all relevant data to the google sheet
		rangeName = range
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes]]
		data = [
			{
				"range": rangeName,
				"values": values
			}
		]
		body = ({
			"valueInputOption": "RAW",
			"data": data
		})
		response = self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#Resize the data after the entries
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
		
	def submitOrganizationDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
		
		#Submit all relevant data to the google sheet
		rangeName = "Organizational Contacts!A1:J1"
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes]]
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
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
			
			
	def submitEditedOrganizationDatabaseInfo(self, submittedState, submittedCity, submittedName, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes, range):
		
		if submittedState == "":
			submittedState = "N/A"
		if submittedCity == "":
			submittedCity = "N/A"
		if submittedName == "":
			submittedName = "N/A"
		if submittedAddress == "":
			submittedAddress = "N/A"
		if submittedZip == "":
			submittedZip = "N/A"
		if submittedPhone == "":
			submittedPhone = "N/A"
		if submittedLinks == "":
			submittedLinks = "N/A"
		if submittedContacts == "":
			submittedContacts = "N/A"
		if submittedEmail == "":
			submittedEmail = "N/A"
		if submittedNotes == "":
			submittedNotes = "N/A"
		
		#Submit all relevant data to the google sheet
		rangeName = range
		values = [[submittedName, submittedState, submittedCity, submittedAddress, submittedZip, submittedPhone, submittedLinks, submittedContacts,  submittedEmail, submittedNotes]]
		data = [
			{
				"range": rangeName,
				"values": values
			}
		]
		body = ({
			"valueInputOption": "RAW",
			"data": data
		})
		response = self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#Resize the data after the entries, and sort it according to name of individual, followed by name of city, followed by name of state
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
					"endColumnIndex": 10
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
		population = self.populate()
			
	def submitDate(self, submittedDate):
		print("Notes added to "+submittedDate.dateName)
		
		#Update the notes first...
		rangeName = submittedDate.dateName+"!A1:A1"
		values = [[submittedDate.notes]]
		data = [
			{
				"range": rangeName,
				"values": values
			}
		]
		body = ({
			"valueInputOption": "RAW",
			"data": data
		})
		response = self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#...and then update the venues, contacts, and organizations met that day
		rangeName = submittedDate.dateName+"!B2:L"
		values = []
		for venue in submittedDate.venues:
			venueRange = []
			venueRange.append("Venue")
			venueRange.append(venue.venueName)
			venueRange.append(venue.stateName)
			venueRange.append(venue.cityName)
			venueRange.append(venue.address)
			venueRange.append(venue.zip)
			venueRange.append(venue.phone)
			venueRange.append(venue.links)
			venueRange.append(venue.contacts)
			venueRange.append(venue.email)
			venueRange.append(venue.notes)
			values.append(venueRange)
		for contact in submittedDate.contacts:
			contactRange = []
			contactRange.append("Individual")
			contactRange.append(contact.name)
			contactRange.append(contact.stateName)
			contactRange.append(contact.cityName)
			contactRange.append(contact.address)
			contactRange.append(contact.zip)
			contactRange.append(contact.phone)
			contactRange.append(contact.links)
			contactRange.append(contact.associations)
			contactRange.append(contact.email)
			contactRange.append(contact.notes)
			values.append(contactRange)
		for organization in submittedDate.organizations:
			organizationRange = []
			organizationRange.append("Organization")
			organizationRange.append(organization.organizationName)
			organizationRange.append(organization.stateName)
			organizationRange.append(organization.cityName)
			organizationRange.append(organization.address)
			organizationRange.append(organization.zip)
			organizationRange.append(organization.phone)
			organizationRange.append(organization.links)
			organizationRange.append(organization.members)
			organizationRange.append(organization.email)
			organizationRange.append(organization.notes)
			values.append(organizationRange)
			
		data = [
			{
				"range": rangeName,
				"values": values
			}
		]
		body = ({
			"valueInputOption": "RAW",
			"data": data
		})
		response = self.service.spreadsheets().values().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#Obtain the sheetId for the sheet in question
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			print(self.title)
			if self.title == submittedDate.dateName:
				self.sheetId = sheet.get("properties", {}).get("sheetId", 0)
		
		#Finally, sort all the data and resize all necessary columns and rows
		requests = []
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheetId,
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 12
				}
			}
		})
		requests.append({
			"autoResizeDimensions": {
				"dimensions": {
					"sheetId": self.sheetId,
					"dimension": "ROWS"
				}
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheetId,
					"startColumnIndex": 1,
					"endColumnIndex": 12,
					"startRowIndex": 1
				},
				"sortSpecs": [
					{
					"dimensionIndex": 1,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheetId,
					"startColumnIndex": 1,
					"endColumnIndex": 12,
					"startRowIndex": 1
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
					"sheetId": self.sheetId,
					"startColumnIndex": 1,
					"endColumnIndex": 12,
					"startRowIndex": 1
				},
				"sortSpecs": [
					{
					"dimensionIndex": 4,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		requests.append({
			"sortRange": {
				"range": {
					"sheetId": self.sheetId,
					"startColumnIndex": 1,
					"endColumnIndex": 12,
					"startRowIndex": 1
				},
				"sortSpecs": [
					{
					"dimensionIndex": 3,
					"sortOrder": "ASCENDING"
					}
				]
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		population = self.populate()
		
	def submitEditedDate(self, submittedDate):
		#Begin by finding the spreadsheet so that the spreadsheet Id can be obtained
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			print(self.title)
			if self.title == submittedDate.dateName:
				self.sheetId = sheet.get("properties", {}).get("sheetId", 0)
		
		#Remove all prior data on the sheet...
		requests = []
		requests.append({
			"deleteDimension": {
				"range": {
					"sheetId": self.sheetId,
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 12
				}
			}
		})
		requests.append({
			"insertDimension": {
				"range": {
					"sheetId": self.sheetId,
					"dimension": "COLUMNS",
					"startIndex": 0,
					"endIndex": 12
				}
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		
		#...and replace it with the new data.
		self.submitDate(submittedDate)
		
	#Obtain the row number of the desired data in google sheets for editing and removal purposes
	def obtainVenueRowNumber(self, stateName, cityName, venueName):
		#Begin with row and col at 1 because of how google sheets counts rows and columns
		rowNum = 1
		
		rangeName = "Venues!A1:J"
		self.venueGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		self.values = self.venueGrouping.get('values', [])
		
		for row in self.values:
			if row[0] == venueName and row[1] == stateName and row[2] == cityName:
				return rowNum
			else:
				rowNum += 1
		return rowNum
	
	def obtainIndividualRowNumber(self, stateName, cityName, contactName):
		#Begin with row and col at 1 because of how google sheets counts rows and columns
		rowNum = 1
		
		rangeName = "Individual Contacts!A1:J"
		self.individualGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		self.values = self.individualGrouping.get('values', [])
		
		for row in self.values:
			if row[0] == contactName and row[1] == stateName and row[2] == cityName:
				return rowNum
			else:
				rowNum += 1
		return rowNum
		
	def obtainOrganizationRowNumber(self, stateName, cityName, contactName):
		#Begin with row and col at 1 because of how google sheets counts rows and columns
		rowNum = 1
		
		rangeName = "Organizational Contacts!A1:J"
		self.organizationalGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		self.values = self.organizationalGrouping.get('values', [])
		
		for row in self.values:
			if row[0] == contactName and row[1] == stateName and row[2] == cityName:
				return rowNum
			else:
				rowNum += 1
		return rowNum
	
	def editVenueRow(self):
		pass
	
	def editIndividualRow(self):
		pass
	
	def editOrganizationRow(self):
		pass
		
	def removeVenueRow(self, rowNum):
		requests = []
		requests.append({
			"deleteDimension": {
				"range": {
					"sheetId": self.sheets[0].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS",
					"startIndex": rowNum,
					"endIndex": rowNum+1
				}
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		print("Row deleted")
		population = self.populate()
	
	def removeIndividualRow(self):
		requests = []
		requests.append({
			"deleteDimension": {
				"range": {
					"sheetId": self.sheets[1].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS",
					"startIndex": rowNum,
					"endIndex": rowNum+1
				}
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		print("Row deleted")
		population = self.populate()
	
	def removeOrganizationRow(self):
		requests = []
		requests.append({
			"deleteDimension": {
				"range": {
					"sheetId": self.sheets[2].get("properties", {}).get("sheetId", 0),
					"dimension": "ROWS",
					"startIndex": rowNum,
					"endIndex": rowNum+1
				}
			}
		})
		
		body = {
			"requests": requests
		}
		
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		print("Row deleted")
		population = self.populate()
	
	#Populate the database's objects 
	def populate(self):
		#Reset all lists of data back to their null states
		self.states = []
		self.stateNames = []
		self.individuals = []
		self.individualNames = []
		self.organizations = []
		self.organizationNames = []
		self.dates = []
		self.dateNames = []
		
		rangeName = "Venues!A1:J"
		self.venueGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		#print(self.venueGrouping)
		self.values = self.venueGrouping.get('values', [])
		if not self.values:
			print("No values found, spreadsheet empty")
		else:
			for row in self.values:
				if row[1] not in self.stateNames:
					newState = state.State(row[1])
					newCity = city.City(row[2])
					newVenue = venue.Venue(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
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
						newVenue = venue.Venue(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						newCity.addVenue(newVenue)
						newCity.venueNames.append(row[0])
						selectedState.addCity(newCity)
						selectedState.cityNames.append(row[2])
					else:
						selectedCity = selectedState.selectCity(row[2])
						newVenue = venue.Venue(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						selectedCity.addVenue(newVenue)
						selectedCity.venueNames.append(row[0])
					
		#ADD FOR CONTACTS AS WELL
		rangeName = "Individual Contacts!A1:J"
		self.contactGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		#print(self.contactGrouping)
		self.values = self.contactGrouping.get('values', [])
		#print(self.values)
		if not self.values:
			print("No values found, spreadsheet empty")
		else:
			for row in self.values:
				#print(row[1])
				if row[1] not in self.stateNames:
					newState = state.State(row[1])
					newCity = city.City(row[2])
					newContact = contact.Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
					newCity.addContact(newContact)
					newCity.contactNames.append(row[0])
					newState.addCity(newCity)
					newState.cityNames.append(row[2])
					self.states.append(newState)
					self.stateNames.append(row[1])
				else:
					selectedState = self.selectState(row[1])
					if row[2] not in selectedState.cityNames:
						newCity = city.City(row[2])
						newContact = contact.Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						newCity.addContact(newContact)
						newCity.contactNames.append(row[0])
						selectedState.addCity(newCity)
						selectedState.cityNames.append(row[2])
					else:
						selectedCity = selectedState.selectCity(row[2])
						newContact = contact.Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						selectedCity.addContact(newContact)
						selectedCity.contactNames.append(row[0])
						
		rangeName = "Organizational Contacts!A1:J"
		self.orgGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=rangeName).execute()
		#print(self.orgGrouping)
		self.values = self.orgGrouping.get('values', [])
		#print(self.values)
		if not self.values:
			print("No values found, spreadsheet empty")
		else:
			for row in self.values:
				#print(row[1])
				if row[1] not in self.stateNames:
					newState = state.State(row[1])
					newCity = city.City(row[2])
					newOrganization = organization.Organization(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
					newCity.addOrganization(newOrganization)
					newCity.organizationNames.append(row[0])
					newState.addCity(newCity)
					newState.cityNames.append(row[2])
					self.states.append(newState)
					self.stateNames.append(row[1])
				else:
					selectedState = self.selectState(row[1])
					if row[2] not in selectedState.cityNames:
						newCity = city.City(row[2])
						newOrganization = organization.Organization(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						newCity.addOrganization(newOrganization)
						newCity.organizationNames.append(row[0])
						selectedState.addCity(newCity)
						selectedState.cityNames.append(row[2])
					else:
						selectedCity = selectedState.selectCity(row[2])
						newOrganization = organization.Organization(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
						selectedCity.addOrganization(newOrganization)
						selectedCity.organizationNames.append(row[0])
						
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			
			if self.title == "Venues" or self.title == "Individual Contacts" or self.title == "Organizational Contacts":
				print("Initial sheet detected.  Continuing...")
			else:
				self.dateNames.append(self.title)
				
				#This subroutine needs to be called ONLY on date selection, and whether or not a date exists should be called from dateNames
				# dateRange = self.title+"!A1:L"
				# self.dateGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=dateRange).execute()
				# dateValues = self.dateGrouping.get("values", [])
				# newDate = dayinfo.DayInfo(self.title)
				# for row in dateValues:
					# if row[0] != "":
						# newDate.notes = row[0]
					# elif row[1] != "":
						# if row[1] == "Venue":
							# newVenue = venue.Venue(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							# newDate.addVenue(newVenue)
						# elif row[1] == "Individual":
							# newContact = contact.Contact(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							# newDate.addContact(newContact)
						# elif row[1] == "Organization":
							# newOrganization = organization.Organization(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							# newDate.addOrganization(newOrganization)
				# self.addDate(newDate)
				
				
		return "Self"
	
	#This is used to grab data only as necessary from google sheets, thereby reducing the number of overall request calls
	def populateDate(self, dateName):
		self.dates = []
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			if self.title == dateName:
				dateRange = self.title+"!A1:L"
				self.dateGrouping = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheetId, range=dateRange).execute()
				dateValues = self.dateGrouping.get("values", [])
				newDate = dayinfo.DayInfo(self.title)
				for row in dateValues:
					if row[0] != "":
						newDate.notes = row[0]
					elif row[1] != "":
						if row[1] == "Venue":
							newVenue = venue.Venue(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							newDate.addVenue(newVenue)
						elif row[1] == "Individual":
							newContact = contact.Contact(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							newDate.addContact(newContact)
						elif row[1] == "Organization":
							newOrganization = organization.Organization(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
							newDate.addOrganization(newOrganization)
				self.addDate(newDate)
		
		return "Self"
	
	def dateFinder(self, dateName):
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			print(self.title)
			if self.title == dateName:
				return True
		return False
		
	def addDateToSpreadsheet(self, dateName):
		requests = []
		requests.append({
				"addSheet": {
					"properties": {
						"title": dateName
					}
				}
			})
			
		body = {
			"requests": requests
		}
		response = self.service.spreadsheets().batchUpdate(spreadsheetId = self.spreadsheetId, body = body).execute()
		population = self.populate()
		
	def removeDateFromSpreadsheet(self, dateName):
		self.sheetMetadata = self.service.spreadsheets().get(spreadsheetId = self.spreadsheetId).execute()
		self.sheets = self.sheetMetadata.get("sheets", "")
		for sheet in self.sheets:
			self.title = sheet.get("properties", {}).get("title", "someTitle")
			if self.title == dateName:
				self.sheetId = sheet.get("properties", {}).get("sheetId", 0)
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
		population = self.populate()
			
	
	#The following 3 functions are self-explanatory by title - add, remove, and print states
	def addState(self, state):
		if state not in self.states:
			self.states.append(state)
		
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
			print(organization.organizationName)
			
	def selectOrganization(self, organizationName):
		organizationFound = False
		
		for organization in self.organizations:
			if organizationName == organization.organizationName:
				organizationFound = True
				return organization
			
		if organizationFound == False:
			print("No organization found by the name of '",organizationName,"'")
			print("Check spelling and make sure contact was initialized")
	
	
	#Finally, it will handle dates.
	def addDate(self, date):
		if date not in self.dates:
			self.dates.append(date)
			#This is where the dates need to be called from google sheets.  The actual, physical dates aren't needed anywhere else.
		
	def removeDate(self, date):
		if date in self.dates:
			self.dates.remove(date)
					
	def printDates(self):
		for date in self.dates:
			print(date.dateName)
				
	def selectDate(self, dateName):
		dateFound = False
		
		for date in self.dates:
			if dateName == date.dateName:
				dateFound = True
				return date
		
		if dateFound == False:
			print("No date found by the name '",dateName,"'")
			return None
