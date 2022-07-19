import re

from ..utils.db_operation.db_operation import connect_db


async def link_uid_to_qq(qid: int, message: str):
    uid = re.findall(r'\d+', message)[0]  # str
    await connect_db(qid, uid)


async def link_mihoyo_id_to_qq(qid: int, message: str):
    mysid = re.findall(r'\d+', message)[0]  # str
    await connect_db(qid, None, mysid)
