from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

# Demo accounts whose passwords were published in this public repository.
DEMO_USERNAMES = ("admin_demo", "operador_demo", "consulta_demo")


class Command(BaseCommand):
    help = "Desactiva los usuarios demo publicados y cierra sus sesiones abiertas."

    def handle(self, *args, **options):
        demo_ids = set()
        for user in User.objects.filter(username__in=DEMO_USERNAMES):
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            user.set_unusable_password()
            user.save()
            demo_ids.add(str(user.pk))

        closed = 0
        for session in Session.objects.all():
            if session.get_decoded().get("_auth_user_id") in demo_ids:
                session.delete()
                closed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuarios demo desactivados: {len(demo_ids)} | sesiones cerradas: {closed}"
            )
        )
