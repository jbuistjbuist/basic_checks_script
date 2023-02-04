# import operating system modules
import os
import os.path

# import google modules
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# import dotenv module to use env variables
from dotenv import load_dotenv
load_dotenv()

# define authorization scope for the api request we will be making
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# load information about the sheet ID from .env file for security and ease of modification, and define ranges to read/write values
sheet_id = os.getenv('sheet_id')
write_range = 'ekata_review!B2:F'
read_range = 'ekata_review!A:A'
status_range = 'ekata_review!G2:G3'

# log into google sheets with stored credentials, and post an update to the sheet that the script is running
def initialize_sheets():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        global sheet
        sheet = service.spreadsheets()
        update_status('In Progress')

    except HttpError as err:
        print(err)

# read the order IDs from the google sheet, flatten the list that comes back into a one-dimension list,
# and return the list with the first cell (heading) removed
def get_order_IDs():
    try:
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=read_range).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        flat_values = [item for l in values for item in l]
        flat_values.remove(flat_values[0])

        return flat_values
    except HttpError as err:
        print(err)
        return

# takes a two dimensional list object representing the updates for each cell
# uses the google sheets api to post an update to the spreadsheet with all of the cell updates
def write_updates_to_sheet(messages):
    range = write_range

    try:

        sheet.values().update(spreadsheetId=sheet_id, range=range,
                              valueInputOption='USER_ENTERED', body={'values':  messages}).execute()
        return True
    except HttpError as err:
        print(err)
        return

# function to update the status cell of the sheet with a message
def update_status(message):
    sheet.values().update(spreadsheetId=sheet_id, range=status_range,
                          valueInputOption='USER_ENTERED', body={'values':  {'values': f'{message}'}}).execute()
