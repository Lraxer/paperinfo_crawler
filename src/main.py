import argparse
import asyncio
import logging
import pickle

import bibtexparser
import bibtexparser.model
import requests
import zendriver as zd
from tqdm import tqdm

import dblp
import entry_acm
import entry_elsevier
import entry_ieee
import entry_iospress
import entry_ndss
import entry_springer
import entry_usenix
from settings import chrome_path, cj_pub_dict, cookie_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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
    "iospress": entry_iospress,
}


def collect_conf_metadata(
    name: str,
    year: str,
    publisher: str,
    need_abstract: bool,
    export_bib_path: str,
    dblp_req_itv: float,
    save_pickle: bool,
) -> list:
    conf_url, entry_type_in_url = dblp.get_conf_url(name, year)
    if conf_url is None:
        logger.error(f"Cannot get dblp URL for {name}, {year}")
        return []
    entry_metadata_list = dblp.get_dblp_page_content(
        conf_url, dblp_req_itv, entry_type_in_url
    )
    logger.debug(f"Number of papers: {len(entry_metadata_list)}")
    if len(entry_metadata_list) <= 0:
        logger.warning(f"No paper found in {name}, {year}")
        return []

    if save_pickle:
        pkl_filename = f"{name}{year}_dblp.pkl"
        logger.debug(f"Save collected dblp data to {pkl_filename}.")
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if need_abstract:
        asyncio.run(
            collect_abstract(
                name,
                entry_metadata_list,
                export_bib_path,
                publisher,
                dblp_req_itv,
            )
        )
    return entry_metadata_list


def collect_journal_metadata(
    name: str,
    volume: str,
    publisher: str,
    need_abstract: bool,
    export_bib_path: str,
    dblp_req_itv: float,
    save_pickle: bool,
) -> list:
    entry_metadata_list = dblp.get_dblp_page_content(
        dblp.get_journal_url(name, volume), dblp_req_itv, "journal"
    )
    logger.debug(f"Number of papers: {len(entry_metadata_list)}")
    if len(entry_metadata_list) <= 0:
        logger.warning(f"No paper found in {name}, {volume}.")
        return []

    if save_pickle:
        pkl_filename = f"{name}{volume}_dblp.pkl"
        logger.debug(f"Save collected dblp data to {pkl_filename}.")
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if need_abstract:
        asyncio.run(
            collect_abstract(
                name,
                entry_metadata_list,
                export_bib_path,
                publisher,
                req_itv,
            )
        )

    return entry_metadata_list


async def collect_abstract_impl(
    entry_func,
    library: bibtexparser.Library,
    entry_metadata_list: list,
    need_webdriver: bool,
    req_itv: float = 10,
    driver=None,
):
    for entry_metadata in tqdm(entry_metadata_list):
        if need_webdriver:
            if entry_func == entry_iospress:
                # special case for iospress
                abs_session = requests.Session()
                abstract = await entry_func.get_full_abstract(
                    abs_session, entry_metadata[1], req_itv, driver
                )
                abs_session.close()
            else:
                abstract = await entry_func.get_full_abstract(
                    entry_metadata[1], driver, req_itv
                )
        else:
            abs_session = requests.Session()
            abstract = entry_func.get_full_abstract(
                abs_session, entry_metadata[1], req_itv
            )
            abs_session.close()
        # if parse failed, the number of entries in library is 0, print warning and process the next paper.
        tmp_library = bibtexparser.parse_string(entry_metadata[2])
        if len(tmp_library.entries) != 1:
            logger.warning(
                f'Cannot parse bibtex string to entry of paper "{entry_metadata[0]}", string is: {repr(entry_metadata[2])}.'
            )
            continue

        if abstract is not None:
            abstract_field = bibtexparser.model.Field("abstract", repr(abstract)[1:-1])
            tmp_library.entries[0].set_field(abstract_field)
        else:
            logger.warning(f'Cannot collect abstract of paper "{entry_metadata[0]}".')
        library.add(tmp_library.blocks)

    return library


