import pandas as pd
import gspread
import os
import base64


def write_to_google_sheets(dataframe: pd.DataFrame, sheet_name: str) -> None:
    """Write the dataframe to the google sheets"""
    # read secrets base64 encoded string
    creds = os.getenv("GSHEETS")
    if creds:
        decoded_creds = base64.b64decode(creds).decode("utf-8")
        with open("plagesquebec.json", "w") as f:
            f.write(decoded_creds)

    try:
        gc = gspread.service_account(filename="plagesquebec.json")
        worksheet = gc.open(sheet_name).sheet1
        worksheet.update(
            [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        )
    except Exception as e:
        print(f"Error writing to google sheets: {e}")
