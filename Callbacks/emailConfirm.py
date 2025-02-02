import re
callback_data = "emailConfirm"
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def handle_callback(bot, call):
    frst = bot.send_message(call.message.chat.id, "Please enter the your Email...")
    bot.delete_message(call.message.chat.id, call.message.message_id)

    def handler(msg):
        bot.delete_message(call.message.chat.id, frst.message_id)
        bot.delete_message(call.message.chat.id, msg.message_id)
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', msg.text):

         user = bot.dbuser.find_one({"email": msg.text})
         if not user:
          markup = InlineKeyboardMarkup(row_width=4)
          markup.add(InlineKeyboardButton("Send OTP", callback_data='sendotp'),
                    InlineKeyboardButton("Change Email", callback_data='changeEmail'))

          bot.send_message(call.message.chat.id, f"Please Confirm Your Email\n\nEmail: {msg.text}\n", reply_markup=markup)
         else:
             newe = InlineKeyboardMarkup(row_width=4)
             newe.add(InlineKeyboardButton("Enter Another Email", callback_data='emailConfirm'))
             bot.send_message(call.message.chat.id, f"The Email You Provided Is Already Used By Someone...",  reply_markup=newe)
        else:
            wrong = InlineKeyboardMarkup(row_width=4)
            wrong.add(InlineKeyboardButton("Enter Email Again", callback_data='emailConfirm'))
            bot.send_message(call.message.chat.id, f"Opps: It's Look Like You Provide An Invalid Email Please Send Your Correct Email...", reply_markup=wrong)
        

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, handler)

