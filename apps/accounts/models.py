from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username =models.CharField(max_length=150, unique=True, verbose_name="Nom d'utilisateur")
    email = models.EmailField(unique= True, blank=True, null=True, verbose_name= "Adresse email",)
    first_name = models.CharField(max_length=100, blank= True, verbose_name="Prénom",)
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nom",)
    is_active= models.BooleanField(default=True, verbose_name= "Compte actif",)
    is_staff = models.BooleanField(default=False, verbose_name="Accès a l'administration")
    created_at= models.DateTimeField(auto_now_add=True, verbose_name="Date de création",)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")


    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username