async def collect_abstract(
    name: str,
    entry_metadata_list: list,
    export_bib_path: str,
    publisher: str,
    req_itv: float = 10,
):
    library = bibtexparser.Library()

    logger.debug(f"Publisher: {publisher}.")

    if publisher == "ieee":
        browser_config = zd.Config(
            headless=True,
            user_data_dir=cookie_path,
            browser_executable_path=chrome_path,
        )
        browser = await zd.start(config=browser_config)
        library = await collect_abstract_impl(
            entry_ieee,
            library,
            entry_metadata_list,
            need_webdriver=True,
            req_itv=req_itv,
            driver=browser,
        )
        await browser.stop()
    elif publisher == "elsevier" or publisher == "iospress" or publisher == "acm":
        browser_config = zd.Config(
            headless=False,
            user_data_dir=cookie_path,
            browser_executable_path=chrome_path,
        )
        browser = await zd.start(config=browser_config)
        if publisher == "elsevier":
            library = await collect_abstract_impl(
                entry_elsevier,
                library,
                entry_metadata_list,
                need_webdriver=True,
                req_itv=req_itv,
                driver=browser,
            )
        elif publisher == "iospress":
            library = await collect_abstract_impl(
                entry_iospress,
                library,
                entry_metadata_list,
                need_webdriver=True,
                req_itv=req_itv,
                driver=browser,
            )
        elif publisher == "acm":
            library = await collect_abstract_impl(
                entry_acm,
                library,
                entry_metadata_list,
                need_webdriver=True,
                req_itv=req_itv,
                driver=browser,
            )
        await browser.stop()
    else:
        selected_module = publisher_module_dict.get(publisher)
        if selected_module is not None:
            library = await collect_abstract_impl(
                selected_module,
                library,
                entry_metadata_list,
                need_webdriver=False,
                req_itv=req_itv,
            )
        else:
            logger.error("Invalid publisher.")
            return

    logger.debug(f"entries in bibtex db: {len(library.entries)}.")
    # 由于bibtexparser.write_file暂时无法指定编码，只能先写入字符串后手动保存到文件，
    # 参考 https://github.com/sciunto-org/python-bibtexparser/pull/405
    bib_str = bibtexparser.write_string(library)
    with open(export_bib_path, "w", encoding="utf-8") as f:
        f.write(bib_str)


def collect_abstract_from_dblp_pkl(
    pkl_filename: str,
    name: str,
    publisher: str,
    export_bib_path: str,
    req_itv: float,
):
    with open(pkl_filename, "rb") as f:
        entry_metadata_list = pickle.load(f)
    asyncio.run(
        collect_abstract(
            name,
            entry_metadata_list,
            export_bib_path,
            publisher,
            req_itv,
        )
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

    save_pkl = args.save_pkl
    need_abs = not args.no_abs
    from_pkl_fn = args.from_pkl

    publisher = cj_pub_dict.get(args.name)
    if args.publisher is not None:
        if publisher is None:
            if from_pkl_fn is not None:
                print(
                    "This conference/journal has not been tested yet. Setting --save-pkl is recommended."
                )
            publisher = args.publisher
        elif publisher != args.publisher:
            print("Input publisher cannot match.")
            selection = input(
                f'Use (1) pre-set publisher "{publisher}" or (2) your input "{args.publisher}"? Input 1 or 2.'
            )
            if selection == "1":
                logger.debug("Use pre-set publisher.")
            else:
                logger.debug("Use user input.")
                publisher = args.publisher
    else:
        if publisher is None:
            print(
                "Cannot find this conference/journal. Please specify publisher by -p or --publisher."
            )
            exit(1)

    if need_abs is False and from_pkl_fn is not None:
        print("--no-abs cannot be set together with --from-pkl (-f).")
        exit(1)

    dblp_req_itv = args.dblp_interval
    # 收集摘要的发送请求时间间隔
    req_itv = args.interval

    if args.year is None:
        # Journal
        volume: str = args.volume

        if args.save is None:
            saved_fn = f"{name}{volume}.bib"
        else:
            saved_fn = args.save

        logger.debug(
            f"\nname:{name}\nvolume:{volume}\nneed_abs:{need_abs}\ndblp_req_itv:{dblp_req_itv}\nreq_itev:{req_itv}\npublisher:{publisher}\nsave_pkl:{save_pkl}\nfrom_pkl_fn:{from_pkl_fn}\n"
        )
        # format: 19
        if volume.isdigit():
            if args.save is None:
                saved_fn = f"{name}{volume}.bib"
            else:
                saved_fn = args.save
            logger.debug(f"saved_fn: {saved_fn}")
            if from_pkl_fn is None:
                collect_journal_metadata(
                    name, volume, publisher, need_abs, saved_fn, dblp_req_itv, save_pkl
                )
                exit(0)
            else:
                collect_abstract_from_dblp_pkl(
                    from_pkl_fn, name, publisher, saved_fn, req_itv
                )
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
            exit(1)

        if from_pkl_fn is not None:
            logger.error(
                '--from-pkl (-f) is not compatible with "72-79" format of volume parameter.'
            )
            exit(1)

        for vol in range(start_vol, end_vol + 1):
            saved_fn = f"{name}{vol}.bib"
            collect_journal_metadata(
                name, str(vol), publisher, need_abs, saved_fn, dblp_req_itv, save_pkl
            )
    else:
        # Conference
        year = args.year

        if args.save is None:
            saved_fn = f"{name}{year}.bib"
        else:
            saved_fn = args.save

        logger.debug(
            f"\nname:{name}\nyear:{year}\nneed_abs:{need_abs}\nsaved_fn:{saved_fn}\ndblp_req_itv:{dblp_req_itv}\nreq_itev:{req_itv}\npublisher:{publisher}\nsave_pkl:{save_pkl}\nfrom_pkl_fn:{from_pkl_fn}\n"
        )
        if from_pkl_fn is None:
            collect_conf_metadata(
                name, year, publisher, need_abs, saved_fn, dblp_req_itv, save_pkl
            )
        else:
            logger.debug("Collect abstract from dblp pickle file.")
            collect_abstract_from_dblp_pkl(
                from_pkl_fn, name, publisher, saved_fn, req_itv
            )
