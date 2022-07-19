from .draw_roleinfo_card import draw_pic
from ..all_import import *  # noqa: F403,F401
from ..utils.db_operation.db_operation import select_db

get_uid_info = on_regex('^(uid|查询)?([0-9]{9})?$', priority=priority)
get_mys_info = on_regex('^(mys)?([0-9]+)?$', priority=priority)


@get_uid_info.handle()
@handle_exception('查询角色信息')
async def send_uid_info(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
    args: Tuple[Any, ...] = RegexGroup(),
    image: ImageAndAt = Depends(),
):
    qid = event.user_id
    nickname = event.sender.nickname
    if args[1] is None:
        uid = await select_db(qid)
    else:
        uid = args[1]
    im = await draw_pic(uid, nickname)
    await matcher.finish(MessageSegment.image(im))
