from quart import Quart, make_response
from typing import Union
from orjson import dumps

app = Quart(__name__)


async def gen_response(
    *,
    status_code=200,
    data: Union[list, dict, str] = None,
    msg: str = "Ok",
):
    response = await make_response(
        dumps(
            {
                "data": data,
                "code": status_code,
                "msg": msg,
            },
        ),
        status_code,
    )
    response.mimetype = "application/json"
    return response
