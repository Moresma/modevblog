from django.db import migrations


def remove_projet(apps, schema_editor):
    # Supprime la catégorie "Projet" seulement si aucun article ne l'utilise.
    Category = apps.get_model("Blog", "Category")
    Category.objects.filter(slug="projet", posts__isnull=True).delete()


def restore_projet(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    Category.objects.get_or_create(
        slug="projet",
        defaults={"name": "Projet", "description": "Les articles liés au projet."},
    )


class Migration(migrations.Migration):
    dependencies = [("Blog", "0004_cuisine_category")]
    operations = [migrations.RunPython(remove_projet, restore_projet)]
