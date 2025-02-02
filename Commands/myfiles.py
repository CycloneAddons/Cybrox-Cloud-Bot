from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
import humanize
from datetime import datetime

name = "myfiles"

def execute(bot, message, chat_id, msgid=None, page=1):
    # Fetch the documents uploaded by the user
    documents = list(bot.dbfiles.find({"uploader": chat_id}))
    
    total_files = len(documents)  # Get the total number of files
    per_page = 10
    total_pages = (len(documents) // per_page) + (1 if len(documents) % per_page > 0 else 0)
    
    # Get paginated results for the current page
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
    
    # Generate pagination buttons
    pagination_buttons = generate_pagination_buttons(page, total_pages)
    
    try:
        if not msgid:
            bot.send_message(
                message.chat.id,
                response_message,
                parse_mode='Markdown',
                reply_markup=pagination_buttons
            )
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msgid,
                text=response_message,
                reply_markup=pagination_buttons,
                parse_mode="Markdown"
            )
    except ApiTelegramException as e:
        pass

def paginate_search_results(results, page=1, per_page=10):
    start_idx = (page - 1) * per_page
    return results[start_idx:start_idx + per_page]

def generate_pagination_buttons(current_page, total_pages):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("First", callback_data="mpage_1"),
            InlineKeyboardButton("Back", callback_data=f"mpage_{max(1, current_page - 1)}"),
            InlineKeyboardButton("Next", callback_data=f"mpage_{min(total_pages, current_page + 1)}"),
            InlineKeyboardButton("Last", callback_data=f"mpage_{total_pages}")
        ]
    ])
