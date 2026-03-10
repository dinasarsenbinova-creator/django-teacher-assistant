import sqlite3, os
DB = os.path.abspath('db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
for t in ('teacher_subject','teacher_studentgroup'):
    try:
        cur.execute(f"ALTER TABLE {t} ADD COLUMN created_by_id INTEGER")
        print('Added created_by_id to', t)
    except Exception as e:
        print('Error adding column to', t, e)
conn.commit()
conn.close()
