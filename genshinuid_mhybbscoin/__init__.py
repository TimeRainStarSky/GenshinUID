from ..all_import import *  # noqa: F403,F401
from .daily_mihoyo_bbs_coin import mihoyo_coin, daily_mihoyo_bbs_coin

bbscoin_scheduler = require('nonebot_plugin_apscheduler').scheduler

get_mihoyo_coin = on_command('开始获取米游币', priority=priority)
all_bbscoin_recheck = on_command(
    '全部重获取', permission=SUPERUSER, priority=priority
)


# 获取米游币
@get_mihoyo_coin.handle()
@handle_exception('获取米游币')
async def send_mihoyo_coin(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    if args:
        return
    await matcher.send('开始操作……', at_sender=True)
    qid = int(event.sender.user_id)
    im = await mihoyo_coin(qid)
    await matcher.finish(im, at_sender=True)


@all_bbscoin_recheck.handle()
async def bbs_recheck(args: Message = CommandArg()):
    if args:
        return
    await all_bbscoin_recheck.send('已开始执行')
    await daily_mihoyo_bbs_coin()


# 每日一点十六分进行米游币获取
@bbscoin_scheduler.scheduled_job('cron', hour='1', minute='16')
async def sign_at_night():
    await daily_mihoyo_bbs_coin()


async def send_daily_mihoyo_bbs_sign():
    bot = get_bot()
    im, im_private = await daily_mihoyo_bbs_coin()
    if im_private:
        for user_id in im_private:
            await bot.send_private_msg(
                user_id=user_id, message=im_private[user_id]
            )
            await asyncio.sleep(5 + random.randint(1, 3))
    for qid in superusers:
        await bot.call_api(api='send_private_msg', user_id=qid, message=im)
        await asyncio.sleep(5 + random.randint(1, 3))
    logger.info('米游币获取已结束。')
