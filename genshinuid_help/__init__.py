from ..all_import import *  # noqa: F403,F401

HELP_IMG = Path(__file__).parent / 'help.png'


@sv.on_fullmatch('gs帮助')
@handle_exception('建议')
async def send_guide_pic(bot: HoshinoBot, ev: CQEvent):
    logger.info('获得gs帮助图片成功！')
    await bot.send(ev, MessageSegment.image(HELP_IMG))
