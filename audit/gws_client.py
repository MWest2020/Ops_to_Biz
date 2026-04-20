"""
Gedeelde gws CLI-wrapper voor de audit pipeline.

Alle Google Workspace API-aanroepen gaan via de `gws` CLI zodat
de OAuth2-sessie van de gebruiker gebruikt wordt (geen service account nodig).
"""

import json
import logging
import os
import subprocess
import tempfile
import time

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


def _gws(*args, body: dict | None = None, params: dict | None = None) -> dict:
    """
    Voer een gws-subcommando uit en retourneer geparseerde JSON.

    Positional args worden direct doorgegeven: bv.
      _gws("drive", "files", "list", params={"q": "..."})
    """
    cmd = ["gws"] + list(args)
    if params:
        cmd += ["--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]

    wacht = 1
    for poging in range(_MAX_RETRIES + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except subprocess.CalledProcessError as e:
            # gws schrijft foutdetails naar stderr
            stderr = e.stderr or ""
            if ("429" in stderr or "503" in stderr or "rateLimitExceeded" in stderr) \
                    and poging < _MAX_RETRIES:
                wacht = min(wacht * 2, 30)
                logger.warning("Rate limit (poging %d) — wacht %ds", poging + 1, wacht)
                time.sleep(wacht)
            else:
                raise


def _gws_binary(*args, params: dict | None = None, suffix: str = ".bin") -> bytes:
    """
    Voer een gws-subcommando uit dat binaire output retourneert.
    Schrijft naar een tijdelijk bestand en retourneert de bytes.
    """
    cmd = ["gws"] + list(args)
    if params:
        cmd += ["--params", json.dumps(params)]

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        tmp_path = f.name
    try:
        wacht = 1
        for poging in range(_MAX_RETRIES + 1):
            try:
                subprocess.run(cmd + ["-o", tmp_path], check=True, capture_output=True)
                break
            except subprocess.CalledProcessError as e:
                stderr = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
                if ("429" in stderr or "503" in stderr) and poging < _MAX_RETRIES:
                    wacht = min(wacht * 2, 30)
                    logger.warning("Rate limit (poging %d) — wacht %ds", poging + 1, wacht)
                    time.sleep(wacht)
                else:
                    raise
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def gws_lijst_bestanden(folder_id: str, drive_id: str | None = None) -> list[dict]:
    """
    Haal recursief alle bestanden op uit folder_id via gws drive files list.
    Ondersteunt zowel reguliere Drive-mappen als Shared Drives (0A... IDs).
    Retourneert [{id, name, mimeType}, ...].
    """
    alle = []
    page_token = None

    while True:
        params: dict = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "nextPageToken, files(id, name, mimeType, modifiedTime)",
            "pageSize": 100,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
        }
        if drive_id:
            params["corpora"] = "drive"
            params["driveId"] = drive_id
        if page_token:
            params["pageToken"] = page_token

        result = _gws("drive", "files", "list", params=params)
        bestanden = result.get("files", [])

        for bestand in bestanden:
            if bestand["mimeType"] == "application/vnd.google-apps.folder":
                alle.extend(gws_lijst_bestanden(bestand["id"], drive_id=drive_id))
            else:
                alle.append(bestand)

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return alle


def gws_exporteer_google_doc(file_id: str) -> str:
    """Exporteer een Google Doc als plain text via gws drive files export."""
    inhoud = _gws_binary(
        "drive", "files", "export",
        params={"fileId": file_id, "mimeType": "text/plain", "supportsAllDrives": True},
        suffix=".txt",
    )
    return inhoud.decode("utf-8", errors="replace")


def gws_download_bestand(file_id: str) -> bytes:
    """
    Download een bestand via gws drive files get met alt=media.
    Werkt voor .docx, .txt en andere niet-Google-native formaten.
    """
    return _gws_binary(
        "drive", "files", "get",
        params={"fileId": file_id, "alt": "media", "supportsAllDrives": True},
    )
