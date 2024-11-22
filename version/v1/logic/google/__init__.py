from google.oauth2.service_account import Credentials

from src.config import settings

def get_creds() -> Credentials:
    creds = Credentials.from_service_account_info(settings.GOOGLE_CREDS)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped