"""Module to hande queue population"""

import asyncio
import json
import logging

from automation_server_client import Workqueue

from helpers import config
from processes.subprocesses.get_forms import get_forms


def retrieve_items_for_queue(logger: logging.Logger) -> list[dict]:
    """Function to populate queue"""
    forms = get_forms(logger=logger)

    if forms is None:
        logger.info("No forms found")
        return []

    data = []
    references = []

    for form in forms:
        form_id = form.get("form_id")
        try:
            form_data = json.loads(form.get("form_data", "{}"))
            attachment_url = form_data["data"]["attachments"]["respekt_for"]["url"]
            references.append(form_id)
            data.append({"attachment_url": attachment_url})
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Error parsing form data for form_id {form_id}: {e}")
            continue

    items = [
        {"reference": ref, "data": d} for ref, d in zip(references, data, strict=True)
    ]

    return items


async def concurrent_add(
    workqueue: Workqueue, items: list[dict], logger: logging.Logger
) -> None:
    """
    Populate the workqueue with items to be processed.
    Uses concurrency and retries with exponential backoff.

    Args:
        workqueue (Workqueue): The workqueue to populate.
        items (list[dict]): List of items to add to the queue.
        logger (logging.Logger): Logger for logging messages.

    Returns:
        None

    Raises:
        Exception: If adding an item fails after all retries.
    """
    sem = asyncio.Semaphore(config.MAX_CONCURRENCY)

    async def add_one(it: dict):
        reference = str(it.get("reference") or "")
        data = {"item": it}

        async with sem:
            for attempt in range(1, config.MAX_RETRIES + 1):
                try:
                    work_item = await asyncio.to_thread(
                        workqueue.add_item, data, reference
                    )
                    logger.info(f"Added item to queue: {work_item}")
                    return True
                except Exception as e:
                    if attempt >= config.MAX_RETRIES:
                        logger.error(
                            f"Failed to add item {reference} after {attempt} attempts: {e}"
                        )
                        return False
                    backoff = config.RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        f"Error adding {reference} (attempt {attempt}/{config.MAX_RETRIES}). "
                        f"Retrying in {backoff:.2f}s... {e}"
                    )
                    await asyncio.sleep(backoff)

    if not items:
        logger.info("No new items to add.")
        return

    results = await asyncio.gather(*(add_one(i) for i in items))
    successes = sum(1 for r in results if r)
    failures = len(results) - successes
    logger.info(
        f"Summary: {successes} succeeded, {failures} failed out of {len(results)}"
    )
