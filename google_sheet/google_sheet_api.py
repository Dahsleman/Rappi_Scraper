# The ID and range of a sample spreadsheet.
from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

from input_settings import InputSettings

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetApi:
    @staticmethod
    def get_google_service(second_try = False):
        print('GETTING GOOGLE SHEET API TOKEN')

        try:
            """Shows basic usage of the Sheets API.
            Prints values from a sample spreadsheet.
            """
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('./google_sheet/token.json'):
                creds = Credentials.from_authorized_user_file('./google_sheet/token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token and not second_try:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        './google_sheet/credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('./google_sheet/token.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('sheets', 'v4', credentials=creds)
            return service
        except RefreshError:
            if not second_try:
                return GoogleSheetApi.get_google_service(True)
            else:
                print('invalid_grant: Token has been expired or revoked.')
                return None
        except HttpError as err:
            print(err)
            return None

    def get_sheet_id(sheet, spread_sheet_id, sheet_name):
        sheets = sheet.get(spreadsheetId=spread_sheet_id).execute()['sheets']
        sheet_id = 0
        for st in sheets:
            if st['properties']['title'] == sheet_name:
                return st['properties']['sheetId']
        
        return None

    @staticmethod
    def update_sheet_api(service, spread_sheet_id, sheet_name, values, is_address = False):
        
        if len(values) == 0:
            return
        
        # Call the Sheets API
        sheet = service.spreadsheets()
        sheet_id = GoogleSheetApi.get_sheet_id(sheet, spread_sheet_id, sheet_name)

        try:
            result = sheet.values().get(spreadsheetId=spread_sheet_id, range=sheet_name).execute()
            _values = result.get('values', [])
            last_index = len(_values)
        except:
            print('Creating Sheet ', sheet_name)
            body = {
                "requests":[{
                    "addSheet":{
                        "properties":{
                            "title": sheet_name,
                            'gridProperties': {
                                'rowCount': 1,
                            },
                        }
                    }
                }]
            }
            try:
                result = service.spreadsheets().batchUpdate(spreadsheetId=spread_sheet_id, body=body).execute()
                sheet_id = GoogleSheetApi.get_sheet_id(sheet, spread_sheet_id, sheet_name)
            except:
                print('Use a sheet from komprk4@gmail.com account.')
                return
            last_index = 1

        if last_index == 0 and not is_address:
            last_index = 1
        elif is_address:
            last_index = 0

        data = []

        if sheet_name == "Products" or sheet_name == "Address" or sheet_name == 'Erros': 
            header = InputSettings.EXCEL_HEADER
        else:
            header = list(values[0].keys())

        header_len = len(header)
        last_column = GoogleSheetApi.list_length_to_column_index(header_len)

        data.append({
            'range': f'{sheet_name}!A1:{last_column}',
            'values': [header]
            })
        
        for i, value in enumerate(values):
            data.append({
                'range': f'{sheet_name}!A{i + 1 + last_index}:{last_column}{i + 1 + last_index}',
                'values': [list(value.values())]
            })
        
        batch_sheet_update_request = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {
                                'rowCount': last_index + len(data) - 1,
                            },
                        },
                        "fields" : "gridProperties(rowCount)"
                    }
                }
            ],
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spread_sheet_id,
            body=batch_sheet_update_request
        ).execute()
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spread_sheet_id,
            body={
                'valueInputOption': "USER_ENTERED",
                'data': data
            }
        ).execute()

    @staticmethod
    def list_length_to_column_index(length):
        if length <= 0:
            raise ValueError("Input length must be greater than 0")
        
        column_index = length - 1
        result = ""
        
        while column_index >= 0:
            remainder = column_index % 26
            result = chr(65 + remainder) + result
            column_index = column_index // 26 - 1
        
        return result

    @staticmethod
    def convertProductsInvalidValuesToValid(products_dict_list:dict)->list:
        new_products_dict_list = []
        for products_dict in products_dict_list:
            new_products_dict = {}
            for key, value in products_dict.items():
                if value == None:
                    value = 'NULL'
                if value == "":
                    value = 'EMPTY'
                new_value = str(value)
                new_value = new_value.replace("\n", "")
                new_products_dict[key] = new_value
            new_products_dict_list.append(new_products_dict)  

        return new_products_dict_list  

    @staticmethod
    def update_google_sheet(products_list, clientDetails, error_list = None):
        if "__SPREADSHEET_ID__" not in clientDetails or clientDetails["__SPREADSHEET_ID__"] == "":
            print ('__SPREADSHEET_ID__ not configured')
            return
        
        address = clientDetails["__ADDRESS__"]
        g_sheet_id = clientDetails["__SPREADSHEET_ID__"]

        service = GoogleSheetApi.get_google_service()

        if service is None:
            print('Fail to generate token')
            return

        # Products Sheet
        print('UPLOADING PRODUCTS SHEET TO GOOGLE SHEET')
        if error_list is not None:
            new_products_list = GoogleSheetApi.convertProductsInvalidValuesToValid(products_list)
            GoogleSheetApi.update_sheet_api(service, g_sheet_id, "Products", new_products_list)

            ## Erros Sheet
            GoogleSheetApi.update_sheet_api(service, g_sheet_id, "Erros", error_list)
        else:
            new_products_list = GoogleSheetApi.convertProductsInvalidValuesToValid(products_list)
            GoogleSheetApi.update_sheet_api(service, g_sheet_id, "MVP", new_products_list)

        ## Address Sheet
        GoogleSheetApi.update_sheet_api(service, g_sheet_id, "Address", [{ "Address": address }], True)