add_cookie = on_command('添加', permission=PRIVATE_FRIEND, priority=priority)
link_mys = on_command('绑定mys', priority=priority)
link_uid = on_command('绑定uid', priority=priority)

CK_HINT = '''获取Cookies教程：https://github.com/KimigaiiWuyi/GenshinUID/issues/255
绑定uid：uid为原神uid，如绑定uid12345
绑定mys：mys为米游社通行证，如绑定mys12345'''