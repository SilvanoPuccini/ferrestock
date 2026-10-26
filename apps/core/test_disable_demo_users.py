from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.test import TestCase

DEMO_USERNAMES = ("admin_demo", "operador_demo", "consulta_demo")
PUBLISHED_PASSWORDS = ("Admin12345!", "Operador12345!", "Consulta12345!")


class DisableDemoUsersTests(TestCase):
    def setUp(self):
        for username, password in zip(DEMO_USERNAMES, PUBLISHED_PASSWORDS):
            User.objects.create_user(username=username, password=password, is_staff=True)

    def test_demo_accounts_can_no_longer_log_in(self):
        call_command("disable_demo_users")

        for username, password in zip(DEMO_USERNAMES, PUBLISHED_PASSWORDS):
            self.assertFalse(self.client.login(username=username, password=password))
            user = User.objects.get(username=username)
            self.assertFalse(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.has_usable_password())

    def test_open_sessions_of_demo_accounts_are_closed(self):
        self.client.login(username="admin_demo", password="Admin12345!")
        self.assertEqual(Session.objects.count(), 1)

        call_command("disable_demo_users")

        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Session.objects.count(), 0)

    def test_real_accounts_are_untouched(self):
        owner = User.objects.create_user(username="owner", password="a-private-pass-55", is_staff=True)

        call_command("disable_demo_users")

        owner.refresh_from_db()
        self.assertTrue(owner.is_active)
        self.assertTrue(owner.check_password("a-private-pass-55"))

    def test_is_idempotent(self):
        call_command("disable_demo_users")
        call_command("disable_demo_users")

        self.assertFalse(User.objects.filter(username__in=DEMO_USERNAMES, is_active=True).exists())

    def test_published_demo_seed_command_no_longer_exists(self):
        from django.core.management import get_commands

        self.assertNotIn("create_demo_users", get_commands())
