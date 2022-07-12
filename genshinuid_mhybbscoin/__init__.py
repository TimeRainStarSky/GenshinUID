scheduler = require('nonebot_plugin_apscheduler').scheduler

get_mihoyo_coin = on_command('开始获取米游币', priority=priority)
all_bbscoin_recheck = on_command('全部重获取',
                                 permission=SUPERUSER,
                                 priority=priority)