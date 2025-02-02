# commands/reload.py
import importlib
import os
import sys

name = "restart"

def execute(bot, message, chat_id):
        bot.reply_to(message, "Bot is restarting...")
        
        os.execv(sys.executable, ['python'] + sys.argv) 
       