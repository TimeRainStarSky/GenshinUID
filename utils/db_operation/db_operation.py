import re
from typing import List, Union, Optional

from .gsuid_db_pool import *  # noqa: F401,F403


async def bind_db(userid, uid=None, mys=None):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS UIDDATA
        (USERID INT PRIMARY KEY     NOT NULL,
        UID         TEXT,
        MYSID       TEXT);"""
    )

    c.execute(
        'INSERT OR IGNORE INTO UIDDATA (USERID,UID,MYSID) \
    VALUES (?, ?, ?)',
        (userid, uid, mys),
    )

    old_data = c.execute('SELECT * FROM UIDDATA WHERE USERID = ?', (userid,))
    old_data = old_data.fetchall()

    im = ''
    if uid:
        if old_data[0][1] is not None:
            if uid in old_data[0][1]:
                return '当前uid已经绑定过了!请勿重复绑定~'
            else:
                new_uid = f'{old_data[0][1]}_{uid}'
        else:
            new_uid = uid
        c.execute(
            'UPDATE UIDDATA SET UID = ? WHERE USERID=?', (new_uid, userid)
        )
        im = f'UID绑定成功!\n当前绑定uid为{new_uid}'
    if mys:
        if old_data[0][2] is not None:
            new_mys = f'{old_data[0][2]}_{mys}'
        else:
            new_mys = mys
        c.execute(
            'UPDATE UIDDATA SET MYSID = ? WHERE USERID=?', (new_mys, userid)
        )
        im = f'米游社通行证绑定成功!\n当前绑定mysid为{new_mys}'

    conn.commit()
    conn.close()
    return im


async def select_db(userid, mode='auto') -> Union[List, None]:
    """
    :说明:
      选择绑定uid/mys库
    :参数:
      * userid (str): QQ号。
      * mode (str): 模式如下
        * auto(默认): 自动选择(优先mys)
        * uid: 选择uid库
        * mys: 选择mys库
        * list: 返回uid列表
    :返回:
      * data (list): 返回获取值
      mode为list时返回uid列表
      其他情况下data[0]为需要的uid/mysid
      data[1]表示data[0]是`uid` or `mysid`
    """
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM UIDDATA WHERE USERID = ?', (userid,))
    c_data = cursor.fetchall()
    for row in c_data:
        uid = None
        mysid = None
        uid_list = None
        if row[1]:
            uid_list = row[1].split('_')
            uid = uid_list[0]
        if row[2]:
            mysid_list = row[2].split('_')
            mysid = mysid_list[0]

        if mode == 'auto':
            if mysid:
                return [mysid, 'mys']
            elif uid:
                return [uid, 'uid']
            else:
                return None
        elif mode == 'uid':
            return [uid, 'uid']
        elif mode == 'mys':
            return [mysid, 'mys']
        elif mode == 'list':
            return uid_list


async def switch_db(userid: str, uid: Optional[str] = None):
    """
    :说明:
      切换绑定的UID列表,绑定一个UID的情况下返回无法切换
      切换前 -> 12_13_14
      切换后 -> 13_14_12
    :参数:
      * userid (str): QQ号。
    :返回:
      * im (str): 回调信息。
    """
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM UIDDATA WHERE USERID = ?', (userid,))
    c_data = cursor.fetchall()
    for row in c_data:
        if len(row[1].split('_')) <= 1:
            return f'你只绑定了一个UID,无法进行切换~\n当前绑定UID{row[1]}!'
        else:
            uid_list = row[1].split('_')
            # 根据传入uid切换
            if uid is None:
                uid = uid_list[1]

            if uid in uid_list:
                uid_list.remove(uid)
                uid_list.insert(0, uid)
            else:
                return f'当前UID{uid}不在绑定列表中,无法切换~'
            new_uid = '_'.join(uid_list)
            new_uid_str = '\n'.join(uid_list)
            c.execute(
                'UPDATE UIDDATA SET UID = ? WHERE USERID=?', (new_uid, userid)
            )
            conn.commit()
            conn.close()
            return f'UID切换成功!\n当前绑定uid列表为\n{new_uid_str}'


async def delete_db(userid: str, uid: Optional[str] = None):
    """
    :说明:
      删除当前绑定的UID信息
      删除前 -> 12_13_14
      删除后 -> 13_14
    :参数:
      * userid (str): QQ号。
    :返回:
      * im (str): 回调信息。
    """
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM UIDDATA WHERE USERID = ?', (userid,))
    c_data = cursor.fetchall()
    for row in c_data:
        # 首个UID被切换到最后
        uid_list = row[1].split('_')
        if uid:
            if uid in uid_list:
                delete_uid = uid
                uid_list.remove(uid)
            else:
                return f'你没有绑定{uid}这个uid,无法进行删除~'
        else:
            delete_uid = uid_list[0]
            uid_list.pop(0)
        new_uid_list = '_'.join(uid_list)
        new_uid_str = '\n'.join(uid_list)
        c.execute(
            'UPDATE UIDDATA SET UID = ? WHERE USERID=?', (new_uid_list, userid)
        )
        conn.commit()
        conn.close()
        return f'UID{delete_uid}已被删除!\n当前绑定uid列表为\n{new_uid_str}'


async def cookies_db(uid, cookies, qid):
    conn = gsuid_pool.connect()
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS NewCookiesTable
    (UID INT PRIMARY KEY     NOT NULL,
    Cookies         TEXT,
    QID         INT,
    StatusA     TEXT,
    StatusB     TEXT,
    StatusC     TEXT,
    NUM         INT,
    Extra       TEXT);"""
    )

    cursor = c.execute('SELECT * from NewCookiesTable WHERE UID = ?', (uid,))
    c_data = cursor.fetchall()
    if len(c_data) == 0:
        c.execute(
            'INSERT OR IGNORE INTO NewCookiesTable (Cookies,UID,StatusA,StatusB,StatusC,NUM,QID) \
            VALUES (?, ?, ?, ?, ?, ?, ?)',
            (cookies, uid, 'off', 'off', 'off', 140, qid),
        )
    else:
        c.execute(
            'UPDATE NewCookiesTable SET Cookies = ? WHERE UID=?',
            (cookies, uid),
        )

    conn.commit()
    conn.close()


