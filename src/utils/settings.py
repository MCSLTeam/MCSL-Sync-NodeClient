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
makedirs("data", exist_ok=True)
makedirs("logs", exist_ok=True)
makedirs("files", exist_ok=True)
makedirs("files/tmp", exist_ok=True)
makedirs("data/upstream", exist_ok=True)


def init_settings() -> None:
    SyncLogger.info("Initialize Settings...")
    if not osp.exists("data/settings.json"):
        with open(
            file="data/settings.json",
            mode="wb+",
        ) as newConfig:
            newConfig.write(dumps(config_template, option=OPT_INDENT_2))
    else:
        pass


def read_settings() -> dict:
    with open(file="data/settings.json", mode="r", encoding="utf-8") as f:
        cfg = loads(f.read())
    return cfg


def set_upstream(url: str) -> None:
    with open(file="data/settings.json", mode="r", encoding="utf-8") as f:
        cfg = loads(f.read())
    cfg["global_upstream"] = url
    with open(file="data/settings.json", mode="w", encoding="utf-8") as f:
        f.write(dumps(cfg, option=OPT_INDENT_2))


cfg = read_settings()  # type: dict
