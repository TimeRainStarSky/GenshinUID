from ..all_import import *
from .add_ck import add_ck
from .link_id import link_uid_to_qq, link_mihoyo_id_to_qq

add_cookie = on_command('添加', permission=PRIVATE_FRIEND)
link_mys = on_command('绑定mys')
link_uid = on_command('绑定uid')

CK_HINT = '''获取Cookies教程：https://github.com/KimigaiiWuyi/GenshinUID/issues/255
绑定uid：uid为原神uid，如绑定uid12345
绑定mys：mys为米游社通行证，如绑定mys12345'''


@add_cookie.handle()
@handle_exception('Cookie', '校验失败！请输入正确的Cookies！')
async def send_add_ck_msg(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    mes = args.extract_plain_text().strip().replace(' ', '')
    im = await add_ck(mes, int(event.sender.user_id))
    await matcher.finish(im)


# 群聊内 绑定uid 的命令，会绑定至当前qq号上
@link_uid.handle()
@handle_exception('绑定uid', '绑定uid异常')
async def send_link_uid_msg(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    await link_uid_to_qq(event.sender.user_id, args.extract_plain_text())
    await matcher.finish('绑定uid成功！', at_sender=True)


# 群聊内 绑定米游社通行证 的命令，会绑定至当前qq号上，和绑定uid不冲突，两者可以同时绑定
@link_mys.handle()
@handle_exception('绑定米游社通行证', '绑定米游社通行证异常')
async def send_link_mysid_msg(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    await link_mihoyo_id_to_qq(event.sender.user_id, args.extract_plain_text())
    await matcher.finish('绑定米游社id成功！', at_sender=True)
