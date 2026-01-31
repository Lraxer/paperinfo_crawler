import logging
from time import sleep

import zendriver as zd

from src.request_wrap import retry_async

logger = logging.getLogger(__name__)


@retry_async
async def get_abs_impl(url: str, driver: zd.Browser) -> str:
    css_selector = "div.abstract.author > div > div"

    # 访问目标网页
    tab = await driver.get(url)
    await tab.wait(5)
    await tab.wait_for(selector=css_selector, timeout=15)
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
#         headless=True,
#         user_data_dir=cookie_path,
#         browser_executable_path=chrome_path,
#     )
#     browser = await zd.start(config=config)
#     abstract = await get_full_abstract(
#         "https://doi.org/10.1016/j.cose.2023.103489", browser, 0
#     )
#     await browser.stop()
#     print(repr(abstract))


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
