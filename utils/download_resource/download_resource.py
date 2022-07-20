from httpx import get

from .RESOURCE_PATH import *  # noqa: E501
from ..alias.alias_to_char_name import alias_to_char_name
from ..alias.avatarId_and_name_covert import name_to_avatar_id
from ..minigg_api.get_minigg_data import (
    get_char_info,
    get_misc_info,
    get_audio_info,
    get_weapon_info,
)


async def get_char_pic(name: str):
    """
    :说明:
      接受角色名称保存图片至RESOURCE目录
      RESOURCE_PATH / 'chars'
      RESOURCE_PATH / 'char_stand'
      RESOURCE_PATH / 'char_side'
      保存立绘、侧视图、头像Icon
      保存为f'{avatar_id}.png'
    :参数:
      * name (str): 武器名称。
    """
    name = await alias_to_char_name(name)
    avatar_id = await name_to_avatar_id(name)
    raw_data = await get_char_info(name)
    icon_url = raw_data['images']['icon']
    stand_url = raw_data['images']['cover1']
    side_url = raw_data['images']['sideicon']
    with open(CHAR_PATH / f'{avatar_id}.png', 'wb') as f:
        f.write(get(icon_url).content)
    with open(CHAR_STAND_PATH / f'{avatar_id}.png', 'wb') as f:
        f.write(get(stand_url).content)
    with open(CHAR_SIDE_PATH / f'{avatar_id}.png', 'wb') as f:
        f.write(get(side_url).content)


async def get_weapon_pic(name: str):
    """
    :说明:
      接受武器名称保存图片至RESOURCE目录
      会在RESOURCE_PATH / 'weapon'下
      保存为f'{weapon_name}.png'
    :参数:
      * name (str): 武器名称。
    """
    raw_data = await get_weapon_info(name)
    icon_url = raw_data['images']['awakenicon']
    with open(WEAPON_PATH / f'{name}.png', 'wb') as f:
        f.write(get(icon_url).content)


async def get_rel_pic(name: str):
    """
    :说明:
      接受圣遗物套装名称保存图片至RESOURCE目录
      会在RESOURCE_PATH / 'reliquaries'下
      一次性保存五个部件的PNG图片
    :参数:
      * name (str): 圣遗物套装名称。
    """
    raw_data = await get_misc_info('artifacts', name)
    for i in ['flower', 'plume', 'sands', 'goblet', 'circlet']:
        url = raw_data['images'][i]
        p_name = raw_data[i]['name']
        with open(REL_PATH / f'{p_name}.png', 'wb') as f:
            f.write(get(url).content)
