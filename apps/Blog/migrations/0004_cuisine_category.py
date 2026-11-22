from django.db import migrations


def create_cuisine(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    Category.objects.get_or_create(
        slug="cuisine",
        defaults={"name": "Cuisine", "description": "Recettes, astuces et bons petits plats à partager."},
    )


def remove_cuisine(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    Category.objects.filter(slug="cuisine", posts__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("Blog", "0003_post_likes")]
    operations = [migrations.RunPython(create_cuisine, remove_cuisine)]
