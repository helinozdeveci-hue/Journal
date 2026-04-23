import sqlite3
from pathlib import Path

db_path = Path("journal.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    # Enable dict-like access to rows
    conn.row_factory = sqlite3.Row 
    # Enable foreign key support
    conn.execute('PRAGMA foreign_keys = ON') 
    return conn

def init_db():
    # as long as the database file doesn't exist, it will be created when we connect to it. If it already exists, it will be opened.
    # connection to the database as conn
    with get_connection() as conn: 
        # The entries table has the following columns: id (primary key), date (text, not null), note (text), created_by (text)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                note TEXT,
                created_by TEXT
            );
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS entry_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                metric_id INTEGER NOT NULL,
                value INTEGER NOT NULL,
                FOREIGN KEY (entry_id) REFERENCES entries (id) ON DELETE CASCADE,
                FOREIGN KEY (metric_id) REFERENCES metrics (id) ON DELETE CASCADE,
                UNIQUE (entry_id, metric_id),
                CHECK (value BETWEEN 1 AND 5)
            );
        """)
        # commit the changes to the database
        conn.commit()

# entry has date, note, created_by 
def create_entry(date: str, note: str | None = None, created_by: str | None = None):
    with get_connection() as conn:
        # ? are placeholders for date, note, created_by 
        cursor = conn.execute("""
        INSERT INTO entries (date, note, created_by) 
        VALUES (?, ?, ?) 
        """, (date, note, created_by))
        conn.commit()
        # lastrowid gives unique auto-incrementing id's
        entry_id = cursor.lastrowid 
        return entry_id
            
# new created metric (e.g. "sadness") is added to the metrics table             
def create_metric(key: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO metrics (key) 
        VALUES (?)
        """, (key,))
        conn.commit()
        metric_id = cursor.lastrowid
        return metric_id
        
def list_metrics():
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, key FROM metrics")
        return [dict(row) for row in cursor.fetchall()]
    
def delete_metric(metric_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM metrics WHERE id = ?", (metric_id,))
        conn.commit()
        return cursor.rowcount > 0 
    
# value (1-5) can be added to an entry for a specific metric (e.g. "sadness" = 3)
def add_entry_value(entry_id: int, metric_id: int, value: int)-> int:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO entry_values (entry_id, metric_id, value)
        VALUES (?, ?, ?)""", (entry_id, metric_id, value))
        conn.commit()
        value_id = cursor.lastrowid
        return value_id

def list_entries(limit: int | None = None):
    sql = "SELECT id, date, note, created_by FROM entries ORDER BY date DESC"
    params = ()
    with get_connection() as conn:
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
def list_entry_values(entry_id: int) -> dict | None:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        entry_row = cursor.fetchone()
        if entry_row is None:
            return None
        
        cursor = conn.execute("""
        SELECT 
            ev.id as entry_value_id,
            m.id as metric_id,
            m.key as metric_key,
            ev.value as metric_value
        FROM entry_values ev
        JOIN metrics m ON m.id = ev.metric_id
        WHERE ev.entry_id = ?
        """, (entry_id,))
        value_rows = [dict(row) for row in cursor.fetchall()]
        entry = dict(entry_row)
        entry['values'] = value_rows
        return entry
    
def update_entry(entry_id: int, date: str, note: str | None = None, created_by: str | None = None) -> bool:
    all_updates = {"date": date, "note": note, "created_by": created_by}
    updates = {field: value for field, value in all_updates.items() if value is not None}
    if not updates:
        return False
    
    with get_connection() as conn:
        field_str = ", ".join(f"{field} = ?" for field in updates)
        cursor = conn.execute(f"""
        UPDATE entries 
        SET {field_str}
        WHERE id = ?
        """, (*updates.values(), entry_id))
        conn.commit()
        return cursor.rowcount > 0 
    
def set_entry_value(entry_id: int, metric_id: int, value: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO entry_values (entry_id, metric_id, value)
        VALUES (?, ?, ?)
        ON CONFLICT(entry_id, metric_id) DO UPDATE SET value = excluded.value
        """, (entry_id, metric_id, value))
        conn.commit()

def get_entry_with_values(entry_id: int) -> dict | None:
    """Get an entry with its associated metric values"""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        entry_row = cursor.fetchone()
        if entry_row is None:
            return None
        
        cursor = conn.execute("""
        SELECT 
            ev.id as entry_value_id,
            m.id as metric_id,
            m.key as metric_key,
            ev.value as value
        FROM entry_values ev
        JOIN metrics m ON m.id = ev.metric_id
        WHERE ev.entry_id = ?
        """, (entry_id,))
        value_rows = [dict(row) for row in cursor.fetchall()]
        entry = dict(entry_row)
        entry['values'] = value_rows
        return entry

