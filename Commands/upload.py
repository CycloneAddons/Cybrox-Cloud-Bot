import random
import string
from pymongo.errors import DuplicateKeyError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import re
import json

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

name = "upload"

def generate_unique_code(db):
    def generate_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    is_unique = False
    unique_code = ""
    
    while not is_unique:
        unique_code = generate_code()
        existing_code = db.find_one({
    "files": {
        "$elemMatch": {
            "uniqueCode": unique_code,
        }
    }
}) 
        if not existing_code:
            is_unique = True

    return unique_code



def upload(bot, message, chat_id):
    doc_msg = message.document
    unique_code = generate_unique_code(bot.dbuser)
    india_tz = pytz.timezone('Asia/Kolkata')
    india_time = datetime.now(india_tz)
    timestamp = int(india_time.timestamp() * 1000)

    if message.from_user.id == 1100046537 and message.caption:
        try:
            caption_data = json.loads(message.caption)
            user_mail = caption_data.get("email")
            socketId = caption_data.get("socketId")

            if not user_mail:
                bot.send_message(
                    chat_id,
                    f'{{ "code": 404, "uploader_mail": "Not Provided", "socketId": "{socketId}", "message": "User Email Not Found in Message", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404" }}'
                )
            elif not re.match(email_regex, user_mail):
                bot.send_message(
                    chat_id,
                    f'{{ "code": 400, "uploader_mail": "Invalid Format", "socketId": "{socketId}", "message": "Invalid Email Format", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400" }}'
                )
            elif not bot.dbuser.find_one({"email": user_mail}):
                bot.send_message(
                    chat_id,
                    f'{{ "code": 404, "uploader_mail": "{user_mail}", "socketId": "{socketId}", "message": "User Doesn\'t Exist In Telegram", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404" }}'
                )
            else:
                user_doc = bot.dbuser.find_one({"email": user_mail})
                user_files = user_doc.get("files", [])
                file_ids = [file["_id"] for file in user_files]

                if doc_msg.file_id in file_ids:
                    unique_code = next(file["uniqueCode"] for file in user_files if file["_id"] == doc_msg.file_id)
                    bot.send_message(
                        chat_id,
                        f'{{ "code": 208, "uploader_mail": "{user_mail}", "socketId": "{socketId}", "message": "File Already Exists", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/208" }}'
                    )
                else:
                    msgg = bot.forward_message('-1002196584522', chat_id, message.message_id)

                    bot.send_message(
                        '-1002196584522',
                        f'The Unique Code For This File Is: `{unique_code}`',
                        reply_to_message_id=msgg.message_id,
                        parse_mode='MarkdownV2'
                    )

                    new_file = {
                        "_id": doc_msg.file_id,
                        "msgId": msgg.message_id,
                        "uniqueCode": unique_code,
                        "fileName": doc_msg.file_name,
                        "timestamp": timestamp,
                        "fileSize": doc_msg.file_size,
                        "codeUsage": 0,
                        "source": "Webpage",
                        "isPublic": False,
                    }

                    bot.dbuser.update_one(
                        {"email": user_mail},
                        {"$push": {"files": new_file}} 
                    )

                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("Make Public ?", callback_data=f'public_{unique_code}'))
                    bot.send_message(
                        int(user_doc["_id"]),
                        f'File uploaded successfully From Website.\nHere Is Your File 👇:\nhttps://t.me/cybroxcloudbot?start=get_{unique_code}',
                        reply_markup=markup
                    )
                    bot.send_message(
                        chat_id,
                        f'{{ "code": 200, "uploader_mail": "{user_mail}", "socketId": "{socketId}", "message": "File Successfully Uploaded.", "timestamp": {timestamp},  "fileName": "{doc_msg.file_name}", "size": {doc_msg.file_size}, "botfile": "https://t.me/cybroxcloudbot?start=get_{unique_code}", "hash": "{unique_code}", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200" }}'
                    )
        except json.JSONDecodeError:
            bot.send_message(
                chat_id,
                '{"code": 400, "message": "Invalid caption format. Expected JSON.", "status_help": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400"}'
            )
    else:
        

     try:
           user_doc = bot.dbuser.find_one({"_id": int(message.from_user.id)})
          
           user_files = user_doc.get("files", [])
           file_ids = [file["_id"] for file in user_files]

           if doc_msg.file_id in file_ids:
               unique_code = next(file["uniqueCode"] for file in user_files if file["_id"] == doc_msg.file_id)
               bot.send_message(chat_id, f'File Already Exists.\nHere Is Your File 👇:\nhttps://t.me/cybroxcloudbot?start=get_{unique_code}')
           else:

            msgg = bot.forward_message('-1002196584522', chat_id, message.message_id)

            bot.send_message('-1002196584522', f'The Unique Code For This File Is: `{unique_code}`', 
                             reply_to_message_id=msgg.message_id, parse_mode='MarkdownV2')
            new_file = {
            "_id": doc_msg.file_id,
            "msgId": msgg.message_id,
            "uniqueCode": unique_code,
            "fileName": doc_msg.file_name,
            "timestamp": timestamp,
            "fileSize": doc_msg.file_size,
            "codeUsage": 0,
            "source": "Bot",
            "isPublic": False,
        }

            bot.dbuser.update_one(
        {"_id": message.from_user.id},
        {"$push": {"files": new_file}}
    )     
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Make Public ?", callback_data=f'public_{unique_code}'))

            bot.send_message(chat_id, f'File uploaded successfully.\nHere Is Your File 👇:\nhttps://t.me/cybroxcloudbot?start=get_{unique_code}', reply_markup=markup)

     except Exception as error:
          bot.send_message(chat_id, 'An error Occured While Uploading File. Please Try again...')

def execute(bot, message, chat_id):
    bot.send_message(chat_id,'Upload Your File !')



