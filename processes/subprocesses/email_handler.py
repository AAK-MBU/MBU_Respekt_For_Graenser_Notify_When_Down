"""Send email with attachment subprocess."""

import logging
import smtplib
from email.message import EmailMessage
from typing import TYPE_CHECKING

from mbu_dev_shared_components.os2forms.documents import download_file_bytes

if TYPE_CHECKING:
    from processes.process_item import EmailContext

logger = logging.getLogger(__name__)


def get_attachment(url: str, api_key: str) -> bytes:
    """Fetch attachment from OS2Forms by url."""
    logger.info("Fetching attachment from OS2Forms...")

    try:
        file_bytes = download_file_bytes(url, api_key)

        if not file_bytes:
            logger.error("No file bytes found.")
            raise ValueError("No file bytes found.")

        logger.info("Successfully fetched attachment.")

        return file_bytes

    except Exception as e:
        logger.error("Error fetching attachment: %s", e)
        raise


def send_email(context: "EmailContext") -> None:
    """Send email with attachment."""
    logger.info("Sending email with attachment for form ID: %s", context.form_id)

    try:
        msg = EmailMessage()
        msg["Subject"] = (
            "Handling kræves: Journalisering fejlede på respekt for grænser "
            "indberetning"
        )
        msg["From"] = context.email_from
        msg["To"] = context.email_to
        msg.set_content(
            f"""
            Til rette vedkommende

            Da der ikke kan oprettes emnesager i GO i nuværende tidsrum, får du
            her en respekt for grænser indberetning tilsendt manuelt.

            Formular ID: {context.form_id}

            Mvh.
            Journaliseringsrobotten
            MBU, Aarhus Kommune
            """
        )

        msg.add_attachment(
            context.data,
            maintype="application",
            subtype="octet-stream",
            filename="respekt-for-graenser.pdf",
        )

        if not context.smtp_server or not context.smtp_port:
            raise ValueError(
                "SMTP_SERVER and SMTP_PORT environment variables must be set"
            )

        with smtplib.SMTP(host=context.smtp_server, port=context.smtp_port) as server:
            server.starttls()
            server.send_message(msg)

        logger.info("Email sent successfully for form ID: %s", context.form_id)

    except Exception as e:
        logger.error("Error sending email for form ID %s: %s", context.form_id, e)
        raise
