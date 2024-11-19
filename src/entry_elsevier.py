from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def retry_elsevier(func):
    def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    logger.warning(
                        "Cannot access {} . Exception: {} Retry {}/3 after 15 sec.".format(
                            args[0], e.__class__.__name__, time + 1
                        )
                    )
                    sleep(15)
                # let driver clear cookies.
                args[1].delete_all_cookies()
        return None

    return wrap


@retry_elsevier
def get_abs_impl(url: str, driver) -> str:
    # 访问目标网页
    driver.get(url)
    # 等待最多10秒
    wait = WebDriverWait(driver, 20)
    abs_tag = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.abstract.author > div > div")
        )
    )
    abstract = abs_tag.text
    return abstract


def get_full_abstract(url: str, driver, req_itv: float) -> str:
    if url == "":
        return None

    sleep(req_itv)
    abstract = get_abs_impl(url, driver)
    return abstract


# if __name__ == "__main__":
#     from selenium.webdriver.chrome.options import Options
#     from selenium.webdriver.chrome.service import Service
#     from settings import chromedriver_path, user_agent
#     from selenium import webdriver

#     chrome_options = Options()
#     # 只用headless会被识别
#     # chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("user-agent={}".format(user_agent))
#     chrome_options.add_argument("--ignore-certificate-errors")
#     chrome_options.add_argument("--ignore-ssl-errors")
#     chrome_options.add_argument("--disable-gpu")
#     # 忽略 ssl_client_socket_impl.cc handshake failed error 错误
#     chrome_options.add_argument("log-level=3")
#     chrome_options.add_argument("--user-data-dir=D:/pycode/chromedriver-user-data/")
#     # headless模式下需要改UA
#     # 创建一个新的Chrome浏览器实例
#     chrome_service = Service(chromedriver_path)
#     driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
#     abstract = get_full_abstract(
#         "https://doi.org/10.1016/j.cose.2023.103489", driver, 0
#     )

#     print(repr(abstract))
