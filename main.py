import os
import telebot
from utils.db_setup import setup_db
from utils.email_util import check_mail 
from utils.loader import load_commands, load_callbacks
from dotenv import load_dotenv

load_dotenv()


bot = telebot.TeleBot(os.getenv('TOKEN'))

bot.dbfiles, bot.dbuser = setup_db()
bot.mail = None 
bot.commands = {}
bot.callbacks = {}
bot.user_otps = {}
bot.otp_success_id = {}
bot.user_invalid_otp_msg_ids = {} 

bot.commands = load_commands(os.path.join(os.path.dirname(__file__), 'Commands'))
bot.callbacks = load_callbacks(os.path.join(os.path.dirname(__file__), 'Callbacks'))
bot.reloadCmd = lambda: load_commands(os.path.join(os.path.dirname(__file__), 'Commands'))
bot.reloadCb = lambda: load_callbacks(os.path.join(os.path.dirname(__file__), 'Callbacks'))

from handlers.callback_handler import handle_callback
from handlers.message_handler import handle_message

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    handle_callback(bot, call)

@bot.message_handler(func=lambda message: True, content_types=['document', 'text'])
def message_handler(message):
    handle_message(bot, message)

check_mail(bot)  

bot.infinity_polling()
