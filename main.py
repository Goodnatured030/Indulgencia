import os
import subprocess
from vk_api import VkApi
from telegram import Bot

# Токены и ID из GitHub Secrets
VK_TOKEN = os.environ['VK_TOKEN']
TG_TOKEN = os.environ['TG_TOKEN']
CHAT_ID  = os.environ['CHAT_ID']
GROUP_ID = 44554509

vk = VkApi(token=VK_TOKEN).get_api()
tg = Bot(token=TG_TOKEN)

def get_last_id():
    try:
        with open('last_id.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_last_id_and_commit(pid):
    # Сохраняем ID в файл
    with open('last_id.txt', 'w') as f:
        f.write(str(pid))

    # Коммитим и пушим last_id.txt обратно в репозиторий
    try:
        subprocess.run(['git', 'config', '--global', 'user.email', 'bot@vk2tg.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'vk2tg-bot'], check=True)
        subprocess.run(['git', 'add', 'last_id.txt'], check=True)
        subprocess.run(['git', 'commit', '-m', f'update last_id to {pid}'], check=True)
        subprocess.run(['git', 'push'], check=True)
    except Exception as e:
        print("❌ Git commit failed:", e)

def run():
    last_id = get_last_id()
    posts = vk.wall.get(owner_id=-GROUP_ID, count=5)['items']

    for post in posts:
        if post.get('is_pinned', 0) == 1:
            continue

        pid = post['id']
        if pid == last_id:
            print("🚫 Уже отправляли этот пост")
            return

        text = post.get('text', '').strip()
        if not text:
            print("⛔ Пустой пост — пропускаем")
            return

        # Отправляем в Telegram
        tg.send_message(CHAT_ID, text)
        print("✅ Отправлено в Telegram")

        # Сохраняем и коммитим
        save_last_id_and_commit(pid)
        return  # только один пост за запуск

if __name__ == '__main__':
    run()