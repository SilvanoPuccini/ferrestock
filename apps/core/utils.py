from apps.core.models import AuditLog


def log_audit_action(
    *,
    user,
    module,
    action,
    object_type,
    object_id="",
    object_repr="",
    description="",
    metadata=None,
):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        module=module,
        action=action,
        object_type=object_type,
        object_id=str(object_id) if object_id else "",
        object_repr=object_repr,
        description=description,
        metadata=metadata or {},
    )
