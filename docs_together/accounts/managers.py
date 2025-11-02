from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email_address, password=None, **kwargs):
        user = self.model(email_address=self.normalize_email(email_address), **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email_address, password=None, **kwargs):
        user = self.create_user(email_address, password, **kwargs)
        user.is_staff = True
        user.save()
        return user
