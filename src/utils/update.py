import os
from asyncio import create_task
from time import sleep

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

    async def load_self(self):
        for core in self.update_core_list:
            await self.load_single_core(core_type=core)

    async def load_single_core(self, core_type: str):
        mc_versions_list = await get_mc_versions(
            database_type="upstream", core_type=core_type
        )
        os.makedirs(f"files/{core_type}", exist_ok=True)
        for mc_version in mc_versions_list:
            await self.load_single_version(core_type=core_type, mc_version=mc_version)

    async def load_single_version(self, core_type: str, mc_version: str):
        core_versions_list = await get_core_versions(
            database_type="upstream", core_type=core_type, mc_version=mc_version
        )
        os.makedirs(f"files/{core_type}/{mc_version}", exist_ok=True)
        tasks = []
        for core_version in core_versions_list:
            while len(tasks) >= cfg.get("max_tasks"):
                sleep(0.5)
            tasks.append(create_task(
                self.load_single_build(
                    core_type=core_type,
                    mc_version=mc_version,
                    core_version=core_version,
                )
            ))
        for task in tasks:
            await task

    async def load_single_build(
            self, core_type: str, mc_version: str, core_version: str
    ):
        core_data = await get_specified_core_data(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
            core_version=core_version,
        )
        await AsyncDownloader(worker_num=4).download(
            uri=core_data["download_url"],
            core_type=core_data["core_type"],
            mc_version=core_data["mc_version"],
            core_version=core_data["core_version"],
        )
