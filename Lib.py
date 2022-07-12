import base64
import sqlite3
import json
from pathlib import Path
from typing import Any, Union, List, Tuple
from httpx import AsyncClient
from datetime import datetime
from time import strptime, strftime, localtime

from nonebot import Bot, get_bot, get_driver, on_command, on_regex, require
from nonebot.adapters.onebot.v11 import (ActionFailed, GroupMessageEvent, Message, MessageEvent, MessageSegment,
                                         PRIVATE_FRIEND, PrivateMessageEvent)
from nonebot.exception import FinishedException, ActionFailed
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, RegexGroup
from nonebot.permission import SUPERUSER

from .utils.handle_exception import handle_exception
from .utils.genshin_fonts import genshin_font_origin
from .utils.alias_to_char_name import alias_to_char_name

priority = 2