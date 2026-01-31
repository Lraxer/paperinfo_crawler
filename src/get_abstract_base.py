import logging
from time import sleep

import requests
from bs4 import BeautifulSoup

from src.request_wrap import make_request
from src.settings import req_headers

logger = logging.getLogger(__name__)


def get_abstract_base(
    abs_session: requests.Session, url: str, req_itv: float, css_selector: str
) -> str | None:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)

    res = make_request(abs_session, url, headers=req_headers)
    # 请求失败
    if res is None:
        logger.warning(f"Request to {url} failed.")
        return None

    if res.status_code != 200:
        logger.warning(f"Cannot access {url} , status code: {res.status_code}.")
    else:
        abs_soup = BeautifulSoup(res.text, "html.parser")
        abs_tags = abs_soup.select(css_selector)
        if abs_tags != []:
            abstract = " ".join([abs_tag.get_text() for abs_tag in abs_tags])

        # 额外检查，可能是多余的
        if abstract == "":
            abstract = None

    return abstract
