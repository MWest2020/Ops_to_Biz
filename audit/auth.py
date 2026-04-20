"""
Google Workspace authenticatie via service account.

Scope-strategie (least privilege):
  - drive.readonly  : documenten lezen uit Drive
  - drive.file      : alleen bestanden schrijven die de app zelf aanmaakt
  - documents       : Google Docs lezen en schrijven
  - spreadsheets    : Google Sheets lezen en schrijven
  - presentations   : Google Slides aanmaken
  - gmail.send      : e-mail versturen
  - calendar        : Calendar-uitnodigingen aanmaken

De echte toegangsmuur is het Drive-deelbeleid:
  share het service account UITSLUITEND met de "Interne Audits"-map.
  Bestanden buiten die map zijn voor het account simpelweg onzichtbaar.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Lezen: alleen de Drive-map die expliciet gedeeld is met het service account
_READ_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]

# Schrijven: alleen bestanden die de app zelf aanmaakt (drive.file)
_WRITE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]


def _get_credentials(scopes: list[str]):
    creds_file = os.environ.get("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE")
    if not creds_file:
        raise EnvironmentError(
            "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE niet ingesteld in .env"
        )
    return service_account.Credentials.from_service_account_file(
        creds_file, scopes=scopes
    )


def drive_read_service():
    """Drive-service met alleen leesrechten."""
    return build("drive", "v3", credentials=_get_credentials(_READ_SCOPES))


def drive_write_service():
    """Drive-service voor aanmaken van bestanden (drive.file scope)."""
    return build("drive", "v3", credentials=_get_credentials(_WRITE_SCOPES))


def docs_read_service():
    return build("docs", "v1", credentials=_get_credentials(_READ_SCOPES))


def docs_write_service():
    return build("docs", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def sheets_service():
    return build("sheets", "v4", credentials=_get_credentials(_WRITE_SCOPES))


def slides_service():
    return build("slides", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def gmail_service():
    return build("gmail", "v1", credentials=_get_credentials(_WRITE_SCOPES))


def calendar_service():
    return build("calendar", "v3", credentials=_get_credentials(_WRITE_SCOPES))
