from .draw_abyss_card import draw_abyss_img
from ..all_import import *  # noqa: F403,F401
from ..utils.db_operation.db_operation import select_db

get_abyss_info = on_regex(
    '^(uid|查询|mys)?([0-9]{9})?(上期)?(深渊)([0-9]{0,2})?$', priority=priority
)


@get_abyss_info.handle()
@handle_exception('查询深渊信息')
async def send_uid_info(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
    args: Tuple[Any, ...] = RegexGroup(),
    image: ImageAndAt = Depends(),
):
    qid = event.user_id

    if args[0] == 'mys':
        mode = 'mys'
    else:
        mode = 'uid'

    # 判断uid
    if args[1] is None:
        uid = await select_db(qid, mode='uid')
        uid = uid[0]
    else:
        uid = args[1]

    # 判断深渊期数
    if args[2] is None:
        schedule_type = '1'
    else:
        schedule_type = '2'

    im = await draw_abyss_img(uid, args[4], mode, schedule_type)
    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish('发生了未知错误,请联系管理员检查后台输出!')
