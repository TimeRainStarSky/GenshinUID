import os.path

from nonebot import load_plugins, logger

load_plugins(
    os.path.dirname(__file__)
)