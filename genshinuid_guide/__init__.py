from ..re_import import * # noqa: F401, F403

get_guide_pic = on_regex('([\u4e00-\u9fa5]+)(推荐|攻略)', priority=priority)
get_bluekun_pic = on_command('参考面板', priority=priority)

@get_guide_pic.handle()
@handle_exception('建议')
async def send_guide_pic(matcher: Matcher, args: Tuple[Any, ...] = RegexGroup()):
    message = args[0].strip().replace(' ', '')
    await alias_to_char_name(message)
    url = 'https://img.genshin.minigg.cn/guide/{}.jpg'.format(name)
    if httpx.head(url).status_code == 200:
        await matcher.finish(MessageSegment.image(url))
    else:
        return


@get_bluekun_pic.handle()
@handle_exception('参考面板')
async def send_bluekun_pic(matcher: Matcher, args: Message = CommandArg()):
    message = args.extract_plain_text().strip().replace(' ', '')
    pic_json = {
        '雷':
            'https://upload-bbs.mihoyo.com/upload/2022/04/04/160367110/1f5e3773874fcf3177b63672b02a88d7_859652593462461477.jpg',
        '火':
            'https://upload-bbs.mihoyo.com/upload/2022/04/04/160367110/c193d7abc4139afccd1ba892d5bb3a99_6658340945648783394.jpg',
        '冰':
            'https://upload-bbs.mihoyo.com/upload/2022/04/04/160367110/afcd1a31744c16f81ad9d8f2d75688a0_4525405643656826681.jpg',
        '风':
            'https://upload-bbs.mihoyo.com/upload/2022/04/04/160367110/689e93122216bfd8d231b8366e42ef46_1275479383799739625.jpg',
        '水':
            'https://upload-bbs.mihoyo.com/upload/2022/05/31/160367110/de5d77307f6997f5e94e2834f9ca86f0_8212017873163996402.png',
        '岩':
            'https://upload-bbs.mihoyo.com/upload/2022/04/04/160367110/d9a7c73f2c2f08ba6f0e960d4e815012_5142810778120366748.jpg'
    }
    await matcher.finish(MessageSegment.image(pic_json[message]))