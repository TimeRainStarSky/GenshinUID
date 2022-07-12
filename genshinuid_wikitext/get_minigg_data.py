async def get_audio_info(name: str, audioid: str, language: str = 'cn') -> str:
    """
        :说明:
          访问miniggAPI获得原神角色音频信息。
        :参数:
          * ``name: str``: 原神角色名称。
          * ``audioid: str``: 语音id。
          * ``language: str``: 默认为cn。
        :返回:
          * ``刷新完成提示语: str``: 包含刷新成功的角色列表。
    """
    url = 'https://genshin.minigg.cn/'
    async with AsyncClient() as client:
        req = await client.get(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/95.0.4638.69 Safari/537.36',
                'Referer'   : 'https://genshin.minigg.cn/index.html'},
            params={'characters': name, 'audioid': audioid, 'language': language}
        )
    return req.text


async def get_weapon_info(name, level=None):
    if level:
        params = {'query': name, 'stats': level}
    else:
        params = {'query': name}
    async with AsyncClient() as client:
        req = await client.get(
            url='https://info.minigg.cn/weapons',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/95.0.4638.69 Safari/537.36'},
            params=params
        )
    data = json.loads(req.text)
    return data


async def get_misc_info(mode, name):
    url = 'https://info.minigg.cn/{}'.format(mode)
    async with AsyncClient() as client:
        req = await client.get(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/97.0.4692.71 Safari/537.36'},
            params={'query': name}
        )
    data = json.loads(req.text)
    return data


async def get_char_info(name, mode='char', level=None):
    url2 = None
    url3 = None
    data2 = None
    baseurl = 'https://info.minigg.cn/characters?query='
    if mode == 'talents':
        url = 'https://info.minigg.cn/talents?query=' + name
    elif mode == 'constellations':
        url = 'https://info.minigg.cn/constellations?query=' + name
    elif mode == 'costs':
        url = baseurl + name + '&costs=1'
        url2 = 'https://info.minigg.cn/talents?query=' + name + '&costs=1'
        url3 = 'https://info.minigg.cn/talents?query=' + name + '&matchCategories=true'
    elif level:
        url = baseurl + name + '&stats=' + level
    else:
        url = baseurl + name

    if url2:
        async with AsyncClient() as client:
            req = await client.get(
                url=url2,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/95.0.4638.69 Safari/537.36',
                    'Referer'   : 'https://genshin.minigg.cn/index.html'})
            data2 = json.loads(req.text)
            if 'errcode' in data2:
                async with AsyncClient() as client_:
                    req = await client_.get(
                        url=url3,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                          'like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                            'Referer'   : 'https://genshin.minigg.cn/index.html'})
                    data2 = json.loads(req.text)

    async with AsyncClient() as client:
        req = await client.get(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/95.0.4638.69 Safari/537.36',
                'Referer'   : 'https://genshin.minigg.cn/index.html'})
        try:
            data = json.loads(req.text)
            if 'errcode' in data:
                async with AsyncClient() as client_:
                    req = await client_.get(
                        url=url + '&matchCategories=true',
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                          'like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                            'Referer'   : 'https://genshin.minigg.cn/index.html'})
                    data = json.loads(req.text)
        except:
            data = None
    return data if data2 is None else [data, data2]