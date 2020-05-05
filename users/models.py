import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.urls import reverse


class User(AbstractUser):

    """Custom User Model Definition"""

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_CHOICES = ((GENDER_MALE, "Male"), (GENDER_FEMALE, "Female"))

    LANG_KR = "kr"
    LANG_EN = "en"
    LANG_CHOICES = ((LANG_KR, "KOREAN"), (LANG_EN, "ENGLISH"))

    CURRNECY_KRW = "krw"
    CURRENCY_USD = "usd"
    CURRENCY_CHOICES = ((CURRNECY_KRW, "KRW"), (CURRENCY_USD, "USD"))

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"
    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGIN_KAKAO, "Kakao"),
    )

    avatar = models.ImageField(upload_to="avatars", blank=True)
    nickname = models.CharField(max_length=20, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(default="", blank=True)
    birthdate = models.DateField(null=True, blank=True)
    language = models.CharField(
        choices=LANG_CHOICES, max_length=2, blank=True, default=LANG_KR
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=3, blank=True, default=CURRNECY_KRW
    )
    superhost = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_authKey = models.CharField(max_length=20, default="", blank=True)
    login_method = models.CharField(
        choices=LOGIN_CHOICES, max_length=50, default=LOGIN_EMAIL
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"pk": self.pk})

    def verify_email(self):
        if self.email_verified is False:
            key = uuid.uuid4().hex[:20]
            self.email_authKey = key
            html_message = render_to_string("emails/verify_email.html", {"key": key})
            send_mail(
                subject="Verify Airbnb Account",
                message=strip_tags(html_message),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.email],
                fail_silently=True,
                html_message=html_message,
            )
            self.save()
        return
