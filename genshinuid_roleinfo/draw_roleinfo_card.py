import asyncio
import datetime
import math
import threading
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from aiohttp import ClientSession
from typing import List, Optional, Tuple

from httpx import get
from nonebot import logger
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..utils.mhy_api.get_mhy_data import get_character, get_calculate_info
from ..utils.get_cookies.get_cookies import GetCookies
from ..utils.draw_image_tools.draw_image_tool import CustomizeImage
from ..utils.download_resource.download_resource import (
    get_char_pic,
    get_weapon_pic,
    get_rel_pic,
    get_char_img_pic,
)
from ..utils.genshin_fonts.genshin_fonts import genshin_font

STATUS = []
TEXT_PATH = Path(__file__).parent / 'texture2d'
RESOURCE_PATH = Path(__file__).parents[1] / 'resource'
WEAPON_PATH = RESOURCE_PATH / 'weapon'
CHAR_PATH = RESOURCE_PATH / 'chars'
CHAR_DONE_PATH = RESOURCE_PATH / 'char_done'
CHAR_IMG_PATH = RESOURCE_PATH / 'char_img'
CHAR_NAMECARD_PATH = RESOURCE_PATH / 'char_namecard'
REL_PATH = RESOURCE_PATH / 'reliquaries'
CHAR_WEAPON_PATH = RESOURCE_PATH / 'char_weapon'
TEXT_PATH = RESOURCE_PATH / 'texture2d'


