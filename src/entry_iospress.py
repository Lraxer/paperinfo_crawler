import requests
import logging
from settings import req_headers
from bs4 import BeautifulSoup
from request_wrap import make_request
from time import sleep
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from settings import retry_interval

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def retry_sagepub(func):
    def wrap(*args, **kwargs):
        for time in range(4):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if time < 3:
                    logger.warning(
                        "Cannot access {} . Exception: {} Retry {}/3 after {} sec.".format(
                            args[0], e.__class__.__name__, time + 1, retry_interval
                        )
                    )
                    sleep(retry_interval)
                # let driver clear cookies.
                args[1].delete_all_cookies()
        return None

    return wrap


@retry_sagepub
def get_abs_from_sagepub(url: str, driver) -> str:
    driver.get(url)
    # 等待最多60秒
    wait = WebDriverWait(driver, 60)
    button_res_list = driver.find_elements(
        By.CSS_SELECTOR, "button[id='onetrust-reject-all-handler']"
    )
    if button_res_list != []:
        cookie_policy_button = wait.until(
            EC.element_to_be_clickable(button_res_list[0])
        )
        # driver.execute_script("arguments[0].click();", button_res_list[0])
        cookie_policy_button.click()
    abs_tag = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "section[id='abstract'] > div[role='paragraph']")
        )
    )
    abstract = abs_tag.text
    return abstract


def get_full_abstract(
    abs_session: requests.Session, url: str, req_itv: float, driver
) -> str:
    abstract = None

    if url == "":
        return None

    sleep(req_itv)
    res = make_request(abs_session, url, headers=req_headers)

    parsed_domain = urlparse(res.url).netloc
    if parsed_domain == "content.iospress.com":
        if res.status_code != 200:
            logger.warning(
                "Cannot access {} , status code: {}.".format(url, res.status_code)
            )
            # print(res.text)
        else:
            abs_soup = BeautifulSoup(res.text, "html.parser")
            css_selector = "h1[data-p13n='journal-article']"
            abs_tags = abs_soup.select_one(css_selector)
            if abs_tags != []:
                abstract = abs_tags["data-abstract"]
            # iospress.com对于Special issue等非期刊论文的条目的设置
            if abstract == "No abstract":
                abstract = None
    # TODO not sure whether we should keep "journals" or not
    elif parsed_domain == "journals.sagepub.com":
        # sagepub is a new website
        abstract = get_abs_from_sagepub(res.url, driver)
    else:
        return None

    return abstract


if __name__ == "__main__":
    with requests.Session() as s:
        # abstract = get_full_abstract(
        #     s,
        #     "https://content.iospress.com/articles/journal-of-computer-security/jcs230047",
        #     0,
        # )
        # TODO requests被反爬，返回403。postman, httpx也不行。maybe selenium
        abstract = get_full_abstract(
            s,
            "https://journals.sagepub.com/doi/10.3233/JCS-220031",
            0,
        )
        print(abstract)
