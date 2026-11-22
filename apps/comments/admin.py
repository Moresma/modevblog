from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ("author", "post", "short_content", "created_at", )
    list_filter = ("created_at",)
    search_fields = ( "content", "author__username", "post__title",)
    ordering = ( "-created_at",)
    readonly_fields = ("created_at", "updated_at",)

    def short_content(self, obj):
        return obj.content[:50] + (
            "..." if len(obj.content) > 50 else ""
        )

    short_content.short_description = "Contenu"