from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Populates all database tables with sample data'

    def handle(self, *args, **options):
        # Run category population
        self.stdout.write(self.style.MIGRATE_HEADING('Populating categories...'))
        call_command('populate_categories')
        
        # Run product population
        self.stdout.write(self.style.MIGRATE_HEADING('Populating products...'))
        call_command('populate_products', '--count=50')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated all data!'))