from .draw_resin_card import draw_resin_img
from ..all_import import *  # noqa: F403,F401
from ..utils.db_operation.db_operation import select_db
from ..utils.message.get_image_and_at import ImageAndAt
from ..utils.message.error_reply import *  # noqa: F403,F401

get_resin_info = on_command(
    '每日', aliases={'mr', '状态', '实时便笺', '便笺', '便签'}, block=True
)
# get_daily_info = on_command('当前状态')


@get_resin_info.handle()
@handle_exception('每日信息')
async def send_uid_info(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
    custom: ImageAndAt = Depends(),
):
    logger.info('开始执行[每日信息]')

    at = custom.get_first_at()
    if at:
        qid = at
    else:
        qid = event.user_id
    logger.info('[每日信息]QQ号: {}'.format(qid))

    try:
        uid = await select_db(qid, mode='uid')
        uid = uid[0]
    except TypeError:
        await matcher.finish(UID_HINT)
    logger.info('[每日信息]UID: {}'.format(uid))

    im = await draw_resin_img(uid)
    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish('发生了未知错误,请联系管理员检查后台输出!')
