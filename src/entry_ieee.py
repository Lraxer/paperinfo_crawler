import logging
from time import sleep

import zendriver as zd

from src.request_wrap import retry_async

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@retry_async
async def get_abs_impl(url: str, driver: zd.Browser) -> str:
    # "Show More" button of abstract
    button_css_selector = "a.abstract-text-view-all"
    css_selector = "div[xplmathjax]"

    # 访问目标网页
    tab = await driver.get(url)
    await tab.wait(5)
    await tab.wait_for(selector=css_selector, timeout=10)

    if await tab.query_selector(button_css_selector) is not None:
        show_more_button = await tab.select(button_css_selector)
        await show_more_button.click()

    await tab.get_content()

    abs_elem = await tab.select(css_selector)
    abstract = abs_elem.text_all
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
#         "https://doi.org/10.1109/TDSC.2021.3129512", browser, 0
#     )
#     await browser.stop()
#     print(abstract)


# if __name__ == "__main__":
#     import asyncio
#     from settings import cookie_path, chrome_path
#     asyncio.run(main())
