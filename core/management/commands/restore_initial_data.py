from pathlib import Path

from django.core.management import BaseCommand, call_command

from teacher.models import Curriculum, Lesson, Quiz


class Command(BaseCommand):
    help = "Restores initial data from backups/sqlite_data.json only if database is empty"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[4]
        fixture_path = base_dir / "backups" / "sqlite_data.json"

        has_domain_data = Quiz.objects.exists() or Lesson.objects.exists() or Curriculum.objects.exists()
        if has_domain_data:
            self.stdout.write(self.style.WARNING("Domain data already exists. Skipping restore."))
            return

        if not fixture_path.exists():
            self.stdout.write(self.style.WARNING(f"Fixture not found: {fixture_path}. Skipping restore."))
            return

        self.stdout.write(f"Loading fixture: {fixture_path}")
        call_command("loaddata", str(fixture_path))
        self.stdout.write(self.style.SUCCESS("Initial data restored successfully."))
