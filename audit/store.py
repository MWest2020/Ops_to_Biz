"""
Lokale SQLite opslag voor audit-landschap.

Schema:
  documents      — Drive-bestanden met volledige tekst
  miro_notes     — Miro sticky notes / tekstvakken
  clause_matches — welke documenten matchen welke clausules
  ingest_log     — wanneer is welke bron voor het laatst gesynchroniseerd
  interviews     — handmatige bevindingen per clausule (NC/OFI/positief)

FTS5 full-text search op documents.naam + documents.tekst zodat
je in Claude Code direct kunt zoeken zonder API-kosten.
"""

import logging
import os
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "output", "audit.db"
)


def db_pad() -> str:
    return os.environ.get("AUDIT_DB_PATH", DEFAULT_DB_PATH)


def verbinding(pad: str | None = None) -> sqlite3.Connection:
    pad = pad or db_pad()
    os.makedirs(os.path.dirname(pad), exist_ok=True)
    conn = sqlite3.connect(pad)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialiseer(conn: sqlite3.Connection) -> None:
    """Maak alle tabellen aan als ze nog niet bestaan."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id          TEXT PRIMARY KEY,
            naam        TEXT NOT NULL,
            tekst       TEXT NOT NULL DEFAULT '',
            herkomst    TEXT NOT NULL DEFAULT 'Drive',
            mime_type   TEXT,
            modified_at TEXT,           -- Drive modifiedTime (ISO 8601), NULL als onbekend
            ingested_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS miro_notes (
            id                TEXT PRIMARY KEY,
            tekst             TEXT NOT NULL,
            kleur             TEXT,
            pre_classificatie TEXT,
            board_id          TEXT,
            ingested_at       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clause_matches (
            doc_id      TEXT NOT NULL,
            herkomst    TEXT NOT NULL,   -- 'Drive' | 'Miro'
            clausule_id TEXT NOT NULL,
            norm        TEXT NOT NULL,
            sub_punt    TEXT NOT NULL DEFAULT '',  -- '' = clausule-niveau, 'a'/'b'/... = sub-punt
            PRIMARY KEY (doc_id, herkomst, clausule_id, sub_punt)
        );

        CREATE TABLE IF NOT EXISTS ingest_log (
            bron        TEXT PRIMARY KEY,  -- 'drive' | 'miro'
            folder_id   TEXT,
            bestand_count INTEGER,
            last_run    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bevindingen (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id           TEXT NOT NULL,
            herkomst         TEXT NOT NULL,
            clausule_id      TEXT NOT NULL,
            norm             TEXT NOT NULL,
            classificatie    TEXT NOT NULL,
            beschrijving     TEXT,
            onderbouwing     TEXT,
            pre_classificatie TEXT,
            document_naam    TEXT,
            classified_at    TEXT NOT NULL,
            UNIQUE(doc_id, herkomst, clausule_id, norm)
        );

        CREATE TABLE IF NOT EXISTS interviews (
            clausule_id    TEXT NOT NULL,
            norm           TEXT NOT NULL,
            bevinding      TEXT NOT NULL,  -- 'NC' | 'OFI' | 'positief' | 'overgeslagen'
            antwoord       TEXT,           -- korte ja/nee/deels samenvatting
            notitie        TEXT,           -- vrije toelichting van de auditor
            interviewed_at TEXT NOT NULL,
            PRIMARY KEY (clausule_id, norm)
        );

        -- FTS5 full-text search over naam + tekst
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(naam, tekst, content=documents, content_rowid=rowid);

        -- FTS triggers to keep index in sync
        CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
            INSERT INTO documents_fts(rowid, naam, tekst)
            VALUES (new.rowid, new.naam, new.tekst);
        END;

        CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, naam, tekst)
            VALUES ('delete', old.rowid, old.naam, old.tekst);
        END;

        CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, naam, tekst)
            VALUES ('delete', old.rowid, old.naam, old.tekst);
            INSERT INTO documents_fts(rowid, naam, tekst)
            VALUES (new.rowid, new.naam, new.tekst);
        END;
    """)
    conn.commit()


