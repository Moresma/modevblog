from django.db import models

from apps.Blog.images import optimize_image


class PageBackground(models.Model):
    """Image de fond d'une page du site, modifiable depuis l'admin."""

    class Page(models.TextChoices):
        HOME = "home", "Accueil"
        MY_POSTS = "my_posts", "Mes articles"
        WRITE = "write", "Écrire un article"
        LOGIN = "login", "Connexion"
        REGISTER = "register", "Inscription"

    # Page concernée (une seule image par page).
    page = models.CharField(max_length=20, choices=Page.choices, unique=True, verbose_name="Page")
    # L'image de fond (redimensionnée automatiquement à l'envoi).
    image = models.ImageField(upload_to="backgrounds/", verbose_name="Image de fond")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        ordering = ["page"]
        verbose_name = "Image de fond"
        verbose_name_plural = "Images de fond"

    def __str__(self):
        return self.get_page_display()

    def save(self, *args, **kwargs):
        # Nouvelle image envoyée : on la réduit (2000 px max, assez pour un plein écran).
        if self.image and not getattr(self.image, "_committed", True):
            result = optimize_image(self.image, max_size=2000)
            if result is not None:
                name, content = result
                self.image.save(name, content, save=False)
        super().save(*args, **kwargs)
