"""Module to handle credentials and constants retrieval from database"""

import logging
from typing import Any

from mbu_dev_shared_components.database.connection import RPAConnection

logger = logging.getLogger(__name__)


def get_credentials(credential_name: str) -> dict[str, Any]:
    """Retrieve a credential by name from the database."""
    try:
        with RPAConnection() as conn:
            credential = conn.get_credential(f"{credential_name}")
        return credential
    except Exception as e:
        logger.error("Error retrieving API key: %s", e)
        raise


def get_constant(constant_name: str) -> dict[str, Any]:
    """Retrieve a constant by name from the database."""
    try:
        with RPAConnection() as conn:
            constant = conn.get_constant(f"{constant_name}")
        return constant
    except Exception as e:
        logger.error("Error retrieving constant: %s", e)
        raise
