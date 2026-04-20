"""
Google Service Account client — vervangt gws CLI voor onbeheerde runs.

Gebruikt google-auth + google-api-python-client met een service account
en domain-wide delegation. Geen browser, geen token-expiry, geen gws auth login.

Configuratie via .env:
  GOOGLE_SERVICE_ACCOUNT_FILE   pad naar service account JSON
  GOOGLE_IMPERSONATE_USER       e-mail van de te impersoneren gebruiker

Valt automatisch terug op gws CLI als service account niet geconfigureerd is.
"""

import logging
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

_SA_FILE = None
_IMPERSONATE = None


def _sa_beschikbaar() -> bool:
    global _SA_FILE, _IMPERSONATE
    _SA_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    _IMPERSONATE = os.environ.get("GOOGLE_IMPERSONATE_USER")
    return bool(_SA_FILE and _IMPERSONATE and os.path.exists(_SA_FILE))


@lru_cache(maxsize=1)
def _credentials():
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        _SA_FILE, scopes=SCOPES
    )
    return creds.with_subject(_IMPERSONATE)


@lru_cache(maxsize=1)
def drive_service():
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


@lru_cache(maxsize=1)
def sheets_service():
    from googleapiclient.discovery import build
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


# ── Drive ─────────────────────────────────────────────────────────────────────

def lijst_bestanden(folder_id: str) -> list[dict]:
    """
    Geeft alle bestanden in een Drive-map (inclusief Shared Drive).
    Retourneert lijst van {id, name, mimeType}.
    """
    if not _sa_beschikbaar():
        return _lijst_bestanden_gws(folder_id)

    svc = drive_service()
    items = []
    page_token = None
    is_shared_drive = folder_id.startswith("0A")

    while True:
        kwargs = dict(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=200,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        if is_shared_drive:
            kwargs["corpora"] = "drive"
            kwargs["driveId"] = folder_id
        if page_token:
            kwargs["pageToken"] = page_token

        result = svc.files().list(**kwargs).execute()
        items.extend(result.get("files", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return items


def exporteer_google_doc(file_id: str) -> str:
    """Exporteer Google Doc als plain text."""
    if not _sa_beschikbaar():
        from audit.gws_client import gws_exporteer_google_doc
        return gws_exporteer_google_doc(file_id)

    svc = drive_service()
    data = svc.files().export(fileId=file_id, mimeType="text/plain").execute()
    return data.decode("utf-8") if isinstance(data, bytes) else data


def download_bestand(file_id: str) -> bytes:
    """Download binair bestand (docx, pdf, etc.)."""
    if not _sa_beschikbaar():
        from audit.gws_client import gws_download_bestand
        return gws_download_bestand(file_id)

    import io
    from googleapiclient.http import MediaIoBaseDownload
    svc = drive_service()
    request = svc.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


# ── Sheets ────────────────────────────────────────────────────────────────────

def lees_sheet(spreadsheet_id: str, bereik: str = None) -> list[list]:
    """
    Leest een bereik uit een Google Sheet.
    Geeft list of lists terug (rijen × kolommen).
    bereik=None leest het eerste blad volledig.
    """
    if not _sa_beschikbaar():
        return _lees_sheet_gws(spreadsheet_id, bereik)

    svc = sheets_service()
    if bereik:
        result = svc.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=bereik
        ).execute()
    else:
        result = svc.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range="A1:ZZ10000"
        ).execute()
    return result.get("values", [])


def lees_alle_tabs(spreadsheet_id: str) -> dict[str, list[list]]:
    """
    Leest alle tabs van een spreadsheet.
    Geeft dict {tabnaam: [[rij], ...]} terug.
    """
    if not _sa_beschikbaar():
        return _lees_alle_tabs_gws(spreadsheet_id)

    svc = sheets_service()
    meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    tabs = {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in meta.get("sheets", [])
    }

    resultaat = {}
    for tab_naam in tabs:
        try:
            waarden = lees_sheet(spreadsheet_id, f"'{tab_naam}'!A1:ZZ10000")
            resultaat[tab_naam] = waarden
            logger.info("Tab '%s': %d rijen", tab_naam, len(waarden))
        except Exception as e:
            logger.warning("Tab '%s' overgeslagen: %s", tab_naam, e)

    return resultaat


def schrijf_sheet(spreadsheet_id: str, bereik: str, waarden: list[list]) -> None:
    """Schrijf waarden naar een bereik in een Google Sheet."""
    if not _sa_beschikbaar():
        raise EnvironmentError(
            "Sheets schrijven vereist service account. "
            "Configureer GOOGLE_SERVICE_ACCOUNT_FILE in .env"
        )
    svc = sheets_service()
    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=bereik,
        valueInputOption="USER_ENTERED",
        body={"values": waarden},
    ).execute()


# ── gws fallbacks ─────────────────────────────────────────────────────────────

def _lijst_bestanden_gws(folder_id: str) -> list[dict]:
    from audit.gws_client import gws_lijst_bestanden
    items = gws_lijst_bestanden(folder_id)
    return [{"id": i["id"], "name": i["naam"], "mimeType": i.get("mime_type", "")} for i in items]


def _lees_sheet_gws(spreadsheet_id: str, bereik: str) -> list[list]:
    import subprocess, json
    range_param = bereik or "A1:ZZ10000"
    result = subprocess.run(
        ["gws", "sheets", "spreadsheets", "values", "get",
         "--params", json.dumps({"spreadsheetId": spreadsheet_id, "range": range_param})],
        capture_output=True, text=True, timeout=60,
    )
    data = json.loads(result.stdout)
    if "error" in data:
        raise RuntimeError(f"Sheets fout: {data['error']}")
    return data.get("values", [])


def _lees_alle_tabs_gws(spreadsheet_id: str) -> dict[str, list[list]]:
    import subprocess, json
    result = subprocess.run(
        ["gws", "sheets", "spreadsheets", "get",
         "--params", json.dumps({"spreadsheetId": spreadsheet_id})],
        capture_output=True, text=True, timeout=30,
    )
    data = json.loads(result.stdout)
    if "error" in data:
        raise RuntimeError(f"Sheets fout: {data['error']}")
    tabs = [s["properties"]["title"] for s in data.get("sheets", [])]
    resultaat = {}
    for tab in tabs:
        try:
            resultaat[tab] = _lees_sheet_gws(spreadsheet_id, f"'{tab}'!A1:AZ500")
            logger.info("Tab '%s': %d rijen", tab, len(resultaat[tab]))
        except Exception as e:
            logger.warning("Tab '%s' overgeslagen: %s", tab, e)
    return resultaat


# ── Test ──────────────────────────────────────────────────────────────────────

def test_verbinding() -> None:
    folder_id = os.environ.get("AUDIT_SOURCE_FOLDER_ID", "").split("?")[0]
    if _sa_beschikbaar():
        logger.info("Service account actief: %s → %s", _SA_FILE, _IMPERSONATE)
        bestanden = lijst_bestanden(folder_id)
        print(f"Drive: OK — {len(bestanden)} bestanden gevonden")
    else:
        logger.warning(
            "Service account niet geconfigureerd. "
            "Zie docs/service_account_setup.md"
        )
        print("Service account: NIET geconfigureerd — gws fallback actief")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_verbinding()
