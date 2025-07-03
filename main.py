import os
import subprocess
from vk_api import VkApi
from telegram import Bot, InputMediaPhoto

# Загружаем токены и настройки
VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = 44554509  # без "club"

vk = VkApi(token=VK_TOKEN).get_api()
tg = Bot(token=TG_TOKEN)

def get_last_id():
    try:
        with open('last_id.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_last_id_and_commit(pid):
    # Сохраняем ID
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))
    # Коммитим и пушим файл обратно
    for cmd in [
        ['git','config','--global','user.email','bot@vk2tg.com'],
        ['git','config','--global','user.name','vk2tg-bot'],
        ['git','add','last_id.txt'],
        ['git','commit','-m',f'update last_id to {pid}'],
        ['git','push']
    ]:
        subprocess.run(cmd, check=False)

def run():
    last_id = get_last_id()

    # 1) Попытка получить ленту, при ошибках — graceful exit
    try:
        posts = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']
    except Exception as e:
        print(f"⚠️ Ошибка VK API: {e}")
        return

    # 2) Ищем первый неприкреплённый новый пост
    for post in posts:
        if post.get('is_pinned', 0):
            continue

        pid = post['id']
        if pid == last_id:
            print("🚫 Дубликат, уже отправляли")
            return

        # 3) Текст
        text = post.get('text','').strip()
        if text:
            tg.send_message(CHAT_ID, text)

        # 4) Фото
        media = []
        for att in post.get('attachments', []):
            if att['type'] == 'photo':
                sizes = att['photo']['sizes']
                best = max(sizes, key=lambda s: s['width'] * s['height'])
                media.append(InputMediaPhoto(media=best['url']))
        if media:
            if len(media) == 1:
                tg.send_photo(CHAT_ID, media[0].media)
            else:
                tg.send_media_group(CHAT_ID, media)

        # 5) Видео как Markdown-ссылка
        for att in post.get('attachments', []):
            if att['type'] == 'video':
                v = att['video']
                owner = v['owner_id']
                vid   = v['id']
                title = v.get('title','Видео')
                link = f"https://vk.com/video{owner}_{vid}"
                if v.get('access_key'):
                    link += f"?access_key={v['access_key']}"
                tg.send_message(
                    CHAT_ID,
                    f"🎥 [{title}]({link})",
                    parse_mode='Markdown'
                )

        # 6) Сохраняем и коммитим
        save_last_id_and_commit(pid)
        print("✅ Отправлено и запомнено")
        return

if __name__ == '__main__':
    run()