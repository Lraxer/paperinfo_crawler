from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


def get_full_abstract(url: str, driver, req_itv: float) -> str:
    abstract = None

    if url == "":
        return None

    try:
        sleep(req_itv)
        # 访问目标网页
        driver.get(url)
        # 等待最多5秒
        wait = WebDriverWait(driver, 5)
        # 发现反爬
        if "Request Rejected" in driver.title:
            print(
                "Anti-crawler found. Chaning UA and more operations might be processed."
            )
            return

        try:
            show_more_button = driver.find_element(
                By.CLASS_NAME, "abstract-text-view-all"
            )
            # 等到按钮能够被点击
            show_more_button = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "abstract-text-view-all"))
            )
            # 滚动到对应位置
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            show_more_button.click()
        except:
            pass
        finally:
            abstract = driver.find_element(By.CSS_SELECTOR, "div[xplmathjax]").text
        # print("Abstract:", abstract)
    except:
        print(
            "Paper [xxx] cannot be loaded. The reason might be anti-crawler defenses or site updates."
        )
    finally:
        return abstract
