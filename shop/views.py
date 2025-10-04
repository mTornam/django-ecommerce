from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Category, Product
# Create your views here.


def home(request):
    featured_categories = Category.objects.all()[:4]
    featured_products = Product.objects.filter(
        available=True).order_by('-created_at')[:8]
    return render(request, 'shop/home.html', {
        'featured_categories': featured_categories,
        'featured_products': featured_products,
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/categories.html', {'categories': categories})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/products.html', {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'query': query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    images = product.images.all()
    related_products = Product.objects.filter(
        category=product.category, available=True).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'images': images,
        'related_products': related_products,
    })
