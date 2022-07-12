from ..re_import import * # noqa: F401, F403
from .draw_event_img import draw_event_img

TEXT_PATH = Path(__file__).parents[0] / 'texture2d'

get_event = on_command('活动列表', priority=priority)

@get_event.handle()
@handle_exception('活动')
async def send_events(matcher: Matcher, args: Message = CommandArg()):
    if args:
        return
    img_path = Path(__file__).parents[0] / 'event.png'
    while True:
        if img_path.exists():
            with open(img_path, 'rb') as f:
                im = MessageSegment.image(f.read())
            break
        else:
            await draw_event_img()
    await matcher.finish(im)