from apps.core.management.commands.disable_demo_users import Command as DisableDemoUsersCommand


class Command(DisableDemoUsersCommand):
    """Legacy name kept for start commands configured outside render.yaml.

    It no longer creates demo users: it disables them, exactly like disable_demo_users.
    """

    help = "Alias legado de disable_demo_users: desactiva los usuarios demo publicados."
