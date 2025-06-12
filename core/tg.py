# # utils/telegram_bot.py
# import requests
import requests
# TELEGRAM_BOT_TOKEN = '8137416132:AAHRlMOPrQx1l4cvRq7LoIV4uU2rVrmyFAU'
# TELEGRAM_CHAT_ID = 'ВАШ_CHAT_ID'  # можно взять вручную, или реализовать автоматическое получение

# def send_telegram_message(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     data = {
#         'chat_id': TELEGRAM_CHAT_ID,
#         'text': message
#     }
#     response = requests.post(url, data=data)
#     return response.json()
# bot.py
# from telegram.ext import Updater, MessageHandler, Filters
from .models import TelegramUser
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def start_handler(update, context):
    user = update.effective_user
    TelegramUser.objects.get_or_create(
        chat_id=user.id,
        defaults={
            'first_name': user.first_name,
            'username': user.username
        }
    )
    update.message.reply_text("Вы подписались на уведомления о новых заказах!")

def run_bot():
    updater = Updater("8137416132:AAHRlMOPrQx1l4cvRq7LoIV4uU2rVrmyFAU", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start_handler))
    updater.start_polling()
    updater.idle()

# utils/telegram_bot.py


TELEGRAM_BOT_TOKEN = '8137416132:AAHRlMOPrQx1l4cvRq7LoIV4uU2rVrmyFAU'

def send_broadcast(message):
    users = TelegramUser.objects.all()
    for user in users:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': user.chat_id, 'text': message}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user.chat_id}: {e}")
