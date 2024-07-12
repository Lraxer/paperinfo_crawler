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
        # 有两个一样的 `div.field...`，选取第二个标签，
        # 以及最后需要选取全部的p标签
        abs_tags = abs_soup.select(
            "div.content > div.field.field-name-field-paper-description.field-type-text-long.field-label-above:nth-child(2) > div.field-items > div.field-item.odd > p"
        )
        if abs_tags != []:
            abstract = " ".join([abs_tag.get_text() for abs_tag in abs_tags])

        # 额外检查，可能是多余的
        if abstract == "":
            abstract = None

    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s, "https://www.usenix.org/conference/usenixsecurity22/presentation/zeng", 0
        )
        print(abstract)
