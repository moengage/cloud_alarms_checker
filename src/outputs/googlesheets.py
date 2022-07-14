import json
import gspread

from google.oauth2.service_account import Credentials
from cloud.aws.utils.secret import AWSSecretStoreSecret

class GoogleSpreadsheetWriter:

    '''
        This class is uded to create a google spreadsheet and used to fill all required info in that
    '''

    def get_google_client(self, inputs):
        
        '''
            This is used to connect to google apis to create the blank spreadsheet
        '''

        scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]

        # Fetching the google account secrets from the AWS Secret Store
        if inputs['useAwsSecretManager'] == True:

            credentials_info = AWSSecretStoreSecret( 'gsheets_service_account_credentials', 'ap-southeast-1').get()
            credentials_info = json.loads( credentials_info)['gsheets_service_account_credentials']
        else:
            credentials_info = json.loads(inputs['credentialsInfo'])

        credentials = Credentials.from_service_account_info(
            json.loads(credentials_info), scopes=scopes)
        
        # Creating the google client after authorizing based on the credentials obtained above
        google_client = gspread.authorize(credentials)
        return google_client

    def create_spreadsheet(self, spreadsheet_name, inputs):
        
        '''
            This will create a empty google spreadsheet.
        '''

        # Creating a google client to authorize from the google server.
        google_client = self.get_google_client(inputs)

        # Creating an emoty spreadsheet
        self.spreadsheet = google_client.create(spreadsheet_name)

        #  Obtaining the sheet Url
        self.sheet_url = ( 'https://docs.google.com/spreadsheets/d/%s' % self.spreadsheet.id)
        print('Google spreadsheet link is : \n%s' % self.sheet_url)

        # Setting up the sharing permission.
        self.spreadsheet.share( inputs['sharing']['reader'], perm_type='domain', role='reader', notify=False)
        self.spreadsheet.share( inputs['sharing']['writer'], perm_type='group', role='writer', notify=False)

    def create_sheet(self, sheet_name, header_row):

        '''
            Filling the basic information in the spreadsheet like the title, header row fields etc.
        '''

        worksheet = self.spreadsheet.add_worksheet( title=sheet_name, rows=0, cols=0)
        worksheet.append_row(header_row, value_input_option='USER_ENTERED')
        worksheet.format("1", {"textFormat": {"bold": True}})
        worksheet.freeze(1, 1)

        return worksheet

    def autoresize_spreadsheet(self):
        '''
            This is used to autoresize the blocks in sheet based on the size/length of contents
        '''

        requests = []

        for worksheet in self.spreadsheet.worksheets():

            n_rows = len(worksheet.row_values(1))

            requests.append({
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": n_rows
                    }
                }
            })

        if requests:
            
            body = {
                "requests": requests,
            }
            self.spreadsheet.batch_update(body)