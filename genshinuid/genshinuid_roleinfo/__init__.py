get_uid_info = on_regex('^(uid|查询)?([0-9]{9})?$', priority=priority)
get_mys_info = on_regex('^(mys)?([0-9]+)?$', priority=priority)