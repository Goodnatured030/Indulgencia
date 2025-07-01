import os
from vk_api import VkApi
from telegram import Bot

VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = int(os.environ.get('GROUP_ID', 44554509))

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
    items = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']
    # Убираем закреплённые посты
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

    # Получаем последние комментарии
    comments_data = vk.wall.getComments(
        owner_id=-GROUP_ID,
        post_id=pid,
        count=20,
        sort='desc',
        preview_length=0
    )['items']

    author_ids = list({c['from_id'] for c in comments_data})
    authors = {}
    if author_ids:
        users = vk.users.get(user_ids=author_ids)
        for u in users:
            authors[u['id']] = f"{u.get('first_name')} {u.get('last_name')}"

    comments = [
        f"{authors.get(c['from_id'], 'ID ' + str(c['from_id']))}: {c['text'].strip()}"
        for c in comments_data
    ]

    comments_block = ""
    if comments:
        comments_block = "\n\nКомментарии:\n— " + "\n— ".join(comments)

    message = text + comments_block
    tg.send_message(CHAT_ID, message)
    print(f"Отправлен пост {pid}")

    save_last_id(pid)

if __name__ == '__main__':
    run()