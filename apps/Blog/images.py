"""Redimensionnement des images d'articles à une taille adaptée au web."""
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

# Plus grand côté autorisé, en pixels (assez pour un écran large ou Retina).
MAX_SIZE = 1600
# Qualité JPEG : 82 = bon compromis entre netteté et poids.
JPEG_QUALITY = 82


def optimize_image(field_file, max_size=MAX_SIZE):
    """
    Lit l'image, la redimensionne si besoin et retourne (nouveau_nom, ContentFile).
    Retourne None si le fichier n'est pas une image lisible.
    """
    try:
        field_file.open("rb")                      # ouvre le fichier envoyé
        img = Image.open(field_file)
        img = ImageOps.exif_transpose(img)         # redresse les photos prises de travers (téléphone)
    except Exception:
        return None

    img.thumbnail((max_size, max_size), Image.LANCZOS)   # réduit sans déformer, jamais agrandi

    buffer = BytesIO()
    stem = Path(field_file.name).stem              # nom sans dossier ni extension

    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

    if has_alpha:
        # Image avec transparence : on garde le PNG
        img.save(buffer, format="PNG", optimize=True)
        name = f"{stem}.png"
    else:
        # Photo classique : JPEG optimisé et progressif (s'affiche vite)
        img.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        name = f"{stem}.jpg"

    return name, ContentFile(buffer.getvalue())
