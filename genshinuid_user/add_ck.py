import re
from ..utils.db_operation.db_cache_and_check import refresh_ck
from ..utils.db_operation.db_operation import (
    cookies_db,
    stoken_db,
    select_db,
    owner_cookies,
)
from ..utils.mhy_api.get_mhy_data import get_mihoyo_bbs_info, get_stoken_by_login_ticket


async def add_ck(mes, qid):
    if 'stoken' in mes:
        login_ticket = (
            re.search(r'login_ticket=([0-9a-zA-Z]+)', mes).group(0).split('=')[1]
        )
        uid = await select_db(qid, 'uid')
        ck = await owner_cookies(uid[0])
        mys_id = re.search(r'account_id=(\d*)', ck).group(0).split('=')[1]
        raw_data = await get_stoken_by_login_ticket(login_ticket, mys_id)
        stoken = raw_data['data']['list'][0]['token']
        s_cookies = 'stuid={};stoken={}'.format(mys_id, stoken)
        await stoken_db(s_cookies, uid[0])
        return '添加Stoken成功！'
    else:
        aid = re.search(r'account_id=(\d*)', mes)
        mysid_data = aid.group(0).split('=')
        mysid = mysid_data[1]
        cookie = ';'.join(
            filter(
                lambda x: x.split('=')[0] in ['cookie_token', 'account_id'],
                [i.strip() for i in mes.split(';')],
            )
        )
        mys_data = await get_mihoyo_bbs_info(mysid, cookie)
        for i in mys_data['data']['list']:
            if i['game_id'] != 2:
                mys_data['data']['list'].remove(i)
        uid = mys_data['data']['list'][0]['game_role_id']
        await refresh_ck(uid, mysid)
        await cookies_db(uid, cookie, qid)
        return (
            f'添加Cookies成功！\nCookies属于个人重要信息，如果你是在不知情的情况下添加，请马上修改米游社账户密码，保护个人隐私！\n————\n'
            f'如果需要【gs开启自动签到】和【gs开启推送】还需要在【群聊中】使用命令“绑定uid”绑定你的uid。\n例如：绑定uid123456789。'
        )
