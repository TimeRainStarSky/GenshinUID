old_url = 'https://api-takumi.mihoyo.com'
new_url = 'https://api-takumi-record.mihoyo.com'
bbs_url = 'https://bbs-api.mihoyo.com'
hk4_url = 'https://hk4-api.mihoyo.com'

bbs_Taskslist = bbs_url + '/apihub/sapi/getUserMissionsState'

'''账号相关'''
# 通过LoginTicket获取Stoken
get_stoken_url = old_url + '/auth/api/getMultiTokenByLoginTicket'

'''米游社相关'''
# 获取签到列表
sign_list_url = old_url + '/event/bbs_sign_reward/home'
# 获取签到信息
sign_info_url = old_url + '/event/bbs_sign_reward/info'
# 执行签到
sign_url = old_url + '/event/bbs_sign_reward/sign'

'''原神相关'''
# 每日信息 树脂 派遣等
dailyNote_url = new_url + '/game_record/app/genshin/api/dailyNote'
# 每月札记
monthlyAward_url = hk4_url + '/event/ys_ledger/monthInfo'
# 获取角色基本信息
player_info_url = new_url + '/game_record/app/genshin/api/index'
# 获取深渊信息
player_abyss_info_url = new_url + '/game_record/app/genshin/api/spiralAbyss'
# 获取详细角色信息
player_detail_info_url = new_url + '/game_record/app/genshin/api/character'
# 天赋计算器API 获取天赋等级信息
calculate_info_url = old_url + '/event/e20200928calculate/v1/sync/avatar/detail'
# 获取米游社内的角色信息 mysid -> uid
mihoyo_bbs_player_info_url = new_url + '/game_record/card/wapi/getGameRecordCard'