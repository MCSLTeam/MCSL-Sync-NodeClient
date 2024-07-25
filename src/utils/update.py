import os
from asyncio import run
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
from time import sleep

from . import SyncLogger
from .database import (
    available_downloads,
    get_mc_versions,
    get_core_versions,
    get_specified_core_data,
)
from .downloader import Downloader
from .settings import cfg

downloader = Downloader(output_path="files")

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
    download_threads = 0
    total_downloads = 0
    finished_downloads = 0
    failed_downloads = []

    def __init__(self, upd: list | str = "all"):
        self.update_core_list = available_downloads if upd == "all" else upd.split(",")

    def load_self(self):
        with ThreadPoolExecutor(max_workers=cfg.get("max_threads")) as executor:
            futures = []

            def progress_logger():
                while True:
                    if self.total_downloads == 0:
                        SyncLogger.info(
                            f"Download threads: {self.download_threads} | "
                            f"Finished downloads: {self.finished_downloads} | "
                            f"Failed downloads: {self.failed_downloads}")
                    else:
                        SyncLogger.info(
                            f"Download threads: {self.download_threads} | "
                            f"Total downloads: {self.total_downloads} | "
                            f"Finished downloads: {self.finished_downloads} | "
                            f"Failed downloads: {len(self.failed_downloads)} | "
                            f"Download progress: {round((self.finished_downloads + len(self.failed_downloads)) * 100.0 / self.total_downloads, 2)}%")
                    sleep(1)

            Thread(target=progress_logger, daemon=True).start()

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
                        futures.append(executor.submit(self.load_single_build, core_type, mc_version, core_version))
            self.total_downloads = len(futures)
            for future in futures:
                future.result()
            SyncLogger.info(f"Finished downloading | Failed downloads: {self.failed_downloads}")

    def load_single_build(
            self, core_type: str, mc_version: str, core_version: str
    ):
        self.download_threads += 1
        core_data = get_specified_core_data(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
            core_version=core_version,
        )

        async def download():
            try:
                downloader.download(
                    uri=core_data["download_url"],
                    core_type=core_data["core_type"],
                    mc_version=core_data["mc_version"],
                    core_version=core_data["core_version"],
                )
                self.finished_downloads += 1
            except Exception:
                self.failed_downloads.append(core_data["core_type"] + '-' + core_data["mc_version"] + '-' + core_data["core_version"])
            finally:
                self.download_threads -= 1

        run(download())
