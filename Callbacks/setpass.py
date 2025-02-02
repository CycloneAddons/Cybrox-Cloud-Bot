
callback_data = "setpassword"
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

def handle_callback(bot, call):
 
  bot.delete_message(call.message.chat.id, call.message.message_id)
  a = bot.send_message(call.message.chat.id, f"Please Enter Your Password\n\n - Passwd Should More Than 8 Chars.\n - Don't Use Same Chars In Passwd.")

  def handler(msg):
        bot.delete_message(call.message.chat.id, msg.message_id)
        bot.delete_message(call.message.chat.id, a.message_id)

        pattern = r'^(?=.*(.)(?!\1{7})).{8,}$'
        if re.match(pattern, msg.text):
            bot.dbuser.update_one(
            {"_id": call.message.chat.id},
            {"$set": {"password": msg.text}}
            )
            bot.send_message(call.message.chat.id, f"Password Successfully Set...")
            cmd = bot.commands.get('/start')
            cmd.execute(bot, call, call.message.chat.id)
        else:
            markup = InlineKeyboardMarkup(row_width=4)
            markup.add(InlineKeyboardButton("Sent Password Again", callback_data='setpassword'))

            bot.send_message(call.message.chat.id, f"Opps! It's Look Like Your Password Is To Short Or Have Similar Characters...", reply_markup=markup)

  bot.register_next_step_handler_by_chat_id(call.message.chat.id, handler)
  #++