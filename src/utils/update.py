import os
from asyncio import run
from concurrent.futures import ThreadPoolExecutor

from .database import (
    available_downloads,
    get_mc_versions,
    get_core_versions,
    get_specified_core_data,
)
from .downloader import AsyncDownloader
from .settings import cfg


async def sync_database():
    from aiohttp import ClientSession

    url_list = {
        (db_name := core_type + ".db"): cfg.get("global_upstream") + db_name
        for core_type in available_downloads
    }
    for database_name, db_url in url_list:
        async with ClientSession() as session:
            async with session.post(db_url) as resp:
                content = await resp.content.read()
                with open(f"data/{database_name}", "wb") as database_file:
                    database_file.write(content)


class FileSync:

    def __init__(self, upd: list | str = "all"):
        self.update_core_list = available_downloads if upd == "all" else upd.split(",")

    def load_self(self):
        with ThreadPoolExecutor(max_workers=cfg.get("max_threads")) as executor:
            futures = []
            for core_type in self.update_core_list:
                mc_versions_list = get_mc_versions(
                    database_type="upstream", core_type=core_type
                )
                os.makedirs(f"files/{core_type}", exist_ok=True)
                for mc_version in mc_versions_list:
                    core_versions_list = get_core_versions(
                        database_type="upstream", core_type=core_type, mc_version=mc_version
                    )
                    os.makedirs(f"files/{core_type}/{mc_version}", exist_ok=True)
                    for core_version in core_versions_list:
                        executor.submit(self.load_single_build, core_type, mc_version, core_version)
            for future in futures:
                future.result()

    def load_single_build(
            self, core_type: str, mc_version: str, core_version: str
    ):
        core_data = get_specified_core_data(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
            core_version=core_version,
        )

        async def download():
            try:
                await AsyncDownloader(worker_num=4).download(
                    uri=core_data["download_url"],
                    core_type=core_data["core_type"],
                    mc_version=core_data["mc_version"],
                    core_version=core_data["core_version"],
                )
            except AssertionError:
                pass

        run(download())