def upsert_document(conn: sqlite3.Connection, doc: dict) -> None:
    conn.execute("""
        INSERT INTO documents (id, naam, tekst, herkomst, mime_type, modified_at, ingested_at)
        VALUES (:id, :naam, :tekst, :herkomst, :mime_type, :modified_at, :ingested_at)
        ON CONFLICT(id) DO UPDATE SET
            naam        = excluded.naam,
            tekst       = excluded.tekst,
            herkomst    = excluded.herkomst,
            mime_type   = excluded.mime_type,
            modified_at = COALESCE(excluded.modified_at, modified_at),
            ingested_at = excluded.ingested_at
    """, {
        "id": doc["id"],
        "naam": doc["naam"],
        "tekst": doc.get("tekst", ""),
        "herkomst": doc.get("herkomst", "Drive"),
        "mime_type": doc.get("mime_type"),
        "modified_at": doc.get("modified_at"),
        "ingested_at": now(),
    })


def upsert_miro_note(conn: sqlite3.Connection, note: dict) -> None:
    conn.execute("""
        INSERT INTO miro_notes (id, tekst, kleur, pre_classificatie, board_id, ingested_at)
        VALUES (:id, :tekst, :kleur, :pre_classificatie, :board_id, :ingested_at)
        ON CONFLICT(id) DO UPDATE SET
            tekst             = excluded.tekst,
            kleur             = excluded.kleur,
            pre_classificatie = excluded.pre_classificatie,
            ingested_at       = excluded.ingested_at
    """, {
        "id": note["miro_item_id"],
        "tekst": note["tekst"],
        "kleur": note.get("kleur"),
        "pre_classificatie": note.get("pre_classificatie"),
        "board_id": note.get("board_id"),
        "ingested_at": now(),
    })


def upsert_clause_match(
    conn: sqlite3.Connection,
    doc_id: str,
    herkomst: str,
    clausule_id: str,
    norm: str,
    sub_punt: str = "",
) -> None:
    conn.execute("""
        INSERT OR IGNORE INTO clause_matches (doc_id, herkomst, clausule_id, norm, sub_punt)
        VALUES (?, ?, ?, ?, ?)
    """, (doc_id, herkomst, clausule_id, norm, sub_punt or ""))


def log_ingest(conn: sqlite3.Connection, bron: str, folder_id: str | None, count: int) -> None:
    conn.execute("""
        INSERT INTO ingest_log (bron, folder_id, bestand_count, last_run)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(bron) DO UPDATE SET
            folder_id     = excluded.folder_id,
            bestand_count = excluded.bestand_count,
            last_run      = excluded.last_run
    """, (bron, folder_id, count, now()))
    conn.commit()


def zoek(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[sqlite3.Row]:
    """Full-text search over document namen en inhoud."""
    return conn.execute("""
        SELECT d.id, d.naam, d.herkomst, d.mime_type,
               snippet(documents_fts, 1, '[', ']', '...', 20) AS fragment
        FROM documents_fts f
        JOIN documents d ON d.rowid = f.rowid
        WHERE documents_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit)).fetchall()


def upsert_interview(
    conn: sqlite3.Connection,
    clausule_id: str,
    norm: str,
    bevinding: str,
    antwoord: str | None = None,
    notitie: str | None = None,
) -> None:
    conn.execute("""
        INSERT INTO interviews (clausule_id, norm, bevinding, antwoord, notitie, interviewed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(clausule_id, norm) DO UPDATE SET
            bevinding      = excluded.bevinding,
            antwoord       = excluded.antwoord,
            notitie        = excluded.notitie,
            interviewed_at = excluded.interviewed_at
    """, (clausule_id, norm, bevinding, antwoord, notitie, now()))


def laad_interviews(conn: sqlite3.Connection, norm: str | None = None) -> list[sqlite3.Row]:
    if norm:
        return conn.execute(
            "SELECT * FROM interviews WHERE norm = ? ORDER BY clausule_id", (norm,)
        ).fetchall()
    return conn.execute("SELECT * FROM interviews ORDER BY clausule_id").fetchall()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
