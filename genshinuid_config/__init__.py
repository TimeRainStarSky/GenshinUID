from ..all_import import *  # noqa: F403, F401
from ..utils.message.get_image_and_at import ImageAndAt
from ..utils.message.error_reply import *  # noqa: F403,F401

open_switch = on_command('gs开启')
close_switch = on_command('gs关闭')


# 开启 自动签到 和 推送树脂提醒 功能
@open_switch.handle()
async def open_switch_func(
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg(),
    at: ImageAndAt = Depends(),
):
    try:
        message = args.extract_plain_text().strip().replace(' ', '')
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))

        qid = int(event.sender.user_id)
        at = at.get_first_at()

        if m == '自动签到':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                gid = (
                    event.get_session_id().split('_')[1]
                    if len(event.get_session_id().split('_')) == 3
                    else 'on'
                )
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, str(gid), 'StatusB')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '推送':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                gid = (
                    event.get_session_id().split('_')[1]
                    if len(event.get_session_id().split('_')) == 3
                    else 'on'
                )
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, str(gid), 'StatusA')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '自动米游币':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                gid = (
                    event.get_session_id().split('_')[1]
                    if len(event.get_session_id().split('_')) == 3
                    else 'on'
                )
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, str(gid), 'StatusC')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '简洁签到报告':
            try:
                if qid in superusers:
                    _ = await config_check('SignReportSimple', 'OPEN')
                    await matcher.finish('成功!', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置简洁签到报告失败')
        elif m == '米游币推送':
            try:
                if qid in superusers:
                    _ = await config_check('MhyBBSCoinReport', 'OPEN')
                    await matcher.finish(
                        '米游币推送已开启！\n该选项不会影响到实际米游币获取，仅开启私聊推送！\n*【管理员命令全局生效】',
                        at_sender=True,
                    )
                else:
                    return
            except ActionFailed as e:
                await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置米游币推送失败')
    except ActionFailed as e:
        await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
        logger.exception('发送开启自动签到信息失败')
    except Exception as e:
        if isinstance(e, FinishedException):
            raise
        await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
        logger.exception('开启自动签到失败')


# 关闭 自动签到 和 推送树脂提醒 功能
@close_switch.handle()
async def close_switch_func(
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg(),
    at: ImageAndAt = Depends(),
):
    try:
        message = args.extract_plain_text().strip().replace(' ', '')
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))

        qid = int(event.sender.user_id)
        at = at.get_first_at()

        if m == '自动签到':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, 'off', 'StatusB')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '推送':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, 'off', 'StatusA')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '自动米游币':
            try:
                if at and qid in superusers:
                    qid = at
                elif at and at != qid:
                    await matcher.finish('你没有权限。', at_sender=True)
                    return
                else:
                    pass
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), qid, 'off', 'StatusC')
                await matcher.finish(im, at_sender=True)
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('未绑定uid信息！', at_sender=True)
        elif m == '简洁签到报告':
            try:
                if qid in superusers:
                    _ = await config_check('SignReportSimple', 'CLOSED')
                    await matcher.finish('成功!', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置简洁签到报告失败')
        elif m == '米游币推送':
            try:
                if qid in superusers:
                    _ = await config_check('MhyBBSCoinReport', 'CLOSED')
                    await matcher.finish(
                        '米游币推送已关闭！\n该选项不会影响到实际米游币获取，仅关闭私聊推送！\n*【管理员命令全局生效】',
                        at_sender=True,
                    )
                else:
                    return
            except ActionFailed as e:
                await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                if isinstance(e, FinishedException):
                    raise
                await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置米游币推送失败')
    except ActionFailed as e:
        await matcher.finish('机器人发送消息失败：{}'.format(e.info['wording']))
        logger.exception('发送开启自动签到信息失败')
    except Exception as e:
        if isinstance(e, FinishedException):
            raise
        await matcher.finish('发生错误 {},请检查后台输出。'.format(e))
        logger.exception('关闭自动签到失败')
