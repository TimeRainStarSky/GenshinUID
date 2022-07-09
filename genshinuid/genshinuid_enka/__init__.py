from nonebot import Bot, get_bot, get_driver, on_command, on_regex, require
from nonebot.adapters.onebot.v11 import (ActionFailed, GroupMessageEvent, Message, MessageEvent, MessageSegment,
                                         PRIVATE_FRIEND, PrivateMessageEvent)
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, RegexGroup
from nonebot.permission import SUPERUSER

from ..util.handle_exception import handle_exception
from .draw_char_card import *
from .enka_to_data import *

refresh = on_command('强制刷新', priority=priority)
get_charcard_list = on_command('毕业度统计', priority=priority)

refresh_scheduler = require('nonebot_plugin_apscheduler').scheduler

@refresh_scheduler.scheduled_job('cron', hour='4')
async def daily_refresh_charData():
    await refresh_charData()


async def refresh_charData():
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    cursor = c.execute('SELECT UID  FROM UIDDATA WHERE UID IS NOT NULL')
    c_data = cursor.fetchall()
    t = 0
    for row in c_data:
        uid = row[0]
        try:
            im = await enkaToData(uid)
            logger.info(im)
            t += 1
            await asyncio.sleep(18 + random.randint(2, 6))
        except:
            logger.exception(f'{uid}刷新失败！')
            logger.error(f'{uid}刷新失败！本次自动刷新结束！')
            return f'执行失败从{uid}！共刷新{str(t)}个角色！'
    else:
        return f'执行成功！共刷新{str(t)}个角色！'


@refresh.handle()
@handle_exception('面板')
async def send_card_info(matcher: Matcher,
                         event: Union[GroupMessageEvent, PrivateMessageEvent],
                         args: Message = CommandArg()):
    message = args.extract_plain_text().strip().replace(' ', '')
    uid = re.findall(r'\d+', message)  # str
    m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
    qid = int(event.sender.user_id)

    if len(uid) >= 1:
        uid = uid[0]
    else:
        if m == '全部数据':
            if qid in superusers:
                await refresh.send('开始刷新全部数据，这可能需要相当长的一段时间！！')
                im = await refresh_charData()
                await matcher.finish(str(im))
                return
            else:
                return
        else:
            uid = await select_db(qid, mode='uid')
            uid = uid[0]
    im = await enkaToData(uid)
    await matcher.finish(str(im))
    logger.info(f'UID{uid}获取角色数据成功！')


@get_charcard_list.handle()
@handle_exception('毕业度统计')
async def send_charcard_list(bot: Bot,
                             event: Union[GroupMessageEvent, PrivateMessageEvent],
                             matcher: Matcher,
                             args: Message = CommandArg(),
                             custom: ImageAndAt = Depends()):

    message = args.extract_plain_text().strip().replace(' ', '')
    limit = re.findall(r'\d+', message)  # str
    if len(limit) >= 1:
        limit = int(limit[0])
    else:
        limit = 24
    at = custom.get_first_at()
    if at:
        uid = await select_db(at, mode='uid')
        message = message.replace(str(at), '')
    else:
        uid = await select_db(int(event.sender.user_id), mode='uid')
    uid = uid[0]
    im = await draw_cahrcard_list(uid, limit)

    if isinstance(im, bytes):
        await matcher.finish(MessageSegment.image(im))
    else:
        await matcher.finish(str(im))
    logger.info(f'UID{uid}获取角色数据成功！')