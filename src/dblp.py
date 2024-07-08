import requests
from conf import *
from bs4 import BeautifulSoup
import bs4
from tqdm import tqdm
from time import sleep
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_conf_url(name: str, year: str) -> str:
    """get URL of dblp.

    Args:
        namne (str): conference name
        year (str): conference year

    Returns:
        str: dblp URL
    """
    conf_url = "{}conf/{}/{}{}.html".format(dblp_url, name, name, year)

    logger.debug("Request URL: {}.".format(conf_url))

    return conf_url


def get_paper_title_and_url(entry: bs4.element.Tag) -> list:
    """获取一篇论文的标题和URL

    Args:
        entry (bs4.element.Tag): 一篇论文经bs4解析后的HTML代码片段

    Returns:
        list: (论文标题，论文URL)
    """
    paper_title = None
    title_span_tag = entry.select_one(
        'cite.data.tts-content > span.title[itemprop="name"]'
    )
    if title_span_tag is not None:
        # 去除可能存在的空格和英文句号
        paper_title = title_span_tag.get_text().strip()[:-1]

    paper_url = None
    # 找到第一个a标签
    a_tag = entry.select_one("li.ee > a")
    if a_tag is not None:
        paper_url = a_tag["href"]
        # 只留下 doi.org 类型的 URL
        # doi.ieeecomputersociety.org 等URL无法访问，需要排除
        # e.g. "Space Odyssey: An Experimental Software Security Analysis of Satellites" in https://dblp.org/db/conf/sp/sp2023.html
        if "doi.ieeecomputersociety.org" in paper_url:
            logger.warning(
                "Unsupported URL {} of paper {}.".format(paper_url, paper_title)
            )
            paper_url = ""

    return [paper_title, paper_url]


def get_paper_bibtex(entry: bs4.element.Tag, req_itv: float) -> str:
    """获取bibtex格式的论文元数据

    Args:
        entry (bs4.element.Tag): 一篇论文经bs4解析后的的HTML代码片段
        req_itv (float): bibtex请求之间的时间间隔（秒）。

    Returns:
        str: bibtex字符串
    """
    bibtex_url = None
    bibtex_url_tag = entry.select_one(
        'li.drop-down > div.body > ul > li > a[rel="nofollow"]'
    )
    if bibtex_url_tag is not None:
        bibtex_url = bibtex_url_tag["href"]
    else:
        # TODO 错误处理
        print("Cannot obtain bibtex URL.")
        return None

    if bibtex_url is not None:
        sleep(req_itv)
        bibtex_res = requests.get(bibtex_url)
        bibtex_soup = BeautifulSoup(bibtex_res.text, "html.parser")
        bibtex_content_tag = bibtex_soup.select_one(
            'div.section[id="bibtex-section"] > pre.verbatim.select-on-click'
        )
        if bibtex_content_tag is not None:
            bibtex_str = bibtex_content_tag.get_text()
            return bibtex_str
    # TODO 错误处理
    print("Cannot obtain bibtex content.")
    return None


def get_dblp_page_content(url: str, req_itv) -> list:
    """获取页面中的论文网址

    Args:
        url (str): 期刊/会议某一期/某一年的URL。e.g. https://dblp.org/db/conf/sp/sp2023.html
        req_itv (float): bibtex请求之间的时间间隔（秒）。

    Returns:
        list: [论文标题, 每篇论文的 doi.org URL, 不含摘要的bibtex字符串]。e.g. [WeRLman: To Tackle Whale (Transactions), Go Deep (RL), https://doi.org/10.1109/SP46215.2023.10179444, @inproceedings...]
    """
    res = requests.get(url)
    if res.status_code != 200:
        print("{} cannot be loaded. Make sure your input is valid.".format(url))
        return
    soup = BeautifulSoup(res.text, "html.parser")
    paper_entry = soup.select(
        'li.entry.inproceedings[itemscope][itemtype="http://schema.org/ScholarlyArticle"]'
    )
    entry_metadata_list = list()

    progress_dblp = tqdm(total=len(paper_entry))
    for entry in paper_entry:
        title_url_list = get_paper_title_and_url(entry)
        bibtex_str = get_paper_bibtex(entry, req_itv)
        entry_metadata_list.append(title_url_list + [bibtex_str])

        progress_dblp.update(1)
    progress_dblp.close()

    return entry_metadata_list


if __name__ == "__main__":
    metadata_list = get_dblp_page_content(get_conf_url("sp", str(2023)), 5)
    # print(title_url_lst)
