from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
import logging
import json

logger = logging.getLogger(__name__)


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
            ValueError: If email is not provided or password is invalid.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            if not self.validate_password(password):
                raise ValueError(
                    'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
            try:
                validate_password(password)
                user.set_password(password)
            except ValidationError as e:
                raise ValueError(f"Invalid password: {', '.join(e.messages)}")
        else:
            raise ValueError('Password must be provided')
        user.save(using=self._db)
        logger.info(f"New user created: {email}")
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a new superuser with the given email and password.

        Args:
            email (str): Superuser's email address.
            password (str, optional): Superuser's password.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: Newly created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(email, password, **extra_fields)
        if 'Admin' not in self.ALLOWED_ROLES:
            raise ValidationError(f"Cannot add role: Admin")
        user.add_role('Admin')
        logger.info(f"New superuser created: {email}")
        return user


class Role(models.Model):
    """Model to represent user roles."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending Django's AbstractBaseUser and PermissionsMixin.

    This model includes fields for user authentication, personal information,
    and role management. It supports multiple roles for users, soft delete
    functionality, and custom methods for role manipulation.
    """
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    ALLOWED_ROLES = ['Investor', 'Startup', 'Admin']

    email = models.EmailField(max_length=255, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    roles = models.ManyToManyField(Role, related_name='users')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, default='')
    about_me = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_soft_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    original_data = models.JSONField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_phone']

    def __str__(self):
        """Return a string representation of the user."""
        return self.email

    def get_full_name(self):
        """Return the user's full name."""
        first_name = self.first_name.strip() or 'Unknown first name'
        last_name = self.last_name.strip() or 'Unknown last name'
        return f"{first_name} {last_name}".strip()

    def get_roles_display(self):
        """Return a string representation of the user's roles."""
        return ', '.join(role.name for role in self.roles.all())

    def add_role(self, role_name):
        """
        Add a role to the user.

        Args:
            role_name (str): Name of the role to add.

        Raises:
            ValidationError: If the role is invalid or already assigned.
        """
        if role_name not in self.ALLOWED_ROLES:
            raise ValidationError(f"Cannot add role: {role_name}")
        if not self.is_active:
            raise ValidationError("This account is not active.")
        if self.is_soft_deleted:
            raise ValidationError("This account is deleted.")
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise ValidationError(f"Role '{role_name}' does not exist.")
        if self.roles.filter(name=role_name).exists():
            raise ValidationError(f"You already have the role: {role_name}")
        self.roles.add(role)
        self.save()
        logger.info(f"Role '{role_name}' added to user {self.email}")

    def remove_role(self, role_name):
        """
        Remove a role from the user.

        Args:
            role_name (str): Name of the role to remove.

        Raises:
            ValidationError: If the role is invalid or not assigned.
        """
        if role_name not in self.ALLOWED_ROLES:
            raise ValidationError(f"Cannot remove role: {role_name}")
        if not self.is_active:
            raise ValidationError("This account is not active.")
        if self.is_soft_deleted:
            raise ValidationError("This account is deleted.")
        try:
            role = self.roles.get(name=role_name)
        except Role.DoesNotExist:
            raise ValidationError(f"User does not have the role: {role_name}")
        self.roles.remove(role)
        self.save()
        logger.info(f"Role '{role_name}' removed from user {self.email}")

    def has_role(self, role_name):
        """
        Check if the user has a specific role.

        Args:
            role_name (str): Name of the role to check.

        Returns:
            bool: True if the user has the role, False otherwise.
        """
        if role_name not in self.ALLOWED_ROLES:
            raise ValidationError(f"Role '{role_name}' is not allowed.")
        return self.roles.filter(name=role_name).exists()

    def is_admin(self):
        """Check if the user has admin role."""
        return self.has_role('Admin')

    def has_multiple_roles(self):
        """Check if the user has multiple roles."""
        return self.roles.exists() and self.roles.count() > 1

    def soft_delete(self):
        """
        Soft delete the user account.

        This method deactivates the account, sets the deleted_at timestamp,
        and marks the account as deleted. Original user data is preserved.

        Raises:
            ValidationError: If the account is already inactive or deleted.
        """
        if not self.is_active or self.is_soft_deleted:
            raise ValidationError("This account is already inactive or deleted.")

        original_data = {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_phone': self.user_phone,
            'about_me': self.about_me,
        }
        self.original_data = json.dumps(original_data)

        self.email = f"deleted_{self.id}@example.com"
        self.first_name = "Deleted"
        self.last_name = "User"
        self.user_phone = ""
        self.about_me = ""
        self.profile_picture.delete(save=False)
        self.is_active = False
        self.is_soft_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        logger.info(f"User {self.id} soft deleted")

    def reactivate(self):
        """
        Reactivate a soft-deleted user account.

        This method reactivates the account and restores the original user data.

        Raises:
            ValidationError: If the account is already active or not soft deleted.
        """
        if self.is_active or not self.is_soft_deleted:
            raise ValidationError("This account is already active or not soft deleted.")

        if self.original_data:
            original_data = json.loads(self.original_data)
            self.email = original_data['email']
            self.first_name = original_data['first_name']
            self.last_name = original_data['last_name']
            self.user_phone = original_data['user_phone']
            self.about_me = original_data['about_me']
            self.original_data = None

        self.is_active = True
        self.is_soft_deleted = False
        self.deleted_at = None
        self.save()
        logger.info(f"User {self.id} reactivated")

    def save(self, *args, **kwargs):
        """
        Save the user instance to the database.

        This method overrides the default save method to ensure
        the email is always normalized before saving.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.email = self.email.lower().strip()

        if User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists.")

        super().save(*args, **kwargs)

    class Meta:
        unique_together = [('email', 'is_active')]
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        default_manager_name = 'objects'
