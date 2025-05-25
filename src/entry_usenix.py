import logging

import requests

from get_abstract_base import get_abstract_base

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_full_abstract(abs_session: requests.Session, url: str, req_itv: float) -> str:
    # 有两个一样的 `div.field...`，选取第二个标签，
    # 以及最后需要选取全部的p标签
    css_selector = "div.content > div.field.field-name-field-paper-description.field-type-text-long.field-label-above:nth-child(2) > div.field-items > div.field-item.odd > p"

    abstract = get_abstract_base(abs_session, url, req_itv, css_selector)
    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s, "https://www.usenix.org/conference/usenixsecurity22/presentation/zeng", 0
        )
        print(abstract)
