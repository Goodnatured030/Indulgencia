import os
from vk_api import VkApi
from telegram import Bot

# Читаем токены и настройки из окружения
VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = 44554509  # ваш ID группы без "club"

# Инициализация клиентов VK и Telegram
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
    # Получаем последний пост
    feed = vk.wall.get(owner_id=-GROUP_ID, count=1)['items']
    if not feed:
        return
    post = feed[0]
    pid = post['id']
    if pid == last_id:
        return  # уже отправляли этот пост

    text = post.get('text', '').strip()

    # --- Получаем комментарии поста ---
    comments_data = vk.wall.getComments(
        owner_id=-GROUP_ID,
        post_id=pid,
        count=20,           # берём до 20 комментариев
        sort='desc',        # самые новые первыми
        preview_length=0    # полный текст
    )['items']

    # Собираем уникальные ID авторов комментариев
    author_ids = list({c['from_id'] for c in comments_data})
    # Запрашиваем данные авторов одной пачкой
    authors = {}
    if author_ids:
        users = vk.users.get(user_ids=author_ids)
        for u in users:
            authors[u['id']] = f"{u.get('first_name','')} {u.get('last_name','')}"

    # Формируем блок комментариев
    comments = []
    for c in comments_data:
        name = authors.get(c['from_id'], f"ID {c['from_id']}")
        comment_text = c.get('text', '').strip()
        comments.append(f"{name}: {comment_text}")

    comments_block = ""
    if comments:
        comments_block = "\n\nКомментарии:\n— " + "\n— ".join(comments)

    # Итоговое сообщение (только текст поста и комментарии)
    message = f"{text}{comments_block}"

    # Отправляем в Telegram
    tg.send_message(CHAT_ID, message)

    # Сохраняем ID отправленного поста
    save_last_id(pid)

if __name__ == '__main__':
    run()
