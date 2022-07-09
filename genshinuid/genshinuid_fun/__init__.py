import base64
import sqlite3
from typing import Any, Union

from nonebot import Bot, get_bot, get_driver, on_command, on_regex, require
from nonebot.adapters.onebot.v11 import (ActionFailed, GroupMessageEvent, Message, MessageEvent, MessageSegment,
                                         PRIVATE_FRIEND, PrivateMessageEvent)
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, RegexGroup
from nonebot.permission import SUPERUSER

from ..util.handle_exception import handle_exception

get_lots = on_command('御神签', priority=priority)

@get_lots.handle()
@handle_exception('御神签')
async def send_lots(event: MessageEvent,
                    matcher: Matcher,
                    args: Message = CommandArg()):
    if args:
        await matcher.finish()
        return
    qid = int(event.sender.user_id)
    raw_data = await get_a_lots(qid)
    im = base64.b64decode(raw_data).decode('utf-8')
    await matcher.finish(im)

async def get_a_lots(qid):
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS UseridDict
            (QID INT PRIMARY KEY     NOT NULL,
            lots        TEXT,
            cache       TEXT,
            permission  TEXT,
            Status      TEXT,
            Subscribe   TEXT,
            Extra       TEXT);""")
    cursor = c.execute('SELECT * from UseridDict WHERE QID = ?', (qid,))
    c_data = cursor.fetchall()
    with open('lots.txt', 'r') as f:
        raw_data = f.read()
        raw_data = raw_data.replace(' ', '').split('-')

    if len(c_data) == 0:
        num = random.randint(1, len(raw_data) - 1)
        data = raw_data[num]
        c.execute('INSERT OR IGNORE INTO UseridDict (QID,lots) \
                            VALUES (?, ?)', (qid, str(num)))
    else:
        if c_data[0][1] is None:
            num = random.randint(0, len(raw_data) - 1)
            data = raw_data[num]
            c.execute('UPDATE UseridDict SET lots = ? WHERE QID=?', (str(num), qid))
        else:
            num = int(c_data[0][1])
            data = raw_data[num]
    conn.commit()
    conn.close()
    return data