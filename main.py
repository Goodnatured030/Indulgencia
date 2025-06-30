import os
from vk_api import VkApi
from telegram import Bot

VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = 44554509

vk = VkApi(token=VK_TOKEN).get_api()
tg = Bot(token=TG_TOKEN)

def get_last_id():
    with open('last_id.txt', 'r') as f:
        return int(f.read().strip())

def save_last_id(pid):
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))

def run():
    last_id = get_last_id()
    posts = vk.wall.get(owner_id=-GROUP_ID, count=1)['items']
    if not posts:
        return
    pid = posts[0]['id']
    if pid == last_id:
        return
    text = posts[0].get('text', '').strip()
    link = f"https://vk.com/wall-{GROUP_ID}_{pid}"
    tg.send_message(CHAT_ID, f"{text}\n\n{link}")
    save_last_id(pid)

if __name__ == '__main__':
    run()
