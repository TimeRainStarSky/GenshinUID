sign_scheduler = require('nonebot_plugin_apscheduler').scheduler

get_sign = on_command('签到', priority=priority)
all_recheck = on_command('全部重签', permission=SUPERUSER, priority=priority)
