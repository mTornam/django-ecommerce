import os
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


# Create your models here.
def category_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.name)}.{ext}"
    return os.path.join("categories", filename)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=category_image_upload_path, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=50)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    
    def total_images(self):
        return self.images.count()
    
def product_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    existing_images_count = instance.product.images.count()    
    filename = f"{slugify(instance.product.name)}__{existing_images_count + 1}.{ext}"
    return os.path.join("products", filename)    


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"
    

