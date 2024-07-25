from quart import Quart, request, send_file
from werkzeug.exceptions import HTTPException
from ..utils import __version__, cfg
import aiofiles.os
import uvicorn
from .model import gen_response

sync_api = Quart(__name__)


def start_production_server():
    uvicorn.run(
        app=sync_api,
        host=cfg.get("url"),
        port=cfg.get("port"),
        ssl_certfile=(
            cfg.get("ssl_cert_path") if cfg.get("ssl_cert_path") != "" else None
        ),
        ssl_keyfile=cfg.get("ssl_key_path") if cfg.get("ssl_key_path") != "" else None,
        headers=[
            (
                "Access-Control-Allow-Origin",
                "*"
            )
        ],
    )


@sync_api.errorhandler(Exception)
async def exception_handler(exc):
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.code
    return await gen_response(
        data={
            "request": {
                "method": request.method,
                "path": request.path,
            },
            "exception": str(exc),
        },
        status_code=status_code,
        msg=str(exc),
    )


@sync_api.route("/")
async def base_dir():
    """
    This is using docstrings for specifications.
    ---
    parameters:
        none
    responses:
      200:
        description: Say hello to the user
    """
    return await gen_response(
        status_code=200,
        msg=f"MCSL-Sync-NodeClient v{__version__} on Quart!",
    )


@sync_api.route("/public/statistics")
@sync_api.route("/public/statistics/")
async def get_app_info():
    (no_secret_cfg := cfg.copy()).pop("secret_key")
    return await gen_response(
        data={
            "name": "MCSL-Sync-Nodeside",
            "author": "MCSLTeam",
            "version": f"v{__version__}",
            "config": no_secret_cfg,
        },
        status_code=200,
        msg="Success!",
    )


@sync_api.route("/core")
@sync_api.route("/core/")
async def get_core():
    from ..utils import available_downloads

    resp = await gen_response(
        data=available_downloads, status_code=200, msg="Success!"
    )
    del available_downloads
    return resp


@sync_api.route("/core/<core_type>")
@sync_api.route("/core/<core_type>/")
async def get_mc_versions(core_type: str = ""):
    from ..utils import get_mc_versions, available_downloads

    database_data = (
        get_mc_versions(
            database_type="upstream",
            core_type=core_type,
        )
        if core_type in available_downloads
        else None
    )

    resp = await gen_response(
        data={"type": "upstream", "versions": database_data}
        if core_type in available_downloads
        else None,
        status_code=200 if core_type in available_downloads else 404,
        msg=(
            "Success!"
            if core_type in available_downloads
            else "Error: No data were found."
        ),
    )
    del get_mc_versions, database_data
    return resp


@sync_api.route("/core/<core_type>/<mc_version>")
@sync_api.route("/core/<core_type>/<mc_version>/")
async def get_core_versions(core_type: str = "", mc_version: str = ""):
    from ..utils import get_mc_versions, get_core_versions, available_downloads

    versions_list = (
        get_mc_versions(
            database_type="upstream",
            core_type=core_type,
        )
        if core_type in available_downloads
        else []
    )
    database_data = (
        get_core_versions(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
        )
        if mc_version in versions_list
        else []
    )
    resp = await gen_response(
        data={"type": "upstream", "builds": database_data}
        if mc_version in versions_list
        else None,
        status_code=200 if mc_version in versions_list else 404,
        msg="Success!" if mc_version in versions_list else "Error: No data were found.",
    )
    del (
        get_core_versions,
        get_mc_versions,
        database_data,
        versions_list,
    )
    return resp


@sync_api.route("/core/<core_type>/<mc_version>/<core_version>")
@sync_api.route("/core/<core_type>/<mc_version>/<core_version>/")
async def get_specified_core(
    core_type: str = "", mc_version: str = "", core_version: str = ""
):
    from ..utils import (
        get_mc_versions,
        get_core_versions,
        available_downloads,
        get_specified_core_data,
    )

    mc_versions_list = (
        get_mc_versions(
            database_type="upstream",
            core_type=core_type,
        )
        if core_type in available_downloads
        else []
    )
    core_versions_list = (
        get_core_versions(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
        )
        if mc_version in mc_versions_list
        else []
    )
    database_data = (
        get_specified_core_data(
            database_type="upstream",
            core_type=core_type,
            mc_version=mc_version,
            core_version=core_version,
        )
        if core_version in core_versions_list
        else {}
    )
    resp = await gen_response(
        data={"type": "upstream", "build": database_data}
        if core_version in core_versions_list
        else None,
        status_code=200 if core_version in core_versions_list else 404,
        msg=(
            "Success!"
            if core_version in core_versions_list
            else "Error: No data were found."
        ),
    )
    del (
        get_core_versions,
        get_mc_versions,
        database_data,
        mc_versions_list,
    )
    return resp


@sync_api.route("/core/<core_type>/<mc_version>/<core_version>/download")
@sync_api.route("/core/<core_type>/<mc_version>/<core_version>/download/")
async def get_file(core_type: str = "", mc_version: str = "", core_version: str = ""):
    if await aiofiles.os.path.exists(
        f"files/{core_type}/{mc_version}/{core_type}-{mc_version}-{core_version}.jar"
    ):
        resp = await send_file(
            filename_or_io=f"files/{core_type}/{mc_version}/{core_type}-{mc_version}-{core_version}.jar",
            attachment_filename=f"{core_type}-{mc_version}-{core_version}.jar",
            as_attachment=True,
        )
    else:
        resp = await gen_response(
            status_code=404,
            msg="Error: File not found.",
        )
    return resp
