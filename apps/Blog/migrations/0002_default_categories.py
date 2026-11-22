from django.db import migrations

CATEGORIES = [
    ("religion", "Religion", "Réflexions et articles sur la foi et la religion."),
    ("projet", "Projet", "Les articles liés au projet."),
    ("tech", "Tech", "Articles techniques : développement, outils et découvertes."),
]


def create_categories(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    for slug, name, description in CATEGORIES:
        Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description},
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    Category.objects.filter(
        slug__in=[slug for slug, _, _ in CATEGORIES], posts__isnull=True
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("Blog", "0001_initial")]
    operations = [migrations.RunPython(create_categories, remove_categories)]
