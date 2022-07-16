from PIL import ImageFont
from pathlib import Path

FONT_PATH = Path(__file__).parent / 'yuanshen.ttf'
FONT_ORIGIN_PATH = Path(__file__).parent / 'yuanshen_origin.ttf'

def genshin_font(size: int):
    return ImageFont.truetype(str(FONT_PATH), size=size)


def genshin_font_origin(size: int) -> ImageFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)