import bibtexparser.model
import entry_ieee
import entry_acm
import entry_elsevier
import entry_ndss
import entry_springer
import entry_usenix
import dblp
import bibtexparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from settings import user_agent, chromedriver_path, cj_pub_dict
import logging
import argparse
import pickle
from tqdm import tqdm
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# TODO Use FileHandler instead.
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


publisher_module_dict = {
    "ieee": entry_ieee,
    "acm": entry_acm,
    "springer": entry_springer,
    "usenix": entry_usenix,
    "ndss": entry_ndss,
    "elsevier": entry_elsevier,
}


def collect_conf_metadata(
    name: str,
    year: str,
    need_abstract: bool,
    export_bib_path: str,
    dblp_req_itv: float,
    save_pickle: bool,
) -> list:
    entry_metadata_list = dblp.get_dblp_page_content(
        dblp.get_conf_url(name, year), dblp_req_itv, "conf"
    )
    logger.debug("Number of papers: {}".format(len(entry_metadata_list)))

    if save_pickle:
        pkl_filename = "{}{}_dblp.pkl".format(name, year)
        logger.debug("Save collected dblp data to {}.".format(pkl_filename))
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if need_abstract:
        collect_abstract(
            name,
            entry_metadata_list,
            export_bib_path,
            cj_pub_dict.get(name, "other"),
            req_itv,
        )

    return entry_metadata_list


def collect_journal_metadata(
    name: str,
    volume: str,
    need_abstract: bool,
    export_bib_path: str,
    dblp_req_itv: float,
    save_pickle: bool,
) -> list:
    entry_metadata_list = dblp.get_dblp_page_content(
        dblp.get_journal_url(name, volume), dblp_req_itv, "journal"
    )
    logger.debug("Number of papers: {}".format(len(entry_metadata_list)))

    if save_pickle:
        pkl_filename = "{}{}_dblp.pkl".format(name, volume)
        logger.debug("Save collected dblp data to {}.".format(pkl_filename))
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if need_abstract:
        collect_abstract(
            name,
            entry_metadata_list,
            export_bib_path,
            cj_pub_dict.get(name, "other"),
            req_itv,
        )

    return entry_metadata_list


def collect_abstract_impl(
    entry_func,
    library: bibtexparser.Library,
    entry_metadata_list: list,
    need_selenium: bool,
    req_itv: float = 10,
    driver=None,
):
    progress_abstract = tqdm(total=len(entry_metadata_list))
    abs_session = requests.Session()
    # for ieee papers
    for entry_metadata in entry_metadata_list:
        if need_selenium:
            abstract = entry_func.get_full_abstract(entry_metadata[1], driver, req_itv)
        else:
            abstract = entry_func.get_full_abstract(
                abs_session, entry_metadata[1], req_itv
            )
        # if parse failed, the number of entries in library is 0, print warning and process the next paper.
        tmp_library = bibtexparser.parse_string(entry_metadata[2])
        if len(tmp_library.entries) != 1:
            logger.warning(
                'Cannot parse bibtex string to entry of paper "{}", string is: {}.'.format(
                    entry_metadata[0], repr(entry_metadata[2])
                )
            )
            continue

        if abstract is not None:
            abstract_field = bibtexparser.model.Field("abstract", repr(abstract)[1:-1])
            tmp_library.entries[0].set_field(abstract_field)
        else:
            logger.warning(
                'Cannot collect abstract of paper "{}".'.format(entry_metadata[0])
            )
        library.add(tmp_library.blocks)
        progress_abstract.update(1)

    abs_session.close()
    progress_abstract.close()
    return library


