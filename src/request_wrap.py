import requests
import logging
from time import sleep

from settings import retry_interval

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


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
                        "Cannot access {} . Exception: {} Retry {}/3 after {} sec.".format(
                            args[1], e.__class__.__name__, time + 1, retry_interval
                        )
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
