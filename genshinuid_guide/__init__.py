from ..all_import import *

IMG_PATH = Path(__file__).parent / 'img'


@sv.on_rex('[\u4e00-\u9fa5]+(推荐|攻略)')
@handle_exception('建议')
async def send_guide_pic(bot: HoshinoBot, ev: CQEvent):
    if ev.message:
        msg = ev.message.extract_plain_text().replace(' ', '')
    else:
        return

    name = await alias_to_char_name(msg)
    url = 'https://img.genshin.minigg.cn/guide/{}.jpg'.format(name)
    if httpx.head(url).status_code == 200:
        logger.info('获得{}推荐图片成功！'.format(name))
        await bot.send(ev, MessageSegment.image(url))
    else:
        logger.warning('未获得{}推荐图片。'.format(name))


@sv.on_prefix('参考面板')
@handle_exception('参考面板')
async def send_bluekun_pic(bot: HoshinoBot, ev: CQEvent):
    if ev.message:
        msg = ev.message.extract_plain_text().replace(' ', '')
    else:
        return

    if str(msg) in ['冰', '水', '火', '草', '雷', '风', '岩']:
        name = str(msg)
    else:
        name = await alias_to_char_name(str(msg))
    img = IMG_PATH / '{}.jpg'.format(name)
    if img.exists():
        with open(img, 'rb') as f:
            im = MessageSegment.image(f.read())
        logger.info('获得{}参考面板图片成功！'.format(name))
        await bot.send(ev, im)
    else:
        logger.warning('未找到{}参考面板图片'.format(name))
