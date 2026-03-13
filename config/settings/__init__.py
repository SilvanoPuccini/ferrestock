import os
if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.production":
    from .production import *
else:
    from .base import *
    from .local import *
