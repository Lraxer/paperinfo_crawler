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
    css_selector = "div.core-container > section[id='abstract'] > div[role='paragraph']"

    abstract = get_abstract_base(abs_session, url, req_itv, css_selector)
    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        abstract = get_full_abstract(s, "https://doi.org/10.1145/3627106.3627193", 0)
        print(abstract)