def delete_entry_value(entry_id: int, metric_id: int) -> bool:
    """Delete a metric value from an entry"""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM entry_values WHERE entry_id = ? AND metric_id = ?",
            (entry_id, metric_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id: int) -> bool:
    """Delete an entry and its associated metric values"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0


# ===== NEUE FUNKTIONEN FÜR THERAPY CAT AI =====

def get_latest_entry_metrics(limit: int = 7) -> list[dict]:
    """
    Holt die letzten N Einträge mit ihren Metrik-Werten.
    
    Args:
        limit: Anzahl der letzten Einträge (Standard: 7)
    
    Returns:
        Liste von Dictionaries mit Entry-Daten und Metrik-Werten
    """
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            e.id as entry_id,
            e.date,
            e.note,
            e.created_by
        FROM entries e
        ORDER BY e.date DESC
        LIMIT ?
        """, (limit,))
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            
            # Hole Metrik-Werte für diesen Entry
            cursor2 = conn.execute("""
            SELECT 
                m.key as metric_key,
                ev.value as metric_value
            FROM entry_values ev
            JOIN metrics m ON ev.metric_id = m.id
            WHERE ev.entry_id = ?
            """, (entry['entry_id'],))
            
            entry['metrics'] = {row2['metric_key']: row2['metric_value'] for row2 in cursor2.fetchall()}
            entries.append(entry)
        
        return entries


def get_todays_metrics() -> dict:
    """
    Holt alle Metrik-Werte für heute.
    
    Returns:
        Dictionary mit Metrik-Keys und deren Werten
    """
    from datetime import date
    today = str(date.today())
    
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date = ?
        """, (today,))
        
        return {row['key']: row['value'] for row in cursor.fetchall()}


def get_metrics_raw_data(days: int = 30) -> dict:
    """
    Sammelt Rohdaten aller Metriken für einen Zeitraum.
    Zur Verwendung für eigene Analyseverfahren und Gewichtungen.
    
    Args:
        days: Anzahl der Tage zur Analyse (Standard: 30)
    
    Returns:
        Dictionary mit Metrik-Keys, ihre Werte über Zeit und Statistiken
    """
    from datetime import date, timedelta
    start_date = str(date.today() - timedelta(days=days))
    
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value,
            e.date
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date >= ?
        ORDER BY m.key, e.date
        """, (start_date,))
        
        # Strukturiere die Daten nach Metrik-Keys
        data = {}
        for row in cursor.fetchall():
            key = row['key']
            if key not in data:
                data[key] = {'values': [], 'dates': []}
            data[key]['values'].append(row['value'])
            data[key]['dates'].append(row['date'])
        
        return data


# ===== MULTI-USER & ENTRY MANAGEMENT FUNKTIONEN =====

