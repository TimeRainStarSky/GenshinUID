from .gsuid_db_pool import *  # noqa: F401,F403


async def connect_db(userid, uid=None, mys=None):
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
    VALUES (?, ?,?)',
        (userid, uid, mys),
    )

    if uid:
        c.execute('UPDATE UIDDATA SET UID = ? WHERE USERID=?', (uid, userid))
    if mys:
        c.execute('UPDATE UIDDATA SET MYSID = ? WHERE USERID=?', (mys, userid))

    conn.commit()
    conn.close()


async def select_db(userid, mode='auto'):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    cursor = c.execute('SELECT *  FROM UIDDATA WHERE USERID = ?', (userid,))
    for row in cursor:
        if mode == 'auto':
            if row[0]:
                if row[2]:
                    return [row[2], 3]
                elif row[1]:
                    return [row[1], 2]
                else:
                    return None
            else:
                return None
        elif mode == 'uid':
            return [row[1], 2]
        elif mode == 'mys':
            return [row[2], 3]


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
        c.execute('UPDATE NewCookiesTable SET Cookies = ? WHERE UID=?', (cookies, uid))

    conn.commit()
    conn.close()


def error_db(ck, err):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    if err == 'error':
        c.execute('UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?', ('error', ck))
    elif err == 'limit30':
        c.execute(
            'UPDATE NewCookiesTable SET Extra = ? WHERE Cookies=?', ('limit30', ck)
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
        'UPDATE NewCookiesTable SET Stoken = ? WHERE UID=?', (s_cookies, int(uid))
    )
    conn.commit()
    conn.close()


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


def cache_db(uid, mode=1, mys=None):
    conn = gsuid_pool.connect()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS CookiesCache
        (UID TEXT PRIMARY KEY,
        MYSID         TEXT,
        Cookies       TEXT);"""
    )

    if mode == 1:
        if mys:
            cursor = c.execute('SELECT *  FROM CookiesCache WHERE MYSID = ?', (mys,))
        else:
            cursor = c.execute('SELECT *  FROM CookiesCache WHERE UID = ?', (uid,))
    else:
        cursor = c.execute('SELECT *  FROM CookiesCache WHERE MYSID = ?', (uid,))
    c_data = cursor.fetchall()

    if len(c_data) == 0:
        if mode == 2:
            conn.create_function('REGEXP', 2, regex_func)
            cursor = c.execute(
                'SELECT *  FROM NewCookiesTable WHERE REGEXP(Cookies, ?)', (uid,)
            )
            d_data = cursor.fetchall()

        else:
            cursor = c.execute('SELECT *  FROM NewCookiesTable WHERE UID = ?', (uid,))
            d_data = cursor.fetchall()

        if len(d_data) != 0:
            if d_data[0][7] != 'error':
                use = d_data[0][1]
                if mode == 1:
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)',
                        (use, uid),
                    )
                elif mode == 2:
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
                    if mode == 1:
                        c.execute(
                            'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                                VALUES (?, ?)',
                            (e_data[0][1], uid),
                        )
                    elif mode == 2:
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
                if mode == 1:
                    c.execute(
                        'INSERT OR IGNORE INTO CookiesCache (Cookies,UID) \
                            VALUES (?, ?)',
                        (e_data[0][1], uid),
                    )
                elif mode == 2:
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
                c.execute('UPDATE CookiesCache SET UID = ? WHERE MYSID=?', (uid, mys))
            except:
                c.execute('UPDATE CookiesCache SET MYSID = ? WHERE UID=?', (mys, uid))

    conn.commit()
    conn.close()
    return use


def regex_func(value, patter):
    c_pattern = re.compile(r'account_id={}'.format(patter))
    return c_pattern.search(value) is not None
