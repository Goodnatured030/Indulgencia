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
    # Берём несколько записей, чтобы пропустить закреплённый
    posts = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']

    # Находим первую неприкреплённую запись
    for post in posts:
        if post.get('is_pinned', 0) == 1:
            continue
        pid = post['id']
        if pid == last_id:
            return  # последнюю уже отсылали
        text = post.get('text', '').strip()
        if not text:
            return  # пустой текст — ничего не шлём

        # Отправляем только текст
        tg.send_message(CHAT_ID, text)

        # Фиксируем, что эту запись уже отослали
        save_last_id(pid)
        return  # после отправки выходим

if __name__ == '__main__':
    run()