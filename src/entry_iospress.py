import logging
from time import sleep
from urllib.parse import urlparse

import requests
import zendriver as zd
from bs4 import BeautifulSoup

from src.request_wrap import make_request, retry_async
from src.settings import req_headers

logger = logging.getLogger(__name__)


@retry_async
async def get_abs_impl(url: str, driver: zd.Browser) -> str:
    button_css_selector = "button[id='onetrust-reject-all-handler']"
    css_selector = "section[id='abstract'] > div[role='paragraph']"

    tab = await driver.get(url)
    await tab.wait(5)

    if await tab.query_selector(button_css_selector) is not None:
        cookie_policy_button = await tab.select(button_css_selector)
        await cookie_policy_button.click()

    await tab.wait_for(selector=css_selector, timeout=15)
    await tab.get_content()

    abs_elems = await tab.select_all(css_selector)
    abstract = " ".join(abs_elem.text_all for abs_elem in abs_elems)
    return abstract


async def get_full_abstract(
    abs_session: requests.Session, url: str, req_itv: float, driver: zd.Browser
) -> str | None:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)
    res = make_request(abs_session, url, headers=req_headers)

    parsed_domain = urlparse(res.url).netloc
    if parsed_domain == "content.iospress.com":
        if res.status_code != 200:
            logger.warning(f"Cannot access {url} , status code: {res.status_code}.")
            # print(res.text)
        else:
            abs_soup = BeautifulSoup(res.text, "html.parser")
            css_selector = "h1[data-p13n='journal-article']"
            abs_tags = abs_soup.select_one(css_selector)
            if abs_tags is not None:
                abstract = abs_tags["data-abstract"]
            # iospress.com对于Special issue等非期刊论文的条目的设置
            if abstract == "No abstract":
                abstract = None
    # TODO not sure whether we should keep "journals" or not
    elif parsed_domain == "journals.sagepub.com":
        # sagepub is a new website
        abstract = await get_abs_impl(res.url, driver)
    else:
        return None

    return str(abstract) if abstract is not None else None


# async def main():
#     config = zd.Config(
#         headless=False,
#         user_data_dir=cookie_path,
#         browser_executable_path=chrome_path,
#     )

#     browser = await zd.start(config=config)

#     with requests.Session() as s:
#         abstract = await get_full_abstract(
#             s, "https://journals.sagepub.com/doi/10.3233/JCS-220031", 0, browser
#         )

#     await browser.stop()
#     print(abstract)


# if __name__ == "__main__":
#     logger.setLevel(logging.DEBUG)
#     handler = logging.StreamHandler()
#     handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     import asyncio
#     from settings import chrome_path, cookie_path
#     asyncio.run(main())
