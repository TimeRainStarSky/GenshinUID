get_guide_pic = on_regex('([\u4e00-\u9fa5]+)(推荐|攻略)', priority=priority)
get_bluekun_pic = on_command('参考面板', priority=priority)

@get_guide_pic.handle()
@handle_exception('建议')
async def send_guide_pic(matcher: Matcher, args: Tuple[Any, ...] = RegexGroup()):
    message = args[0].strip().replace(' ', '')
    with open(os.path.join(INDEX_PATH, 'char_alias.json'),
              'r',
              encoding='utf8') as fp:
        char_data = json.load(fp)
    name = message
    for i in char_data:
        if message in i:
            name = i
        else:
            for k in char_data[i]:
                if message in k:
                    name = i
    # name = str(event.get_message()).strip().replace(' ', '')[:-2]
    url = 'https://img.genshin.minigg.cn/guide/{}.jpg'.format(name)
    if httpx.head(url).status_code == 200:
        await matcher.finish(MessageSegment.image(url))
    else:
        return