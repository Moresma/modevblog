from .models import PageBackground


def page_backgrounds(request):
    """
    Ajoute {{ page_bg }} aux templates : l'adresse de l'image de fond de chaque page,
    ex. {{ page_bg.my_posts }}. Vide si aucune image n'a été envoyée dans l'admin.
    """
    return {"page_bg": {bg.page: bg.image.url for bg in PageBackground.objects.all() if bg.image}}
