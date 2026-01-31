import asyncio
import logging
from time import sleep

import zendriver as zd

from src.request_wrap import retry_async

logger = logging.getLogger(__name__)


@retry_async
async def get_abs_impl(url: str, driver: zd.Browser) -> str:
    basic_css_selector = (
        r"div.core-container > section[id='abstract'] > div[role='paragraph']"
    )
    oa_css_selector = r"div.core-container > section[id='core-tabbed-abstracts'] > section[id='abstract'] > div[role='paragraph']"
    # 访问目标网页
    tab = await driver.get(url)
    await tab.wait(5)
    try:
        css_selector = oa_css_selector
        await tab.wait_for(selector=css_selector, timeout=5)
    except asyncio.TimeoutError:
        # some papers use a different abstract css selector
        css_selector = basic_css_selector
        await tab.wait_for(selector=css_selector, timeout=5)
    await tab.get_content()

    abs_elems = await tab.select_all(css_selector)
    abstract = " ".join(abs_elem.text_all for abs_elem in abs_elems)
    return abstract


async def get_full_abstract(url: str, driver: zd.Browser, req_itv: float) -> str | None:
    if url == "":
        return None

    sleep(req_itv)
    abstract = await get_abs_impl(url, driver)
    return abstract


# async def main():
#     config = zd.Config(
#         headless=False,
#         user_data_dir=cookie_path,
#         browser_executable_path=chrome_path,
#     )

#     browser = await zd.start(config=config)
#     abstract = await get_full_abstract(
#         "https://dl.acm.org/doi/10.1145/3690624.3709199", browser, 0
#     )
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
#     from settings import cookie_path, chrome_path
#     asyncio.run(main())
