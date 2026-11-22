"""
Images de fond par défaut (accueil, pages, rubriques).

Les fichiers sont versionnés dans media/backgrounds/ et media/categories/.
Cette migration les relie à la base de données pour qu'une installation neuve
(par exemple chez un collègue) affiche directement les mêmes images.
Elle ne touche à rien si une image a déjà été choisie dans l'admin.
"""
from pathlib import Path

from django.conf import settings
from django.db import migrations

PAGE_BACKGROUNDS = {
    "home": "backgrounds/home-bureau.jpg",
    "my_posts": "backgrounds/my_posts.jpg",
    "write": "backgrounds/write.jpg",
    "login": "backgrounds/login.jpg",
    "register": "backgrounds/register.jpg",
}

CATEGORY_COVERS = {
    "religion": "categories/religion.jpg",
    "tech": "categories/tech-code.jpg",
    "cuisine": "categories/cuisine-cameroun.jpg",
}


def _exists(name):
    return (Path(settings.MEDIA_ROOT) / name).exists()


def set_defaults(apps, schema_editor):
    PageBackground = apps.get_model("cms", "PageBackground")
    Category = apps.get_model("Blog", "Category")

    for page, name in PAGE_BACKGROUNDS.items():
        if _exists(name) and not PageBackground.objects.filter(page=page).exists():
            PageBackground.objects.create(page=page, image=name)

    for slug, name in CATEGORY_COVERS.items():
        if _exists(name):
            Category.objects.filter(slug=slug, cover__in=["", None]).update(cover=name)


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0001_initial"),
        ("Blog", "0009_category_cta_casual"),
    ]
    operations = [migrations.RunPython(set_defaults, migrations.RunPython.noop)]
