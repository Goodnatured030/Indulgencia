import os
import vk_api
import telegram

# Конфигурация
VK_TOKEN = os.getenv("VK_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))  # без минуса!

LAST_ID_FILE = "last_id.txt"

def get_last_id():
    """Читаем последний опубликованный пост"""
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def set_last_id(post_id):
    """Сохраняем id последнего поста"""
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(post_id))

def send_to_telegram(post):
    """Отправка поста в Telegram"""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    text = post.get("text", "")
    attachments = post.get("attachments", [])

    # Если есть фото → берём самое большое
    photos = [a for a in attachments if a["type"] == "photo"]
    if photos:
        photo = max(photos[0]["photo"]["sizes"], key=lambda x: x["width"])["url"]
        bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=text[:1024] or None)
    else:
        bot.send_message(chat_id=CHAT_ID, text=text or "(без текста)")

def run():
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()

    posts = vk.wall.get(owner_id=-GROUP_ID, count=5)["items"]

    last_id = get_last_id()
    new_posts = [p for p in posts if p["id"] > last_id]

    # Если новых постов нет — выходим
    if not new_posts:
        print("Нет новых постов.")
        return

    # Отправляем от старого к новому
    for post in reversed(new_posts):
        send_to_telegram(post)

    # Сохраняем id последнего
    set_last_id(new_posts[0]["id"])

if __name__ == "__main__":
    run()