def collect_abstract(
    name: str,
    entry_metadata_list: list,
    export_bib_path: str,
    publisher: str,
    req_itv: float = 10,
):
    library = bibtexparser.Library()

    logger.debug("Publisher: {}.".format(publisher))

    if publisher == "ieee" or publisher == "elsevier":
        chrome_service = Service(chromedriver_path)
        chrome_options = Options()
        # 只用headless会被elsevier识别
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("user-agent={}".format(user_agent))

        if publisher == "ieee":
            # 设置headless浏览器选项
            # chrome_options.add_argument("--window-size=1920x1080")
            # 使 selenium 只输出wanrning及以上的日志信息
            chrome_options.add_argument("log-level=1")
            # headless模式下需要改UA
            chrome_options.add_argument("user-agent={}".format(user_agent))
            # 创建一个新的Chrome浏览器实例
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            library = collect_abstract_impl(
                entry_ieee,
                library,
                entry_metadata_list,
                need_selenium=True,
                req_itv=req_itv,
                driver=driver,
            )
        elif publisher == "elsevier":
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            # 忽略 ssl_client_socket_impl.cc handshake failed error 错误
            chrome_options.add_argument("log-level=3")
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            library = collect_abstract_impl(
                entry_elsevier,
                library,
                entry_metadata_list,
                need_selenium=True,
                req_itv=req_itv,
                driver=driver,
            )

        # 关闭浏览器
        driver.quit()
    elif publisher == "other":
        logger.error("Not supported.")
        return
    else:
        selected_module = publisher_module_dict.get(publisher)
        if selected_module is not None:
            library = collect_abstract_impl(
                selected_module,
                library,
                entry_metadata_list,
                need_selenium=False,
                req_itv=req_itv,
            )
        else:
            logger.error("Invalid publisher.")
            return

    logger.debug("entries in bibtex db: {}.".format(len(library.entries)))
    # 由于bibtexparser.write_file暂时无法指定编码，只能先写入字符串后手动保存到文件，
    # 参考 https://github.com/sciunto-org/python-bibtexparser/pull/405
    bib_str = bibtexparser.write_string(library)
    with open(export_bib_path, "w", encoding="utf-8") as f:
        f.write(bib_str)


