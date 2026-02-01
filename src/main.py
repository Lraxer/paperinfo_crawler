import argparse
import asyncio
import logging
import pickle
from dataclasses import dataclass

import bibtexparser
import bibtexparser.entrypoint
import bibtexparser.library
import bibtexparser.model
import nodriver as nd
import requests
from rich.logging import RichHandler
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           TaskProgressColumn, TextColumn, TimeElapsedColumn,
                           TimeRemainingColumn)

import src.dblp as dblp
import src.entry_acm as entry_acm
import src.entry_elsevier as entry_elsevier
import src.entry_ieee as entry_ieee
import src.entry_iospress as entry_iospress
import src.entry_ndss as entry_ndss
import src.entry_springer as entry_springer
import src.entry_usenix as entry_usenix
from src.settings import chrome_path, cj_pub_dict, cookie_path


def setup_logging():
    # set root logger
    root = logging.getLogger()
    # 屏蔽所有第三方库的 DEBUG 日志
    root.setLevel(logging.WARNING)
    root.handlers.clear()  # 防止重复输出

    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=False,
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # 显式开启本项目代码的 DEBUG 日志
    logging.getLogger("src").setLevel(logging.DEBUG)
    logging.getLogger("__main__").setLevel(logging.DEBUG)
    # 屏蔽 nodriver 的低级别日志
    # logging.getLogger("nodriver").setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(__name__)


publisher_module_dict = {
    "ieee": entry_ieee,
    "acm": entry_acm,
    "springer": entry_springer,
    "usenix": entry_usenix,
    "ndss": entry_ndss,
    "elsevier": entry_elsevier,
    "iospress": entry_iospress,
}


@dataclass
class JournalObj:
    name: str
    volume: str
    publisher: str
    need_abs: bool
    save_pkl: bool
    bib_fn: str
    from_pkl: str | None
    dblp_req_interval: float
    req_interval: float


@dataclass
class ConferenceObj:
    name: str
    year: str
    publisher: str
    need_abs: bool
    save_pkl: bool
    bib_fn: str
    from_pkl: str | None
    dblp_req_interval: float
    req_interval: float


def collect_conf_metadata(*, entry: ConferenceObj):
    conf_url, entry_type_in_url = dblp.get_conf_url(entry.name, entry.year)
    if conf_url is None:
        logger.error(f"Cannot get dblp URL for {entry.name}, {entry.year}")
        return []
    entry_metadata_list = dblp.get_dblp_page_content(
        conf_url, entry.dblp_req_interval, entry_type_in_url
    )
    logger.debug(f"Number of papers: {len(entry_metadata_list)}")
    if len(entry_metadata_list) <= 0:
        logger.warning(f"No paper found in {entry.name}, {entry.year}")
        return []

    if entry.save_pkl:
        pkl_filename = f"{entry.name}{entry.year}_dblp.pkl"
        logger.debug(f"Save collected dblp data to {pkl_filename}.")
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if entry.need_abs:
        nd.loop().run_until_complete(
            collect_abstract(
                entry.name,
                entry_metadata_list,
                entry.bib_fn,
                entry.publisher,
                entry.req_interval,
            )
        )
    return entry_metadata_list


def collect_journal_metadata(*, entry: JournalObj) -> list:
    entry_metadata_list = dblp.get_dblp_page_content(
        dblp.get_journal_url(entry.name, entry.volume),
        entry.dblp_req_interval,
        "journal",
    )
    logger.debug(f"Number of papers: {len(entry_metadata_list)}")
    if len(entry_metadata_list) <= 0:
        logger.warning(f"No paper found in {entry.name}, {entry.volume}.")
        return []

    if entry.save_pkl:
        pkl_filename = f"{entry.name}{entry.volume}_dblp.pkl"
        logger.debug(f"Save collected dblp data to {pkl_filename}.")
        with open(pkl_filename, "wb") as f:
            pickle.dump(entry_metadata_list, f)

    if entry.need_abs:
        nd.loop().run_until_complete(
            collect_abstract(
                entry.name,
                entry_metadata_list,
                entry.bib_fn,
                entry.publisher,
                entry.req_interval,
            )
        )

    return entry_metadata_list


