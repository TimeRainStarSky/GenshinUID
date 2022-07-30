from ..all_import import *  # noqa: F403,F401

get_lots = on_command('御神签', priority=priority)


@get_lots.handle()
@handle_exception('御神签')
async def send_lots(
    event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    if args:
        await matcher.finish()
    qid = int(event.sender.user_id)
    raw_data = await get_a_lots(qid)
    im = base64.b64decode(raw_data).decode('utf-8')
    await matcher.finish(im)
