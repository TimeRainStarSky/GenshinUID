from pathlib import Path
from httpx import AsyncClient
from json import loads
from datetime import datetime
from time import strptime, strftime, localtime

from nonebot import Bot, get_bot, get_driver, on_command, on_regex, require
from nonebot.adapters.onebot.v11 import (ActionFailed, GroupMessageEvent, Message, MessageEvent, MessageSegment,
                                         PRIVATE_FRIEND, PrivateMessageEvent)
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, RegexGroup
from nonebot.permission import SUPERUSER

from ..util.handle_exception import handle_exception
from ..util.genshin_fonts import genshin_font_origin

TEXT_PATH = Path(__file__).parents[0] / 'texture2d'

get_event = on_command('活动列表', priority=priority)

@get_event.handle()
@handle_exception('活动')
async def send_events(matcher: Matcher, args: Message = CommandArg()):
    if args:
        return
    img_path = Path(__file__).parents[0] / 'event.png'
    while True:
        if img_path.exists():
            with open(img_path, 'rb') as f:
                im = MessageSegment.image(f.read())
            break
        else:
            await draw_event_pic()
    await matcher.finish(im)


async def get_genshin_events(mode: str = 'List') -> dict:
    """
        :说明:
            接受mode: str = 'List'或'Calendar'或'Content'。
            'List'模式为米游社列表, 包含最基本的信息。
            'Content'模式为游戏内活动公告, 包含html页面, 时间信息来源。
            'Calendar'模式为米游社日历, 一般不用。
        :参数:
        * ``mode: str``: 'List'或'Calendar'或'Content'。
        :返回:
        * ``data: dict``: json.loads。
    """
    if mode == 'Calendar':
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        base_url = 'https://api-takumi.mihoyo.com/event/bbs_activity_calendar/getActList'
        params = {
            'time'    : now_time,
            'game_biz': 'ys_cn',
            'page'    : 1,
            'tag_id'  : 0
        }
    else:
        base_url = 'https://hk4e-api.mihoyo.com/common/hk4e_cn/announcement/api/getAnn{}'.format(mode)
        params = {
            'game'     : 'hk4e',
            'game_biz' : 'hk4e_cn',
            'lang'     : 'zh-cn',
            'bundle_id': 'hk4e_cn',
            'platform' : 'pc',
            'region'   : 'cn_gf01',
            'level'    : 55,
            'uid'      : 100000000
        }

    async with AsyncClient() as client:
        req = await client.get(
            url=base_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/95.0.4638.69 Safari/537.36'},
            params=params
        )
    data = json.loads(req.text)
    return data


async def get_month_and_time(time_data: str) -> List:
    """
        :说明:
            接收时间字符串`2022/02/09 18:59:59`
            转换为`['02/09', '18:59PM']`
        :参数:
        * ``time_data: str``: 时间字符串。
        :返回:
        * ``[month, time]: list``: ['02/09', '18:59PM']。
    """
    time_data = time_data.split(' ')
    time_data[0] = time_data[0].replace('-', '/')
    month = time_data[0].split('/', 1)[1]
    time = ':'.join(time_data[1].split(':')[:-1])
    if int(time.split(':')[0]) <= 12:
        time = time + 'AM'
    else:
        time = time + 'PM'
    return [month, time]


