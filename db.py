import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

db_path = Path("journal.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    conn.execute('PRAGMA foreign_keys = ON') 
    return conn

def init_db():
    with get_connection() as conn: 
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                note TEXT,
                user_id INTEGER,
                created_by TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                pin INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (pin BETWEEN 1000 AND 9999)
            );
        """)
        conn.commit()


def create_entry(date: str, note: str | None = None, created_by: str | None = None, user_id: int | None = None) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO entries(date, note, created_by, user_id) 
        VALUES (?, ?, ?, ?)  
        """, (date, note, created_by, user_id,))
        conn.commit()
        entry_id = cursor.lastrowid
        return entry_id
            
def create_metric(key: str):
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
    
def add_entry_value(entry_id: int, metric_id: int, value: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO entry_values (entry_id, metric_id, value)
        VALUES (?, ?, ?)                    
        """, (entry_id, metric_id, value,))
        conn.commit()
        value_id = cursor.lastrowid
        return value_id

def list_entries(user_id: int, limit: int | None = None):
    sql = "SELECT * FROM entries WHERE user_id = ? ORDER BY date DESC"
    params = [user_id]
    with get_connection() as conn:
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
def list_entry_values(entry_id: int, user_id: int) -> dict | None:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id,))
        entry_row = cursor.fetchone()
        if entry_row is None:
            return None
        
        cursor = conn.execute("""
        SELECT 
            ev.id as entry_value_id,
            m.id as metric_id,
            m.key as metric_key,
            ev.value as metric_value,
            u.id as user_id
        FROM entry_values ev
        JOIN metrics m ON m.id = ev.metric_id
        JOIN entries e ON e.id = ev.entry_id
        JOIN users u ON u.id = e.user_id
        WHERE ev.entry_id = ? AND u.id = ?
        """, (entry_id, user_id,))
        value_rows = [dict(row) for row in cursor.fetchall()]
        entry = dict(entry_row)
        entry['values'] = value_rows
        return entry
    
def update_entry(entry_id: int, date: str, note: str | None = None, created_by: str | None = None, user_id: int | None = None) -> bool:
    all_updates = {"date": date, "note": note, "created_by": created_by}
    updates = {field: value for field, value in all_updates.items() if value is not None}
    if not updates:
        return False
    
    with get_connection() as conn:
        field_str = ", ".join(f"{field} = ?" for field in updates)
        cursor = conn.execute(f"""
        UPDATE entries 
        SET {field_str}
        WHERE id = ? AND user_id = ?
        """, (*updates.values(), entry_id, user_id,))
        conn.commit()
        return cursor.rowcount > 0

    
def set_entry_value(entry_id: int, metric_id: int, value: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("""
        INSERT INTO entry_values (entry_id, metric_id, value)
        VALUES (?, ?, ?)
        ON CONFLICT(entry_id, metric_id) DO UPDATE SET value = excluded.value
        """, (entry_id, metric_id, value,))
        conn.commit()
        return cursor.rowcount > 0 
    
def get_entry_with_values(entry_id: int, user_id: int) -> dict | None:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id,))
        entry_row = cursor.fetchone()
        if entry_row is None:
            return None
        
        cursor = conn.execute("""
        SELECT 
            ev.id as entry_value_id,
            m.id as metric_id,
            m.key as metric_key,
            ev.value as value,
            u.id as user_id
        FROM entry_values ev
        JOIN metrics m ON m.id = ev.metric_id
        JOIN users u ON u.id = e.user_id
        JOIN entries e ON e.id = ev.entry_id
        WHERE ev.entry_id = ? AND e.user_id = ?
        """, (entry_id, user_id,))
        value_rows = [dict(row) for row in cursor.fetchall()]
        entry = dict(entry_row)
        entry['values'] = value_rows
        return entry

def delete_entry_value(entry_id: int, metric_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM entry_values WHERE entry_id = ? AND metric_id = ?",
            (entry_id, metric_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id: int, user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_latest_entry_metrics(user_id: int, limit: int | None = None) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            e.id as entry_id,
            e.date,
            e.note,
            e.created_by,
            e.user_id
        FROM entries e WHERE e.user_id = ?
        ORDER BY e.date DESC
        LIMIT ?
        """, (user_id, limit,))
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
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

def get_todays_metrics(user_id: int) -> dict:
    today = str(date.today())
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date = ? AND e.user_id = ?
        """, (today, user_id,))

        return {row['key']: row['value'] for row in cursor.fetchall()}

def get_metrics_raw_data(user_id: int, days: int | None = None) -> dict:
    start_date = str(date.today() - timedelta(days=days))
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT 
            m.key,
            ev.value,
            e.date,
            e.created_by
        FROM entry_values ev
        JOIN metrics m ON ev.metric_id = m.id
        JOIN entries e ON ev.entry_id = e.id
        WHERE e.date >= ? AND e.user_id = ?
        ORDER BY m.key, e.date
        """, (start_date, user_id,)) 
        
        data = {}
        for row in cursor.fetchall():
            key = row['key']
            if key not in data:
                data[key] = {'values': [], 'dates': []}
            data[key]['values'].append(row['value'])
            data[key]['dates'].append(row['date']) 
        
        return data

def list_created_by(user_id: int) -> list[str]:
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT DISTINCT created_by FROM entries WHERE created_by IS NOT NULL AND user_id = ?
        ORDER BY created_by
        """, (user_id,))
        return [row['created_by'] for row in cursor.fetchall()]

def login_user(username: str, pin: int):
    with get_connection() as conn:
        result = conn.execute(
            "SELECT id FROM users WHERE username = ? AND pin = ?",
            (username, pin)
        ).fetchone()
    if result:
        return result[0]
    return None

def register_user(username: str, pin: int) -> bool:
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, pin) VALUES (?, ?)",
                (username, pin)
            )
            conn.commit()
            return True
        except Exception:
            return False

def update_username(user_id: int, new_username: str) -> bool:
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "UPDATE users SET username = ? WHERE id = ?",
                (new_username, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

init_db()