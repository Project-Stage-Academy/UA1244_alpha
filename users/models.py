from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password


class CustomUserManager(BaseUserManager):
    """Custom user manager for the User model."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a new user with the given email and password.

        Args:
            email (str): User's email address.
            password (str, optional): User's password.
            **extra_fields: Additional fields for the user.

        Returns:
            User: Newly created user instance.

        Raises:
            ValueError: If email is not provided or password is not set.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
            validate_password(password, user)
        else:
            raise ValueError('Password must be provided')
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Create and save a new superuser with the given email and password.

        Args:
            email (str): Superuser's email address.
            password (str, optional): Superuser's password.

        Returns:
            User: Newly created superuser instance.
        """
        user = self.create_user(
            email,
            password=password,
            first_name='Admin',
            last_name='User',
            user_phone='',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            role=User.ADMIN
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending Django's AbstractBaseUser and PermissionsMixin.

    This model includes fields for user authentication, personal information,
    and role management. It supports multiple roles for users, soft delete
    functionality, and custom methods for role manipulation.
    """

    USER = 1
    INVESTOR = 2
    STARTUP = 4
    ADMIN = 8

    ROLE_CHOICES = [
        (USER, 'User'),
        (INVESTOR, 'Investor'),
        (STARTUP, 'Startup'),
        (ADMIN, 'Admin'),
    ]

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=USER, db_index=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    about_me = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    original_email = models.EmailField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_phone']

    def __str__(self):
        """Return a string representation of the user."""
        return self.email

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_roles_display(self):
        """Return a string representation of the user's roles."""
        return ', '.join(name for value, name in self.ROLE_CHOICES if self.role & value)

    def add_role(self, role_name):
        """
        Add a role to the user.

        Args:
            role_name (str): Name of the role to add.

        Raises:
            ValidationError: If the role is invalid or already assigned.
        """
        role_dict = {r[1].upper(): r[0] for r in self.ROLE_CHOICES}
        if role_name.upper() not in ['INVESTOR', 'STARTUP']:
            raise ValidationError("You can only add Investor or Startup roles.")
        if self.has_role(role_name):
            raise ValidationError(f"You already have the role: {role_name}")
        self.role |= role_dict[role_name.upper()]
        self.save()

    def remove_role(self, role_name):
        """
        Remove a role from the user.

        Args:
            role_name (str): Name of the role to remove.

        Raises:
            ValidationError: If the role is invalid or not assigned.
        """
        role_dict = {r[1].upper(): r[0] for r in self.ROLE_CHOICES}
        if role_name.upper() not in ['INVESTOR', 'STARTUP']:
            raise ValidationError("Users can only remove Investor or Startup roles.")
        if not self.has_role(role_name):
            raise ValidationError(f"User does not have the role: {role_name}")
        self.role &= ~role_dict[role_name.upper()]
        if self.role == 0:
            self.role = self.USER
        self.save()

    def has_role(self, role_name):
        """
        Check if the user has a specific role.

        Args:
            role_name (str): Name of the role to check.

        Returns:
            bool: True if the user has the role, False otherwise.
        """
        role_dict = {r[1].upper(): r[0] for r in self.ROLE_CHOICES}
        return self.role & role_dict.get(role_name.upper(), 0) != 0

    def is_admin(self):
        """Check if the user has admin role."""
        return bool(self.role & self.ADMIN)

    def has_multiple_roles(self):
        """Check if the user has multiple roles."""
        return bin(self.role).count('1') > 1

    def soft_delete(self):
        """
        Soft delete the user account.

        This method deactivates the account, sets the deleted_at timestamp,
        and anonymizes user data.

        Raises:
            ValidationError: If the account is already inactive or deleted.
        """
        if not self.is_active:
            raise ValidationError("This account is already inactive.")
        if self.deleted_at:
            raise ValidationError("This account has already been deleted.")
        self.is_active = False
        self.deleted_at = timezone.now()
        self.original_email = self.email
        self.email = f"deleted_{self.id}_{self.email}"
        self.first_name = "Deleted"
        self.last_name = "User"
        self.user_phone = ""
        self.about_me = ""
        self.profile_picture.delete(save=False)
        self.save()

    def reactivate(self):
        """
        Reactivate a soft-deleted user account.

        This method reactivates the account, clears the deleted_at timestamp,
        and restores the original email.

        Raises:
            ValidationError: If the account is already active or not deleted.
        """
        if self.is_active:
            raise ValidationError("This account is already active.")
        if not self.deleted_at:
            raise ValidationError("This account was not deleted.")
        self.is_active = True
        self.deleted_at = None
        self.email = self.original_email
        self.original_email = None
        self.save()

    def save(self, *args, **kwargs):
        """
        Save the user instance to the database.

        This method overrides the default save method to validate the password
        before saving a new user instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if self._state.adding and self.password:
            validate_password(self.password, self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
