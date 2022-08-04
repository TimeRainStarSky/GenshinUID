from .draw_resin_card import get_resin_img
from ..all_import import *  # noqa: F403,F401
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
    args: Tuple[Any, ...] = CommandArg(),
):
    logger.info('开始执行[每日信息]')
    if args:
        return

    at = custom.get_first_at()
    qid = event.user_id
    if at:
        qid = at
    logger.info('[每日信息]QQ号: {}'.format(qid))

    im = await get_resin_img(qid)
    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish('发生了未知错误,请联系管理员检查后台输出!')
