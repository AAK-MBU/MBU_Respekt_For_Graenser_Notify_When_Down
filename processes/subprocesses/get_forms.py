"""Module to interact with the journalizing database and fetch forms."""

import logging
import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text


def get_forms(logger: logging.Logger) -> list[dict] | None:
    """Fetch forms with status 'Failed' from the journalizing database."""
    logger.info("Fetching forms with status 'InProgress' from the database.")

    try:
        db_conn = os.getenv("DBConnectionStringDev")
        if not db_conn:
            logger.error("Database connection string is not set in environment variable 'DBConnectionStringDev'.")
            return None
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quote_plus(db_conn)}")
        query = text(
            """SELECT * FROM [RPA].[journalizing].[view_Journalizing]
            WHERE form_type in ('respekt_for_graenser','respekt_for_graenser_privat','indmeld_kraenkelser_af_boern')
            AND status = :status ORDER BY form_submitted_date ASC"""
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
