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


def retry_ieee(func):
    def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    logger.error(
                        "Cannot access {}. Exception: {} Retry {}/3 after 15 sec.".format(
                            args[0], e.__class__.__name__, time + 1
                        )
                    )
                    sleep(15)
                # let driver clear cookies.
                args[1].delete_all_cookies()
        return None

    return wrap


@retry_ieee
def get_abs_impl(url: str, driver) -> str:
    # 访问目标网页
    driver.get(url)
    # 等待最多10秒
    wait = WebDriverWait(driver, 5)
    # 发现反爬
    if "Request Rejected" in driver.title:
        print("Anti-crawler found. Chaning UA and more operations might be processed.")
        return None

    abstract = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[xplmathjax]"))
    )
    button_res_list = driver.find_elements(By.CLASS_NAME, "abstract-text-view-all")

    if button_res_list != []:
        show_more_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "abstract-text-view-all"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
        show_more_button.click()

    abstract = driver.find_element(By.CSS_SELECTOR, "div[xplmathjax]").text
    return abstract


def get_full_abstract(url: str, driver, req_itv: float) -> str:
    if url == "":
        return None

    sleep(req_itv)
    abstract = get_abs_impl(url, driver)
    return abstract
