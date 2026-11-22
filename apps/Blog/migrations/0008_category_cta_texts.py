from django.db import migrations

# Phrases d'appel à écrire, affichées sur le bandeau de chaque rubrique.
CTA = {
    "religion": "Un verset qui t'a touché, un témoignage, une réflexion sur ta foi ? "
                "Partage-le avec la communauté.",
    "tech": "Une astuce, un outil, un projet de code dont tu es fier ? "
            "Écris un article et fais-en profiter tout le monde.",
    "cuisine": "Ta recette de ndolé, ton poulet DG ou ton plat préféré ? "
               "Partage-la avec nous, on a déjà l'eau à la bouche !",
}


def add_cta(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    for slug, text in CTA.items():
        Category.objects.filter(slug=slug, cta="").update(cta=text)


def remove_cta(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    for slug, text in CTA.items():
        Category.objects.filter(slug=slug, cta=text).update(cta="")


class Migration(migrations.Migration):
    dependencies = [("Blog", "0007_category_cta")]
    operations = [migrations.RunPython(add_cta, remove_cta)]
