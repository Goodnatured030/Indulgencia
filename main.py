import os
from vk_api import VkApi
from telegram import Bot

# Читаем токены и настройки из окружения
VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = int(os.environ.get('GROUP_ID', 44554509))

# Инициализация клиентов VK и Telegram
vk = VkApi(token=VK_TOKEN).get_api()
tg = Bot(token=TG_TOKEN)

def get_last_id():
    try:
        with open('last_id.txt', 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_last_id(pid):
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))

def fetch_new_post():
    # Берём первые 5 постов и отфильтровываем закреплённые
    items = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']
    posts = [p for p in items if not p.get('is_pinned')]
    return posts[0] if posts else None

def run():
    last_id = get_last_id()
    post = fetch_new_post()
    if not post:
        print("Нет новых постов")
        return

    pid = post['id']
    if pid == last_id:
        print(f"Пост {pid} уже отправлен")
        return

    text = post.get('text', '').strip()

    # Отправляем только текст поста
    tg.send_message(CHAT_ID, text)
    print(f"Отправлен пост {pid}")

    save_last_id(pid)

if __name__ == '__main__':
    run()