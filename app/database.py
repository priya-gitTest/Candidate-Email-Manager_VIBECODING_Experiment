import duckdb
from pathlib import Path

DB_PATH = Path("data/candidates.duckdb")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    try:
        con = duckdb.connect(DB_PATH)
        con.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER,
                name TEXT,
                email TEXT,
                stage INTEGER DEFAULT 0
            );
        """)
        return con
    except duckdb.IOException as e:
        print("DuckDB error, resetting DB:", e)
        import os
        os.remove(DB_PATH)
        return init_db()

def add_candidate(name: str, email: str):
    con = init_db()
    next_id = get_next_id(con)
    con.execute(
        "INSERT INTO candidates (id, name, email, stage) VALUES (?, ?, ?, 0)",
        (next_id, name, email)
    )

def get_candidates():
    con = init_db()
    rows = con.execute("SELECT * FROM candidates").fetchall()
    return [{"id": r[0], "name": r[1], "email": r[2], "stage": r[3]} for r in rows]

def update_stage(candidate_id, new_stage):
    con = init_db()
    con.execute("UPDATE candidates SET stage = ? WHERE id = ?;", (new_stage, candidate_id))

def update_template(stage: int, content: str):
    with open(f"app/email_templates/email_{stage}.txt", "w") as f:
        f.write(content)

def read_template(stage: int):
    with open(f"app/email_templates/email_{stage}.txt") as f:
        return f.read()
    
def get_next_id(con):
    result = con.execute("SELECT MAX(id) FROM candidates").fetchone()[0]
    return (result or 0) + 1