from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Champs affichés dans le formulaire, dans cet ordre.
        fields = ["title", "excerpt", "content", "image", "category", "tags", "status"]

        # Apparence de chaque champ dans le HTML.
        widgets = {
            # Titre : une ligne, sans bordure (style "éditeur").
            "title": forms.TextInput(attrs={"placeholder": "Le titre de ton article…", "autocomplete": "off"}),
            # Résumé : zone de 2 lignes, utilisée sur les cartes d'articles.
            "excerpt": forms.Textarea(attrs={"rows": 2, "placeholder": "En une phrase : de quoi tu vas nous parler ?"}),
            # Contenu : grande zone qui s'agrandit en tapant (géré par main.js).
            "content": forms.Textarea(attrs={"rows": 14, "placeholder": "Écris ton article ici, exprime-toi librement…"}),
            # Image : n'accepte que des images dans la fenêtre de sélection.
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            # Tags : cases à cocher (affichées comme des pastilles) au lieu d'une liste multiple.
            "tags": forms.CheckboxSelectMultiple,
            # Statut : boutons radio (affichés comme un interrupteur Brouillon / Publié).
            "status": forms.RadioSelect,
        }
