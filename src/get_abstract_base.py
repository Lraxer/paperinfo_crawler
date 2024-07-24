import requests
from time import sleep
from settings import req_headers
from bs4 import BeautifulSoup
import logging
from request_wrap import make_request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_abstract_base(
    abs_session: requests.Session, url: str, req_itv: float, css_selector: str
) -> str:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)

    res = make_request(abs_session, url, headers=req_headers)
    # 请求失败
    if res is None:
        return None
    
    if res.status_code != 200:
        logger.warning(
            "Cannot access {} , status code: {}.".format(url, res.status_code)
        )
    else:
        abs_soup = BeautifulSoup(res.text, "html.parser")
        abs_tags = abs_soup.select(css_selector)
        if abs_tags != []:
            abstract = " ".join([abs_tag.get_text() for abs_tag in abs_tags])

        # 额外检查，可能是多余的
        if abstract == "":
            abstract = None

    return abstract
