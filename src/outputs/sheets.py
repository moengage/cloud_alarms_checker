import datetime

from dateutil import tz

from outputs.googlesheets import GoogleSpreadsheetWriter
from outputs.writer import *

def create_sheets(cloud, env, inputs):

    # Creating Timezones details
    india_timezone = tz.gettz('Asia/Kolkata')
    date_str = datetime.datetime.today().astimezone( india_timezone).strftime('%d-%m-%Y %H:%M:%S %Z')
    
    if inputs['sheets']['googleSheets']['useSheets'] == True:
        spreadsheet_writer = GoogleSpreadsheetWriter()
        spreadsheet_writer.create_spreadsheet( 'Unmonitored {env} {cloud} resources on {date}'.format(env=env, cloud=cloud, date=date_str), inputs['sheets']['googleSheets'])

    else:
        print('Please add code for some other ouput medium')
        raise Exception("Please add code for some other ouput medium like CSV, DB etc")

    return spreadsheet_writer