from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    """custom user model"""

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_CHOICES = ((GENDER_MALE, "Male"), (GENDER_FEMALE, "Female"))

    LANG_KR = "kr"
    LANG_EN = "en"
    LANG_CHOICES = ((LANG_KR, "KOREAN"), (LANG_EN, "ENGLISH"))

    CURRNECY_KRW = "krw"
    CURRENCY_USD = "usd"
    CURRENCY_CHOICES = ((CURRNECY_KRW, "KRW"), (CURRENCY_USD, "USD"))

    avatar = models.ImageField(blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(default="", blank=True)
    birthdate = models.DateField(null=True, blank=True)
    language = models.CharField(choices=LANG_CHOICES, max_length=2, blank=True)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3, blank=True)
    superhost = models.BooleanField(default=False)

    def __str__(self):
        return self.username
