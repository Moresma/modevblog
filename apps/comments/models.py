from django.db import models
from django.conf import settings
from apps.Blog.models import Post

class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name="comments", verbose_name="auteur")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Article")
    content = models.TextField(verbose_name= "contenu")
    # Utilisateurs qui ont liké ce commentaire.
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="liked_comments", verbose_name="J'aime")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "commentaire"
        verbose_name_plural ="commentaires"

    def __str__(self):
        return f"{self.author} sur {self.post} ({self.created_at:%Y-%m-%d})"