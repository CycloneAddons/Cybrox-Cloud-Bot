import re
from datetime import datetime
import humanize
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
import threading

def delete_message_after_delay(bot, chat_id, message_id, delay=120):
    threading.Timer(delay, bot.delete_message, [chat_id, message_id]).start()

name ="logfiles"
# Pagination function
def paginate_search_results(documents, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return documents[start:end]

# Function to generate pagination buttons
def generate_pagination_buttons(page, total_pages, user_id):
    markup = InlineKeyboardMarkup(row_width=4)
    
    if page > 1:
        markup.add(
            InlineKeyboardButton("First", callback_data=f"lpage_1_{user_id}"),
            InlineKeyboardButton("Back", callback_data=f"lpage_{page - 1}_{user_id}")
        )
    if page < total_pages:
        markup.add(
            InlineKeyboardButton("Next", callback_data=f"lpage_{page + 1}_{user_id}"),
            InlineKeyboardButton("Last", callback_data=f"lpage_{total_pages}_{user_id}")
        )
    
    return markup

def getPass(msg, mail, bot, chat_id, aa):
    bot.delete_message(chat_id, msg.message_id)
    bot.delete_message(chat_id, aa.message_id)
    
    if mail:
        user_data = bot.dbuser.find_one({"email": mail, "password": msg.text})
        if user_data:
            bot.send_message(chat_id, f"You Successfully logined as: {user_data.get('first_name')}\n - Your Session Will Be End Within 2 Minutes...")
            documents = list(bot.dbfiles.find({"uploader": user_data.get("_id")}))

            total_files = len(documents)  # Get the total number of files
            per_page = 10
            total_pages = (len(documents) // per_page) + (1 if len(documents) % per_page > 0 else 0)

            page = 1
            paginated_results = paginate_search_results(documents, page, per_page)

            # Generate message with filenames as Markdown hyperlinks and timestamp
            response_message = f"Your {total_files} Files:\n\n"
            for idx, doc in enumerate(paginated_results):
                file_name = doc.get('fileName')
                unique_code = doc.get('uniqueCode')
                timestamp = doc.get('timestamp')

                # If timestamp is not available, set a default value
                if timestamp:
                    file_time = datetime.fromtimestamp(timestamp / 1000)  # Convert from ms to seconds
                    time_diff = humanize.naturaltime(datetime.now() - file_time)  # Get human-readable time diff
                else:
                    time_diff = "Once upon a time"

                response_message += f"{idx + 1}. [{file_name}](https://t.me/cybroxcloudbot?start=metadata_{unique_code}) - {time_diff}\n\n"

            response_message += f"\nPage {page} of {total_pages}"

            sent_message = bot.send_message(chat_id, response_message, reply_markup=generate_pagination_buttons(page, total_pages, user_data.get("_id")), parse_mode='Markdown')

            # Delete the message after 2 minutes (120 seconds)
            delete_message_after_delay(bot, chat_id, sent_message.message_id, delay=120)

        else:
            bot.send_message(chat_id, "Incorrect password")
    else:
        bot.send_message(chat_id, "Email not found")


def execute(bot, message, chat_id):
    a = bot.send_message(chat_id, "Please Enter Your Email...")
    mail = None  

    def getMail(msg):
        bot.delete_message(chat_id, msg.message_id)
        bot.delete_message(chat_id, a.message_id)

        nonlocal mail  # Access to the outer mail variable
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', msg.text):
            mail = bot.dbuser.find_one({"email": msg.text})
            if mail:
                aa = bot.send_message(chat_id, "Please Enter Your Password...")
                # Pass `msg.text` as a parameter to `getPass` using a lambda
                bot.register_next_step_handler_by_chat_id(chat_id, lambda message: getPass(message, msg.text, bot, chat_id, aa))
            else:
                bot.send_message(chat_id, "Given Email Doesn't Exist...")
        else:
            bot.send_message(chat_id, "Invalid Email Format...")      

    bot.register_next_step_handler_by_chat_id(chat_id, getMail)



def handleLfile(bot, page, user_id, call, chat_id, msg_id):
    user = bot.dbuser.find_one({"_id": int(user_id)})

    if user:
        # Get the documents associated with the user
        documents = list(bot.dbfiles.find({"uploader": user["_id"]}))
        total_files = len(documents)
        per_page = 10
        total_pages = (len(documents) // per_page) + (1 if len(documents) % per_page > 0 else 0)

        # Paginate the results
        paginated_results = paginate_search_results(documents, page, per_page)

        # Generate response message
        response_message = f"Your {total_files} Files:\n\n"
        for idx, doc in enumerate(paginated_results):
            file_name = doc.get('fileName')
            unique_code = doc.get('uniqueCode')
            timestamp = doc.get('timestamp')

            if timestamp:
                file_time = datetime.fromtimestamp(timestamp / 1000)  # Convert from ms to seconds
                time_diff = humanize.naturaltime(datetime.now() - file_time)
            else:
                time_diff = "Once upon a time"

            response_message += f"{idx + 1}. [{file_name}](https://t.me/cybroxcloudbot?start=metadata_{unique_code}) - {time_diff}\n\n"

        response_message += f"\nPage {page} of {total_pages}"

        # Edit the message with updated content and pagination buttons
        bot.edit_message_text(response_message, chat_id=chat_id, message_id=msg_id, reply_markup=generate_pagination_buttons(page, total_pages, user_id), parse_mode='Markdown')

# Starting the process
"""
# Callback handler for pagination buttons
@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination(call):
    # Extract page number and user_id from callback data
    page, user_id = call.data.split('_')[1], call.data.split('_')[2]
    page = int(page)
    
    # Fetch user info based on user_id
   
"""