async def collect_abstract_impl(
    entry_func,
    library: bibtexparser.library.Library,
    entry_metadata_list: list,
    need_webdriver: bool,
    req_itv: float = 10,
    driver=None,
):
    progress = Progress(
        TextColumn("{task.description}"),
        TaskProgressColumn(),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(compact=True),
        TextColumn("{task.fields[avg_sec_per_it]:>6.2f} s/it"),
    )
    progress.start()
    task_id = progress.add_task(
        "Collecting Abstracts", total=len(entry_metadata_list), avg_sec_per_it=0
    )

    for entry_metadata in entry_metadata_list:
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
        tmp_library = bibtexparser.entrypoint.parse_string(entry_metadata[2])
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

        # set speed display
        task_fields = progress.tasks[task_id]
        avg_speed = (
            task_fields.elapsed / (task_fields.completed + 1)
            if task_fields.elapsed
            else 0
        )
        progress.update(task_id, advance=1, avg_sec_per_it=avg_speed)

    progress.stop()
    return library


async def collect_abstract(
    name: str,
    entry_metadata_list: list,
    export_bib_path: str,
    publisher: str,
    req_itv: float = 10,
):
    library = bibtexparser.library.Library()

    logger.debug(f"Publisher: {publisher}.")

    match publisher:
        case "ieee":
            browser_config = nd.Config(
                headless=False,
                user_data_dir=cookie_path,
                browser_executable_path=chrome_path,
                browser_args=["--disable-gpu"],
            )
            browser = await nd.start(config=browser_config)
            library = await collect_abstract_impl(
                entry_ieee,
                library,
                entry_metadata_list,
                need_webdriver=True,
                req_itv=req_itv,
                driver=browser,
            )
            browser.stop()
        case "elsevier" | "iospress" | "acm":
            browser_config = nd.Config(
                headless=False,
                user_data_dir=cookie_path,
                browser_executable_path=chrome_path,
                browser_args=["--disable-gpu"],
            )
            browser = await nd.start(config=browser_config)
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
            browser.stop()
        case _:
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
    bibtexparser.entrypoint.write_file(export_bib_path, library, encoding="utf-8")


def collect_abstract_from_dblp_pkl(*, entry: JournalObj | ConferenceObj):
    if entry.from_pkl is None:
        logger.error("from_pkl is None.")
        return

    with open(entry.from_pkl, "rb") as f:
        entry_metadata_list = pickle.load(f)
    nd.loop().run_until_complete(
        collect_abstract(
            entry.name,
            entry_metadata_list,
            entry.bib_fn,
            entry.publisher,
            entry.req_interval,
        )
    )


def parse_args(parser: argparse.ArgumentParser, argv: list[str] | None):
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

    args = parser.parse_args(argv)

    return args


def validate_publisher(publisher: str | None, name: str, from_pkl: str | None) -> str:
    tested_publisher = cj_pub_dict.get(name)
    if publisher is not None:
        if tested_publisher is None:
            if from_pkl is not None:
                logger.warning(
                    "This conference/journal has not been tested yet. Setting --save-pkl is recommended."
                )
        elif tested_publisher != publisher:
            logger.warning("Input publisher cannot match.")
            selection = input(
                f'Use (1) pre-set publisher "{tested_publisher}" or (2) your input "{publisher}"? Input 1 or 2.'
            )
            match selection:
                case "1":
                    logger.debug("Use pre-set publisher.")
                    publisher = tested_publisher
                case "2":
                    logger.debug("Use user input.")
                case _:
                    logger.error("Invalid input.")
                    exit(1)
    else:
        if tested_publisher is None:
            logger.error(
                "Cannot find this conference/journal. Please specify publisher by -p or --publisher."
            )
            exit(1)
        publisher = tested_publisher

    return publisher


