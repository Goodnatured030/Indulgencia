import os
import subprocess
from vk_api import VkApi
from telegram import Bot, InputMediaPhoto

# Загрузка токенов и настроек из окружения
VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = 44554509

vk = VkApi(token=VK_TOKEN).get_api()
tg = Bot(token=TG_TOKEN)

def get_last_id():
    try:
        return int(open('last_id.txt').read().strip())
    except:
        return 0

def save_last_id_and_commit(pid):
    # Сохраняем ID
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))
    # Коммитим и пушим обратно в репозиторий
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
    posts = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']

    for post in posts:
        if post.get('is_pinned', 0):
            continue

        pid = post['id']
        if pid == last_id:
            return

        # 1) Отправляем текст поста
        text = post.get('text', '').strip()
        if text:
            tg.send_message(CHAT_ID, text)

        # 2) Отправляем фотографии
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

        # 3) Отправляем видео как Markdown-ссылку
        for att in post.get('attachments', []):
            if att['type'] == 'video':
                v = att['video']
                owner = v['owner_id']
                vid   = v['id']
                title = v.get('title', 'Видео')
                access = v.get('access_key')
                link = f"https://vk.com/video{owner}_{vid}"
                if access:
                    link += f"?access_key={access}"
                tg.send_message(
                    CHAT_ID,
                    f"🎥 [{title}]({link})",
                    parse_mode='Markdown'
                )

        # Сохраняем и коммитим last_id
        save_last_id_and_commit(pid)
        return  # только один пост за запуск

if __name__ == '__main__':
    run()