def error_db(ck, err):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    if err == 'error':
        c.execute(
            'UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?',
            ('error', ck),
        )
    elif err == 'limit30':
        c.execute(
            'UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?',
            ('limit30', ck),
        )
    conn.commit()
    conn.close()


async def owner_cookies(uid):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM NewCookiesTable WHERE UID = ?', (uid,))
    c_data = cursor.fetchall()
    cookies = c_data[0][1]
    return cookies


async def get_stoken(uid):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM NewCookiesTable WHERE UID = ?', (uid,))
    c_data = cursor.fetchall()
    stoken = c_data[0][8]
    return stoken


async def stoken_db(s_cookies, uid):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    columns = [i[1] for i in c.execute('PRAGMA table_info(NewCookiesTable)')]
    if 'Stoken' not in columns:
        c.execute('ALTER TABLE NewCookiesTable ADD COLUMN Stoken TEXT')
    c.execute(
        'UPDATE NewCookiesTable SET Stoken = ? WHERE UID=?',
        (s_cookies, int(uid)),
    )
    conn.commit()
    conn.close()


async def open_push(uid, qid, status, mode):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT * from NewCookiesTable WHERE UID = ?', (uid,))
    c_data = cursor.fetchall()
    if len(c_data) != 0:
        try:
            c.execute(
                'UPDATE NewCookiesTable SET {s} = ?,QID = ? WHERE UID=?'.format(
                    s=mode
                ),
                (status, qid, uid),
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    else:
        return False


async def config_check(func, mode='CHECK'):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS Config
            (Name TEXT PRIMARY KEY     NOT NULL,
            Status      TEXT,
            GroupList   TEXT,
            Extra       TEXT);"""
    )
    c.execute(
        'INSERT OR IGNORE INTO Config (Name,Status) \
                            VALUES (?, ?)',
        (func, 'on'),
    )
    if mode == 'CHECK':
        cursor = c.execute('SELECT * from Config WHERE Name = ?', (func,))
        c_data = cursor.fetchall()
        conn.close()
        if c_data[0][1] != 'off':
            return True
        else:
            return False
    elif mode == 'OPEN':
        c.execute('UPDATE Config SET Status = ? WHERE Name=?', ('on', func))
        conn.commit()
        conn.close()
        return True
    elif mode == 'CLOSED':
        c.execute('UPDATE Config SET Status = ? WHERE Name=?', ('off', func))
        conn.commit()
        conn.close()
        return True


async def get_all_signin_list():
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute(
        'SELECT *  FROM NewCookiesTable WHERE StatusB != ?', ('off',)
    )
    c_data = cursor.fetchall()
    return c_data


def cache_db(uid, mode: str = 'uid', mys=None):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS CookiesCache
        (UID TEXT PRIMARY KEY,
        MYSID         TEXT,
        Cookies       TEXT);"""
    )

    if mode == 'uid':
        if mys:
            cursor = c.execute(
                'SELECT *  FROM CookiesCache WHERE MYSID = ?', (mys,)
            )
        else:
            cursor = c.execute(
                'SELECT *  FROM CookiesCache WHERE UID = ?', (uid,)
            )
    else:
        cursor = c.execute(
            'SELECT *  FROM CookiesCache WHERE MYSID = ?', (uid,)
        )
    c_data = cursor.fetchall()

    if len(c_data) == 0:
        if mode == 'mys':
            conn.create_function('REGEXP', 2, regex_func)
            cursor = c.execute(
                'SELECT *  FROM NewCookiesTable WHERE REGEXP(Cookies, ?)',
                (uid,),
            )
            d_data = cursor.fetchall()

        else:
            cursor = c.execute(
                'SELECT *  FROM NewCookiesTable WHERE UID = ?', (uid,)
            )
            d_data = cursor.fetchall()

        if len(d_data) != 0:
            if d_data[0][7] != 'error':
                use = d_data[0][1]
                if mode == 'uid':
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)',
                        (use, uid),
                    )
                elif mode == 'mys':
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                            VALUES (?, ?)',
                        (use, uid),
                    )
            else:
                cookies_row = c.execute(
                    'SELECT * FROM NewCookiesTable WHERE Extra IS NULL ORDER BY RANDOM() LIMIT 1'
                )
                e_data = cookies_row.fetchall()
                if len(e_data) != 0:
                    if mode == 'uid':
                        c.execute(
                            'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                                VALUES (?, ?)',
                            (e_data[0][1], uid),
                        )
                    elif mode == 'mys':
                        c.execute(
                            'INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                                VALUES (?, ?)',
                            (e_data[0][1], uid),
                        )
                    use = e_data[0][1]
                else:
                    return '没有可以使用的Cookies！'
        else:
            cookies_row = c.execute(
                'SELECT * FROM NewCookiesTable WHERE Extra IS NULL ORDER BY RANDOM() LIMIT 1'
            )
            e_data = cookies_row.fetchall()
            if len(e_data) != 0:
                if mode == 'uid':
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)',
                        (e_data[0][1], uid),
                    )
                elif mode == 'mys':
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,MYSID) \
                            VALUES (?, ?)',
                        (e_data[0][1], uid),
                    )
                use = e_data[0][1]
            else:
                return '没有可以使用的Cookies！'
    else:
        use = c_data[0][2]
        if mys:
            try:
                c.execute(
                    'UPDATE CookiesCache SET UID = ? WHERE MYSID=?', (uid, mys)
                )
            except:
                c.execute(
                    'UPDATE CookiesCache SET MYSID = ? WHERE UID=?', (mys, uid)
                )

    conn.commit()
    conn.close()
    return use


def regex_func(value, patter):
    c_pattern = re.compile(r'account_id={}'.format(patter))
    return c_pattern.search(value) is not None
