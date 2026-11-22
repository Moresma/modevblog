from django.db import migrations

# Anciennes phrases (trop formelles) -> nouvelles, plus détendues.
OLD = {
    "religion": "Un verset qui t'a touché, un témoignage, une réflexion sur ta foi ? "
                "Partage-le avec la communauté.",
    "tech": "Une astuce, un outil, un projet de code dont tu es fier ? "
            "Écris un article et fais-en profiter tout le monde.",
    "cuisine": "Ta recette de ndolé, ton poulet DG ou ton plat préféré ? "
               "Partage-la avec nous, on a déjà l'eau à la bouche !",
}
NEW = {
    "religion": "Un verset te parle en ce moment ? Dieu a fait un truc fort dans ta vie ? "
                "Viens partager ça avec nous, ça peut toucher quelqu'un !",
    "tech": "T'as trouvé une astuce de ouf ? Enfin vaincu ce bug qui te rendait fou ? "
            "Viens frimer un peu, on veut savoir !",
    "cuisine": "Ton ndolé fait parler tout le quartier ? Ton poulet DG est imbattable ? "
               "Balance ta recette, on a faim !",
}


def forward(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    for slug, text in NEW.items():
        # Ne remplace que si la phrase n'a pas été modifiée à la main dans l'admin.
        Category.objects.filter(slug=slug, cta__in=["", OLD[slug]]).update(cta=text)


def backward(apps, schema_editor):
    Category = apps.get_model("Blog", "Category")
    for slug, text in OLD.items():
        Category.objects.filter(slug=slug, cta=NEW[slug]).update(cta=text)


class Migration(migrations.Migration):
    dependencies = [("Blog", "0008_category_cta_texts")]
    operations = [migrations.RunPython(forward, backward)]
