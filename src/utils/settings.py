from hashlib import md5
from os import path as osp, makedirs, name as osname, getenv, getlogin
from platform import processor, system as sysType

from orjson import loads, dumps, OPT_INDENT_2

from .logger import SyncLogger

config_template = {
    "url": "0.0.0.0",
    "port": 4524,
    "ssl_cert_path": "",
    "ssl_key_path": "",
    "max_threads": 32,
    "global_upstream": "",
    "secret_key": "".join(
        [
            md5(
                f"{getlogin() if osname == 'nt' else getenv('USER')}{processor()}{sysType()}".encode()
            ).hexdigest()[i: i + 4]
            for i in range(0, 24, 1)
        ]
    ),
}
makedirs("data", exist_ok=True)
makedirs("logs", exist_ok=True)
makedirs("files", exist_ok=True)
makedirs("data/upstream", exist_ok=True)

def init_settings() -> None:
    SyncLogger.info("Initializing Settings...")
    if not osp.exists("data/settings.json"):
        with open(
            file="data/settings.json",
            mode="wb+",
        ) as newConfig:
            newConfig.write(dumps(config_template, option=OPT_INDENT_2))
    else:
        pass


def read_settings() -> dict:
    try:
        with open(file="data/settings.json", mode="r", encoding="utf-8") as f:
            cfg = loads(f.read())
        return cfg
    except FileNotFoundError:
        init_settings()
        read_settings()


cfg = read_settings()

def set_upstream(url: str) -> None:
    with open(file="data/settings.json", mode="r", encoding="utf-8") as f:
        cfg = loads(f.read())
    cfg["global_upstream"] = url
    with open(file="data/settings.json", mode="w", encoding="utf-8") as f:
        f.write(dumps(cfg, option=OPT_INDENT_2))
