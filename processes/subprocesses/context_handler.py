"""Context handler"""

from dataclasses import dataclass


@dataclass
class EmailContext:
    """Context dataclass for email sending"""

    data: bytes
    form_id: str
    email_to: str
    email_from: str
    smtp_server: str | None = None
    smtp_port: int | None = None
