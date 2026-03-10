import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.abspath(DB)
print('DB:', DB)
conn = sqlite3.connect(DB)
cur = conn.cursor()

TABLES_WITH_SUBJECT = [
    'teacher_curriculum',
    'teacher_lesson',
    'teacher_schedule',
    'teacher_grade',
    'teacher_test',
]
TABLES_WITH_CLASS = [
    'teacher_schedule',
    'teacher_lesson',
    'teacher_grade',
    'teacher_test',
]

def has_table(t):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
    return cur.fetchone() is not None

def has_column(t, col):
    try:
        cur.execute(f"PRAGMA table_info('{t}')")
        cols = [r[1] for r in cur.fetchall()]
        return col in cols
    except Exception:
        return False

def distinct_values(t, col):
    try:
        cur.execute(f"SELECT DISTINCT {col} FROM {t} WHERE {col} IS NOT NULL AND TRIM({col}) <> ''")
        return [r[0] for r in cur.fetchall()]
    except Exception as e:
        return []

# Create teacher_subject table if missing
if not has_table('teacher_subject'):
    print('Creating table teacher_subject')
    cur.execute('''CREATE TABLE teacher_subject (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, description TEXT, created_by INTEGER)''')
    conn.commit()
else:
    print('teacher_subject exists')

# Create teacher_studentgroup table if missing
if not has_table('teacher_studentgroup'):
    print('Creating table teacher_studentgroup')
    cur.execute('''CREATE TABLE teacher_studentgroup (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, year INTEGER, students TEXT, created_by INTEGER)''')
    conn.commit()
else:
    print('teacher_studentgroup exists')

# Collect subject names from string columns or subject_id columns
subject_names = set()
for t in TABLES_WITH_SUBJECT:
    if has_table(t):
        if has_column(t, 'subject'):
            vals = distinct_values(t, 'subject')
            subject_names.update([v for v in vals if v])
        if has_column(t, 'subject_id'):
            # subject_id might contain string values
            vals = distinct_values(t, 'subject_id')
            subject_names.update([v for v in vals if v])

print('Found subjects:', subject_names)
for name in sorted(subject_names):
    # insert or ignore
    try:
        cur.execute('INSERT OR IGNORE INTO teacher_subject (name) VALUES (?)', (name,))
    except Exception as e:
        print('Insert subject error', name, e)
conn.commit()

# Collect group names
group_names = set()
for t in TABLES_WITH_CLASS:
    if has_table(t):
        if has_column(t, 'class_name'):
            vals = distinct_values(t, 'class_name')
            group_names.update([v for v in vals if v])
        if has_column(t, 'class_name_id'):
            vals = distinct_values(t, 'class_name_id')
            group_names.update([v for v in vals if v])

print('Found groups:', group_names)
for name in sorted(group_names):
    try:
        cur.execute('INSERT OR IGNORE INTO teacher_studentgroup (name) VALUES (?)', (name,))
    except Exception as e:
        print('Insert group error', name, e)
conn.commit()

# Update subject_id columns where exists and value matches a subject name
for t in TABLES_WITH_SUBJECT:
    if has_table(t) and has_column(t, 'subject_id'):
        print('Updating subject_id in', t)
        # Update only where a matching subject exists
        cur.execute(f"UPDATE {t} SET subject_id = (SELECT id FROM teacher_subject WHERE name = {t}.subject_id) WHERE {t}.subject_id IS NOT NULL AND {t}.subject_id <> '' AND EXISTS (SELECT 1 FROM teacher_subject WHERE name = {t}.subject_id)")
conn.commit()

# Update class_name_id columns
for t in TABLES_WITH_CLASS:
    if has_table(t) and has_column(t, 'class_name_id'):
        print('Updating class_name_id in', t)
        cur.execute(f"UPDATE {t} SET class_name_id = (SELECT id FROM teacher_studentgroup WHERE name = {t}.class_name_id) WHERE {t}.class_name_id IS NOT NULL AND {t}.class_name_id <> '' AND EXISTS (SELECT 1 FROM teacher_studentgroup WHERE name = {t}.class_name_id)")
conn.commit()

print('Done updates. Verify DB and re-run migrate if needed.')
conn.close()
