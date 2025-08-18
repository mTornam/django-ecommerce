from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductImage
from django.utils.text import slugify
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with sample products'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of products to create')

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Please run populate_categories first.'))
            return

        product_count = options['count']
        product_names = [
            "Hydrating Facial Moisturizer", "Matte Lipstick Set", "Volumizing Shampoo",
            "Eau de Parfum", "Body Butter Collection", "Anti-Aging Serum",
            "Makeup Brush Kit", "Charcoal Face Mask", "Hair Growth Oil",
            "Sunscreen SPF 50", "Eyebrow Pencil", "Nourishing Hair Mask"
        ]

        for i in range(product_count):
            # Create base product
            name = f"{random.choice(product_names)} {fake.color_name().title()}"
            category = random.choice(categories)
            price = round(random.uniform(5, 150), 2)
            
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                category=category,
                description=fake.paragraph(nb_sentences=5),
                price=price,
                available=random.choice([True, False])
            )

            # Add 1-4 images per product
            # num_images = random.randint(1, 4)
            # for j in range(num_images):
            #     ProductImage.objects.create(
            #         product=product,
            #         # In a real scenario, you would add actual image files
            #         # For demo purposes, we'll just record that images would be here
            #         image=f"products/{slugify(name)}-{j+1}.jpg",
            #         is_featured=(j == 0)
            #     )

            self.stdout.write(self.style.SUCCESS(f'Created product: {name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {product_count} products!'))