from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models, IntegrityError

from rest_framework.exceptions import ValidationError


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address.')

        user = self.model(**kwargs)
        email = self.normalize_email(email)
        user.email = email
        user.name = name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password, **kwargs):
        
        u = self.create_user(email, name ,password, **kwargs)
        u.is_staff = True
        u.is_superuser = True

        u.save(using=self._db)
        return u


class MyUser(AbstractBaseUser):

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    picture_id = models.IntegerField(blank=False, default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'picture_id']

    """
    groupID = models.ForeignKey(members, related_name='group_member', on_delete=models.CASCADE)

    """
    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def get_is_staff(self):
        return self.is_staff
