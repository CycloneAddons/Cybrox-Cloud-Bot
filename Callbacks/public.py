# callbacks/example_callback.py

callback_data = "public"
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def handle_callback(bot, call):
    unique_code = call.data.split('_')[1]
    result = bot.dbuser.update_one(
    {"files.uniqueCode": unique_code},  # Find document with a file matching uniqueCode
    {"$set": {
        "files.$.isPublic": True,  # Update the 'isPublic' field
        
    }}
)
        
    if result.modified_count > 0:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Search", callback_data=f'search'))

            # Send confirmation message if the update was successful
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f"Your File Is Successfuly Public And Can Be Search  \n\nFile Link: https://t.me/cybroxcloudbot?start=get_{unique_code}", reply_markup=markup)
    else:
            # Send error message if no matching document was found
            bot.send_message(call.message.chat.id, "File not found or already public.")
    
    