import base64
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

import httpx
from nonebot.log import logger
from aiohttp import ClientConnectorError
from aiocqhttp.exceptions import ActionFailed
from nonebot import MessageSegment, get_bot  # type: ignore

from hoshino import Service
from hoshino.typing import CQEvent, HoshinoBot

from .utils.db_operation.db_operation import select_db
from .utils.message.get_image_and_at import ImageAndAt
from .utils.message.error_reply import *  # noqa: F403,F401
from .utils.alias.alias_to_char_name import alias_to_char_name
from .utils.exception.handle_exception import handle_exception
from .utils.genshin_fonts.genshin_fonts import genshin_font_origin

sv = Service('genshinuid')
hoshino_bot = get_bot()
