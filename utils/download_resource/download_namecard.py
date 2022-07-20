import re
import asyncio
import traceback

from bs4 import BeautifulSoup
from httpx import AsyncClient

from .RESOURCE_PATH import *  # noqa: E501

baseurl = "https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki"


async def get_url(url):
    async with AsyncClient() as client:
        req = await client.get(url=url)
    return req.text


async def download(url, char_name, file_name):
    print("正在下载{},{}".format(char_name, url))
    # asyncio.sleep(1)
    try:
        async with AsyncClient() as client:
            req = await client.get(url=url)

        while 1:
            if os.path.exists(NameCard_PATH):
                with open(CHAR_NAMECARD_PATH / file_name, 'wb') as f:
                    f.write(req.content)
                    f.close
                print("下载完成!")
                break
            else:
                os.makedirs(CHAR_NAMECARD_PATH, exist_ok=True)
    except:
        traceback.print_exc()
        print("下载失败，该文件不存在。")


async def main():
    base_data = await get_url(baseurl)
    content_bs = BeautifulSoup(base_data, 'lxml')
    raw_data_5star = content_bs.find_all(
        "div", class_='card_container card_5 hidden'
    )
    raw_data_4star = content_bs.find_all(
        "div", class_='card_container card_4 hidden'
    )
    raw_data_5astar = content_bs.find_all(
        "div", class_='card_container card_5a hidden'
    )
    raw_data = raw_data_5star + raw_data_4star + raw_data_5astar
    char_list = {}
    for i in raw_data:
        char_url = (
            "https://genshin-impact.fandom.com"
            + i.find("a")["href"]
            + "/Media"
        )
        if i.find("a")["title"] != "Traveler":
            char_list[i.find("a")["title"]] = char_url
    tasks = []
    for i in char_list.keys():
        cahr_voice_data = await get_url(char_list[i])
        char_info_data = await get_url(char_list[i][:-6])
        info_bs = BeautifulSoup(char_info_data, 'lxml')
        chinese_name = info_bs.find_all("span", lang='zh-Hans')[0].text
        print(chinese_name)
        namecard_bs = BeautifulSoup(cahr_voice_data, 'lxml')
        namecard_data = namecard_bs.find_all(
            "div", class_='wikia-gallery-item'
        )
        if i == "Gorou":
            namecard = namecard_data[-3].find_all("img")[0]["src"]
        else:
            namecard = namecard_data[-2].find_all("img")[0]["src"]
        namecard_url = re.search(r"[\s\S]+.png", namecard).group(0)
        tasks.append(
            download(namecard_url, chinese_name, chinese_name + ".png")
        )
    await asyncio.wait(tasks)
    print("全部下载完成！")


if __name__ == "__main__":
    asyncio.run(main())
