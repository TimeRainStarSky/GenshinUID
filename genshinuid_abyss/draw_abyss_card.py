import math
import time
import datetime
import threading
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from typing import List, Tuple, Optional

from httpx import get
from nonebot import logger
from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..utils.get_cookies.get_cookies import GetCookies
from ..utils.mhy_api.get_mhy_data import get_character
from ..utils.draw_image_tools.send_image_tool import convert_img
from ..utils.draw_image_tools.draw_image_tool import get_simple_bg
from ..utils.genshin_fonts.genshin_fonts import genshin_font_origin

TEXT_PATH = Path(__file__).parent / 'texture2D'
CHAR_PATH = Path(__file__).parents[1] / 'resource' / 'chars'
CHAR_STAND_PATH = Path(__file__).parents[1] / 'resource' / 'char_stand'
CHAR_SIDE_PATH = Path(__file__).parents[1] / 'resource' / 'char_side'

abyss_title_pic = Image.open(TEXT_PATH / 'abyss_title.png')
char_mask = Image.open(TEXT_PATH / 'char_mask.png')
char_frame = Image.open(TEXT_PATH / 'char_frame.png')

text_title_color = (29, 29, 29)
text_floor_color = (30, 31, 25)

genshin_font_70 = genshin_font_origin(70)
genshin_font_32 = genshin_font_origin(32)
genshin_font_27 = genshin_font_origin(27)


async def get_abyss_star_pic(star: int) -> Image:
    star_pic = Image.open(TEXT_PATH / f'star{star}.png')
    return star_pic


async def get_rarity_pic(rarity: int) -> Image:
    rarity_pic = Image.open(TEXT_PATH / f'rarity{rarity}.png')
    return rarity_pic


async def get_rank_data(data: dict, path: Path):
    char_id = data[0]['avatar_id']
    char_pic = Image.open(path / f'{char_id}.png').convert('RGBA')
    if path == CHAR_STAND_PATH:
        char_pic = char_pic.resize((862, 528), Image.Resampling.BICUBIC)
    elif path == CHAR_SIDE_PATH:
        char_pic = char_pic.resize((60, 60), Image.Resampling.BICUBIC)
    rank_value = str(data[0]['value'])
    return char_pic, rank_value


