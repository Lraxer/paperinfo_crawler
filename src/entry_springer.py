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


def get_full_abstract(
    abs_session: requests.Session, url: str, req_itv: float
) -> str | None:
    css_selector = "section[data-title='Abstract'] > div.c-article-section > div.c-article-section__content > p"

    abstract = get_abstract_base(abs_session, url, req_itv, css_selector)
    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s,
            "https://link.springer.com/chapter/10.1007/978-981-99-7356-9_1",
            0,
        )
        print(abstract)
