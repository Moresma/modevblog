from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self,username,  email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire.")
        username = username.strip()

        if not username:
            raise ValueError("Le nom d'utilisateur est obligatoire.")

        if email:
         email= self.normalize_email(email)

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        user = self.model(username =username, email= email, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)

        return user

    def create_superuser(self, username, email=None, password = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
      
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff = True")

        if extra_fields.get ("is_superuser") is not True:
            raise ValueError ("le superutilisateur doit avoir is_superuser = True.")


        return self.create_user (
            username = username , email=email, password=password, **extra_fields
        )