async def draw_abyss_img(
    uid: str, floor: str = None, mode: str = 'uid', schedule_type: str = '1'
) -> Image:
    # 获取Cookies
    data_def = GetCookies()
    retcode = await data_def.get_useable_cookies(uid, mode, schedule_type)
    if not retcode:
        return retcode
    raw_data = data_def.raw_data
    raw_abyss_data = data_def.raw_abyss_data
    use_cookies = data_def.useable_cookies
    uid = data_def.uid

    # 获取数据
    raw_abyss_data = raw_abyss_data['data']
    char_data = raw_data['data']['avatars']
    char_temp = {}

    # 获取查询者数据
    is_unfull = False
    if floor:
        floor = int(floor) - 9
        if floor < 0:
            return '楼层不能小于9层!'
        if len(raw_abyss_data['floors']) >= floor + 1:
            floors_data = raw_abyss_data['floors'][floor]
        else:
            return '你还没有挑战该层!'
    else:
        floors_data = raw_abyss_data['floors'][-1]
    levels_num = len(floors_data['levels'])
    if floors_data['levels'][0]['battles']:
        floors_title = str(floors_data['index']) + '层'
    else:
        floors_title = '统计'
        is_unfull = True

    # 获取背景图片各项参数
    based_w = 625
    based_h = 415 if is_unfull else 415 + levels_num * 440
    bg_img = await get_simple_bg(based_w, based_h)

    white_overlay = Image.new('RGBA', (based_w, based_h), (255, 255, 255, 188))
    bg_img.paste(white_overlay, (0, 0), white_overlay)

    abyss_title = Image.new('RGBA', (625, 415), (0, 0, 0, 0))

    damage_rank = raw_abyss_data['damage_rank']
    defeat_rank = raw_abyss_data['defeat_rank']
    take_damage_rank = raw_abyss_data['take_damage_rank']
    normal_skill_rank = raw_abyss_data['normal_skill_rank']
    energy_skill_rank = raw_abyss_data['energy_skill_rank']

    dmg_pic, dmg_val = await get_rank_data(damage_rank, CHAR_STAND_PATH)
    defeat_pic, defeat_val = await get_rank_data(defeat_rank, CHAR_SIDE_PATH)
    (
        take_damage_pic,
        take_damage_val,
    ) = await get_rank_data(take_damage_rank, CHAR_SIDE_PATH)
    (
        normal_skill_pic,
        normal_skill_val,
    ) = await get_rank_data(normal_skill_rank, CHAR_SIDE_PATH)
    (
        energy_skill_pic,
        energy_skill_val,
    ) = await get_rank_data(energy_skill_rank, CHAR_SIDE_PATH)

    abyss_title.paste(dmg_pic, (13, -42), dmg_pic)
    abyss_title = Image.alpha_composite(abyss_title, abyss_title_pic)
    abyss_title.paste(defeat_pic, (5, 171), defeat_pic)
    abyss_title.paste(take_damage_pic, (5, 171 + 54), take_damage_pic)
    abyss_title.paste(normal_skill_pic, (5, 171 + 54 * 2), normal_skill_pic)
    abyss_title.paste(energy_skill_pic, (5, 171 + 54 * 3), energy_skill_pic)

    abyss_title_draw = ImageDraw.Draw(abyss_title)
    abyss_title_draw.text(
        (41, 95),
        f'深渊{floors_title}',
        font=genshin_font_70,
        fill=text_title_color,
        anchor='lm',
    )
    abyss_title_draw.text(
        (41, 139),
        f'UID{uid}',
        font=genshin_font_27,
        fill=text_title_color,
        anchor='lm',
    )
    abyss_title_draw.text(
        (610, 282),
        dmg_val,
        font=genshin_font_32,
        fill=text_title_color,
        anchor='rm',
    )
    abyss_title_draw.text(
        (610, 357),
        str(raw_abyss_data['total_battle_times']),
        font=genshin_font_32,
        fill=text_title_color,
        anchor='rm',
    )
    abyss_title_draw.text(
        (64, 217),
        defeat_val,
        font=genshin_font_27,
        fill=text_title_color,
        anchor='lm',
    )
    abyss_title_draw.text(
        (64, 217 + 54),
        take_damage_val,
        font=genshin_font_27,
        fill=text_title_color,
        anchor='lm',
    )
    abyss_title_draw.text(
        (64, 217 + 54 * 2),
        normal_skill_val,
        font=genshin_font_27,
        fill=text_title_color,
        anchor='lm',
    )
    abyss_title_draw.text(
        (64, 217 + 54 * 3),
        energy_skill_val,
        font=genshin_font_27,
        fill=text_title_color,
        anchor='lm',
    )

    bg_img.paste(abyss_title, (0, 0), abyss_title)
    if is_unfull:
        pass
    else:
        for index_floor, level in enumerate(floors_data['levels']):
            floor_pic = Image.new('RGBA', (615, 440), (0, 0, 0, 0))
            level_star = level['star']
            timestamp = int(level['battles'][0]['timestamp'])
            time_array = time.localtime(timestamp)
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_array)
            for index_part, battle in enumerate(level['battles']):
                for index_char, char in enumerate(battle['avatars']):
                    char_card = Image.new('RGBA', (150, 190), (0, 0, 0, 0))
                    # 获取命座
                    if char["id"] in char_temp:
                        talent_num = char_temp[char["id"]]
                    else:
                        for i in char_data:
                            if i["id"] == char["id"]:
                                talent_num = str(
                                    i["actived_constellation_num"]
                                )
                                char_temp[char["id"]] = talent_num
                                break
                    # 根据稀有度获取背景
                    char_bg = await get_rarity_pic(char['rarity'])
                    char_pic = (
                        Image.open(CHAR_PATH / f'{char["id"]}.png')
                        .convert('RGBA')
                        .resize((150, 150), Image.Resampling.LANCZOS)
                    )
                    char_img = Image.new('RGBA', (150, 190), (0, 0, 0, 0))
                    char_img.paste(char_pic, (0, 3), char_pic)
                    char_bg = Image.alpha_composite(char_bg, char_img)
                    char_card.paste(char_bg, (0, 0), char_mask)
                    char_card = Image.alpha_composite(char_card, char_frame)
                    char_card.draw = ImageDraw.Draw(char_card)
                    char_card.draw.text(
                        (75, 170),
                        f'Lv.{char["level"]}',
                        font=genshin_font_32,
                        fill=text_floor_color,
                        anchor='mm',
                    )
                    char_card.draw.text(
                        (6, 113),
                        f'{talent_num}命',
                        font=genshin_font_27,
                        fill=text_floor_color,
                        anchor='lm',
                    )
                    floor_pic.paste(
                        char_card,
                        (0 + 155 * index_char, 50 + index_part * 195),
                        char_card,
                    )
            star_pic = await get_abyss_star_pic(level_star)
            floor_pic.paste(star_pic, (420, -5), star_pic)
            floor_pic_draw = ImageDraw.Draw(floor_pic)
            floor_pic_draw.text(
                (31, 25),
                time_str,
                font=genshin_font_27,
                fill=text_floor_color,
                anchor='lm',
            )
            bg_img.paste(floor_pic, (5, 415 + index_floor * 440), floor_pic)

    res = await convert_img(bg_img)
    return res
