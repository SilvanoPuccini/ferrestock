from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea usuarios demo para Administrador, Operador y Consulta."

    def handle(self, *args, **options):
        users_config = [
            {
                "username": "admin_demo",
                "email": "admin@ferrestock.local",
                "password": "Admin12345!",
                "group": "Administrador",
                "is_staff": True,
            },
            {
                "username": "operador_demo",
                "email": "operador@ferrestock.local",
                "password": "Operador12345!",
                "group": "Operador",
                "is_staff": False,
            },
            {
                "username": "consulta_demo",
                "email": "consulta@ferrestock.local",
                "password": "Consulta12345!",
                "group": "Consulta",
                "is_staff": False,
            },
        ]

        for config in users_config:
            user, created = User.objects.get_or_create(
                username=config["username"],
                defaults={
                    "email": config["email"],
                    "is_staff": config["is_staff"],
                },
            )

            if created:
                user.set_password(config["password"])
                user.is_staff = config["is_staff"]
                user.save()
            else:
                user.email = config["email"]
                user.is_staff = config["is_staff"]
                user.set_password(config["password"])
                user.save()

            group = Group.objects.get(name=config["group"])
            user.groups.clear()
            user.groups.add(group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario listo: {config['username']} | grupo: {config['group']}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Usuarios demo creados/actualizados correctamente."))
