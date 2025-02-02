

callback_data = "changeEmail"
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def handle_callback(bot, call):
          bot.delete_message(call.message.chat.id, call.message.message_id)
          try:
           bot.clear_step_handler_by_chat_id(call.message.chat.id)
          except Exception as e:
                pass
          
          wrong = InlineKeyboardMarkup(row_width=4)
          wrong.add(InlineKeyboardButton("Enter New Email", callback_data='emailConfirm'))
          bot.send_message(call.message.chat.id, f"You Wish To Change Your Email Please Click on Button...", reply_markup=wrong)
        
