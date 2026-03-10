import sqlite3, os
DB = os.path.abspath('db.sqlite3')
conn=sqlite3.connect(DB)
cur=conn.cursor()
for t in ['teacher_test','teacher_lesson','teacher_grade','teacher_schedule','teacher_curriculum','teacher_subject','teacher_studentgroup']:
    try:
        cur.execute(f"PRAGMA table_info('{t}')")
        cols=cur.fetchall()
        print('\nTable',t,'cols:')
        for c in cols:
            print(c)
    except Exception as e:
        print('\nTable',t,'error',e)
conn.close()
