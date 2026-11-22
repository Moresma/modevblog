from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from .images import optimize_image


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True, editable=False)
    description= models.TextField(blank=True, verbose_name="Description")
    # Phrase affichée sur le bandeau de la rubrique pour donner envie d'écrire.
    cta = models.TextField(blank=True, verbose_name="Appel à écrire")
    # Image de fond de la page de la rubrique (et des articles sans photo).
    cover = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Image de fond")
    parent= models.ForeignKey("self", on_delete = models.PROTECT, null=True , blank= True, related_name="children", verbose_name="Catégorie parente")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)

    class Meta:
        ordering = ["name"]
        verbose_name ="Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Nouvelle image de fond : réduite à 2000 px max.
        if self.cover and not getattr(self.cover, "_committed", True):
            result = optimize_image(self.cover, max_size=2000)
            if result is not None:
                name, content = result
                self.cover.save(name, content, save=False)
        super().save(*args, **kwargs)

class Tag (models.Model):
    name = models.CharField(max_length=50, unique= True, verbose_name="Nom")
    slug =  models.SlugField(max_length=255, unique=True, editable = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural= "Tags"

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publié"
    category= models.ForeignKey(Category, on_delete= models.PROTECT, related_name="posts", verbose_name="Catégorie")
    tags = models.ManyToManyField(Tag, blank = True, related_name="posts", verbose_name="Tag")
    title = models.CharField(max_length= 255, verbose_name="Titre")
    slug = models.SlugField(max_length=255, unique = True, editable= False)
    excerpt = models.TextField(blank=True, verbose_name="Résumé")
    content = models.TextField(verbose_name="Contenu")
    image = models.ImageField(upload_to= "posts/", blank=True, null= True, verbose_name="Image de couverture")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", verbose_name="Auteur")
    # Utilisateurs qui ont liké l'article (un like par personne).
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="liked_posts", verbose_name="J'aime")
    status = models.CharField(max_length=10, choices=Status.choices, default= Status.DRAFT, verbose_name="Statut")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de publication")
    created_at = models.DateTimeField(auto_now_add= True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "article"
            slug = base_slug
            counter = 2

            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        if self.status == self.Status.DRAFT:
            self.published_at = None

        # Nouvelle image envoyée (pas encore enregistrée sur le disque) :
        # on la redimensionne à 1600 px max et on la compresse avant de l'écrire.
        if self.image and not getattr(self.image, "_committed", True):
            result = optimize_image(self.image)
            if result is not None:
                name, content = result
                self.image.save(name, content, save=False)

        super().save(*args, **kwargs)
