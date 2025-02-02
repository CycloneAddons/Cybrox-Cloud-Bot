name = "start"
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import telebot
in_msg = {}
def execute(bot, message, chat_id):
  user = bot.dbuser.find_one({"_id": message.from_user.id})
  
  if not user:
    # User not found, send the message with the button and insert the new user
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Accept Terms & Condition", callback_data='tocaccept'))
    bot.send_message(message.chat.id, f'''Hey, {message.from_user.first_name} By using Cybrox Cloud Bot, you agree to the following terms:

Prohibited Content:

Do not upload or share any content that is illegal, harmful, offensive, or violates any laws.
Strictly NO posting of 18+, adult content, or explicit material.

Illegal Activities:

This bot is not to be used for any unlawful purposes, including but not limited to piracy, fraud, or malicious activities.

User Responsibility:

You are solely responsible for the content you upload, share, or access.
Cybrox Cloud Bot and its developers are not liable for any misuse or illegal activity conducted by users.

Content Moderation:

Any content reported or found violating these terms will be removed, and offending users may be banned.

By continuing to use this bot, you agree to abide by these terms. Failure to comply may result in termination of your access. ''' , reply_markup=markup)
    
    # Add new user to the database with toc set to False
    new_user = {
        "_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "toc": False,
        "email": None,
        "password": None,
        "isVerified": False
    }
    bot.dbuser.insert_one(new_user)

  elif user and not user.get("toc"):
    # User found, but toc is False
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Accept Terms & Condition", callback_data='tocaccept'))
    bot.send_message(message.chat.id, f'''Hey, {message.from_user.first_name} By using Cybrox Cloud Bot, you agree to the following terms:

Prohibited Content:

Do not upload or share any content that is illegal, harmful, offensive, or violates any laws.
Strictly NO posting of 18+, adult content, or explicit material.

Illegal Activities:

This bot is not to be used for any unlawful purposes, including but not limited to piracy, fraud, or malicious activities.

User Responsibility:

You are solely responsible for the content you upload, share, or access.
Cybrox Cloud Bot and its developers are not liable for any misuse or illegal activity conducted by users.

Content Moderation:

Any content reported or found violating these terms will be removed, and offending users may be banned.

By continuing to use this bot, you agree to abide by these terms. Failure to comply may result in termination of your access. ''' , reply_markup=markup)
    
  elif user and not user.get("isVerified"):

    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Enter Your Email", callback_data='emailConfirm'))
    bot.send_message(message.chat.id, f"Hey, {message.from_user.first_name} Welcome Back To Cybrox Cloud. Please Sign Up to Continue....", reply_markup=markup)

  elif user and not user.get("password"):
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(InlineKeyboardButton("Set Password", callback_data='setpassword'))
    bot.send_message(message.chat.id, f"Hey, {message.from_user.first_name} Welcome Back To Cybrox Cloud. Please Set Your Password to Continue....", reply_markup=markup)

  elif isinstance(message, telebot.types.Message) and "get_" in message.text:
    unique_code = message.text.split("get_", 1)[1]
    if unique_code:
     bot.delete_message(chat_id, message.id)
     getrq(bot, chat_id, unique_code)
    else:
      bot.send_message(message.chat.id, "There is no unique code provided.")
  elif isinstance(message, telebot.types.Message) and "metadata_" in message.text:
    unique_code = message.text.split("metadata_", 1)[1]
    if unique_code:
      bot.delete_message(chat_id, message.id)

      metadata(bot, chat_id, unique_code)
    else:
      bot.send_message(message.chat.id, "There is no unique code provided.")
 
  else:
  
       markup = InlineKeyboardMarkup(row_width=4)  # Set row width to 4 to fit all buttons in a single row
       markup.add(
    InlineKeyboardButton("Upload", callback_data='upload'),
    InlineKeyboardButton("Get", callback_data='get'),
    InlineKeyboardButton("Help", callback_data='help'),
    InlineKeyboardButton("Search", callback_data='search')
)
       bot.send_animation(chat_id, 'https://cdn.glitch.global/1910be23-ef5a-4bf6-8290-3773422935f4/Purple%20Pink%20Gradient%20Mobile%20Application%20Presentation.gif?v=1732384869230', 
        caption=('''You can easily upload, access, manage, and share your files securely within our platform. 

If you need any assistance or have any questions, feel free to explore the options below. We're here to help every step of the way.
                — your files, our priority. '''),  reply_markup=markup)



    
def getrq(bot, chat_id, unique_code_msg):
    file_owner = bot.dbuser.find_one({"files.uniqueCode": unique_code_msg}, {"files.$": 1})

    if file_owner and "files" in file_owner:
        file_record = file_owner["files"][0]  
        file_id = file_record["_id"]

        bot.send_document(chat_id, file_id)

        new_count = file_record.get("codeUsage", 0) + 1
        bot.dbuser.update_one(
            {"_id": file_owner["_id"], "files.uniqueCode": unique_code_msg},
            {"$set": {"files.$.codeUsage": new_count}}
        )
    else:
        bot.send_message(chat_id, "Invalid unique code. Please try again.")

    
      


from datetime import datetime

def metadata(bot, chat_id, unique_code_msg):
    file_owner = bot.dbuser.find_one({"files.uniqueCode": unique_code_msg}, {"files.$": 1})

    if file_owner and "files" in file_owner:
        file_record = file_owner["files"][0]
        status = "Public" if file_record.get("isPublic", True) else "Private"
        timeee = "Unavailable"

        tim = file_record.get("timestamp")
        if tim:
            timestamp_s = tim / 1000
            timeee = datetime.fromtimestamp(timestamp_s).strftime('%H:%M:%S, %d/%m/%y')

        bot.send_document(
            chat_id,
            file_record["_id"],
            caption=(
                f"\nFile: `{file_record['fileName']}`\n\n"
                f"Unique Code: `{file_record['uniqueCode']}`\n\n"
                f"Status: `{status}`\n\n"
                f"Views: `{file_record.get('codeUsage', 0)}`\n\n"
                f"Uploaded At: `{timeee}`"
            ),
            parse_mode='Markdown'
        )
    else:
        bot.send_message(chat_id, "Invalid unique code. Please try again.")
