import asyncio
import os
import pathlib
import time
from asyncio import Task
from typing import Optional

import aiohttp
from multidict import CIMultiDictProxy

from .logger import SyncLogger
from .network import get_proxy, headers


class AsyncDownloader:
    def __init__(self, worker_num=4, output_path="files"):
        self.worker_num = worker_num
        self.output_path = output_path

    async def download(
            self,
            uri: str,
            core_type: str = "",
            mc_version: str = "",
            core_version: str = "",
            retries: int = 3,
    ) -> pathlib.Path:
        """
        :param uri: 下载地址
        :param filename: 指定文件名, 缺省则自动获取
        :return: 下载完成的文件路径
        """
        content_length: int = 0
        filename = (
                core_type + "-" + mc_version + "-" + core_version + "." + uri.split(".")[-1]
        )
        file_path: pathlib.Path = pathlib.Path(
            self.output_path, core_type, mc_version, filename
        ).absolute()
        r_headers: Optional[CIMultiDictProxy] = None
        start_time = time.time()

        async with aiohttp.ClientSession(
                trust_env=not bool(isinstance(await get_proxy(), str)), headers=headers
        ) as session:
            async with session.head(uri, allow_redirects=True) as head_response:
                try:
                    assert head_response.ok
                except AssertionError as err:
                    retries -= 1
                    if retries > 0:
                        SyncLogger.warning(f"Download failed | {filename} | {retries} retries left")
                        await self.download(uri, core_type, mc_version, core_version, retries)
                    else:
                        SyncLogger.error(f"Download failed | {filename} ")
                        raise err
                r_headers = head_response.headers
                content_length = int(r_headers.get("Content-Length"), 0)
                SyncLogger.info(
                    f"Downloading | {filename} | {round(content_length / 1000000, 2)} MB"
                )

        if r_headers.get("Accept-Ranges", "none") == "bytes":
            await self.__download_with_range(uri, file_path, content_length)
        else:
            SyncLogger.warning(
                "Server does not support range requests, downloading with 1 worker!"
            )
            await self.__download_without_range(uri, file_path)
        SyncLogger.success(
            f"Downloaded | {filename} | {(content_length / 1000 / 1000) / (time.time() - start_time):.2f} MB/s | {time.time() - start_time:.2f} s"
        )
        return file_path

    async def __download_with_range(
            self, uri: str, file_path: pathlib.Path, content_length: int
    ):
        partial_length = content_length // self.worker_num + 1
        task_list = []

        for i in range(self.worker_num):
            begin = i * partial_length
            end = min((i + 1) * partial_length - 1, content_length)
            task_list.append(self.__download_task(uri, i, file_path, begin, end))
        await asyncio.gather(*task_list)
        self.__gather_part_files(file_path)

    async def __download_without_range(
            self, uri: str, file_path: pathlib.Path, chunk_size: int = 4096
    ):
        async with aiohttp.ClientSession(
                trust_env=not bool(isinstance(await get_proxy(), str)), headers=headers
        ) as session:
            async with session.get(uri) as response:
                with open(file_path, "wb") as f:
                    while True:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

    def __download_task(
            self,
            uri: str,
            serial: int,
            file_path: pathlib.Path,
            begin: int,
            end: int,
            chunk_size: int = 4096,
    ) -> Task:
        partial_filename = f"{self.output_path}/tmp/{file_path.stem}.part{serial}"

        async def download():
            async with aiohttp.ClientSession(
                    trust_env=not bool(isinstance(await get_proxy(), str)), headers=headers
            ) as session:
                async with session.get(
                        uri, headers={"Range": f"bytes={begin}-{end}"}
                ) as response:
                    with open(partial_filename, "wb") as f:
                        while True:
                            chunk = await response.content.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)

        return asyncio.create_task(download())

    def __gather_part_files(self, file_path: pathlib.Path):
        file_path = pathlib.Path(file_path)
        part_files = [
            self.output_path + "/tmp/" + file_path.stem + ".part" + str(i)
            for i in range(self.worker_num)
        ]

        with open(file_path, "wb") as f:
            for part_file in part_files:
                with open(part_file, "rb") as part:
                    f.write(part.read())
                # remove file
                os.remove(part_file)
