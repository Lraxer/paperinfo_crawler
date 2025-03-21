import requests
import logging
from get_abstract_base import get_abstract_base

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_full_abstract(abs_session: requests.Session, url: str, req_itv: float) -> str:
    # css_selector = "div.col-span-full.tile-break-3\:col-span-8 > p.col-span-full.py-\[20px\].leading-relaxed"
    css_selector = "div.col-span-full.tile-break-3\:col-span-8 > p"

    abstract = get_abstract_base(abs_session, url, req_itv, css_selector)
    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(
            s,
            r"https://www.vldb.org/pvldb/volumes/17/paper/Language%20Models%20Enable%20Simple%20Systems%20for%20Generating%20Structured%20Views%20of%20Heterogeneous%20Data%20Lakes",
            0,
        )
        print(abstract)