def list_users() -> list[str]:
    """
    Gibt eine Liste aller Nutzer zurück, die Entries erstellt haben.
    
    Returns:
        Liste von eindeutigen created_by Werten
    """
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT DISTINCT created_by FROM entries WHERE created_by IS NOT NULL
        ORDER BY created_by
        """)
        return [row['created_by'] for row in cursor.fetchall()]


# [21.04.2026] - User-gefilterte Entry-Abfrage mit Multi-User Support
def get_user_entries(created_by: str, limit: int | None = None) -> list[dict]:
    """
    Holt alle Einträge eines spezifischen Nutzers mit ihren Metrik-Werten.
    MULTI-USER: Filtert automatisch nach User & berücksichtigt Standard-User (NULL entries).
    
    Args:
        created_by: Der Nutzer-Identifier
        limit: Optional - maximale Anzahl der Einträge (Standard: alle)
    
    Returns:
        Liste von Dictionaries mit Entry-Daten und Metriken, sortiert nach Datum (DESC)
    """
    with get_connection() as conn:
        # [21.04.2026] SQL-Query mit User-Filterung:
        # - Gibt Entries des Users zurück
        # - Gibt auch NULL-Entries zurück wenn User = 'Standard' (backward compatible)
        sql = """
        SELECT 
            e.id as entry_id,
            e.date,
            e.note,
            e.created_by
        FROM entries e
        WHERE e.created_by = ? OR (e.created_by IS NULL AND ? = 'Standard')
        ORDER BY e.date DESC
        """
        # [21.04.2026] Holt die letzten N Einträge eines spezifischen Nutzers
        if limit:
            sql += " LIMIT ?"
            params = (created_by, created_by, limit)
        else:
            params = (created_by, created_by)
        
        cursor = conn.execute(sql, params)
        entries = []
        
        for row in cursor.fetchall():
            entry = dict(row)
            
            # [21.04.2026] Hole Metrik-Werte für diesen Entry
            cursor2 = conn.execute("""
            SELECT 
                m.id as metric_id,
                m.key as metric_key,
                ev.value as metric_value
            FROM entry_values ev
            JOIN metrics m ON ev.metric_id = m.id
            WHERE ev.entry_id = ?
            """, (entry['entry_id'],))
            
            entry['metrics'] = {row2['metric_key']: row2['metric_value'] for row2 in cursor2.fetchall()}
            entries.append(entry)
        
        return entries


def get_entry_with_metrics(entry_id: int, created_by: str | None = None) -> dict | None:
    """
    Holt einen einzelnen Entry mit allen seinen Metrik-Werten.
    SICHERHEIT: Kann optional überprüfen, ob dieser Entry vom korrekten User stammt.
    
    Args:
        entry_id: Die ID des Entries
        created_by: Optional - überprüfe ob dieser Entry von diesem User stammt
    
    Returns:
        Dictionary mit Entry-Daten und Metriken, oder None wenn nicht gefunden
    """
    with get_connection() as conn:
        if created_by:
            # Sicherheits-Check: User darf nur auf eigene Entries zugreifen
            cursor = conn.execute("""
            SELECT id, date, note, created_by 
            FROM entries 
            WHERE id = ? AND (created_by = ? OR (created_by IS NULL AND ? = 'Standard'))
            """, (entry_id, created_by, created_by))
        else:
            cursor = conn.execute("""
            SELECT id, date, note, created_by 
            FROM entries 
            WHERE id = ?
            """, (entry_id,))
        
        entry_row = cursor.fetchone()
        if not entry_row:
            return None
        
        entry = dict(entry_row)
        
        # Hole Metrik-Werte
        cursor = conn.execute("""
        SELECT 
            m.id as metric_id,
            m.key as metric_key,
            ev.value as metric_value
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        WHERE ev.entry_id = ?
        """, (entry_id,))
        
        entry['metrics'] = {row['metric_key']: row['metric_value'] for row in cursor.fetchall()}
        return entry


def get_user_todays_metrics(created_by: str) -> dict:
    """
    Holt die heutigen Metrik-Werte eines spezifischen Nutzers.
    
    Args:
        created_by: Der Nutzer-Identifier
        
    Returns:
        Dictionary mit Metrik-Keys und deren Werten für heute
    """
    from datetime import date
    today = str(date.today())
    
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date = ? AND (e.created_by = ? OR (e.created_by IS NULL AND ? = 'Standard'))
        """, (today, created_by, created_by))
        
        return {row['key']: row['value'] for row in cursor.fetchall()}


def get_user_metrics_raw_data(created_by: str, days: int = 30) -> dict:
    """
    Sammelt Rohdaten aller Metriken für einen Nutzer über einen Zeitraum.
    
    Args:
        created_by: Der Nutzer-Identifier
        days: Anzahl der Tage zur Analyse (Standard: 30)
    
    Returns:
        Dictionary mit Metrik-Keys, ihre Werte über Zeit für diesen User
    """
    from datetime import date, timedelta
    start_date = str(date.today() - timedelta(days=days))
    
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value,
            e.date
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date >= ? AND (e.created_by = ? OR (e.created_by IS NULL AND ? = 'Standard'))
        ORDER BY m.key, e.date
        """, (start_date, created_by, created_by))
        
        # Strukturiere die Daten nach Metrik-Keys
        data = {}
        for row in cursor.fetchall():
            key = row['key']
            if key not in data:
                data[key] = {'values': [], 'dates': []}
            data[key]['values'].append(row['value'])
            data[key]['dates'].append(row['date'])
        
        return data
    from datetime import date, timedelta
    start_date = str(date.today() - timedelta(days=days))
    
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value,
            e.date
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.created_by = ? AND e.date >= ?
        ORDER BY m.key, e.date
        """, (created_by, start_date))
        
        # Strukturiere die Daten nach Metrik-Keys
        data = {}
        for row in cursor.fetchall():
            key = row['key']
            if key not in data:
                data[key] = {'values': [], 'dates': []}
            data[key]['values'].append(row['value'])
            data[key]['dates'].append(row['date'])
        
        return data


init_db()