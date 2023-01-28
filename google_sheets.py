import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sheet_id = '1hbGwi3YoE3aNs37xBHospljYLzuGhDbjY7gna5Iqj0k'
read_range = 'BOT review!A:A'
write_range = 'BOT review!B'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


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
    except HttpError as err:
        print(err)


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


def write_status_to_sheet(count, message):
    try:
        range = write_range + str(count + 1)
        sheet.values().update(spreadsheetId=sheet_id, range=range,
                              valueInputOption='USER_ENTERED', body={ 'values': {'values' : message }}).execute()
    except HttpError as err:
        print(err)
