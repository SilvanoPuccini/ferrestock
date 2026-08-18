from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied


class AppPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied


def require_perms(*perms):
    """Equivalente a AppPermissionMixin para vistas de función: exige que el
    usuario tenga todos los permisos indicados, o lanza PermissionDenied (403)."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.has_perms(perms):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
