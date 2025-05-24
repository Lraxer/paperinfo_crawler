import logging
from settings import retry_interval
from time import sleep

import asyncio
from settings import cookie_path

import zendriver as zd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def retry_acm(func):
    async def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    # ProtocolException seems to be a known issue, see
                    # https://github.com/stephanlensky/zendriver/issues/76
                    logger.warning(
                        "Cannot access {} . Exception: {} Retry {}/3 after {} sec.".format(
                            args[0], e.__class__.__name__, time + 1, retry_interval
                        )
                    )
                    # logger.warning("{}".format(repr(e)))
                    sleep(retry_interval)
        return None

    return wrap


@retry_acm
async def get_abs_impl(url: str, driver:zd.Browser) -> str:
    # 访问目标网页
    css_selector = (
        r"div.core-container > section[id='abstract'] > div[role='paragraph']"
    )
    
    tab = await driver.get(url)
    await tab.wait_for(selector=css_selector, timeout=10)
    await tab.get_content()

    abstract = ""
    abs_elems = await tab.select_all(css_selector)
    abstract = " ".join(abs_elem.text_all for abs_elem in abs_elems)
    # await tab.close()

    return abstract


async def get_full_abstract(url: str, driver, req_itv: float) -> str:
    if url == "":
        return None

    sleep(req_itv)
    abstract = await get_abs_impl(url, driver)
    return abstract

# async def main():
#     css_selector = (
#         r"div.core-container > section[id='abstract'] > div[role='paragraph']"
#     )

#     config = zd.Config(
#         headless=False,
#         user_data_dir=cookie_path,
#         browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#     )

#     browser = await zd.start(config=config)
#     tab = await browser.get("https://dl.acm.org/doi/10.1145/3690624.3709199")
#     await tab.get_content()
#     await tab.wait_for(selector=css_selector, timeout=10)
#     abs_elems = await tab.select_all(css_selector)
#     abstract = " ".join(abs_elem.text_all for abs_elem in abs_elems)
#     print(abstract)
#     # print(abs_elems)
#     # for abs_elem in abs_elems:
#         # print(abs_elem.text_all)



# if __name__ == "__main__":
#     asyncio.run(main())
