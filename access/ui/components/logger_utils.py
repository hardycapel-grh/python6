from ui.components.logger import logger

def log_event(level, event, **details):
    """
    Unified logging helper for consistent audit logs.

    Example:
        log_event("info", "User created", user="graham", target="wilma")
    """
    # Build detail string: key='value', key='value'
    detail_str = ", ".join(f"{k}='{v}'" for k, v in details.items())

    # Final message
    message = f"{event}: {detail_str}" if detail_str else event

    # Dispatch to logger.<level>()
    getattr(logger, level)(message)

