import requests
from time import sleep
from conf import req_headers
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_full_abstract(url: str, req_itv: float) -> str:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)

    res = requests.get(url, headers=req_headers)
    if res.status_code != 200:
        logger.warning(
            "Cannot access {}, status code: {}.".format(url, res.status_code)
        )
    else:
        abs_soup = BeautifulSoup(res.text, "html.parser")
        # 有两个一样的 `div.field...`，选取第二个标签
        abs_tag = abs_soup.select_one(
            "div.content > div.field.field-name-field-paper-description.field-type-text-long.field-label-above:nth-child(2) > div.field-items > div.field-item.odd > p"
        )
        if abs_tag is not None:
            abstract = abs_tag.get_text()
    return abstract


if __name__ == "__main__":
    abstract = get_full_abstract(
        "https://www.usenix.org/conference/usenixsecurity23/presentation/li-ang", 0
    )
    print(abstract)