async def _draw_char_pic(
    img: Image,
    char_data: dict,
    index: int,
    bg_color: Tuple[int, int, int],
    text_color: Tuple[int, int, int],
    bg_detail_color: Tuple[int, int, int],
    char_high_color: Tuple[int, int, int],
    char_talent_data: dict,
):
    char_mingzuo = 0
    for k in char_data['constellations']:
        if k['is_actived']:
            char_mingzuo += 1
    if char_data['rarity'] == 5:
        char_0 = Image.new('RGBA', (180, 90), char_high_color)
    else:
        char_0 = Image.new('RGBA', (180, 90), bg_color)
    char_0_raw = Image.open(TEXT_PATH / 'char_0.png')
    alpha = char_0_raw.getchannel('A')
    char_0.putalpha(alpha)

    char_2 = Image.new('RGBA', (180, 90), bg_detail_color)
    char_2_raw = Image.open(TEXT_PATH / 'char_2.png')
    alpha = char_2_raw.getchannel('A')
    char_2.putalpha(alpha)
    char_1_mask = Image.open(TEXT_PATH / 'char_1_mask.png')
    STATUS.append(char_data['name'])
    weapon_img_path = WEAPON_PATH / str(char_data['weapon']['icon'].split('/')[-1])
    char_img_path = CHAR_PATH / (str(char_data['id']) + '.png')
    if not weapon_img_path.exists():
        get_weapon_pic(char_data['weapon']['icon'])
    if not char_img_path.exists():
        get_char_pic(char_data['id'], char_data['icon'])

    char_img = Image.open(char_img_path).resize((81, 81), Image.ANTIALIAS)
    weapon_img = Image.open(weapon_img_path).resize((40, 40), Image.ANTIALIAS)
    weapon_1_mask = char_1_mask.resize((40, 40), Image.ANTIALIAS)
    char_0_temp = Image.new('RGBA', (180, 90))
    char_0_temp.paste(char_img, (8, 5), char_1_mask)
    char_0_temp.paste(weapon_img, (70, 45), weapon_1_mask)
    char_0.paste(char_0_temp, (0, 0), char_0_temp)
    char_0.paste(char_2, (0, 0), char_2)
    draw_text = ImageDraw.Draw(char_0)
    for i in range(0, 2):
        draw_text.text(
            (106 + 23 * i, 17),
            f'{str(char_talent_data["data"]["skill_list"][i]["level_current"])}',
            text_color,
            genshin_font(15),
            anchor='mm',
        )

    if (
        len(char_talent_data['data']['skill_list']) == 7
        and char_data['name'] != '珊瑚宫心海'
    ):
        draw_text.text(
            (106 + 23 * 2, 17),
            f'{str(char_talent_data["data"]["skill_list"][3]["level_current"])}',
            text_color,
            genshin_font(15),
            anchor='mm',
        )
    else:
        draw_text.text(
            (106 + 23 * 2, 17),
            f'{str(char_talent_data["data"]["skill_list"][2]["level_current"])}',
            text_color,
            genshin_font(15),
            anchor='mm',
        )

    draw_text.text(
        (42, 77),
        'Lv.{}'.format(str(char_data['level'])),
        text_color,
        genshin_font(16),
        anchor='mm',
    )
    draw_text.text(
        (162, 38), '{}命'.format(char_mingzuo), text_color, genshin_font(18), anchor='rm'
    )
    draw_text.text(
        (115, 57),
        'Lv.{}'.format(str(char_data['weapon']['level'])),
        text_color,
        genshin_font(18),
        anchor='lm',
    )
    draw_text.text(
        (115, 75),
        '{}精'.format(str(char_data['weapon']['affix_level'])),
        text_color,
        genshin_font(16),
        anchor='lm',
    )

    if str(char_data['fetter']) == '10' or str(char_data['name']) == '旅行者':
        draw_text.text((74, 19), '♥', text_color, genshin_font(14), anchor='mm')
    else:
        draw_text.text(
            (73, 18),
            '{}'.format(str(char_data['fetter'])),
            text_color,
            genshin_font(16),
            anchor='mm',
        )

    char_crop = (75 + 190 * (index % 4), 900 + 100 * (index // 4))
    STATUS.remove(char_data['name'])
    img.paste(char_0, char_crop, char_0)
    logger.debug(f"Draw {char_data['name']}")


async def get_all_calculate_info(
    client: ClientSession, uid: str, char_id: List[str], ck: str, name: list
):
    tasks = []
    for id_, name_ in zip(char_id, name):
        tasks.append(get_calculate_info(client, uid, id_, ck, name_))
    data = []
    repos = await asyncio.wait(tasks)
    for i in repos[0]:
        data.append(i.result())
    return data


async def draw_pic(
    uid: str,
    nickname: str,
    image: Optional[str] = None,
    mode: int = 2,
    role_level: Optional[int] = None,
):
    # 获取Cookies
    data_def = GetCookies()
    retcode = await data_def.get_useable_cookies(uid, mode)
    if not retcode:
        return retcode
    use_cookies = data_def.useable_cookies
    raw_data = data_def.raw_data
    uid = data_def.uid
    nickname = data_def.nickname if data_def.nickname else nickname

    # 记录数据
    raw_data = raw_data['data']
    char_data = raw_data['avatars']

    char_ids = []
    char_names = []

    for i in char_data:
        char_ids.append(i['id'])
        char_names.append(i['name'])

    char_rawdata = await get_character(uid, char_ids, use_cookies)
    char_datas = char_rawdata['data']['avatars']

    # 确定角色占用行数
    char_num = len(char_datas)
    char_hang = 1 + (char_num - 1) // 4 if char_num > 8 else char_num

    # 获取背景图片各项参数
    based_w = 900
    based_h = 970 + char_hang * 100 if char_num > 8 else 990 + char_hang * 110
    image_def = CustomizeImage(image, based_w, based_h)
    bg_img = image_def.bg_img
    bg_color = image_def.bg_color
    text_color = image_def.text_color
    char_color = image_def.char_color
    bg_detail_color = image_def.bg_detail_color
    char_high_color = image_def.char_high_color

    # 确定texture2D路径
    panle1_path = TEXT_PATH / 'panle_1.png'
    panle3_path = TEXT_PATH / 'panle_3.png'

    avatar_bg_path = TEXT_PATH / 'avatar_bg.png'
    avatar_fg_path = TEXT_PATH / 'avatar_fg.png'

    all_mask_path = TEXT_PATH / 'All_Mask.png'

    # 转换遮罩的颜色、大小匹配，并paste上去
    all_mask = Image.open(all_mask_path).resize(bg_img.size, Image.ANTIALIAS)
    all_mask_img = Image.new('RGBA', (based_w, based_h), bg_color)
    bg_img.paste(all_mask_img, (0, 0), all_mask)

    # 操作图片
    panle1 = Image.open(panle1_path)
    panle3 = Image.open(panle3_path)
    avatar_bg = Image.open(avatar_bg_path)
    avatar_fg = Image.open(avatar_fg_path)

    # 确定主体框架
    avatar_bg_color = Image.new('RGBA', (316, 100), bg_color)
    panle1_color = Image.new('RGBA', (900, 900), text_color)
    bg_img.paste(panle1_color, (0, 0), panle1)
    bg_img.paste(
        panle3,
        (0, char_hang * 100 + 880) if char_num > 8 else (0, char_hang * 110 + 900),
        panle3,
    )
    bg_img.paste(avatar_bg_color, (113, 98), avatar_bg)
    bg_img.paste(avatar_fg, (114, 95), avatar_fg)

    # 绘制基础信息文字
    text_draw = ImageDraw.Draw(bg_img)

    if role_level:
        text_draw.text(
            (140, 200), '冒险等级：' + f'{role_level}', text_color, genshin_font(20)
        )

    text_draw.text((220, 123), f'{nickname}', text_color, genshin_font(32))
    text_draw.text((235, 163), 'UID ' + f'{uid}', text_color, genshin_font(14))

    # 活跃天数/成就数量/深渊信息
    text_draw.text(
        (640, 94.8),
        str(raw_data['stats']['active_day_number']),
        text_color,
        genshin_font(26),
    )
    text_draw.text(
        (640, 139.3),
        str(raw_data['stats']['achievement_number']),
        text_color,
        genshin_font(26),
    )
    text_draw.text(
        (640, 183.9), raw_data['stats']['spiral_abyss'], text_color, genshin_font(26)
    )

    # 奇馈宝箱
    text_draw.text(
        (505, 375),
        str(raw_data['stats']['magic_chest_number']),
        text_color,
        genshin_font(24),
    )

    # 开启锚点和秘境数量
    text_draw.text(
        (505, 426),
        str(raw_data['stats']['way_point_number']),
        text_color,
        genshin_font(24),
    )
    text_draw.text(
        (505, 477),
        str(raw_data['stats']['domain_number']),
        text_color,
        genshin_font(24),
    )

    # 已获角色
    text_draw.text(
        (505, 528),
        str(raw_data['stats']['avatar_number']),
        text_color,
        genshin_font(24),
    )

    # 宝箱
    text_draw.text(
        (245, 375),
        str(raw_data['stats']['common_chest_number']),
        text_color,
        genshin_font(24),
    )
    text_draw.text(
        (245, 426),
        str(raw_data['stats']['exquisite_chest_number']),
        text_color,
        genshin_font(24),
    )
    text_draw.text(
        (245, 477),
        str(raw_data['stats']['precious_chest_number']),
        text_color,
        genshin_font(24),
    )
    text_draw.text(
        (245, 528),
        str(raw_data['stats']['luxurious_chest_number']),
        text_color,
        genshin_font(24),
    )

    mondstadt = (
        liyue
    ) = dragonspine = inazuma = offering = chasms_maw = under_chasms_maw = dict()
    for i in raw_data['world_explorations']:
        # 蒙德
        if i['id'] == 1:
            mondstadt = i
        # 璃月
        elif i['id'] == 2:
            liyue = i
        # 龙脊雪山
        elif i['id'] == 3:
            dragonspine = i
        # 稻妻
        elif i['id'] == 4:
            inazuma = i
        # 渊下宫
        elif i['id'] == 5:
            offering = i
        # 璃月层岩巨渊
        elif i['id'] == 6:
            chasms_maw = i
        # 璃月层岩巨渊·地下矿区
        elif i['id'] == 7:
            under_chasms_maw = i

    # 层岩巨渊
    if chasms_maw:
        text_draw.text(
            (477, 727),
            str(chasms_maw['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )
        text_draw.text(
            (500, 782),
            'lv.' + str(chasms_maw['offerings'][0]['level']),
            text_color,
            genshin_font(22),
        )

    if under_chasms_maw:
        text_draw.text(
            (523, 753),
            str(under_chasms_maw['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )

    # 蒙德
    if mondstadt:
        text_draw.text(
            (235, 600),
            str(mondstadt['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )
        text_draw.text(
            (235, 630), 'lv.' + str(mondstadt['level']), text_color, genshin_font(22)
        )
    text_draw.text(
        (258, 660),
        str(raw_data['stats']['anemoculus_number']),
        text_color,
        genshin_font(22),
    )

    # 璃月
    if liyue:
        text_draw.text(
            (480, 597),
            str(liyue['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )
        text_draw.text(
            (480, 627), 'lv.' + str(liyue['level']), text_color, genshin_font(22)
        )
    text_draw.text(
        (503, 657),
        str(raw_data['stats']['geoculus_number']),
        text_color,
        genshin_font(22),
    )

    # 雪山
    if dragonspine:
        text_draw.text(
            (238, 733),
            str(dragonspine['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )
        text_draw.text(
            (238, 764), 'lv.' + str(dragonspine['level']), text_color, genshin_font(22)
        )

    # 稻妻
    if inazuma:
        text_draw.text(
            (750, 588),
            str(inazuma['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )
        text_draw.text(
            (750, 616), 'lv.' + str(inazuma['level']), text_color, genshin_font(22)
        )
        text_draw.text(
            (750, 644),
            'lv.' + str(inazuma['offerings'][0]['level']),
            text_color,
            genshin_font(22),
        )
    text_draw.text(
        (773, 672),
        str(raw_data['stats']['electroculus_number']),
        text_color,
        genshin_font(22),
    )

    # 渊下宫
    if offering:
        text_draw.text(
            (750, 750),
            str(offering['exploration_percentage'] / 10) + '%',
            text_color,
            genshin_font(22),
        )

    # 家园
    if len(raw_data['homes']):
        text_draw.text(
            (720, 375),
            'lv.' + str(raw_data['homes'][0]['level']),
            text_color,
            genshin_font(24),
        )
        text_draw.text(
            (720, 426),
            str(raw_data['homes'][0]['visit_num']),
            text_color,
            genshin_font(24),
        )
        text_draw.text(
            (720, 477),
            str(raw_data['homes'][0]['item_num']),
            text_color,
            genshin_font(24),
        )
        text_draw.text(
            (720, 528),
            str(raw_data['homes'][0]['comfort_num']),
            text_color,
            genshin_font(24),
        )
    else:
        text_draw.text((720, 375), '未开', text_color, genshin_font(24))
        text_draw.text((720, 426), '未开', text_color, genshin_font(24))
        text_draw.text((720, 477), '未开', text_color, genshin_font(24))
        text_draw.text((720, 528), '未开', text_color, genshin_font(24))

    # 确定texture2D路径
    charpic_mask_path = TEXT_PATH / 'charpic_mask.png'
    weaponpic_mask_path = TEXT_PATH / 'weaponpic_mask.png'

    def get_text(star, step):
        return TEXT_PATH / '{}s_{}.png'.format(str(star), str(step))

    charpic_mask = Image.open(charpic_mask_path)
    weaponpic_mask = Image.open(weaponpic_mask_path)

    char_bg_path = TEXT_PATH / 'char_bg.png'
    char_fg_path = TEXT_PATH / 'char_fg.png'

    char_bg = Image.open(char_bg_path)
    char_fg = Image.open(char_fg_path)

    num = 0
    for index, i in enumerate(char_datas):
        if i['rarity'] > 5:
            char_datas[index]['rarity'] = 3
    char_datas.sort(key=lambda x: (-x['rarity'], -x['level'], -x['fetter']))

    if char_num > 8:
        client = ClientSession()
        talent_data = await get_all_calculate_info(
            client, uid, char_ids, use_cookies, char_names
        )
        await client.close()

        tasks = []
        for index, i in enumerate(char_datas):
            for j in talent_data:
                if j['name'] == i['name']:
                    tasks.append(
                        _draw_char_pic(
                            bg_img,
                            i,
                            index,
                            char_color,
                            text_color,
                            bg_detail_color,
                            char_high_color,
                            j,
                        )
                    )
        await asyncio.wait(tasks)
    else:
        charset_mask = Image.new('RGBA', (900, 130), char_color)
        for i in char_datas:
            char_mingzuo = 0
            for k in i['constellations']:
                if k['is_actived']:
                    char_mingzuo += 1

            char_name = i['name']
            char_id = i['id']
            char_level = i['level']
            char_img_icon = i['image']

            char_weapon_star = i['weapon']['rarity']
            char_weapon_level = i['weapon']['level']
            char_weapon_jinglian = i['weapon']['affix_level']
            char_weapon_icon = i['weapon']['icon']

            weapon_img_path = WEAPON_PATH / str(char_weapon_icon.split('/')[-1])
            char_img_path = CHAR_IMG_PATH / str(char_img_icon.split('/')[-1])
            char_path = CHAR_PATH / (str(i['id']) + '.png')
            if not weapon_img_path.exists():
                get_weapon_pic(char_weapon_icon)
            if not char_img_path.exists():
                get_char_img_pic(char_img_icon)
            if not char_path.exists():
                get_char_pic(i['id'], i['icon'])

            char_stand_mask = Image.open(TEXT_PATH / 'stand_mask.png')
            char_stand = Image.open(char_img_path)
            char_img = Image.open(char_path)
            weapon_img = Image.open(weapon_img_path)

            char_img = char_img.resize((100, 100), Image.ANTIALIAS)
            weapon_img = weapon_img.resize((47, 47), Image.ANTIALIAS)

            charpic = Image.new('RGBA', (900, 130))
            charpic_temp = Image.new('RGBA', (900, 130))

            charpic.paste(charset_mask, (0, 0), char_bg)

            weapon_bg = Image.open(get_text(char_weapon_star, 3))
            charpic_temp.paste(char_stand, (395, -99), char_stand_mask)
            charpic.paste(weapon_bg, (72, 10), weapon_bg)
            charpic_temp.paste(char_img, (81, 13), charpic_mask)
            charpic_temp.paste(char_fg, (0, 0), char_fg)
            charpic_temp.paste(weapon_img, (141, 72), weaponpic_mask)
            charpic.paste(charpic_temp, (0, 0), charpic_temp)

            for _, k in enumerate(i['reliquaries']):
                if not os.path.exists(REL_PATH / str(k['icon'].split('/')[-1])):
                    get_rel_pic(k['icon'])
                rel = REL_PATH / str(k['icon'].split('/')[-1])
                rel_img = Image.open(rel).resize((43, 43), Image.ANTIALIAS)
                rel_bg = Image.open(get_text(k['rarity'], 3))

                if k['pos_name'] == '生之花':
                    charpic.paste(rel_bg, (287 + 55 * 0, -14), rel_bg)
                    charpic.paste(rel_img, (360 + 55 * 0, 49), rel_img)
                elif k['pos_name'] == '死之羽':
                    charpic.paste(rel_bg, (287 + 55 * 1, -14), rel_bg)
                    charpic.paste(rel_img, (360 + 55 * 1, 49), rel_img)
                elif k['pos_name'] == '时之沙':
                    charpic.paste(rel_bg, (287 + 55 * 2, -14), rel_bg)
                    charpic.paste(rel_img, (360 + 55 * 2, 49), rel_img)
                elif k['pos_name'] == '空之杯':
                    charpic.paste(rel_bg, (287 + 55 * 3, -14), rel_bg)
                    charpic.paste(rel_img, (360 + 55 * 3, 49), rel_img)
                elif k['pos_name'] == '理之冠':
                    charpic.paste(rel_bg, (287 + 55 * 4, -14), rel_bg)
                    charpic.paste(rel_img, (360 + 55 * 4, 49), rel_img)

            char_draw = ImageDraw.Draw(charpic)

            char_draw.text(
                (188, 30),
                i['name'] + ' ' + f'Lv.{str(char_level)}',
                text_color,
                genshin_font(22),
            )
            char_draw.text(
                (222, 87),
                f'{str(i["fetter"])}' if str(char_name) != '旅行者' else '10',
                text_color,
                genshin_font(15),
                anchor='mm',
            )
            char_draw.text(
                (255, 87),
                f'{str(char_mingzuo)}',
                text_color,
                genshin_font(15),
                anchor='mm',
            )
            char_draw.text(
                (218, 67),
                f'{str(char_weapon_level)}级{str(char_weapon_jinglian)}精',
                text_color,
                genshin_font(15),
                anchor='lm',
            )
            char_crop = (0, 900 + 110 * num)
            num += 1
            bg_img.paste(charpic, char_crop, charpic)

    # 转换之后发送
    bg_img = bg_img.convert('RGB')
    result_buffer = BytesIO()
    bg_img.save(result_buffer, format='JPEG', subsampling=0, quality=90)
    imgmes = 'base64://' + b64encode(result_buffer.getvalue()).decode()
    resultmes = imgmes
    return resultmes
