from httpx import get
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RESOURCE_PATH = Path(__file__).parents[2] / 'resource'
WEAPON_PATH = RESOURCE_PATH / 'weapon'
CHAR_PATH = RESOURCE_PATH / 'chars'
CHAR_DONE_PATH = RESOURCE_PATH / 'char_done'
CHAR_IMG_PATH = RESOURCE_PATH / 'char_img'
CHAR_NAMECARD_PATH = RESOURCE_PATH / 'char_namecard'
REL_PATH = RESOURCE_PATH / 'reliquaries'
CHAR_WEAPON_PATH = RESOURCE_PATH / 'char_weapon'
TEXT_PATH = RESOURCE_PATH / 'texture2d'


def get_char_pic(_id: str, url: str):
    with open(CHAR_PATH / f'{_id}.png', 'wb') as f:
        f.write(get(url).content)


def get_char_done_pic(_id: str, url: str, star: int):
    name = url.split('_')[-1]
    url = (
        'https://upload-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_'
        + name
    )
    char_data = get(url).content
    if star == 4:
        star1_path = TEXT_PATH / '4star_1.png'
        star2_path = TEXT_PATH / '4star_2.png'
    else:
        star1_path = TEXT_PATH / '5star_1.png'
        star2_path = TEXT_PATH / '5star_2.png'
    star_1 = Image.open(star1_path)
    star_2 = Image.open(star2_path)
    char_img = Image.open(BytesIO(char_data)).resize((104, 104), Image.ANTIALIAS)
    star_1.paste(char_img, (12, 15), char_img)
    star_1.paste(star_2, (0, 0), star_2)
    star_1.save(CHAR_DONE_PATH / str(_id) + '.png')


def get_weapon_pic(url: str):
    with open(WEAPON_PATH / url.split('/')[-1], 'wb') as f:
        f.write(get(url).content)


def get_char_img_pic(url: str):
    with open(CHAR_IMG_PATH / url.split('/')[-1], 'wb') as f:
        f.write(get(url).content)


def get_rel_pic(url: str):
    with open(REL_PATH / url.split('/')[-1], 'wb') as f:
        f.write(get(url).content)
