from django.core.management.base import BaseCommand
from django.db import connection, transaction


TABLES_WITH_SUBJECT = [
    "teacher_curriculum",
    "teacher_lesson",
    "teacher_schedule",
    "teacher_grade",
    "teacher_test",
]

TABLES_WITH_CLASS = [
    "teacher_schedule",
    "teacher_lesson",
    "teacher_grade",
    "teacher_test",
]


def table_has_column(table, column):
    with connection.cursor() as c:
        try:
            c.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=%s",
                [table],
            )
            if not c.fetchone():
                return False
            c.execute(f"PRAGMA table_info('{table}')")
            cols = [row[1] for row in c.fetchall()]
            return column in cols
        except Exception:
            return False


def distinct_values(table, column):
    with connection.cursor() as c:
        try:
            c.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL AND TRIM({column}) <> ''")
            return [row[0] for row in c.fetchall()]
        except Exception:
            return []


class Command(BaseCommand):
    help = "Convert existing string 'subject' and 'class_name' columns into Subject and StudentGroup FK relations."

    def handle(self, *args, **options):
        from teacher.models import Subject, StudentGroup

        created_subjects = 0
        created_groups = 0

        # Collect subject names
        subject_names = set()
        for t in TABLES_WITH_SUBJECT:
            if table_has_column(t, "subject"):
                vals = distinct_values(t, "subject")
                subject_names.update([v for v in vals if v])

        # Create Subject rows
        for name in sorted(subject_names):
            obj, created = Subject.objects.get_or_create(name=name.strip())
            if created:
                created_subjects += 1

        # Collect class/group names
        group_names = set()
        for t in TABLES_WITH_CLASS:
            if table_has_column(t, "class_name"):
                vals = distinct_values(t, "class_name")
                group_names.update([v for v in vals if v])

        # Create StudentGroup rows
        for name in sorted(group_names):
            obj, created = StudentGroup.objects.get_or_create(name=name.strip())
            if created:
                created_groups += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_subjects} Subject(s) and {created_groups} StudentGroup(s)."))

        # Now update FK fields if present (subject_id, class_name_id)
        with transaction.atomic():
            with connection.cursor() as c:
                # Update subject_id from subject text
                for t in TABLES_WITH_SUBJECT:
                    if table_has_column(t, "subject") and table_has_column(t, "subject_id"):
                        self.stdout.write(f"Updating subject_id in {t}...")
                        c.execute(
                            f"UPDATE {t} SET subject_id = (SELECT id FROM teacher_subject WHERE name = {t}.subject) WHERE {t}.subject IS NOT NULL"
                        )
                # Update class_name_id from class_name text
                for t in TABLES_WITH_CLASS:
                    if table_has_column(t, "class_name") and table_has_column(t, "class_name_id"):
                        self.stdout.write(f"Updating class_name_id in {t}...")
                        c.execute(
                            f"UPDATE {t} SET class_name_id = (SELECT id FROM teacher_studentgroup WHERE name = {t}.class_name) WHERE {t}.class_name IS NOT NULL"
                        )

        self.stdout.write(self.style.SUCCESS("FK update finished. Please run makemigrations/migrate if needed and verify data."))
