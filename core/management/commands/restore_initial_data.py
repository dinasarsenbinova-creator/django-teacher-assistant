from pathlib import Path
import json

from django.core.management import BaseCommand, call_command
from django.core import serializers

from teacher.models import Curriculum, Lesson, Quiz


class Command(BaseCommand):
    help = "Restores initial data from backups/sqlite_data.json only if database is empty"

    RESTORE_ORDER = [
        "auth.user",
        "teacher.subject",
        "teacher.studentgroup",
        "teacher.curriculum",
        "teacher.topic",
        "teacher.schedule",
        "teacher.lesson",
        "teacher.test",
        "teacher.quiz",
        "teacher.quizquestion",
        "teacher.quizattempt",
    ]

    def _has_domain_data(self):
        return Quiz.objects.exists() or Lesson.objects.exists() or Curriculum.objects.exists()

    def _restore_via_upsert_fallback(self, fixture_path: Path):
        """Fallback: мягкое восстановление только ключевых моделей через upsert-поведение save()."""
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))

        order_index = {name: i for i, name in enumerate(self.RESTORE_ORDER)}
        filtered = [item for item in raw if item.get("model") in order_index]
        filtered.sort(key=lambda item: order_index.get(item.get("model"), 10_000))

        payload = json.dumps(filtered, ensure_ascii=False)
        restored = 0
        skipped = 0

        for obj in serializers.deserialize("json", payload, ignorenonexistent=True):
            try:
                obj.save()
                restored += 1
            except Exception:
                skipped += 1

        self.stdout.write(
            self.style.WARNING(
                f"Fallback restore completed: restored={restored}, skipped={skipped}."
            )
        )

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[4]
        fixture_path = base_dir / "backups" / "sqlite_data.json"

        if self._has_domain_data():
            self.stdout.write(self.style.WARNING("Domain data already exists. Skipping restore."))
            return

        if not fixture_path.exists():
            self.stdout.write(self.style.WARNING(f"Fixture not found: {fixture_path}. Skipping restore."))
            return

        self.stdout.write(f"Loading fixture: {fixture_path}")
        try:
            call_command("loaddata", str(fixture_path))
            if self._has_domain_data():
                self.stdout.write(self.style.SUCCESS("Initial data restored successfully."))
                return

            self.stdout.write(self.style.WARNING("loaddata finished, but no domain data detected. Running fallback restore..."))
            self._restore_via_upsert_fallback(fixture_path)
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"loaddata error: {exc}. Running fallback restore..."
                )
            )
            try:
                self._restore_via_upsert_fallback(fixture_path)
            except Exception as fallback_exc:
                self.stdout.write(
                    self.style.WARNING(
                        f"Fallback restore failed: {fallback_exc}. App startup continues."
                    )
                )
