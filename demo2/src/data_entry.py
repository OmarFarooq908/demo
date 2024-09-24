import openpyxl  # type: ignore # Use gspread for Google Sheets

def populate_spreadsheet(data):
    # Load or create a workbook
    try:
        wb = openpyxl.load_workbook('email_data.xlsx')
    except FileNotFoundError:
        wb = openpyxl.Workbook()

    ws = wb.active
    ws.append([data["network upgrades"], data["change IDs"], data["device statuses"]])

    wb.save('email_data.xlsx')
