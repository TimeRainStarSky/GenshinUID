from ..all_import import *

add_cookie = on_command('添加', permission=PRIVATE_FRIEND)
link_mys = on_command('绑定mys')
link_uid = on_command('绑定uid')

CK_HINT = '''获取Cookies教程：https://github.com/KimigaiiWuyi/GenshinUID/issues/255
绑定uid：uid为原神uid，如绑定uid12345
绑定mys：mys为米游社通行证，如绑定mys12345'''


@add_cookie.handle()
@handle_exception('Cookie', '校验失败！请输入正确的Cookies！')
async def add_cookie_func(event: MessageEvent,
                          matcher: Matcher,
                          args: Message = CommandArg()):
    mes = args.extract_plain_text().strip().replace(' ', '')
    im = await deal_ck(mes, int(event.sender.user_id))
    await matcher.finish(im)