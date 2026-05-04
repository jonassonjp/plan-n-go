from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Define um usuário como superusuário. Uso: manage.py set_superuser <email>"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="E-mail do usuário a promover.")

    def handle(self, *args, **options):
        email = options["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(f"Usuário '{email}' não encontrado.")

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(update_fields=["is_staff", "is_superuser", "is_active"])
        self.stdout.write(self.style.SUCCESS(f"'{user.email}' agora é superusuário."))
