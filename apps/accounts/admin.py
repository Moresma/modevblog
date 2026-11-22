from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User
    list_display =("username", "email", "first_name", "last_name", "is_active","is_staff",)
    ordering = ("username",)
    search_fields = ("username","email", "first_name", "last_name",)
    fieldsets =((None,{"fields":("username", "email","password",)}),
                ("informations personnelles",{"fields":("first_name", "last_name")}),
                ("permissions",{"fields":("is_active", "is_staff", "is_superuser", "groups","user_permissions",)}),
                ("Dates",{"fields":("last_login", "created_at","updated_at")}),)
    readonly_fields = ("last_login", "created_at","updated_at")