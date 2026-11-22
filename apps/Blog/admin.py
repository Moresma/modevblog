from django.contrib import admin
from.models import Category, Tag, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_at", "updated_at")
    search_fields =("name",)
    list_filter = ("parent",)
    fields = ("name", "description", "cta", "cover", "parent")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display =("name", "created_at", "updated_at")
    search_fields =("name",)
   
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=("title", "category","author", "status", "published_at","created_at")
    search_fields =("title", "content", "excerpt", )
    list_filter = ("status", "category", "author")
    date_hierarchy = "created_at"
    fieldsets = (
        ("Article", { "fields":("title", "excerpt", "content", "image",)},),
        ("Classement",{"fields":("category", "tags")},),
        ("Publication",{"fields":("author", "status", "published_at",)},),
    )