from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Redefine a senha de todos os usuários para '123'."

    def handle(self, *args, **options):
        users = User.objects.all()
        count = 0
        for user in users:
            user.set_password("123")
            user.save(update_fields=["password"])
            self.stdout.write(f"  {user.email}")
            count += 1
        self.stdout.write(self.style.SUCCESS(f"\n{count} senha(s) redefinida(s) para '123'."))
