from django.contrib import admin
from django.utils.html import format_html

from .models import PageBackground


@admin.register(PageBackground)
class PageBackgroundAdmin(admin.ModelAdmin):
    list_display = ("page", "preview", "updated_at")
    readonly_fields = ("preview",)

    @admin.display(description="Aperçu")
    def preview(self, obj):
        # Petite miniature de l'image dans l'admin.
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px">', obj.image.url)
        return "—"
