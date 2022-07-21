import asyncio
from typing import Any, List, Tuple, Union

import aiofiles
from nonebot import logger
from aiohttp.client import ClientSession

from .RESOURCE_PATH import *  # noqa: E501
from ..alias.alias_to_char_name import alias_to_char_name
from ..alias.avatarId_and_name_covert import name_to_avatar_id
from .resource_list import REL_ALL_LIST, CHAR_ALL_LIST, WEAPON_ALL_LIST
from ..minigg_api.get_minigg_data import (
    get_char_info,
    get_misc_info,
    get_audio_info,
    get_weapon_info,
)

MAX_TASKS = 5


async def _download(
    url: str,
    sess: ClientSession,
    sem: asyncio.Semaphore,
    file_name: str,
    file_path: Path,
):
    async with sem:
        logger.info(f'正在下载{file_name},URL为{url}')
        async with sess.get(url) as res:
            content = await res.read()

        if res.status != 200:
            logger.info(f"下载失败: {res.status}")

        async with aiofiles.open(file_path / file_name, "+wb") as f:
            await f.write(content)
            logger.info(f"下载成功: {res.status}")


async def download_by_minigg():
    await get_char_pic(CHAR_ALL_LIST)
    await get_weapon_pic(WEAPON_ALL_LIST)
    await get_rel_pic(REL_ALL_LIST)


async def get_char_pic(name_list: List):
    """
    :说明:
      接受角色名称保存图片至RESOURCE目录
      RESOURCE_PATH / 'chars'
      RESOURCE_PATH / 'char_stand'
      RESOURCE_PATH / 'char_side'
      保存立绘、侧视图、头像Icon
      保存为f'{avatar_id}.png'
    :参数:
      * name_list (str): 角色名称列表。
    """
    tasks = []
    sem = asyncio.Semaphore(MAX_TASKS)
    async with ClientSession() as sess:
        for name in name_list:
            logger.info(f'正在下载角色{name}的图片')
            name = await alias_to_char_name(name)
            avatar_id = await name_to_avatar_id(name)
            raw_data = await get_char_info(name)
            icon_url = raw_data['images']['icon']
            if name in ['空', '荧']:
                pass
            else:
                stand_url = raw_data['images']['cover1']
                tasks.append(
                    asyncio.wait_for(
                        _download(
                            stand_url,
                            sess,
                            sem,
                            f'{avatar_id}.png',
                            CHAR_STAND_PATH,
                        ),
                        timeout=20,
                    )
                )
            side_url = raw_data['images']['sideicon']
            tasks.append(
                asyncio.wait_for(
                    _download(
                        side_url,
                        sess,
                        sem,
                        f'{avatar_id}.png',
                        CHAR_SIDE_PATH,
                    ),
                    timeout=20,
                )
            )
            tasks.append(
                asyncio.wait_for(
                    _download(
                        icon_url,
                        sess,
                        sem,
                        f'{avatar_id}.png',
                        CHAR_PATH,
                    ),
                    timeout=20,
                )
            )
            if len(tasks) > MAX_TASKS:
                await asyncio.gather(*tasks)
                tasks = []
        await asyncio.gather(*tasks)


async def get_weapon_pic(name_list: List):
    """
    :说明:
      接受武器名称保存图片至RESOURCE目录
      会在RESOURCE_PATH / 'weapon'下
      保存为f'{weapon_name}.png'
    :参数:
      * name_list (str): 武器名称列表。
    """
    tasks = []
    sem = asyncio.Semaphore(MAX_TASKS)
    async with ClientSession() as sess:
        for name in name_list:
            logger.info(f'正在下载武器{name}的图片')
            raw_data = await get_weapon_info(name)
            icon_url = raw_data['images']['awakenicon']
            tasks.append(
                asyncio.wait_for(
                    _download(
                        icon_url,
                        sess,
                        sem,
                        f'{name}.png',
                        WEAPON_PATH,
                    ),
                    timeout=20,
                )
            )
            if len(tasks) > MAX_TASKS:
                await asyncio.gather(*tasks)
                tasks = []
        await asyncio.gather(*tasks)


async def get_rel_pic(name_list: List):
    """
    :说明:
      接受圣遗物套装名称保存图片至RESOURCE目录
      会在RESOURCE_PATH / 'reliquaries'下
      一次性保存五个部件的PNG图片
    :参数:
      * name_list (str): 武器套装名称列表。
    """
    tasks = []
    sem = asyncio.Semaphore(MAX_TASKS)
    async with ClientSession() as sess:
        for name in name_list:
            logger.info(f'正在下载圣遗物{name}的图片')
            raw_data = await get_misc_info('artifacts', name)
            for i in ['flower', 'plume', 'sands', 'goblet', 'circlet']:
                url = raw_data['images'][i]
                p_name = raw_data[i]['name']
                tasks.append(
                    asyncio.wait_for(
                        _download(
                            icon_url,
                            sess,
                            sem,
                            f'{p_name}.png',
                            REL_PATH,
                        ),
                        timeout=20,
                    )
                )
            if len(tasks) > MAX_TASKS:
                await asyncio.gather(*tasks)
                tasks = []
        await asyncio.gather(*tasks)
