import logging
from time import sleep

import requests

from src.settings import retry_interval

logger = logging.getLogger(__name__)


# Decorator
# Reference: https://kingname.info/2023/06/11/retry-in-requests/
def retry(func):
    def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    logger.warning(
                        f"Cannot access {args[1]} . Exception: {e.__class__.__name__} Retry {time + 1}/3 after {retry_interval} sec."
                    )
                    sleep(retry_interval)
        return None

    return wrap


@retry
def make_request(session: requests.Session, url: str, headers=None):
    if headers is None:
        res = session.get(url)
    else:
        res = session.get(url, headers=headers)
    return res


def retry_async(func):
    async def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    logger.warning(
                        f"Cannot access {args[0]} . Exception: {e.__class__.__name__} Retry {time + 1}/3 after {retry_interval} sec."
                    )
                    sleep(retry_interval)
        return None

    return wrap
