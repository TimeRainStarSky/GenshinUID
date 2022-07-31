from .draw_roleinfo_card import draw_pic
from ..all_import import *  # noqa: F403,F401
from ..utils.db_operation.db_operation import select_db

get_role_info = on_regex('^(uid|查询|mys)?([0-9]{9})?$', block=True)


@get_role_info.handle()
@handle_exception('查询角色信息')
async def send_role_info(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
    args: Tuple[Any, ...] = RegexGroup(),
):
    qid = event.user_id
    if args[1] is None:
        uid = await select_db(qid, mode='uid')
        uid = uid[0]
    else:
        uid = args[1]
    im = await draw_pic(uid)
    await matcher.finish(MessageSegment.image(im))
