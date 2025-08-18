from django.core.management.base import BaseCommand
from shop.models import Category
import random

class Command(BaseCommand):
    help = 'Populates the database with sample categories'

    def handle(self, *args, **options):
        categories = [
            "Skincare",
            "Makeup",
            "Haircare",
            "Fragrance",
            "Bath & Body",
            "Men's Grooming",
            "Tools & Brushes",
            "Natural & Organic"
        ]

        for name in categories:
            Category.objects.get_or_create(
                name=name,
                slug=name.lower().replace(' ', '-').replace("'", "").replace("&", "and")
            )
            self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated categories!'))