# Waves In Motion

CURRENT VERSION: Alpha 0.1

This app is designed to be an open-source "One Stop Shop" for organization contact management and day planning.  It utilizes Google Sheets to store and manage contact information and notes about them, and is particularly well-suited for bands and other similar art groups.  It also allows for a user to add venues and contacts to a day via the UI, and automatically plots venue locations on a map for visual aid.  

It consists of two main pages:
  1) The Database Manager
  2) The Calendar
  
Each page has a link submitter at the top.  If you're new to the app, create a new spreadsheet in Google Sheets, and put the link to that spreadsheet in that box and submit it.  The app will automatically format the sheet such that information can be stored and accessed.  Likewise, if you feel like manipulating Google Sheets directly, you may do that as long as you follow the format and it will read in the new information. 

The Database Manager allows a user to add a venue, contact, or organization to Google Sheets.  Venues, contacts, and organizations each make up their own sheet, and are the first 3 sheets on the spreadsheet as a whole.  Each data point contains their name, location, phone and email, any links that might be associated with them, any associations they may have, and any notes you may have on them.

The Calendar allows you to take this data and add it to specific days, stored as their own sheets.  Simply select the state and city, and then add the venues and contacts you want for that day.  You may also add notes to that day, as well.  An abbreviated list of that information is then immediately accessible from the main calendar page on selection of the day on the calendar.  Selecting a day on the calendar will also generate markers on the map, and automatically center on the first location entered on the sheet.  An expanded view for the day, containing each contact and venue's relevant information, can also be generated by clicking the "Expand" button.  This information is selectable from this page, and thus can be copied and pasted elsewhere. 

The app's privacy policy can be found here:
https://docs.google.com/document/d/e/2PACX-1vRRTL24F-NTx2ifTl2tOZdD7NNcleRxPdqHT-_Zn2T24oxgjvYz1Vgsv9pTByyIPldLQumgOHZpxR71/pub

This app is not well optimized at the moment, however it is fully functional.  There are plans to optimize and improve the looks of the app in the near future.  Please feel free to contact me with any suggestions!

DEPENDENCIES:
  -Python 3.5.2: https://www.python.org/downloads/
  -Kivy 1.10.0: https://kivy.org/docs/installation/installation.html
  -Geopy 1.13.0: https://pypi.org/project/geopy/
  -Google API Client (most recent): https://developers.google.com/api-client-library/python/apis/sheets/v4
