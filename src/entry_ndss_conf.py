import requests
from time import sleep
from conf import req_headers
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


def get_full_abstract(abs_session: requests.Session, url: str, req_itv: float) -> str:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)

    res = make_request(abs_session, url, headers=req_headers)
    if res.status_code != 200:
        logger.warning(
            "Cannot access {}, status code: {}.".format(url, res.status_code)
        )
    else:
        abs_soup = BeautifulSoup(res.text, "html.parser")
        # request得到的原始页面和浏览器直接查看到的html不一样，需要去Network里面找到原始响应
        abs_tags = abs_soup.select(
            "div.entry-content > div.paper-data > p:nth-child(2) > p"
        )
        if abs_tags != []:
            abstract = " ".join(
                [abs_tag.get_text() for abs_tag in abs_tags if abs_tag.get_text() != ""]
            )
    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s,
            "https://www.ndss-symposium.org/ndss-paper/assessing-the-impact-of-interface-vulnerabilities-in-compartmentalized-software/",
            0,
        )
        print(abstract)