async def draw_event_pic() -> None:
    """
        :说明:
            绘制原神活动列表图片，存放至同级目录``event.png``。
    """
    raw_data = await get_genshin_events('List')
    raw_time_data = await get_genshin_events('Content')

    data = raw_data['data']['list'][1]['list']

    event_data = {'gacha_event': [], 'normal_event': [], 'other_event': []}
    for k in data:
        for i in raw_time_data['data']['list']:
            if k['title'] in i['title']:
                content_bs = BeautifulSoup(i['content'], 'lxml')
                for index, value in enumerate(content_bs.find_all('p')):
                    if value.text == '〓任务开放时间〓':
                        time_data = content_bs.find_all('p')[index + 1].text
                        if '<t class=' in time_data:
                            time_data = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', time_data)[0]
                        month_start, time_start = await get_month_and_time(time_data)
                        k['start_time'] = [month_start, time_start]
                        k['end_time'] = ['更新后', '永久开放']
                    elif value.text == '〓活动时间〓':
                        time_data = content_bs.find_all('p')[index + 1].text
                        if '<t class=' in time_data:
                            time_datas = []
                            for s in time_data.split(' ~ '):
                                if '<t class=' in s:
                                    time_datas.append(findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', s)[0])
                                else:
                                    time_datas.append(s)
                            if ' ' in time_datas[0]:
                                month_start, time_start = await get_month_and_time(time_datas[0])
                            else:
                                month_start, time_start = '版本更新后', '更新后'

                            if ' ' in time_datas[1]:
                                month_end, time_end = await get_month_and_time(time_datas[1])
                            else:
                                month_end, time_end = '永久开放', '更新后'
                            k['start_time'] = [month_start, time_start]
                            k['end_time'] = [month_end, time_end]
                        elif '活动内容' in time_data:
                            for n in range(2, 10):
                                time_data = content_bs.find_all('p')[index + n].text
                                if '版本更新后' in time_data:
                                    time_data_end = content_bs.find_all('p')[index + n + 1].text
                                    if '<t class=' in time_data_end:
                                        time_data_end = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', time_data_end)[0]
                                        month_end, time_end = await get_month_and_time(time_data_end)
                                        k['start_time'] = [time_data[:5], '更新后']
                                        k['end_time'] = [month_end, time_end]
                                    else:
                                        k['start_time'] = [time_data, '维护后']
                                        k['end_time'] = ['更新后', '永久开放']
                                    break
                                elif '<t class=' in time_data:
                                    time_data = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', time_data)[0]
                                    month_start, time_start = await get_month_and_time(time_data)
                                    k['start_time'] = [month_start, time_start]
                                    time_data_end = content_bs.find_all('p')[index + n + 1].text
                                    if '<t class=' in time_data_end:
                                        time_data_end = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', time_data_end)[0]
                                        month_end, time_end = await get_month_and_time(time_data_end)
                                        k['end_time'] = [month_end, time_end]
                                    else:
                                        k['end_time'] = ['更新后', '永久开放']
                                    break
                        else:
                            month_start, time_start = await get_month_and_time(time_data)
                            k['start_time'] = [month_start, time_start]
                            k['end_time'] = ['更新后', '永久开放']
                    elif value.text == '〓祈愿介绍〓':
                        start_time = content_bs.find_all('tr')[1].td.find_all('p')[0].text
                        if '<t class=' in start_time:
                            start_time = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', start_time)[0]
                        end_time = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>',
                                           content_bs.find_all('tr')[1].td.find_all('p')[2].text)[0]
                        if '<t class=' in end_time:
                            end_time = findall('<[a-zA-Z]+.*?>([\s\S]*?)</[a-zA-Z]*?>', end_time)[0]

                        month_start, time_start = await get_month_and_time(start_time)
                        month_end, time_end = await get_month_and_time(end_time)

                        k['start_time'] = [month_start, time_start]
                        k['end_time'] = [month_end, time_end]

        if '冒险助力礼包' in k['title'] or '纪行' in k['title']:
            continue
        # if '角色试用' in k['title'] or '传说任务' in k['title']:
        #    event_data['other_event'].append(k)
        elif k['tag_label'] == '扭蛋':
            event_data['gacha_event'].append(k)
        elif k['tag_label'] == '活动':
            event_data['normal_event'].append(k)

    base_h = 450 + len(event_data['normal_event']) * (270 + 10) + len(event_data['gacha_event']) * (370 + 10)
    base_img = Image.new(mode='RGBA', size=(950, base_h), color=(255, 253, 248, 255))

    text_color = (60, 59, 64)
    event_color = (250, 93, 93)
    gacha_color = (93, 198, 250)
    font_l = genshin_font_origin(52)
    font_m = genshin_font_origin(34)
    font_s = genshin_font_origin(28)
    
    now_time = datetime.datetime.now().strftime('%Y/%m/%d')
    event_title_path = TEXT_PATH / 'event_title.png'
    event_title = Image.open(event_title_path)
    event_title_draw = ImageDraw.Draw(event_title)
    event_title_draw.text((7, 380), now_time, font = font_l, fill = text_color, anchor='lm')
    base_img.paste(event_title, (0, 0), event_title)

    for index, value in enumerate(event_data['normal_event']):
        event_img = Image.new(mode='RGBA', size=(950, 280))
        img = Image.open(BytesIO(get(value['banner']).content))
        img = img.resize((745, 270), Image.Resampling.LANCZOS)
        event_img.paste(img, (205, 10))
        event_img_draw = ImageDraw.Draw(event_img)

        if isinstance(value['start_time'], str):
            value['start_time'] = await get_month_and_time(value['start_time'])
        if isinstance(value['end_time'], str):
            value['end_time'] = await get_month_and_time(value['end_time'])
        event_img_draw.rectangle([(0, 0), (950, 10)], fill = event_color)
        event_img_draw.polygon([(32, 150), (32, 176), (55,163)], fill = (243, 110, 110))
        event_img_draw.text((8, 83), value['start_time'][0], text_color, font_l, anchor='lm')
        event_img_draw.text((8, 129), value['start_time'][1], text_color, font_s, anchor='lm')
        event_img_draw.text((39, 213), value['end_time'][0], text_color, font_l, anchor='lm')
        event_img_draw.text((39, 256), value['end_time'][1], text_color, font_s, anchor='lm')

        base_img.paste(event_img, (0, 450 + 280 * index), event_img)

    for index, value in enumerate(event_data['gacha_event']):
        event_img = Image.new(mode='RGBA', size=(950, 380))
        img = Image.open(BytesIO(get(value['banner']).content))
        img = img.resize((745, 370), Image.Resampling.LANCZOS)
        event_img.paste(img, (205, 10))
        event_img_draw = ImageDraw.Draw(event_img)

        event_img_draw.rectangle([(0, 0), (950, 10)], fill = gacha_color)
        event_img_draw.rectangle([(8, 45), (58, 75)], fill = gacha_color)
        event_img_draw.text((65, 60), '祈愿', text_color, font_m, anchor='lm')
        event_img_draw.polygon([(32, 250), (32, 276), (55,263)], fill = (243, 110, 110))
        event_img_draw.text((8, 183), value['start_time'][0], text_color, font_l, anchor='lm')
        event_img_draw.text((8, 229), value['start_time'][1], text_color, font_s, anchor='lm')
        event_img_draw.text((39, 313), value['end_time'][0], text_color, font_l, anchor='lm')
        event_img_draw.text((39, 356), value['end_time'][1], text_color, font_s, anchor='lm')
        
        base_img.paste(event_img, (0, 450 + len(event_data['normal_event']) * 280 + 380 * index), event_img)

    base_img = base_img.convert('RGB')
    base_img.save('event.jpg', format='JPEG', subsampling=0, quality=90)
    return