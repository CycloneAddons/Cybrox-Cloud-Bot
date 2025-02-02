from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

callback_data = "tocaccept"

def handle_callback(bot, call):
    user = bot.dbuser.find_one({"_id": call.message.chat.id})
    
    if user:

        bot.dbuser.update_one(
            {"_id": call.message.chat.id},
            {"$set": {"toc": True}}
        )
        print(f"User {call.message.chat.id} has accepted the terms.")

        markup = InlineKeyboardMarkup(row_width=4)
        markup.add(InlineKeyboardButton("Enter Your Email", callback_data='emailConfirm'))
        bot.send_message(call.message.chat.id, f"Thanks For Accepting Terms & Condition To Cybrox Cloud.\nPlease Sign Up to Continue....", reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    else:
        print(f"User {call.message.from_user.id} not found in the database.")
        # Optionally, send a message if the user isn't found
        bot.answer_callback_query(call.id, "Something went wrong. User not found.")
