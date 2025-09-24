from .models import Category


def base_context(request):
    return {
        'categories_list': Category.objects.all().only('name', 'slug') 
    }