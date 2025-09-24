"""Module to interact with the journalizing database and fetch forms."""

import logging
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


def get_forms() -> list[dict] | None:
    """Fetch forms with status 'Failed' from the journalizing database."""
    logger.info("Fetching forms with status 'Failed' from the database.")

    try:
        load_dotenv()
        db_conn = os.getenv("DBCONNECTIONSTRINGPROD")
        if not db_conn:
            logger.error("Error getting database connection string.")
            return None
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quote_plus(db_conn)}")
        query = text(
            """
            SELECT *
            FROM [RPA].[journalizing].[view_Journalizing]
            WHERE status = :status
            AND form_type in (
                'respekt_for_graenser',
                'respekt_for_graenser_privat',
                'indmeld_kraenkelser_af_boern'
            )
            ORDER BY form_submitted_date ASC"""
        )

        with engine.connect() as connection:
            result = connection.execute(query, {"status": "Failed"})
            rows = result.mappings().all()

        if not rows:
            return None

        logger.info("Found %d forms.", len(rows))

        return [dict(row) for row in rows]

    except Exception as e:
        logger.error("Error fetching forms from database: %s", e)
        raise
