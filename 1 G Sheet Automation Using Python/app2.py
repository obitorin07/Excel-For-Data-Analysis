
import gspread
import config
from google.oauth2.service_account import Credentials
from collections import Counter

# --------------------------------
# 1. AUTHENTICATION
# --------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

credentials = Credentials.from_service_account_file(
    config.credential_api,
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# --------------------------------
# 2. CONNECT TO SPREADSHEET
# --------------------------------

spreadsheet = client.open_by_key(
    config.sheet_credential
)

# --------------------------------
# 3. FETCH ALL SOURCE SHEETS
# --------------------------------

all_sheets = spreadsheet.worksheets()

master_data = []
headers = None

for sheet in all_sheets:

    # Ignore output worksheets during reruns
    if sheet.title in ["master_data", "_master_report"]:
        continue

    print("Fetching:", sheet.title)

    data = sheet.get_all_values()

    if not data:
        continue

    # First row contains column headers
    if headers is None:
        headers = data[0]

        if "report_date" not in headers:
            raise ValueError("report_date column not found!")

        master_data.append(headers)

    elif data[0] != headers:
        raise ValueError(
            f"Column mismatch in worksheet: {sheet.title}"
        )

    # Append records, excluding header
    master_data.extend(data[1:])


# --------------------------------
# 4. CREATE / UPDATE MASTER_DATA
# --------------------------------

try:
    master_sheet = spreadsheet.worksheet("master_data")
except gspread.WorksheetNotFound:
    master_sheet = spreadsheet.add_worksheet(
        title="master_data",
        rows=1000,
        cols=50
    )

master_sheet.clear()

if master_data:
    master_sheet.update(
        range_name="A1",
        values=master_data
    )

print("Master data created successfully!")


# --------------------------------
# 5. CREATE PIVOT REPORT
# --------------------------------

if headers:

    date_index = headers.index("report_date")

    report_dates = [
        row[date_index]
        for row in master_data[1:]
        if len(row) > date_index and row[date_index].strip()
    ]

    date_counts = Counter(report_dates)

    report_data = [
        ["report_date", "record_count"]
    ]

    for report_date, count in sorted(date_counts.items()):
        report_data.append([report_date, count])

    # Create or access report worksheet
    try:
        report_sheet = spreadsheet.worksheet("_master_report")
    except gspread.WorksheetNotFound:
        report_sheet = spreadsheet.add_worksheet(
            title="_master_report",
            rows=1000,
            cols=10
        )

    report_sheet.clear()

    report_sheet.update(
        range_name="A1",
        values=report_data
    )

    print("Pivot report created successfully!")

else:
    print("No source data found.")
