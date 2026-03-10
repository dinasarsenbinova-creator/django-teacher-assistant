import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print(f"Total URL patterns: {len(resolver.url_patterns)}")
print("\nAll patterns:")
for pattern in resolver.url_patterns:
    print(f"  {pattern.pattern} -> {pattern.name}")
