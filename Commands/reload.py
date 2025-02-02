# commands/reload.py
import importlib
import os
import sys

name = "reload"

def execute(bot, message, chat_id):
        initial = int(len(bot.commands))
        final = int(bot.reloadCmd())
        bot.reloadCb()
        result = (-1) * (initial - final)
        added = 0
        removed = 0
        if result > 0 :
            added = result
        elif result < 0:
            removed = (-1) * result
            
        bot.send_message(chat_id, f"Successfuly Reloaded Commands: \n Total Reload: {final}\n Total Added: {added}\n Total Removed: {removed}")
    