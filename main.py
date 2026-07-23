import src.main
import sys

# def test_ieee():
#     from src.entry_ieee import get_full_abstract
#     import nodriver as nd
#     import logging
#     import asyncio
#     from src.settings import cookie_path, chrome_path
#     logger = logging.getLogger(__name__)
#     async def run_test():
#         config = nd.Config(
#             headless=False,
#             user_data_dir=cookie_path,
#             browser_executable_path=chrome_path,
#         )

#         browser = await nd.start(config=config)
#         # abstract = await get_full_abstract(
#         #     "https://doi.org/10.1109/TDSC.2021.3129512", browser, 0
#         # )
#         abstract = await get_full_abstract(
#             "https://ieeexplore.ieee.org/document/11391975", browser, 0
#         )
#         print(abstract)
#         browser.stop()
#         await asyncio.sleep(1)


#     logger.setLevel(logging.DEBUG)
#     handler = logging.StreamHandler()
#     handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)

#     asyncio.run(run_test())


if __name__ == "__main__":
    src.main.main(sys.argv[1:])
    # test_ieee()
