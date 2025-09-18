"""Helper module to call some functionality in Automation Server using the API"""

import json
import logging
import os
import sys

import requests
from automation_server_client import WorkItem, Workqueue
from dotenv import load_dotenv


def get_workqueue_items(workqueue: Workqueue):
    """
    Retrieve items from the specified workqueue.
    If the queue is empty, return an empty list.
    """
    load_dotenv()

    url = os.getenv("ATS_URL")
    token = os.getenv("ATS_TOKEN")

    if not url or not token:
        raise EnvironmentError("ATS_URL or ATS_TOKEN is not set in the environment")

    headers = {"Authorization": f"Bearer {token}"}

    workqueue_items = set()
    page = 1
    size = 200  # max allowed

    while True:
        full_url = f"{url}/workqueues/{workqueue.id}/items?page={page}&size={size}"
        response = requests.get(full_url, headers=headers, timeout=60)
        response.raise_for_status()

        res_json = response.json().get("items", [])

        if not res_json:
            break

        for row in res_json:
            ref = row.get("reference")
            if ref:
                workqueue_items.add(ref)

        page += 1

    return workqueue_items


def get_item_info(item: WorkItem):
    """Unpack item"""
    return item.data["item"]["data"], item.data["item"]["reference"]


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        args:
            record (logging.LogRecord): The log record to format.
        returns:
            str: The formatted log record as a JSON string.
        """
        data = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "msg": record.getMessage(),
        }
        std = set(vars(logging.makeLogRecord({})).keys()) | {"message", "asctime"}
        extras = {k:v for k,v in record.__dict__.items() if k not in std and not k.startswith("_")}
        if extras:
            data["extra"] = extras
        return json.dumps(data, ensure_ascii=False)


def init_logger():
    """Initialize the root logger with JSON formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
