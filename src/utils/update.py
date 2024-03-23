from .database import (
    available_downloads,
    get_mc_versions,
    get_core_versions,
    get_specified_core_data,
)
from .downloader import AsyncDownloader
from asyncio import create_task


async def sync_database():
    pass


class FileSync:
    def __init__(self, upd: list | str = "all"):
        self.update_core_list = available_downloads if upd == "all" else upd.split(",")
        self.download_tasks: list = []

    async def load_self(self):
        tasks = [
            create_task(self.load_single_core(core_type=core))
            for core in self.update_core_list
        ]
        for task in tasks:
            await task
        for task in self.download_tasks:
            await task

    async def load_single_core(self, core_type: str):
        mc_versions_list = await get_mc_versions(
            database_type="upstream", core_type=core_type
        )
        tasks = [
            create_task(
                self.load_single_version(core_type=core_type, mc_version=mc_version)
            )
            for mc_version in mc_versions_list
        ]
        for task in tasks:
            await task

    async def load_single_version(self, core_type: str, mc_version: str):
        core_versions_list = await get_core_versions(
            database_type="upstream", core_type=core_type, mc_version=mc_version
        )
        tasks = [
            create_task(
                self.load_single_build(
                    core_type=core_type,
                    mc_version=mc_version,
                    core_version=core_version,
                )
            )
            for core_version in core_versions_list
        ]
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
        self.download_tasks.append(
            create_task(AsyncDownloader().download(
                uri=core_data["download_url"],
                core_type=core_data["core_type"],
                mc_version=core_data["mc_version"],
                core_version=core_data["core_version"],
            ))
        )
