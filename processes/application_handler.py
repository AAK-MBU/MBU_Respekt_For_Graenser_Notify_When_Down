"""Module for handling application startup, and close"""

import logging

logger = logging.getLogger(__name__)


def startup():
    """Function for starting applications"""
    logger.info("Starting applications...")


def soft_close():
    """Function for closing applications softly"""
    logger.info("Closing applications softly...")


def hard_close():
    """Function for closing applications hard"""
    logger.info("Closing applications hard...")


def close():
    """Function for closing applications softly or hardly if necessary"""
    try:
        soft_close()
    except Exception:
        hard_close()


def reset():
    """Function for resetting application"""
    close()
    startup()