def collect_abstract_from_dblp_pkl(
    pkl_filename: str,
    name: str,
    export_bib_path: str,
    req_itv: float,
):
    with open(pkl_filename, "rb") as f:
        entry_metadata_list = pickle.load(f)
    collect_abstract(
        name,
        entry_metadata_list,
        export_bib_path,
        cj_pub_dict.get(name, "other"),
        req_itv,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect paper metadata.")

    parser.add_argument("--name", "-n", type=str, required=True, help="会议/期刊标识")

    # conference or journal
    grp1 = parser.add_mutually_exclusive_group(required=True)
    grp1.add_argument(
        "--year", "-y", type=str, default=None, help="会议举办时间（年）e.g. 2023"
    )
    grp1.add_argument(
        "--volume",
        "-u",
        type=str,
        default=None,
        help="期刊卷号，格式为单个数字，或要爬取的起止卷号，以短横线连接。e.g. 72-79",
    )

    parser.add_argument("--publisher", "-p", type=str, default=None, help="指定出版社")
    parser.add_argument(
        "--save-pkl",
        "-e",
        action="store_true",
        default=False,
        help="是否将从dblp收集的元数据保存到pickle文件，默认名称为[name][year/volume]_dblp.pkl, 对于期刊，该选项只支持volume为数字的输入（e.g. -u 72），不支持多卷的输入（e.g. -u 72-79）",
    )
    parser.add_argument(
        "--no-abs",
        action="store_true",
        default=False,
        help="是否从出版社网站收集摘要，设置此选项表示不收集摘要",
    )
    parser.add_argument(
        "--from-pkl",
        "-f",
        type=str,
        default=None,
        help="从pickle加载dblp元数据，并收集摘要",
    )
    parser.add_argument(
        "--dblp-interval",
        "-d",
        type=float,
        default=10,
        help="向dblp发送请求的间隔（秒）",
    )
    parser.add_argument(
        "--interval", "-t", type=float, default=10, help="收集摘要的请求发送间隔（秒）"
    )
    # 保存不含摘要的bibtex不在设计意图内
    parser.add_argument(
        "--save",
        "-s",
        type=str,
        default=None,
        help="bibtex文件的保存位置，默认是[name][year].bib, 对于期刊，该选项只支持volume为数字的输入（e.g. -u 72），不支持多卷的输入（e.g. -u 72-79）",
    )

    args = parser.parse_args()

    name = args.name

    publisher = cj_pub_dict.get(args.name)
    if args.publisher is not None:
        if publisher is None:
            print(
                "This conference/journal has not been tested yet. Setting `--save-pkl` is recommended."
            )
            cj_pub_dict[args.name] = args.publisher
        elif publisher != args.publisher:
            print("Input publisher cannot match.")
            selection = input(
                'Use pre-set publisher "{}" or your input "{}"? Input 1 or 2.'.format(
                    publisher, args.publisher
                )
            )
            if selection == "1":
                logger.debug("Use pre-set publisher.")
            else:
                logger.debug("Use user input.")
                publisher = args.publisher
    else:
        if publisher is None:
            print(
                "Cannot find this conference. Please specify publisher by -p or --publisher."
            )
            exit(1)

    save_pkl = args.save_pkl
    need_abs = not args.no_abs
    from_pkl_fn = args.from_pkl

    if need_abs is False and from_pkl_fn is not None:
        print("--no-abs cannot be set while using --from-pkl (-f).")
        exit(1)

    dblp_req_itv = args.dblp_interval
    # 收集摘要的发送请求时间间隔
    req_itv = args.interval

    if args.year is None:
        # Journal
        volume: str = args.volume

        if args.save is None:
            saved_fn = "{}{}.bib".format(name, volume)
        else:
            saved_fn = args.save

        logger.debug(
            "\nname:{}\nvolume:{}\nneed_abs:{}\ndblp_req_itv:{}\nreq_itev:{}\nsave_pkl:{}\nfrom_pkl_fn:{}\n".format(
                name,
                volume,
                need_abs,
                dblp_req_itv,
                req_itv,
                save_pkl,
                from_pkl_fn,
            )
        )
        # format: 19
        if volume.isdigit():
            if args.save is None:
                saved_fn = "{}{}.bib".format(name, volume)
            else:
                saved_fn = args.save
            logger.debug("saved_fn:{}".format(saved_fn))
            if from_pkl_fn is None:
                collect_journal_metadata(
                    name, volume, need_abs, saved_fn, dblp_req_itv, save_pkl
                )
                exit(0)
            else:
                collect_abstract_from_dblp_pkl(from_pkl_fn, name, saved_fn, req_itv)
                exit(0)

        # format: 19-29
        vol_list = volume.split("-")
        if len(vol_list) != 2:
            logger.error("Invalid volume input.")
            exit(1)
        start_vol = int(vol_list[0])
        end_vol = int(vol_list[1])
        if end_vol <= start_vol:
            logger.error("Invalid volume input.")

        for vol in range(start_vol, end_vol + 1):
            saved_fn = "{}{}.bib".format(name, vol)
            if from_pkl_fn is None:
                collect_journal_metadata(
                    name, vol, need_abs, saved_fn, dblp_req_itv, save_pkl
                )
            else:
                logger.warning(
                    '--from-pkl (-f) is not compatible with "72-79" format of volume parameter.'
                )
    else:
        # Conference
        year = args.year

        if args.save is None:
            saved_fn = "{}{}.bib".format(name, year)
        else:
            saved_fn = args.save

        logger.debug(
            "\nname:{}\nyear:{}\nneed_abs:{}\nsaved_fn:{}\ndblp_req_itv:{}\nreq_itev:{}\nsave_pkl:{}\nfrom_pkl_fn:{}\n".format(
                name,
                year,
                need_abs,
                saved_fn,
                dblp_req_itv,
                req_itv,
                save_pkl,
                from_pkl_fn,
            )
        )
        if from_pkl_fn is None:
            collect_conf_metadata(
                name, year, need_abs, saved_fn, dblp_req_itv, save_pkl
            )
        else:
            logger.debug("Collect abstract from dblp pickle file.")
            collect_abstract_from_dblp_pkl(from_pkl_fn, name, saved_fn, req_itv)
