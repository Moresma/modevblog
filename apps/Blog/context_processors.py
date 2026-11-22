from .models import Category

# Onglets affichés dans le menu, dans cet ordre (slugs des catégories).
NAV_CATEGORY_SLUGS = ["religion", "tech", "cuisine"]


def nav_categories(request):
    categories = {c.slug: c for c in Category.objects.filter(slug__in=NAV_CATEGORY_SLUGS)}
    return {
        "nav_categories": [categories[s] for s in NAV_CATEGORY_SLUGS if s in categories],
    }
