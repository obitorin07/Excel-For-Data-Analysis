import gspread
from google.oauth2.service_account import Credentials
import config
import pandas  as pd

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_file(config.credential_api, scopes=scopes)

client = gspread.authorize(credentials)

print("Connected")

spread_sheet = client.open_by_key(config.sheet_credential)
print(spread_sheet.worksheet('Data_Automation'))


# print how many sheets are there :)
sheets =  spread_sheet.worksheets()
for names in sheets:
    print(names.title)
    
    
# i want to print the all the data inside data_automation
# here i took the data from specific sheet then i selected all the records
data = spread_sheet.worksheet('Data_Automation').get_all_records()

df = pd.DataFrame(data)
print(df.head())