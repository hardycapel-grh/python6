from ui.components.logger import logger


_SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "credentials",
}


def _redact(value, key=None):
    if key and key.lower() in _SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {name: _redact(item, name) for name, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_redact(item) for item in value)
    return value


def log_event(level, event, **details):
    """
    Unified logging helper for consistent audit logs.

    Example:
        log_event("info", "User created", user="graham", target="wilma")
    """
    safe_details = _redact(details)

    # Build detail string: key='value', key='value'
    detail_str = ", ".join(f"{k}='{v}'" for k, v in safe_details.items())

    # Final message
    message = f"{event}: {detail_str}" if detail_str else event

    # Dispatch to logger.<level>()
    getattr(logger, level)(message)

