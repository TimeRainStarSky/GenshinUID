from typing import List, Tuple, Optional

from ..db_operation.db_operation import cache_db, error_db
from ..mhy_api.get_mhy_data import (
    get_info,
    get_mihoyo_bbs_info,
    get_spiral_abyss_info,
)


class GetCookies:
    def __init__(self) -> None:
        self.useable_cookies: Optional[str] = None
        self.uid: Optional[str] = None
        self.mode: Optional[int] = None
        self.raw_abyss_data: Optional[dict] = None
        self.raw_data: Optional[dict] = None
        self.nickname: Optional[int] = None
        self.schedule_type: Optional[str] = None

    async def get_useable_cookies(
        self, uid: str, mode: int = 2, schedule_type: str = '1'
    ):
        self.uid = uid
        self.schedule_type = schedule_type
        while True:
            self.useable_cookies = cache_db(uid, mode - 1)
            if self.useable_cookies == '':
                return '绑定记录不存在。'
            elif self.useable_cookies == '没有可以使用的Cookies！':
                return '没有可以使用的Cookies！'
            if mode == 3:
                await self.get_mihoyo_bbs_data()
            else:
                await self.get_uid_data()

            msg = await self.check_cookies_useable()
            if isinstance(msg, str):
                return msg
            elif isinstance(msg, bool):
                if msg:
                    return True

    async def get_mihoyo_bbs_data(self):
        mys_data = await get_mihoyo_bbs_info(self.uid, self.useable_cookies)
        for i in mys_data['data']['list']:
            if i['game_id'] != 2:
                mys_data['data']['list'].remove(i)
        self.uid = mys_data['data']['list'][0]['game_role_id']
        self.nickname = mys_data['data']['list'][0]['nickname']
        self.raw_data = await get_info(self.uid, self.useable_cookies)
        self.raw_abyss_data = await get_spiral_abyss_info(
            self.uid, self.useable_cookies, self.schedule_type
        )

    async def get_uid_data(self):
        self.raw_abyss_data = await get_spiral_abyss_info(
            self.uid, self.useable_cookies, self.schedule_type
        )
        self.raw_data = await get_info(self.uid, self.useable_cookies)

    async def check_cookies_useable(self):
        if self.raw_data:
            if self.raw_data['retcode'] != 0:
                if self.raw_data['retcode'] == 10001:
                    error_db(self.useable_cookies, 'error')
                    return False
                elif self.raw_data['retcode'] == 10101:
                    error_db(self.useable_cookies, 'limit30')
                    return False
                elif self.raw_data['retcode'] == 10102:
                    return '当前查询id已经设置了隐私，无法查询！'
                else:
                    return (
                        'Api报错，返回内容为：\r\n'
                        + str(self.raw_data)
                        + '\r\n出现这种情况可能的UID输入错误 or 不存在'
                    )
            else:
                return True
        else:
            return '没有可以使用的Cookies！'
