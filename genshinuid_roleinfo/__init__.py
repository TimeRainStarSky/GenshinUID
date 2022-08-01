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
    logger.info('开始执行[查询角色信息]')
    logger.info('[查询角色信息]参数: {}'.format(args))
    qid = event.user_id
    if args[1] is None:
        uid = await select_db(qid, mode='uid')
        uid = uid[0]
    else:
        uid = args[1]
    logger.info('[查询角色信息]uid: {}'.format(uid))
    im = await draw_pic(uid)

    if isinstance(im, str):
        await matcher.finish(im)
    elif isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish('发生了未知错误,请联系管理员检查后台输出!')
