import os
import subprocess
from vk_api import VkApi
from telegram import Bot, InputMediaPhoto

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
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))
    # коммитим и пушим back
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
        if post.get('is_pinned'): continue
        pid = post['id']
        if pid == last_id: return

        text = post.get('text','').strip()
        if text:
            tg.send_message(CHAT_ID, text)

        # Обработка фото вложений
        photos = []
        for att in post.get('attachments', []):
            if att['type'] == 'photo':
                sizes = att['photo']['sizes']
                # выбираем ссылку на наибольшее изображение
                max_photo = max(sizes, key=lambda s: s['width']*s['height'])
                photos.append(InputMediaPhoto(media=max_photo['url']))

        if photos:
            # если одно фото, можно tg.send_photo
            if len(photos) == 1:
                tg.send_photo(CHAT_ID, photos[0].media)
            else:
                tg.send_media_group(CHAT_ID, photos)

        # Обработка видео вложений (отправляем ссылкой)
        for att in post.get('attachments', []):
            if att['type'] == 'video':
                owner = att['video']['owner_id']
                vid = att['video']['id']
                access = att['video'].get('access_key')
                link = f"https://vk.com/video{owner}_{vid}"
                if access:
                    link += f"?access_key={access}"
                tg.send_message(CHAT_ID, f"Видео: {link}")

        # Обработка прочих файлов (документы, аудио и т.д.)
        for att in post.get('attachments', []):
            t = att['type']
            if t not in ('photo','video'):
                doc = att[t]
                url = doc.get('url') or doc.get('mp3'), 
                if url:
                    tg.send_document(CHAT_ID, url if isinstance(url,str) else url[0])

        save_last_id_and_commit(pid)
        return

if __name__ == '__main__':
    run()