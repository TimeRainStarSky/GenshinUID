from .set_config import set_config
from ..all_import import *  # noqa: F403, F401
from ..utils.db_operation.db_operation import select_db
from ..utils.message.get_image_and_at import ImageAndAt
from ..utils.message.error_reply import *  # noqa: F403,F401

open_and_close_switch = on_regex(
    '^(\[CQ:at,qq=[0-9]+\] )?(gs)(开启|关闭)(.*)(\[CQ:at,qq=[0-9]+\])?$'
)


# 开启 自动签到 和 推送树脂提醒 功能
@open_and_close_switch.handle()
async def open_switch_func(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    matcher: Matcher,
    args: Tuple[Any, ...] = RegexGroup(),
    at: ImageAndAt = Depends(),
):
    qid = int(event.sender.user_id)
    at = at.get_first_at()
    config_name = args[3]

    logger.info(f'{qid} 尝试 {args[2]} 了 {config_name} 功能')

    if args[2] == '开启':
        query = 'OPEN'
        gid = (
            event.get_session_id().split('_')[1]
            if len(event.get_session_id().split('_')) == 3
            else 'on'
        )
    else:
        query = 'CLOSED'
        gid = 'off'

    if qid in SUPERUSERS:
        is_admin = True
    else:
        is_admin = False

    if at and is_admin:
        qid = at
    elif at and at != qid:
        await matcher.finish('你没有权限操作别人的状态噢~', at_sender=True)
        return

    try:
        uid = await select_db(qid, mode='uid')
        uid = uid[0]
    except TypeError:
        await matcher.finish(UID_HINT)

    im = await set_config(
        config_name=config_name,
        uid=uid,
        qid=qid,
        option=gid,
        query=query,
        is_admin=is_admin,
    )
    await matcher.finish(im, at_sender=True)
