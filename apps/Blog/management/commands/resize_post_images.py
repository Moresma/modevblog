"""
Redimensionne les images déjà envoyées.
Usage : python manage.py resize_post_images
Les originaux sont copiés dans media/originals_backup/ avant d'être remplacés.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.Blog.images import optimize_image
from apps.Blog.models import Post


class Command(BaseCommand):
    help = "Redimensionne les images des articles existants (max 1600 px)."

    def handle(self, *args, **options):
        backup_dir = Path(settings.MEDIA_ROOT) / "originals_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        for post in Post.objects.exclude(image="").exclude(image__isnull=True):
            old_path = Path(post.image.path)
            if not old_path.exists():
                self.stdout.write(self.style.WARNING(f"Introuvable : {post.image.name}"))
                continue

            old_size = old_path.stat().st_size
            result = optimize_image(post.image)
            post.image.close()
            if result is None:
                self.stdout.write(self.style.WARNING(f"Illisible : {post.image.name}"))
                continue

            shutil.copy2(old_path, backup_dir / old_path.name)        # sauvegarde de l'original
            name, content = result
            post.image.save(name, content, save=False)               # écrit la version optimisée
            Post.objects.filter(pk=post.pk).update(image=post.image.name)
            old_path.unlink(missing_ok=True)                         # supprime l'ancien gros fichier

            new_size = Path(post.image.path).stat().st_size
            self.stdout.write(
                f"{old_path.name} : {old_size // 1024} Ko -> {post.image.name} ({new_size // 1024} Ko)"
            )
