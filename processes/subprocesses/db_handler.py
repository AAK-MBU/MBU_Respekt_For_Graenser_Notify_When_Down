"""Database handler for updating form status in the journalizing database."""

import logging
import os
import urllib.parse

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


def update_form_status_in_database(form_id: str, status: str) -> None:
    """Update form status in the journalizing database."""
    logger.info("Updating form status in the database for form ID: %s", form_id)

    try:
        params = urllib.parse.quote_plus(os.environ["DBCONNECTIONSTRINGPROD"])
        connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
        engine = create_engine(connection_string)
        query = text(
            """UPDATE [RPA].[journalizing].[Journalizing]
            SET status = :status
            WHERE form_id = :form_id"""
        )

        with engine.connect() as connection:
            connection.execute(query, {"status": status, "form_id": form_id})
            connection.commit()

        logger.info("Form ID %s status updated to %s.", form_id, status)

    except Exception as e:
        logger.error("Error updating form status for form ID %s: %s", form_id, e)
        raise
