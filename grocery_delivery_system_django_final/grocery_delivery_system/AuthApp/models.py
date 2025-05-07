from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models

class AppUserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, address, password = None, **extra_fields):
        if not email:
            raise ValueError('The Email field is mandatory')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            phone_number=phone_number,
            address=address,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, phone_number, address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, username, phone_number, address, password, **extra_fields)


class AppUser(AbstractUser):

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=False)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    birth_date = models.DateField()
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number', 'address']

    def __str__(self):
        return self.username
    

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)  
    subject = models.CharField(max_length=200, blank=True) 
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.full_name} - {self.email}"