def crawl_journal(
    *,
    name: str,
    volume: str,
    publisher: str,
    need_abs: bool,
    save_pkl: bool,
    bib_fn: str | None,
    from_pkl: str | None,
    dblp_req_itv: float,
    req_itv: float,
):
    # format: 19
    if volume.isdigit():
        if bib_fn is None:
            saved_fn = f"{name}{volume}.bib"
        else:
            saved_fn = bib_fn
        journal_entry = JournalObj(
            name=name,
            volume=volume,
            publisher=publisher,
            need_abs=need_abs,
            save_pkl=save_pkl,
            bib_fn=saved_fn,
            from_pkl=from_pkl,
            dblp_req_interval=dblp_req_itv,
            req_interval=req_itv,
        )
        logger.debug(f"journal_entry: {journal_entry}")
        if journal_entry.from_pkl is None:
            collect_journal_metadata(entry=journal_entry)
            exit(0)
        else:
            collect_abstract_from_dblp_pkl(entry=journal_entry)
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

    if from_pkl is not None:
        logger.error(
            '--from-pkl (-f) is not compatible with "72-79" format of volume parameter.'
        )
        exit(1)

    journal_entry = JournalObj(
        name=name,
        volume=vol_list[0],
        publisher=publisher,
        need_abs=need_abs,
        save_pkl=save_pkl,
        bib_fn=f"{name}{start_vol}.bib",
        from_pkl=from_pkl,
        dblp_req_interval=dblp_req_itv,
        req_interval=req_itv,
    )

    for vol in range(start_vol, end_vol + 1):
        saved_fn = f"{name}{vol}.bib"
        journal_entry.volume = str(vol)
        journal_entry.bib_fn = saved_fn
        collect_journal_metadata(entry=journal_entry)


def crawl_conference(
    *,
    name: str,
    year: str,
    publisher: str,
    need_abs: bool,
    save_pkl: bool,
    bib_fn: str | None,
    from_pkl: str | None,
    dblp_req_itv: float,
    req_itv: float,
):
    # Conference
    if bib_fn is None:
        saved_fn = f"{name}{year}.bib"
    else:
        saved_fn: str = bib_fn

    conference_entry = ConferenceObj(
        name=name,
        year=year,
        publisher=publisher,
        need_abs=need_abs,
        save_pkl=save_pkl,
        bib_fn=saved_fn,
        from_pkl=from_pkl,
        dblp_req_interval=dblp_req_itv,
        req_interval=req_itv,
    )
    logger.debug(f"conference_entry: {conference_entry}")
    if from_pkl is None:
        collect_conf_metadata(
            # name, year, publisher, need_abs, saved_fn, dblp_req_itv, save_pkl
            entry=conference_entry
        )
    else:
        logger.debug("Collect abstract from dblp pickle file.")
        collect_abstract_from_dblp_pkl(entry=conference_entry)


def main(argv: list[str] | None):
    parser = argparse.ArgumentParser(description="Collect paper metadata.")

    args = parse_args(parser, argv)

    name: str = args.name

    save_pkl: bool = args.save_pkl
    need_abs: bool = not args.no_abs
    from_pkl: str | None = args.from_pkl
    year: str | None = args.year  # only set for conference

    dblp_req_itv: float = args.dblp_interval
    # 收集摘要的发送请求时间间隔
    req_itv: float = args.interval

    publisher = validate_publisher(args.publisher, name, from_pkl)

    if need_abs is False and from_pkl is not None:
        logger.error("--no-abs cannot be set together with --from-pkl (-f).")
        exit(1)

    if year is None:
        # Journal
        volume: str = args.volume
        crawl_journal(
            name=name,
            volume=volume,
            publisher=publisher,
            need_abs=need_abs,
            save_pkl=save_pkl,
            bib_fn=args.save,
            from_pkl=from_pkl,
            dblp_req_itv=dblp_req_itv,
            req_itv=req_itv,
        )
    else:
        crawl_conference(
            name=name,
            year=year,
            publisher=publisher,
            need_abs=need_abs,
            save_pkl=save_pkl,
            bib_fn=args.save,
            from_pkl=from_pkl,
            dblp_req_itv=dblp_req_itv,
            req_itv=req_itv,
        )
