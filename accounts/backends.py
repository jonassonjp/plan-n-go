"""
Plan N'Go — Backend de autenticação por e-mail
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Autentica usando e-mail + senha em vez de username + senha.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Aceita tanto 'username' quanto 'email' como chave
        email = kwargs.get("email", username)

        if not email or not password:
            return None

        try:
            user = User.objects.get(email__iexact=email.strip())
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
