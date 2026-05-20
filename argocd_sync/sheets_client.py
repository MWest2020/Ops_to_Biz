"""Google Sheets client for argocd_sync — direct Sheets API via service
account, replacing the third-party `gws` CLI on the timer path so daily
runs don't need interactive browser auth.

Required env (set in .env, loaded by systemd via EnvironmentFile):
  GOOGLE_SERVICE_ACCOUNT_FILE             path to the SA JSON key
  GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE   legacy alias for the same path
  GOOGLE_IMPERSONATE_USER                 email to impersonate (DWD)
"""

import os
from functools import lru_cache

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _sa_path() -> str:
    p = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE") or os.environ.get(
        "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"
    )
    if not p:
        raise EnvironmentError(
            "Sheets output requires a service account. Set "
            "GOOGLE_SERVICE_ACCOUNT_FILE (preferred) or "
            "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE in .env."
        )
    if not os.path.exists(p):
        raise FileNotFoundError(f"Service account JSON not found at: {p}")
    return p


def _impersonate() -> str:
    user = os.environ.get("GOOGLE_IMPERSONATE_USER")
    if not user:
        raise EnvironmentError(
            "Sheets output requires GOOGLE_IMPERSONATE_USER in .env "
            "(domain-wide delegation target email)."
        )
    return user


@lru_cache(maxsize=1)
def _credentials():
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        _sa_path(), scopes=SCOPES
    )
    return creds.with_subject(_impersonate())


@lru_cache(maxsize=1)
def _service():
    from googleapiclient.discovery import build
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def get_values(spreadsheet_id: str, range_a1: str) -> list[list]:
    result = _service().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_a1
    ).execute()
    return result.get("values", [])


def ensure_tab(spreadsheet_id: str, tab_name: str) -> None:
    meta = _service().spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets.properties.title"
    ).execute()
    titles = [s["properties"]["title"] for s in meta.get("sheets", [])]
    if tab_name in titles:
        return
    _service().spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
    ).execute()
    print(f"[sheets_client] Created tab '{tab_name}'")


def clear_range(spreadsheet_id: str, range_a1: str) -> None:
    _service().spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=range_a1, body={}
    ).execute()


def batch_update_values(
    spreadsheet_id: str,
    data: list[dict],
    value_input_option: str = "RAW",
) -> None:
    _service().spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": value_input_option, "data": data},
    ).execute()


def col_letter(n: int) -> str:
    """Convert 1-based column number to A1 letter (e.g. 27 → AA)."""
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
