from apiclient.discovery import build
from google.oauth2.service_account import Credentials
import os.path

# Location of variables we don't want published on Github
# SPREADSHEET_ID is the unique identifier for the spreadsheet we want
# to read/write. You can find it in the URL of the spreadsheet
# bewteen "/d/" and "/edit"
from private.config import SPREADSHEET_ID

# Limits what the sheets service we create is allowed to do.
# Find scopes at
# https://developers.google.com/identity/protocols/googlescopes#sheetsv4
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Location on the computer of the email and "password" (private key) for
# the bot account used to access the Google sheet
_key_file_path = "private/credentials.json"

def get_sheets_service(key_file_path=_key_file_path, scopes=SCOPES):
    """Get the Python object that lets our bot interact with Google sheets."""

    # Load the information for the bot account
    creds = Credentials.from_service_account_file(
        key_file_path, scopes=scopes)

    # Establish the connection to the Google bot account
    service = build('sheets', 'v4', credentials=creds,
        # The following keyword argument fixes some weird errors. See
        # https://github.com/googleapis/google-api-python-client/issues/299
        cache_discovery=False)

    # Return a direct line to Google Sheets
    return service.spreadsheets()

# Call the function to establish a connection to Google Sheets
_sheets_service = get_sheets_service()

def read(rng, sheets_service=_sheets_service, spreadsheet_id=None):
    """Get data from the spreadsheet."""

    # Get the default spreadsheet ID if it's not provided
    # (Do this instead of setting the default in the kwargs so that a user
    # can import gsheet;SPREADSHEET_ID = 'whatever'.
    if spreadsheet_id is None:
        spreadsheet_id = SPREADSHEET_ID

    # Request the data from the spreadsheet
    result = sheets_service.values().get(
            spreadsheetId=spreadsheet_id,
            range=rng
        ).execute()

    # Send the data back to whoever called this function
    return result.get('values', [])

def write(rng, values, sheets_service=_sheets_service, spreadsheet_id=None):
    """Write data into the spreadsheet."""

    # Get the default spreadsheet ID if it's not provided
    # (Do this instead of setting the default in the kwargs so that a user
    # can import gsheet;SPREADSHEET_ID = 'whatever'.
    if spreadsheet_id is None:
        spreadsheet_id = SPREADSHEET_ID

    # This variable collects all of the edits to make in one dict
    # This function only makes one edit at a time
    body = {'values': values}

    # Request that Google Sheets to make the edit
    # The `result` object tells us what Sheets actually did
    result = sheets_service.values().append(
            spreadsheetId=spreadsheet_id,
            range=rng, # search for a table to append to in this range
            valueInputOption='USER_ENTERED', # Sheets parses input. not RAW
            body=body,
            insertDataOption='INSERT_ROWS' # rather than overwriting
        ).execute()

    # Tell whoever called this function a summary of the result
    return '{0} cells appended to {1}.'.format(
            result.get('updates').get('updatedCells'),
            spreadsheet_id
            )
