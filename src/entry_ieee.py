import asyncio
import logging
from time import sleep

import nodriver as nd

from src.request_wrap import retry_async

logger = logging.getLogger(__name__)


@retry_async
async def get_abs_impl(url: str, driver: nd.Browser) -> str:
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

    abs_elem = await tab.select(css_selector)
    abstract = abs_elem.text_all
    return abstract


async def get_full_abstract(url: str, driver: nd.Browser, req_itv: float) -> str | None:
    if url == "":
        return None

    await asyncio.sleep(req_itv)
    abstract = await get_abs_impl(url, driver)
    return abstract
