import requests
import logging
from settings import req_headers
from bs4 import BeautifulSoup
from request_wrap import make_request
from time import sleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_full_abstract(abs_session: requests.Session, url: str, req_itv: float) -> str:
    css_selector = "h1[data-p13n='journal-article']"

    abstract = None

    if url == "":
        return None

    sleep(req_itv)

    res = make_request(abs_session, url, headers=req_headers)
    if res.status_code != 200:
        logger.warning(
            "Cannot access {} , status code: {}.".format(url, res.status_code)
        )
    else:
        abs_soup = BeautifulSoup(res.text, "html.parser")
        abs_tags = abs_soup.select_one(css_selector)
        if abs_tags != []:
            abstract = abs_tags["data-abstract"]
        
        # iospress的网站对于Special issue等非期刊论文的条目的设置
        if abstract == "No abstract":
            abstract = None

    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s,
            "https://content.iospress.com/articles/journal-of-computer-security/jcs230047",
            0,
        )
        print(abstract)
