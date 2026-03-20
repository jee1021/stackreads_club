from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# ✅ 1. 커스텀 매니저
class SignupUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, password, **extra_fields)


class SignupUser(AbstractBaseUser, PermissionsMixin):

    class Status(models.TextChoices):
        ACTIVE = 'active', '활성'
        INACTIVE = 'inactive', '비활성'
        SUSPENDED = 'suspended', '정지'

    email = models.EmailField(
        unique=True,
        max_length=255,
        db_index=True
    )

    username = models.CharField(
        max_length=50,
        unique=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 🔥 실무에서 중요
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🔑 인증 필드
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = SignupUserManager()

    class Meta:
        db_table = 'signup_user'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"{self.email} ({self.username})"

    def deactivate(self):
        self.status = self.Status.INACTIVE
        self.is_active = False
        self.save()

    def suspend(self):
        self.status = self.Status.SUSPENDED
        self.is_active = False
        self.save()
