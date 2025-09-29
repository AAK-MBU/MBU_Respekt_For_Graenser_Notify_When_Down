"""Module to handle item processing"""

import logging

from processes.subprocesses.context_handler import EmailContext
from processes.subprocesses.credentials_constant_handler import (
    get_constant,
    get_credentials,
)
from processes.subprocesses.db_handler import update_form_status_in_database
from processes.subprocesses.email_handler import get_attachment, send_email

logger = logging.getLogger(__name__)


def process_item(item_data: dict, item_reference: str) -> None:
    """Function to handle item processing"""
    try:
        api_key = get_credentials("os2_api")["decrypted_password"]

        attachment_data = get_attachment(
            url=item_data.get("attachment_url", ""),
            api_key=api_key,
        )

        email_context = EmailContext(
            data=attachment_data,
            form_id=item_reference,
            email_to=get_constant("rfg_email")["value"],
            email_from=get_constant("E-mail")["value"],
            smtp_server=get_constant("smtp_adm_server")["value"],
            smtp_port=int(get_constant("smtp_port")["value"]),
        )

        send_email(context=email_context)

        update_form_status_in_database(form_id=item_reference, status="Manual")

    except Exception as e:
        logger.error("Error processing item %s: %s", item_reference, e)
        raise
