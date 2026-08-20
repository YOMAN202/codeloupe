"""
Initialize (or re-initialize) the SQLite database and seed Day 1's lesson.

Run directly: `python3 db/init_db.py` from the backend/ directory.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "traceviz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

DAY_1_CONCEPT_MARKDOWN = """\
## Day 1 — Variables

A variable is a name you give to a value so you can use that value again \
later without retyping it.

Think of it like a labeled box. You write a label on the box (the variable \
name), and you put something inside it (the value). Whenever you use the \
label later, Python looks inside that box and gives you what's there.

```python
x = 5
```

This line does not check whether `x` equals 5. It *creates* a box labeled \
`x` and puts `5` inside it. The single `=` here means "store this value," \
not "is equal to."
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.execute(
        """
        INSERT INTO lessons (day, title, concept_markdown)
        VALUES (1, 'Variables', ?)
        ON CONFLICT(day) DO UPDATE SET
            title = excluded.title,
            concept_markdown = excluded.concept_markdown
        """,
        (DAY_1_CONCEPT_MARKDOWN,),
    )
    conn.commit()
    conn.close()
    print(f"Initialized database at {DB_PATH}")


if __name__ == "__main__":
    init_db()
