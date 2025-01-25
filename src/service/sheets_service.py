from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import polars as pl

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_PATH = ".token.pickle"


class SheetsService:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = self._get_service()

    def _get_credentials(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def _get_service(self):
        creds = self._get_credentials()
        return build("sheets", "v4", credentials=creds)

    def append_dataframe(self, df: pl.DataFrame, sheet_range: str):
        """
        Append DataFrame to Google Sheet with deduplication.

        Args:
            df: DataFrame to append
            sheet_range: Range in A1 notation (e.g., 'Sheet1!A:E')
        """
        # Get existing data
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=sheet_range)
            .execute()
        )
        existing_data = result.get("values", [])

        # Convert existing data to DataFrame
        if existing_data:
            headers = existing_data[0]
            existing_df = pl.DataFrame(
                existing_data[1:], schema={col: str for col in headers}
            )
        else:
            existing_df = pl.DataFrame()

        # If sheet is empty, write headers and all data
        if existing_df.empty:
            values = [df.columns.tolist()] + df.values.tolist()
            body = {"values": values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                valueInputOption="RAW",
                body=body,
            ).execute()
            return

        # Deduplicate based on issue_key
        merged_df = pl.concat([existing_df, df]).unique(
            subset=["issue_key"], keep="last"
        )

        # Clear existing content
        self.service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id, range=sheet_range
        ).execute()

        # Write deduplicated data
        values = [merged_df.columns.tolist()] + merged_df.values.tolist()
        body = {"values": values}
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body=body,
        ).execute()
