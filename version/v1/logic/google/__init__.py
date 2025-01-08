from google.oauth2.service_account import Credentials

from src.utils.constants import DATA_DIR

def get_creds() -> Credentials:
    creds = Credentials.from_service_account_file(DATA_DIR / 'google_api.json')
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped