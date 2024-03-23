from orjson import loads, dumps, OPT_INDENT_2
from os import path as osp, makedirs
from .logger import SyncLogger

config_template = {
    "url": "127.0.0.1",
    "port": 4523,
    "ssl_cert_path": "",
    "ssl_key_path": "",
    "global_upstream": "",
}
cfg = config_template.copy()  # type: dict
makedirs("data", exist_ok=True)
makedirs("logs", exist_ok=True)
makedirs("files", exist_ok=True)
makedirs("files/tmp", exist_ok=True)
makedirs("data/upstream", exist_ok=True)


def init_settings():
    SyncLogger.info("Initialize Settings...")
    if not osp.exists("data/settings.json"):
        with open(
            file="data/settings.json",
            mode="wb+",
        ) as newConfig:
            newConfig.write(dumps(config_template, option=OPT_INDENT_2))
    else:
        pass


def read_settings():
    global cfg
    with open(file="data/settings.json", mode="r", encoding="utf-8") as f:
        cfg = loads(f.read())
