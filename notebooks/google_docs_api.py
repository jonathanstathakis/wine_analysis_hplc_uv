"""
A very simple Google Sheets API interface for pulling tabular data values, creating new sheets and uploading values from dataframes.

Note: currently note built with any tests.

Example Workflow:

1. Get the spreadsheet ID from the second last part of the spreadsheet URL.
2. Get path to downloaded certificate. If first time running, generate a token.
3. Use get_sheets_values_as_df to get values from desired sheet.
4. Do stuff
5. Make a new sheet to upload changes to with post_new_sheet
6. Upload stuff done to new sheet with post_df_as_sheet_values

Note: A Google spreadsheet is made up of many sheets. This fact may help you conceptualise how the REST API works.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

import pandas as pd

def get_credentials(creds_parent_path : str):
    """gets the credientials for the google sheets API
    """
    creds = None

    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    path_to_token = f'{creds_parent_path}/token_sheets.json'

    path_to_credentials = f'{creds_parent_path}credentials_sheets.json'

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(path_to_token):
        creds = Credentials.from_authorized_user_file(path_to_token, scopes)
    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path_to_credentials, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(path_to_token, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_sheets_service(creds_parent_path : str):
    
    creds = get_credentials(creds_parent_path)

    service = build('sheets', 'v4', credentials = creds)

    return service

def get_sheets_values_as_df(spreadsheet_id : str, range : str, creds_parent_path : str):
    
    service = get_sheets_service(creds_parent_path)

    sheets_api = service.spreadsheets()

    values = sheets_api.values().get(spreadsheetId = spreadsheet_id, range = range).execute().get('values')

    # values are of shape row, col where each element of the values list is a row that contains its column values.

    values_df = pd.DataFrame(values[1:], columns = values[0])

    return values_df

def post_new_sheet(spreadsheet_id : str, sheet_title : str, creds_parent_path):

    """
    Make a new sheet in a given spreadsheet. Returns the response dict.
    """

    service = get_sheets_service(creds_parent_path)

    sheet_body = {
    'requests': [{
        'addSheet': {
            'properties': {
                'title': str(sheet_title)
            }
        }
    }]
    }
    
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=sheet_body).execute()

    return response

def post_df_as_sheet_values(df : pd.DataFrame, spreadsheet_id : str, range : str, creds_parent_path : str):

    service = get_sheets_service(creds_parent_path)

    """
    upload a given df to a specified sheet. Returns the response dict. Range should include the sheet title in the format "sheet_title!A1"
    """

    # 73 here, including column. Lost it earlier.
    data = df.astype(str).values.tolist()

    columns = df.columns.tolist()

    data = [columns] + data

    data_body = {
    'range': range,
    'majorDimension': 'ROWS',
    'values': data
    }

    response = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                          range=data_body['range'],
                                                          valueInputOption='USER_ENTERED',
                                                          body=data_body).execute()

    return response